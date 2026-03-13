"""p-adic Neural Network - Non-Archimedean Machine Learning.

Inspired by: p-adic number theory and ultrametric spaces

Key insights:
- p-adic numbers use different metric than reals
- Strong triangle inequality: |x + y| ≤ max(|x|, |y|)
- Natural for hierarchical structures
- Different notion of "closeness"

Architecture:
    p-adic Embedding: Map to p-adic space
    Ultrametric Distance: Compute p-adic distances
    Hierarchical Aggregation: Tree-structured computation
    p-adic Activation: Non-Archimedean activation functions
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


def p_adic_norm(x: torch.Tensor, p: int = 2) -> torch.Tensor:
    """Compute p-adic norm of tensor.
    
    For p-adic numbers, the norm is based on divisibility by p.
    Simplified: use valuation-based norm.
    """
    # Simplified p-adic norm approximation
    # In practice, would compute p-adic valuation
    return torch.abs(x)


def ultrametric_distance(x: torch.Tensor, y: torch.Tensor, p: int = 2) -> torch.Tensor:
    """Compute ultrametric (p-adic) distance.
    
    Strong triangle inequality: d(x, z) ≤ max(d(x, y), d(y, z))
    """
    diff = x - y
    return p_adic_norm(diff, p)


class PAdicEmbedding(nn.Module):
    """Embed into p-adic space."""
    
    def __init__(self, vocab_size: int, embed_dim: int, p: int = 2):
        super().__init__()
        
        self.p = p
        self.embed_dim = embed_dim
        
        # Standard embedding
        self.embed = nn.Embedding(vocab_size, embed_dim)
        
        # p-adic scaling (learnable)
        self.p_adic_scale = nn.Parameter(torch.ones(embed_dim))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Embed and scale to p-adic space."""
        embedded = self.embed(x)
        
        # Apply p-adic scaling
        scaled = embedded * self.p_adic_scale
        
        return scaled


class UltrametricAttention(nn.Module):
    """Attention using ultrametric distances."""
    
    def __init__(self, embed_dim: int, num_heads: int = 4, p: int = 2):
        super().__init__()
        
        self.p = p
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        
        # Query, Key, Value projections
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        
        # Output projection
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Apply ultrametric attention."""
        batch_size, seq_len, embed_dim = x.shape
        
        # Project to Q, K, V
        q = self.q_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Compute ultrametric distances instead of dot products
        # d(q, k) = max(|q_i - k_i|) over dimensions
        q_expanded = q.unsqueeze(3)  # [batch, heads, seq, 1, head_dim]
        k_expanded = k.unsqueeze(2)  # [batch, heads, 1, seq, head_dim]
        
        # Ultrametric distance: max over dimensions
        distances = ultrametric_distance(q_expanded, k_expanded, self.p).max(dim=-1)[0]
        
        # Convert to attention weights (closer = higher weight)
        attention_weights = F.softmax(-distances, dim=-1)
        
        if mask is not None:
            attention_weights = attention_weights.masked_fill(mask == 0, 0)
        
        # Apply attention to values
        attended = torch.matmul(attention_weights, v)
        
        # Reshape and project
        attended = attended.transpose(1, 2).contiguous().view(batch_size, seq_len, embed_dim)
        output = self.out_proj(attended)
        
        return output


class HierarchicalAggregation(nn.Module):
    """Aggregate using tree structure (natural for p-adic)."""
    
    def __init__(self, embed_dim: int, tree_depth: int = 4):
        super().__init__()
        
        self.tree_depth = tree_depth
        self.embed_dim = embed_dim
        
        # Aggregation at each level
        self.aggregation_layers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embed_dim * 2, embed_dim),
                nn.GELU()
            )
            for _ in range(tree_depth)
        ])
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Aggregate hierarchically."""
        batch_size, seq_len, embed_dim = x.shape
        
        # Pad to power of 2
        padded_len = 2 ** (seq_len - 1).bit_length()
        if padded_len > seq_len:
            padding = torch.zeros(batch_size, padded_len - seq_len, embed_dim, device=x.device)
            x = torch.cat([x, padding], dim=1)
            seq_len = padded_len
        
        # Hierarchical aggregation
        current = x
        
        for layer in self.aggregation_layers:
            if current.size(1) >= 2:
                # Pair adjacent elements
                even = current[:, ::2, :]
                odd = current[:, 1::2, :]
                paired = torch.cat([even, odd], dim=-1)
                current = layer(paired)
        
        # Global representation
        if current.size(1) > 0:
            global_repr = current.mean(dim=1)
        else:
            global_repr = current.mean(dim=1)
        
        return global_repr


class PAdicActivation(nn.Module):
    """p-adic inspired activation function."""
    
    def __init__(self, p: int = 2):
        super().__init__()
        self.p = p
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply p-adic activation.
        
        Uses ultrametric property: values cluster at discrete levels.
        """
        # Discretize based on p-adic valuation
        # Simplified: use log-scale quantization
        magnitude = torch.abs(x)
        sign = torch.sign(x)
        
        # Quantize to p-adic levels
        log_magnitude = torch.log(magnitude + 1e-9) / torch.log(torch.tensor(float(self.p)))
        quantized_level = torch.floor(log_magnitude)
        
        # Reconstruct
        reconstructed = torch.pow(self.p, quantized_level) * sign
        
        return reconstructed


class PAdicNeuralNetwork(nn.Module):
    """Complete p-adic Neural Network.
    
    Applications:
    - Hierarchical data modeling
    - Tree-structured representations
    - Ultrametric clustering
    - Non-Archimedean reasoning
    """
    
    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 128,
        hidden_dim: int = 256,
        num_heads: int = 4,
        tree_depth: int = 4,
        p: int = 2
    ):
        super().__init__()
        
        self.p = p
        
        # Embedding
        self.embedding = PAdicEmbedding(vocab_size, embed_dim, p)
        
        # Ultrametric attention
        self.attention = UltrametricAttention(embed_dim, num_heads, p)
        
        # Feed-forward with p-adic activation
        self.feed_forward = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            PAdicActivation(p),
            nn.Linear(hidden_dim, embed_dim)
        )
        
        # Hierarchical aggregation
        self.hierarchical_agg = HierarchicalAggregation(embed_dim, tree_depth)
        
        # Layer norms
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        
        # Output
        self.output_proj = nn.Linear(embed_dim, embed_dim)
        
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Dict:
        """Process through p-adic network.
        
        Args:
            x: [batch, seq_len] token IDs
            mask: Optional [batch, seq_len] attention mask
        Returns:
            Dict with representations and ultrametric structure
        """
        # Embed
        h = self.embedding(x)
        
        # Ultrametric attention
        attended = self.attention(h, mask)
        h = self.norm1(h + attended)
        
        # Feed-forward
        ff_output = self.feed_forward(h)
        h = self.norm2(h + ff_output)
        
        # Hierarchical aggregation
        global_repr = self.hierarchical_agg(h)
        
        # Output
        output = self.output_proj(global_repr)
        
        # Compute ultrametric structure (for analysis)
        ultrametric_structure = self._compute_ultrametric_structure(h)
        
        return {
            'output': output,
            'token_reprs': h,
            'global_repr': global_repr,
            'ultrametric_structure': ultrametric_structure,
            'p': self.p
        }
    
    def _compute_ultrametric_structure(
        self,
        h: torch.Tensor
    ) -> torch.Tensor:
        """Compute ultrametric distance matrix."""
        batch_size, seq_len, embed_dim = h.shape
        
        # Compute pairwise ultrametric distances
        h_expanded1 = h.unsqueeze(2)  # [batch, seq, 1, dim]
        h_expanded2 = h.unsqueeze(1)  # [batch, 1, seq, dim]
        
        distances = ultrametric_distance(h_expanded1, h_expanded2, self.p)
        
        return distances


    @classmethod
    def self_test(cls) -> bool:
        """Create model, run forward pass, assert output shapes."""
        model = cls(vocab_size=100, embed_dim=32, hidden_dim=64, num_heads=4, tree_depth=3, p=2)
        model.eval()
        x = torch.randint(0, 100, (2, 8))
        with torch.no_grad():
            result = model(x)
        assert result['output'].shape == (2, 32), f"output shape {result['output'].shape}"
        assert result['global_repr'].shape == (2, 32), f"global shape {result['global_repr'].shape}"
        assert result['p'] == 2
        print("PAdicNeuralNetwork self_test PASSED")
        return True


def create_p_adic_network(
    vocab_size: int = 10000,
    embed_dim: int = 128,
    hidden_dim: int = 256,
    p: int = 2
) -> PAdicNeuralNetwork:
    """Create PAdicNeuralNetwork."""
    return PAdicNeuralNetwork(vocab_size, embed_dim, hidden_dim, p=p)
