"""Narrative Structure Network - Story Arcs.

Inspired by: Narrative Theory
"""

import torch
import torch.nn as nn


class NarrativeStructureNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Three-act structure
        self.act1 = nn.Linear(input_dim, embed_dim)  # Setup
        self.act2 = nn.Linear(input_dim, embed_dim)  # Confrontation
        self.act3 = nn.Linear(input_dim, embed_dim)  # Resolution
        # Character arcs
        self.positive_arc = nn.Linear(input_dim, embed_dim)
        self.negative_arc = nn.Linear(input_dim, embed_dim)
        self.flat_arc = nn.Linear(input_dim, embed_dim)
        # Plot types
        self.plots = nn.ModuleDict({
            'overcoming_monster': nn.Linear(input_dim, embed_dim),
            'rags_to_riches': nn.Linear(input_dim, embed_dim),
            'quest': nn.Linear(input_dim, embed_dim),
            'voyage_return': nn.Linear(input_dim, embed_dim),
            'comedy': nn.Linear(input_dim, embed_dim),
            'tragedy': nn.Linear(input_dim, embed_dim),
            'rebirth': nn.Linear(input_dim, embed_dim)
        })
        
    def forward(self, x: torch.Tensor) -> dict:
        plot_embs = {k: v(x) for k, v in self.plots.items()}
        return {
            'three_acts': {'act1': self.act1(x), 'act2': self.act2(x), 'act3': self.act3(x)},
            'character_arcs': {
                'positive': self.positive_arc(x),
                'negative': self.negative_arc(x),
                'flat': self.flat_arc(x)
            },
            'plot_types': plot_embs,
            'dominant_plot': max(plot_embs.keys(), key=lambda k: plot_embs[k].mean(dim=-1).max().item()),
            'narrative_strength': torch.sigmoid((self.act1(x) + self.act2(x) + self.act3(x)).mean(dim=-1, keepdim=True))
        }


def create_narrative_structure_network(input_dim: int = 128, embed_dim: int = 256):
    return NarrativeStructureNetwork(input_dim, embed_dim)
