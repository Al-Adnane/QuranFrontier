"""Neural Layer: Transformer-based embeddings for Arabic text and Quranic verses.

This module implements the neural component of the three-world architecture,
providing transformer-based embeddings with Arabic BPE tokenization.
"""

import torch
import torch.nn as nn
import math
from typing import Tuple, List, Optional


class ArabicBPETokenizer:
    """Byte-Pair Encoding tokenizer specialized for Arabic text."""

    def __init__(self, vocab_size: int = 1000, max_merges: int = 100):
        """Initialize Arabic BPE tokenizer.

        Args:
            vocab_size: Size of the vocabulary
            max_merges: Maximum number of merge operations for BPE
        """
        self.vocab_size = vocab_size
        self.max_merges = max_merges
        # Initialize with character-level vocabulary
        self.token_to_id = {}
        self.id_to_token = {}
        self._build_vocab()

    def _build_vocab(self):
        """Build initial character-level vocabulary."""
        # Arabic character ranges and special tokens
        special_tokens = ["<pad>", "<unk>", "<bos>", "<eos>", "<sep>"]
        for token in special_tokens:
            idx = len(self.token_to_id)
            self.token_to_id[token] = idx
            self.id_to_token[idx] = token

        # Add Arabic characters (simplified subset)
        arabic_chars = (
            "ابجدهوزحطيكلمنسعفصقرشتثخذضظغ"
            "ءةؤئأأىآاً هِهُّهَهـ"
            "0123456789"
            " .,;:!?"
        )
        for char in arabic_chars:
            if char not in self.token_to_id:
                idx = len(self.token_to_id)
                self.token_to_id[char] = idx
                self.id_to_token[idx] = char

    def tokenize(self, text: str) -> List[int]:
        """Tokenize Arabic text to token IDs.

        Args:
            text: Arabic text to tokenize

        Returns:
            List of token IDs
        """
        # For simplicity, use character-level tokenization
        token_ids = []
        for char in text:
            if char in self.token_to_id:
                token_ids.append(self.token_to_id[char])
            else:
                # Use <unk> for unknown characters
                token_ids.append(self.token_to_id["<unk>"])
        return token_ids

    def decode(self, token_ids: List[int]) -> str:
        """Decode token IDs back to text.

        Args:
            token_ids: List of token IDs

        Returns:
            Decoded text
        """
        return "".join(
            self.id_to_token.get(tid, "<unk>") for tid in token_ids
        )


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer (adapted for sequence positions)."""

    def __init__(self, embedding_dim: int, max_seq_len: int = 512):
        """Initialize positional encoding.

        Args:
            embedding_dim: Dimension of embeddings
            max_seq_len: Maximum sequence length
        """
        super().__init__()
        self.embedding_dim = embedding_dim
        self.max_seq_len = max_seq_len

        # Create positional encoding matrix
        pe = torch.zeros(max_seq_len, embedding_dim)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, embedding_dim, 2).float()
            * -(math.log(10000.0) / embedding_dim)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        if embedding_dim % 2 == 1:
            pe[:, 1::2] = torch.cos(position * div_term[:-1])
        else:
            pe[:, 1::2] = torch.cos(position * div_term)

        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to embeddings.

        Args:
            x: Tensor of shape (batch_size, seq_len, embedding_dim)

        Returns:
            Tensor with positional encoding added
        """
        return x + self.pe[:, : x.size(1)]


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism."""

    def __init__(self, embedding_dim: int, num_heads: int = 4):
        """Initialize multi-head attention.

        Args:
            embedding_dim: Dimension of embeddings
            num_heads: Number of attention heads
        """
        super().__init__()
        assert embedding_dim % num_heads == 0, "embedding_dim must be divisible by num_heads"

        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.head_dim = embedding_dim // num_heads

        self.query = nn.Linear(embedding_dim, embedding_dim)
        self.key = nn.Linear(embedding_dim, embedding_dim)
        self.value = nn.Linear(embedding_dim, embedding_dim)
        self.fc_out = nn.Linear(embedding_dim, embedding_dim)

    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass for multi-head attention.

        Args:
            query: Query tensor
            key: Key tensor
            value: Value tensor
            mask: Attention mask (optional)

        Returns:
            Attention output
        """
        batch_size = query.shape[0]

        Q = self.query(query)
        K = self.key(key)
        V = self.value(value)

        # Split into multiple heads
        Q = Q.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)

        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))

        attention_weights = torch.softmax(scores, dim=-1)
        context = torch.matmul(attention_weights, V)

        # Concatenate heads
        context = context.transpose(1, 2).contiguous()
        context = context.view(batch_size, -1, self.embedding_dim)

        output = self.fc_out(context)
        return output


class FeedForwardNetwork(nn.Module):
    """Feed-forward network for transformer encoder."""

    def __init__(self, embedding_dim: int, hidden_dim: int = 512):
        """Initialize feed-forward network.

        Args:
            embedding_dim: Input/output dimension
            hidden_dim: Hidden layer dimension
        """
        super().__init__()
        self.fc1 = nn.Linear(embedding_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embedding_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input tensor

        Returns:
            Output tensor
        """
        return self.fc2(self.dropout(self.relu(self.fc1(x))))


class TransformerEncoderLayer(nn.Module):
    """Single transformer encoder layer."""

    def __init__(self, embedding_dim: int, num_heads: int = 4):
        """Initialize encoder layer.

        Args:
            embedding_dim: Embedding dimension
            num_heads: Number of attention heads
        """
        super().__init__()
        self.attention = MultiHeadAttention(embedding_dim, num_heads)
        self.feed_forward = FeedForwardNetwork(embedding_dim)
        self.norm1 = nn.LayerNorm(embedding_dim)
        self.norm2 = nn.LayerNorm(embedding_dim)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with residual connections.

        Args:
            x: Input tensor

        Returns:
            Output tensor
        """
        # Self-attention with residual connection
        attn_output = self.attention(x, x, x)
        x = self.norm1(x + self.dropout(attn_output))

        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))

        return x


class NeuralLayer(nn.Module):
    """Neural embedding layer for the three-world architecture.

    Uses transformer-based architecture with Arabic BPE tokenization
    to produce semantic embeddings for Quranic verses and Islamic texts.
    """

    def __init__(
        self,
        vocab_size: int = 1000,
        embedding_dim: int = 128,
        num_heads: int = 4,
        num_layers: int = 2,
        max_seq_len: int = 512,
    ):
        """Initialize neural layer.

        Args:
            vocab_size: Size of vocabulary
            embedding_dim: Dimension of embeddings
            num_heads: Number of attention heads
            num_layers: Number of transformer encoder layers
            max_seq_len: Maximum sequence length
        """
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len

        # Tokenizer
        self.tokenizer = ArabicBPETokenizer(vocab_size)

        # Embeddings
        self.token_embedding = nn.Embedding(vocab_size, embedding_dim)
        self.positional_encoding = PositionalEncoding(embedding_dim, max_seq_len)

        # Transformer encoder layers
        self.encoder_layers = nn.ModuleList([
            TransformerEncoderLayer(embedding_dim, num_heads)
            for _ in range(num_layers)
        ])

        self.dropout = nn.Dropout(0.1)

    def tokenize(self, text: str) -> torch.Tensor:
        """Tokenize Arabic text using BPE.

        Args:
            text: Arabic text to tokenize

        Returns:
            Tensor of token IDs
        """
        token_ids = self.tokenizer.tokenize(text)
        # Pad or truncate to max_seq_len
        if len(token_ids) < self.max_seq_len:
            token_ids = token_ids + [0] * (self.max_seq_len - len(token_ids))
        else:
            token_ids = token_ids[:self.max_seq_len]
        return torch.tensor(token_ids, dtype=torch.long).unsqueeze(0)

    def embed(self, token_ids: torch.Tensor) -> torch.Tensor:
        """Embed token IDs to continuous vectors.

        Args:
            token_ids: Tensor of shape (batch_size, seq_len)

        Returns:
            Embeddings of shape (batch_size, seq_len, embedding_dim)
        """
        return self.token_embedding(token_ids)

    def get_position_embeddings(self, seq_len: int) -> torch.Tensor:
        """Get positional embeddings for a sequence.

        Args:
            seq_len: Sequence length

        Returns:
            Position embeddings of shape (1, seq_len, embedding_dim)
        """
        zeros = torch.zeros(1, seq_len, self.embedding_dim)
        return self.positional_encoding(zeros)

    def attention(self, hidden: torch.Tensor) -> torch.Tensor:
        """Apply multi-head self-attention.

        Args:
            hidden: Hidden states of shape (batch_size, seq_len, embedding_dim)

        Returns:
            Attended output
        """
        attention_layer = self.encoder_layers[0].attention
        return attention_layer(hidden, hidden, hidden)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        """Forward pass through encoder.

        Args:
            token_ids: Tensor of shape (batch_size, seq_len)

        Returns:
            Encoded embeddings of shape (batch_size, seq_len, embedding_dim)
        """
        # Embed tokens
        x = self.embed(token_ids)

        # Add positional encoding
        x = self.positional_encoding(x)

        # Apply dropout
        x = self.dropout(x)

        # Apply transformer encoder layers
        for layer in self.encoder_layers:
            x = layer(x)

        return x

    def encode_verse(self, verse: str) -> torch.Tensor:
        """Encode a Quranic verse to embeddings.

        Args:
            verse: Arabic verse text

        Returns:
            Verse embeddings of shape (seq_len, embedding_dim)
        """
        token_ids = self.tokenize(verse)
        embeddings = self.forward(token_ids)
        # Remove batch dimension and padding
        return embeddings.squeeze(0)
