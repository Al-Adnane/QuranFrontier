"""Sarf Group Network - Arabic Morphology as Group Action.

This model treats Arabic morphological derivation as a group action:
    word = pattern ⊗ root

where ⊗ is the morphological product. The model learns continuous
representations of roots and patterns, with morphological operations
as group transformations.

Architecture:
    Root Encoder: Trilateral root → embedding
    Pattern Encoder: Morphological pattern → embedding  
    Group Action: pattern_embedding ⊗ root_embedding → word_embedding
    Decoder: word_embedding → surface form

Based on frontierqu.linguistic.sarf for morphological rules.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass
import math


# Arabic morphological patterns (from sarf.py)
VERB_PATTERNS = {
    "فَعَلَ": {"form": 1, "meaning": "basic_action"},
    "فَعَّلَ": {"form": 2, "meaning": "intensive_causative"},
    "فَاعَلَ": {"form": 3, "meaning": "reciprocal"},
    "أَفْعَلَ": {"form": 4, "meaning": "causative"},
    "تَفَعَّلَ": {"form": 5, "meaning": "reflexive_intensive"},
    "تَفَاعَلَ": {"form": 6, "meaning": "reciprocal_reflexive"},
    "اِنْفَعَلَ": {"form": 7, "meaning": "passive"},
    "اِفْتَعَلَ": {"form": 8, "meaning": "reflexive"},
    "اِفْعَلَّ": {"form": 9, "meaning": "colors_defects"},
    "اِسْتَفْعَلَ": {"form": 10, "meaning": "seeking"},
}

NOUN_PATTERNS = {
    "فِعَال": "verbal_noun",
    "فَعِيل": "adjective_intensive",
    "فَاعِل": "active_participle",
    "مَفْعُول": "passive_participle",
    "فُعُول": "broken_plural",
    "أَفْعَال": "broken_plural",
    "مَفْعَل": "place_instrument",
    "فِعَالَة": "profession",
}


@dataclass
class MorphologicalAnalysis:
    """Morphological analysis result."""
    word: str
    root: str
    pattern: str
    pos: str
    form: Optional[int]
    meaning_class: str
    root_embedding: torch.Tensor
    pattern_embedding: torch.Tensor
    confidence: float


class RootEncoder(nn.Module):
    """Encodes trilateral roots to embeddings."""
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 256,
        num_letters: int = 28  # Arabic letters
    ):
        super().__init__()
        
        # Letter embeddings
        self.letter_embed = nn.Embedding(num_letters + 1, embed_dim, padding_idx=0)
        
        # Position embeddings for root positions (ف, ع, ل)
        self.pos_embed = nn.Parameter(torch.randn(3, embed_dim) * 0.1)
        
        # Root encoder
        self.root_encoder = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim * 2),
            nn.GELU(),
            nn.LayerNorm(embed_dim * 2),
            nn.Linear(embed_dim * 2, embed_dim)
        )
        
        # Root type embeddings (strong, weak, geminated, etc.)
        self.root_type_embed = nn.Embedding(5, embed_dim)
        
    def forward(
        self,
        root_letters: torch.Tensor,
        root_type: torch.Tensor
    ) -> torch.Tensor:
        """Encode root to embedding.
        
        Args:
            root_letters: [batch, 3] letter indices
            root_type: [batch] root type index
        Returns:
            root_embedding: [batch, embed_dim]
        """
        # Letter embeddings with positional encoding
        letter_emb = self.letter_embed(root_letters)  # [batch, 3, embed_dim]
        letter_emb = letter_emb + self.pos_embed.unsqueeze(0)
        
        # Flatten and encode
        letter_flat = letter_emb.view(letter_emb.size(0), -1)
        root_emb = self.root_encoder(letter_flat)
        
        # Add root type
        type_emb = self.root_type_embed(root_type)
        root_emb = root_emb + type_emb
        
        return root_emb


class PatternEncoder(nn.Module):
    """Encodes morphological patterns to embeddings."""
    
    def __init__(
        self,
        num_patterns: int,
        embed_dim: int = 256
    ):
        super().__init__()
        
        # Pattern embeddings
        self.pattern_embed = nn.Embedding(num_patterns, embed_dim)
        
        # Pattern type (verb/noun)
        self.type_embed = nn.Embedding(2, embed_dim)  # 0=verb, 1=noun
        
        # Form embeddings (I-X for verbs)
        self.form_embed = nn.Embedding(11, embed_dim)  # 0-10
        
        # Meaning class embeddings
        self.meaning_embed = nn.Embedding(20, embed_dim)
        
    def forward(
        self,
        pattern_id: torch.Tensor,
        pattern_type: torch.Tensor,
        form: torch.Tensor,
        meaning_class: torch.Tensor
    ) -> torch.Tensor:
        """Encode pattern to embedding.
        
        Args:
            pattern_id: [batch] pattern index
            pattern_type: [batch] 0=verb, 1=noun
            form: [batch] morphological form
            meaning_class: [batch] semantic class
        Returns:
            pattern_embedding: [batch, embed_dim]
        """
        emb = (
            self.pattern_embed(pattern_id) +
            self.type_embed(pattern_type) +
            self.form_embed(form) +
            self.meaning_embed(meaning_class)
        )
        return emb


class MorphologicalGroupAction(nn.Module):
    """Implements morphological group action: pattern ⊗ root → word."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Group action parameters
        # Pattern acts as transformation on root
        self.action_matrix = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim * 2),
            nn.GELU(),
            nn.Linear(embed_dim * 2, embed_dim)
        )
        
        # Vowel melody injection
        self.vowel_injector = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.Sigmoid()
        )
        
        # Template filler
        self.template_filler = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.Tanh()
        )
        
    def forward(
        self,
        root_emb: torch.Tensor,
        pattern_emb: torch.Tensor
    ) -> torch.Tensor:
        """Apply morphological group action.
        
        Args:
            root_emb: [batch, embed_dim]
            pattern_emb: [batch, embed_dim]
        Returns:
            word_emb: [batch, embed_dim]
        """
        # Concatenate root and pattern
        combined = torch.cat([root_emb, pattern_emb], dim=-1)
        
        # Apply group action
        word_emb = self.action_matrix(combined)
        
        # Modulate by pattern (vowel melody)
        vowel_mask = self.vowel_injector(pattern_emb)
        word_emb = word_emb * vowel_mask
        
        # Template filling
        template = self.template_filler(combined)
        word_emb = word_emb + template
        
        return word_emb


class WordDecoder(nn.Module):
    """Decodes word embeddings to surface forms."""
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 256,
        max_word_length: int = 10
    ):
        super().__init__()
        
        self.embed_dim = embed_dim
        self.max_word_length = max_word_length
        
        # Character-level decoder
        self.char_decoder = nn.LSTM(
            input_size=embed_dim,
            hidden_size=256,
            num_layers=2,
            batch_first=True
        )
        
        # Output projection
        self.char_head = nn.Linear(256, vocab_size)
        
    def forward(
        self,
        word_emb: torch.Tensor,
        target_chars: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Decode word embedding to character sequence.
        
        Args:
            word_emb: [batch, embed_dim]
            target_chars: Optional [batch, seq_len] for training
        Returns:
            char_logits: [batch, seq_len, vocab_size]
        """
        batch_size = word_emb.size(0)
        
        # Use word embedding as initial hidden state
        h0 = word_emb.unsqueeze(0).expand(2, -1, -1)
        c0 = word_emb.unsqueeze(0).expand(2, -1, -1)
        
        # Generate characters
        if target_chars is not None:
            # Teacher forcing during training
            char_emb = torch.zeros(
                batch_size, self.max_word_length, self.embed_dim,
                device=word_emb.device
            )
            char_emb[:, 0, :] = word_emb
            
            output, _ = self.char_decoder(char_emb, (h0, c0))
            char_logits = self.char_head(output)
        else:
            # Autoregressive generation
            char_logits = []
            char_input = word_emb.unsqueeze(1)
            hidden = (h0, c0)
            
            for _ in range(self.max_word_length):
                output, hidden = self.char_decoder(char_input, hidden)
                logits = self.char_head(output)
                char_logits.append(logits)
                
                # Greedy decoding
                next_char = logits.argmax(dim=-1)
                char_input = char_input.new_zeros(batch_size, 1, self.embed_dim)
            
            char_logits = torch.cat(char_logits, dim=1)
        
        return char_logits


class SarfGroupNetwork(nn.Module):
    """Main Sarf Group Network model.
    
    Learns morphological derivation as group action:
        word = pattern ⊗ root
    """
    
    def __init__(
        self,
        vocab_size: int,
        num_letters: int = 28,
        num_patterns: int = 50,
        embed_dim: int = 256
    ):
        super().__init__()
        
        self.root_encoder = RootEncoder(vocab_size, embed_dim, num_letters)
        self.pattern_encoder = PatternEncoder(num_patterns, embed_dim)
        self.group_action = MorphologicalGroupAction(embed_dim)
        self.word_decoder = WordDecoder(vocab_size, embed_dim)
        
        # Classification heads
        self.pos_head = nn.Linear(embed_dim, 4)  # noun, verb, particle, proper_noun
        self.form_head = nn.Linear(embed_dim, 11)  # Form 0-X
        self.meaning_head = nn.Linear(embed_dim, 20)  # Semantic classes
        
        # Root extraction head
        self.root_extractor = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, num_letters * 3)
        )
        
        self.vocab_size = vocab_size
        self.num_letters = num_letters
        
    def analyze(
        self,
        word: str,
        token_ids: List[int]
    ) -> MorphologicalAnalysis:
        """Analyze a word morphologically.
        
        Args:
            word: Surface form
            token_ids: Token indices
        Returns:
            MorphologicalAnalysis
        """
        self.eval()
        
        with torch.no_grad():
            # Encode word
            word_emb = self._encode_word(token_ids)
            
            # Predict POS
            pos_logits = self.pos_head(word_emb)
            pos_id = pos_logits.argmax().item()
            pos_map = ['noun', 'verb', 'particle', 'proper_noun']
            
            # Predict form
            form_logits = self.form_head(word_emb)
            form_id = form_logits.argmax().item()
            
            # Predict meaning
            meaning_logits = self.meaning_head(word_emb)
            meaning_id = meaning_logits.argmax().item()
            
            # Extract root
            root_logits = self.root_extractor(word_emb)
            root_logits = root_logits.view(-1, 3, self.num_letters)
            root_letters = root_logits.argmax(dim=-1)[0].tolist()
            
            # Decode root letters
            root = self._decode_root(root_letters)
            
            # Get pattern
            pattern = self._get_pattern(pos_id, form_id)
            
            # Get embeddings
            root_tensor = torch.tensor([root_letters], dtype=torch.long)
            root_emb = self.root_encoder(
                root_tensor,
                torch.zeros(1, dtype=torch.long)
            )[0]
            
            pattern_tensor = torch.tensor([form_id], dtype=torch.long)
            pattern_emb = self.pattern_encoder(
                pattern_tensor,
                torch.tensor([1 if pos_id == 0 else 0]),
                torch.tensor([form_id]),
                torch.tensor([meaning_id])
            )[0]
            
            # Compute confidence
            pos_conf = F.softmax(pos_logits, dim=-1).max().item()
            form_conf = F.softmax(form_logits, dim=-1).max().item()
            confidence = (pos_conf + form_conf) / 2
            
            return MorphologicalAnalysis(
                word=word,
                root=root,
                pattern=pattern,
                pos=pos_map[pos_id],
                form=form_id if pos_id == 1 else None,
                meaning_class=str(meaning_id),
                root_embedding=root_emb,
                pattern_embedding=pattern_emb,
                confidence=confidence
            )
    
    def _encode_word(self, token_ids: List[int]) -> torch.Tensor:
        """Encode word to embedding."""
        input_ids = torch.tensor([token_ids], dtype=torch.long)
        
        # Simple mean pooling of token embeddings
        # In practice would use more sophisticated encoding
        with torch.no_grad():
            emb = self.root_encoder.letter_embed(torch.clamp(input_ids, 0, self.num_letters))
            return emb.mean(dim=1)
    
    def _decode_root(self, root_letters: List[int]) -> str:
        """Decode root letter indices to string."""
        # Placeholder - would need actual letter mapping
        arabic_letters = "ءابتثجحخدذرزسشصضطظعغفقكلمنهوي"
        return ''.join(arabic_letters[i-1] if i > 0 else '' for i in root_letters)
    
    def _get_pattern(self, pos_id: int, form_id: int) -> str:
        """Get pattern string from predictions."""
        if pos_id == 1:  # Verb
            patterns = list(VERB_PATTERNS.keys())
            if form_id < len(patterns):
                return patterns[form_id]
        else:  # Noun
            patterns = list(NOUN_PATTERNS.keys())
            if form_id < len(patterns):
                return patterns[form_id]
        return "فَعَلَ"
    
    def forward(
        self,
        root_letters: torch.Tensor,
        root_type: torch.Tensor,
        pattern_id: torch.Tensor,
        pattern_type: torch.Tensor,
        form: torch.Tensor,
        meaning_class: torch.Tensor,
        target_word: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """Forward pass.
        
        Args:
            root_letters: [batch, 3]
            root_type: [batch]
            pattern_id: [batch]
            pattern_type: [batch]
            form: [batch]
            meaning_class: [batch]
            target_word: Optional [batch, seq_len] for training
        Returns:
            Dict with predictions and loss
        """
        # Encode root and pattern
        root_emb = self.root_encoder(root_letters, root_type)
        pattern_emb = self.pattern_encoder(pattern_id, pattern_type, form, meaning_class)
        
        # Apply group action
        word_emb = self.group_action(root_emb, pattern_emb)
        
        # Decode to surface form
        char_logits = self.word_decoder(word_emb, target_word)
        
        # Classification heads
        pos_logits = self.pos_head(word_emb)
        form_logits = self.form_head(word_emb)
        meaning_logits = self.meaning_head(word_emb)
        
        result = {
            'char_logits': char_logits,
            'pos_logits': pos_logits,
            'form_logits': form_logits,
            'meaning_logits': meaning_logits,
            'word_embedding': word_emb
        }
        
        if target_word is not None:
            result['generation_loss'] = F.cross_entropy(
                char_logits.view(-1, self.vocab_size),
                target_word.view(-1),
                ignore_index=0
            )
        
        return result
    
    def generate_word(
        self,
        root: str,
        pattern_name: str,
        form: Optional[int] = None
    ) -> str:
        """Generate word from root and pattern.
        
        Args:
            root: Trilateral root (e.g., "كتب")
            pattern_name: Pattern name (e.g., "فَعَلَ")
            form: Optional form number
        Returns:
            Generated word
        """
        self.eval()
        
        # Convert root to indices
        arabic_letters = "ءابتثجحخدذرزسشصضطظعغفقكلمنهوي"
        letter_to_idx = {c: i+1 for i, c in enumerate(arabic_letters)}
        
        root_indices = [letter_to_idx.get(c, 0) for c in root[:3]]
        while len(root_indices) < 3:
            root_indices.append(0)
        
        root_tensor = torch.tensor([root_indices], dtype=torch.long)
        root_type = torch.zeros(1, dtype=torch.long)
        
        # Get pattern index
        pattern_idx = list(VERB_PATTERNS.keys()).index(pattern_name) if pattern_name in VERB_PATTERNS else 0
        pattern_id = torch.tensor([pattern_idx], dtype=torch.long)
        pattern_type = torch.tensor([1 if pattern_name in NOUN_PATTERNS else 0], dtype=torch.long)
        form_tensor = torch.tensor([form if form else 1], dtype=torch.long)
        meaning_tensor = torch.zeros(1, dtype=torch.long)
        
        # Generate
        with torch.no_grad():
            root_emb = self.root_encoder(root_tensor, root_type)
            pattern_emb = self.pattern_encoder(
                pattern_id, pattern_type, form_tensor, meaning_tensor
            )
            word_emb = self.group_action(root_emb, pattern_emb)
            char_logits = self.word_decoder(word_emb)
            
            # Decode characters
            chars = char_logits.argmax(dim=-1)[0].tolist()
            
        return self._decode_root(chars[:3])


def create_sarf_model(
    vocab_size: int = 30000,
    num_patterns: int = 50,
    embed_dim: int = 256
) -> SarfGroupNetwork:
    """Create SarfGroupNetwork model."""
    return SarfGroupNetwork(
        vocab_size=vocab_size,
        num_patterns=num_patterns,
        embed_dim=embed_dim
    )
