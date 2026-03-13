"""Geomancy Network - Earth Divination.

Inspired by: Geomancy
"""

import torch
import torch.nn as nn


FIGURES = [
    'Via', 'Populus', 'Conjunctio', 'Albus', 'Rubeus',
    'Fortuna_Major', 'Fortuna_Minor', 'Acquisitio', 'Amissio',
    'Laetitia', 'Tristitia', 'Carcer', 'Puer', 'Puella',
    'Caput_Draconis', 'Cauda_Draconis'
]


class GeomancyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.figures = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(16)
        ])
        self.shield_chart = nn.Linear(embed_dim * 16, 4)  # 4 mothers
        
    def forward(self, x: torch.Tensor) -> dict:
        figure_embs = [f(x) for f in self.figures]
        figure_scores = torch.stack([f.mean(dim=-1) for f in figure_embs], -1)
        dominant_idx = int(figure_scores.argmax(dim=-1).item())
        return {
            'figures': dict(zip(FIGURES, figure_embs)),
            'figure_scores': torch.sigmoid(figure_scores),
            'shield_chart': torch.sigmoid(self.shield_chart(torch.cat(figure_embs, -1))),
            'dominant_figure': FIGURES[dominant_idx]
        }


def create_geomancy_network(input_dim: int = 128, embed_dim: int = 256):
    return GeomancyNetwork(input_dim, embed_dim)
