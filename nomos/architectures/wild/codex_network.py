"""Codex Network - Pictographic/Symbolic Visual Reasoning.

Inspired by: Mesoamerican Codices (Borgia, Borbonicus)

Key insights:
- Meaning encoded in visual symbols, not phonetic text
- Calendrical/temporal cycles embedded in structure
- Multiple interpretation layers (divinatory, ritual, cosmic)
- Symbols gain meaning from position and relationship
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional
from dataclasses import dataclass


class SymbolEmbedding(nn.Module):
    """Embed pictographic symbols with multiple meaning layers."""
    
    def __init__(self, num_symbols: int = 1000, embed_dim: int = 128, num_layers: int = 3):
        super().__init__()
        
        self.embed_dim = embed_dim
        self.num_layers = num_layers
        
        # Base symbol embedding
        self.symbol_embed = nn.Embedding(num_symbols, embed_dim)
        
        # Layer-specific meaning embeddings
        self.layer_embeds = nn.ModuleList([
            nn.Embedding(num_symbols, embed_dim) for _ in range(num_layers)
        ])
        
        # Calendar position embedding (260 day Tzolk'in)
        self.calendar_embed = nn.Embedding(260, embed_dim // 4)
        
        # Cosmic association embedding (20 day signs)
        self.cosmic_embed = nn.Embedding(20, embed_dim // 4)
        
    def forward(
        self,
        symbol_ids: torch.Tensor,
        layer: int = 0,
        calendar_pos: Optional[torch.Tensor] = None,
        cosmic_assoc: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Get multi-layered symbol embedding."""
        # Base + layer-specific meaning
        embed = self.symbol_embed(symbol_ids) + self.layer_embeds[layer](symbol_ids)
        
        # Add calendar context
        if calendar_pos is not None:
            cal_embed = self.calendar_embed(calendar_pos)
            embed = torch.cat([embed, cal_embed], dim=-1)
        
        # Add cosmic context
        if cosmic_assoc is not None:
            cosmic_embed = self.cosmic_embed(cosmic_assoc)
            embed = torch.cat([embed, cosmic_embed], dim=-1)
        
        return embed


class PositionalGrammar(nn.Module):
    """Compute meaning from spatial relationships between symbols."""
    
    def __init__(self, embed_dim: int = 128):
        super().__init__()
        
        self.embed_dim = embed_dim
        self.relation_types = 6
        
        # Learn relationship transformations
        self.relation_transforms = nn.ModuleList([
            nn.Linear(embed_dim, embed_dim) for _ in range(self.relation_types)
        ])
        
    def forward(
        self,
        symbols: torch.Tensor,  # [batch, num_symbols, embed_dim]
        positions: torch.Tensor  # [batch, num_symbols, 2]
    ) -> torch.Tensor:
        """Compute meaning from spatial grammar."""
        batch_size, num_symbols, embed_dim = symbols.shape
        
        # Compute pairwise relationships
        transformed = symbols.clone()
        
        for b in range(batch_size):
            for i in range(num_symbols):
                for j in range(num_symbols):
                    if i != j:
                        dx = positions[b, j, 0] - positions[b, i, 0]
                        dy = positions[b, j, 1] - positions[b, i, 1]
                        
                        relation_type = self._get_relation_type(dx, dy)
                        transform = self.relation_transforms[relation_type](symbols[b, i:i+1])
                        transformed[b, j:j+1] = transformed[b, j:j+1] + transform
        
        return transformed
    
    def _get_relation_type(self, dx: float, dy: float) -> int:
        """Determine spatial relationship type."""
        if dy > 0.5:
            return 0  # above
        elif dy < -0.5:
            return 1  # below
        elif dx < -0.5:
            return 2  # left
        elif dx > 0.5:
            return 3  # right
        elif abs(dx) < 0.3 and abs(dy) < 0.3:
            return 4  # center
        else:
            return 5  # diagonal


class CalendarAttention(nn.Module):
    """Cyclical attention based on sacred calendar patterns."""
    
    def __init__(self, embed_dim: int = 128, cycle_length: int = 260):
        super().__init__()
        
        self.cycle_patterns = nn.Parameter(torch.randn(cycle_length, embed_dim) * 0.1)
        self.attention = nn.MultiheadAttention(embed_dim, num_heads=4, batch_first=True)
        
    def forward(
        self,
        symbols: torch.Tensor,
        calendar_positions: torch.Tensor
    ) -> torch.Tensor:
        """Apply calendar-based attention."""
        # Get cycle pattern for each position
        cycle_patterns = self.cycle_patterns[calendar_positions]
        
        # Combine with symbol embeddings
        enhanced = symbols + cycle_patterns
        
        # Self-attention
        attended, _ = self.attention(enhanced, enhanced, enhanced)
        
        return attended


class LayeredInterpretation(nn.Module):
    """Multiple interpretation layers."""
    
    def __init__(self, embed_dim: int = 128, num_layers: int = 3):
        super().__init__()
        
        self.interpretation_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embed_dim, embed_dim),
                nn.GELU(),
                nn.Linear(embed_dim, 1)
            )
            for _ in range(num_layers)
        ])
        
    def forward(self, symbols: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Get interpretations at all layers."""
        interpretations = {}
        layer_names = ['exoteric', 'esoteric', 'sacred']
        
        for i, head in enumerate(self.interpretation_heads):
            interpretations[layer_names[i]] = head(symbols)
        
        return interpretations


class CodexNetwork(nn.Module):
    """Complete Codex Network for pictographic reasoning."""
    
    def __init__(
        self,
        num_symbols: int = 1000,
        embed_dim: int = 128,
        num_interpretation_layers: int = 3
    ):
        super().__init__()
        
        self.symbol_embed = SymbolEmbedding(num_symbols, embed_dim, num_interpretation_layers)
        self.positional_grammar = PositionalGrammar(embed_dim)
        self.calendar_attention = CalendarAttention(embed_dim)
        self.interpretation = LayeredInterpretation(embed_dim, num_interpretation_layers)
        self.output_proj = nn.Linear(embed_dim, embed_dim)
        
    def forward(
        self,
        symbol_ids: torch.Tensor,
        positions: torch.Tensor,
        calendar_positions: Optional[torch.Tensor] = None,
        interpretation_layer: int = 0
    ) -> Dict:
        """Process codex symbols."""
        # Get symbol embeddings
        symbols = self.symbol_embed(symbol_ids, layer=interpretation_layer, calendar_pos=calendar_positions)
        
        # Apply spatial grammar
        symbols = self.positional_grammar(symbols, positions)
        
        # Apply calendar attention if provided
        if calendar_positions is not None:
            symbols = self.calendar_attention(symbols, calendar_positions)
        
        # Get layered interpretations
        interpretations = self.interpretation(symbols)
        
        # Output
        output = self.output_proj(symbols)
        
        return {
            'output': output,
            'interpretations': interpretations,
            'symbols': symbols,
            'interpretation_layer': interpretation_layer
        }


def create_codex_network(num_symbols: int = 1000, embed_dim: int = 128) -> CodexNetwork:
    """Create CodexNetwork."""
    return CodexNetwork(num_symbols, embed_dim)
