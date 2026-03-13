"""I Ching Network - Hexagram State Transitions.

Inspired by: I Ching (Book of Changes)

Key insights:
- 64 hexagrams (6-line figures)
- Changing lines create transitions
- Nuclear hexagrams (inner structure)
- Temporal dynamics of change

Architecture:
    Hexagram Encoding: 6-line binary representation
    Line Interpretation: Each line has meaning
    State Transition: Changing lines create new hexagrams
    Nuclear Structure: Inner hexagram extraction
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class HexagramState:
    """State of a hexagram."""
    lines: torch.Tensor           # 6 binary lines
    hexagram_index: torch.Tensor  # 0-63
    nuclear: torch.Tensor         # Nuclear hexagram
    changing_lines: torch.Tensor  # Which lines are changing


class HexagramEncoder(nn.Module):
    """Encode 64 hexagrams."""
    
    def __init__(self, hex_dim: int = 256):
        super().__init__()
        
        self.hex_dim = hex_dim
        
        # 64 hexagram embeddings
        self.hexagram_embed = nn.Embedding(64, hex_dim)
        
        # Line embeddings (each of 6 positions has meaning)
        self.line_position_embed = nn.Embedding(6, hex_dim // 6)
        
        # Binary to hexagram index
        self.binary_to_hex = nn.Linear(6, 64, bias=False)
        with torch.no_grad():
            for i in range(64):
                binary = torch.zeros(6)
                for j in range(6):
                    binary[j] = (i >> j) & 1
                self.binary_to_hex.weight.data[i] = binary
        
    def forward(self, lines: torch.Tensor) -> HexagramState:
        """Encode hexagram from lines."""
        batch_size = lines.size(0)
        
        # Ensure 6 lines
        if lines.size(-1) != 6:
            lines = lines[:, :6]
        
        # Convert to long for indexing
        lines_long = lines.long()
        
        # Get hexagram index from binary
        hex_index = (
            lines_long[:, 0] * 1 +
            lines_long[:, 1] * 2 +
            lines_long[:, 2] * 4 +
            lines_long[:, 3] * 8 +
            lines_long[:, 4] * 16 +
            lines_long[:, 5] * 32
        )
        
        # Get hexagram embedding
        hexagram_emb = self.hexagram_embed(hex_index)
        
        # Line position embeddings
        line_embs = self.line_position_embed(torch.arange(6, device=lines.device))
        line_embs = line_embs.unsqueeze(0).expand(batch_size, -1, -1)
        
        # Compute nuclear hexagram (lines 2-5 form inner hexagram)
        nuclear_lines = lines[:, 1:5]  # Lines 2-5
        nuclear_upper = lines[:, 3:6]  # Lines 4-6 (upper trigram)
        nuclear_lower = lines[:, 0:3]  # Lines 1-3 (lower trigram)
        
        # Nuclear hexagram
        nuclear = torch.cat([nuclear_lower, nuclear_upper], dim=-1)
        
        return HexagramState(
            lines=lines,
            hexagram_index=hex_index,
            nuclear=nuclear,
            changing_lines=torch.zeros_like(lines)
        )


class LineInterpreter(nn.Module):
    """Interpret individual lines of hexagram."""
    
    def __init__(self, hex_dim: int = 256):
        super().__init__()
        
        # Line-specific interpretations
        self.line_interpreters = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hex_dim, hex_dim),
                nn.GELU(),
                nn.Linear(hex_dim, hex_dim)
            )
            for _ in range(6)
        ])
        
        # Line position importance
        self.position_importance = nn.Parameter(torch.ones(6))
        
    def forward(self, hexagram_emb: torch.Tensor, lines: torch.Tensor) -> Dict:
        """Interpret each line."""
        line_interpretations = []
        
        for i, interpreter in enumerate(self.line_interpreters):
            # Get line-specific interpretation
            line_emb = interpreter(hexagram_emb)
            
            # Weight by line value (yin/yang)
            line_weight = lines[:, i:i+1]
            weighted_emb = line_emb * line_weight
            
            line_interpretations.append(weighted_emb)
        
        # Combine with position importance
        importance = F.softmax(self.position_importance, dim=0)
        combined = sum(
            interp * importance[i]
            for i, interp in enumerate(line_interpretations)
        )
        
        return {
            'line_interpretations': line_interpretations,
            'position_importance': importance,
            'combined': combined
        }


class HexagramTransition(nn.Module):
    """Model transitions between hexagrams via changing lines."""
    
    def __init__(self, hex_dim: int = 256):
        super().__init__()
        
        # Transition dynamics
        self.transition_network = nn.Sequential(
            nn.Linear(hex_dim * 2, 512),
            nn.GELU(),
            nn.Linear(512, hex_dim)
        )
        
        # Changing line detector
        self.changing_detector = nn.Sequential(
            nn.Linear(hex_dim, 256),
            nn.GELU(),
            nn.Linear(256, 6),
            nn.Sigmoid()
        )
        
        # Result hexagram predictor
        self.result_predictor = nn.Linear(hex_dim, 64)
        
    def forward(
        self,
        current_hex: HexagramState,
        hexagram_emb: torch.Tensor
    ) -> Dict:
        """Compute transition to new hexagram."""
        # Detect changing lines
        changing_probs = self.changing_detector(hexagram_emb)
        
        # Apply changing lines
        new_lines = current_hex.lines.clone()
        for i in range(6):
            # If line is changing (prob > 0.5), flip it
            flip_mask = changing_probs[:, i:i+1] > 0.5
            new_lines[:, i:i+1] = torch.where(
                flip_mask,
                1 - new_lines[:, i:i+1],
                new_lines[:, i:i+1]
            )
        
        # Encode new hexagram
        new_hex_index_logits = self.result_predictor(hexagram_emb)
        new_hex_index = F.softmax(new_hex_index_logits, dim=-1).argmax(dim=-1)
        
        # Transition embedding
        transition_input = torch.cat([
            hexagram_emb,
            torch.zeros_like(hexagram_emb)  # Placeholder for target
        ], dim=-1)
        transition_emb = self.transition_network(transition_input)
        
        return {
            'original_lines': current_hex.lines,
            'new_lines': new_lines,
            'changing_probs': changing_probs,
            'new_hex_index': new_hex_index,
            'transition_emb': transition_emb
        }


class TrigramProcessor(nn.Module):
    """Process upper and lower trigrams."""
    
    def __init__(self, hex_dim: int = 256):
        super().__init__()
        
        # 8 trigram embeddings
        self.trigram_embed = nn.Embedding(8, hex_dim // 2)
        
        # Trigram relationships
        self.relationship_network = nn.Sequential(
            nn.Linear(hex_dim, 256),
            nn.GELU(),
            nn.Linear(256, hex_dim)
        )
        
    def forward(self, lines: torch.Tensor) -> Dict:
        """Process trigrams."""
        # Upper trigram (lines 4-6)
        upper_lines = lines[:, 3:6]
        upper_index = (upper_lines[:, 0] * 4 + upper_lines[:, 1] * 2 + upper_lines[:, 2]).long()
        
        # Lower trigram (lines 1-3)
        lower_lines = lines[:, 0:3]
        lower_index = (lower_lines[:, 0] * 4 + lower_lines[:, 1] * 2 + lower_lines[:, 2]).long()
        
        # Get trigram embeddings
        upper_emb = self.trigram_embed(upper_index)
        lower_emb = self.trigram_embed(lower_index)
        
        # Combine
        combined = torch.cat([upper_emb, lower_emb], dim=-1)
        relationship = self.relationship_network(combined)
        
        return {
            'upper_index': upper_index,
            'lower_index': lower_index,
            'upper_emb': upper_emb,
            'lower_emb': lower_emb,
            'relationship': relationship
        }


class IChingNetwork(nn.Module):
    """Complete I Ching Network for hexagram reasoning.
    
    Applications:
    - State transition modeling
    - Change and transformation
    - Binary-hierarchical reasoning
    - Temporal dynamics
    """
    
    def __init__(
        self,
        input_dim: int = 256,
        hex_dim: int = 256,
        hidden_dim: int = 512
    ):
        super().__init__()
        
        # Input projection
        self.input_proj = nn.Linear(input_dim, hex_dim)
        
        # Hexagram encoding
        self.hexagram_encoder = HexagramEncoder(hex_dim)
        
        # Line interpretation
        self.line_interpreter = LineInterpreter(hex_dim)
        
        # Trigram processing
        self.trigram_processor = TrigramProcessor(hex_dim)
        
        # State transition
        self.transition = HexagramTransition(hex_dim)
        
        # Judgment head
        self.judgment_head = nn.Sequential(
            nn.Linear(hex_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        x: torch.Tensor,
        compute_transition: bool = True
    ) -> Dict:
        """Process through I Ching reasoning.
        
        Args:
            x: [batch, input_dim] input
            compute_transition: Whether to compute state transition
        Returns:
            Dict with hexagram state and judgment
        """
        # Project input
        projected = self.input_proj(x)
        
        # Generate lines from input (6 binary lines)
        line_logits = projected.mean(dim=-1, keepdim=True).expand(-1, 6)
        line_logits = line_logits + torch.randn_like(line_logits) * 0.5
        lines = (torch.sigmoid(line_logits) > 0.5).float()
        
        # Encode hexagram
        hex_state = self.hexagram_encoder(lines)
        
        # Get hexagram embedding
        hexagram_emb = self.hexagram_encoder.hexagram_embed(hex_state.hexagram_index)
        
        # Interpret lines
        line_result = self.line_interpreter(hexagram_emb, lines)
        
        # Process trigrams
        trigram_result = self.trigram_processor(lines)
        
        # Compute transition
        transition_result = None
        if compute_transition:
            transition_result = self.transition(hex_state, hexagram_emb)
        
        # Judgment
        judgment_input = line_result['combined']
        if transition_result is not None:
            judgment_input = judgment_input + transition_result['transition_emb']
        
        judgment = self.judgment_head(judgment_input)
        
        return {
            'hex_state': hex_state,
            'line_result': line_result,
            'trigram_result': trigram_result,
            'transition_result': transition_result,
            'judgment': judgment
        }


def create_i_ching_network(
    input_dim: int = 256,
    hex_dim: int = 256,
    hidden_dim: int = 512
) -> IChingNetwork:
    """Create IChingNetwork."""
    return IChingNetwork(input_dim, hex_dim, hidden_dim)
