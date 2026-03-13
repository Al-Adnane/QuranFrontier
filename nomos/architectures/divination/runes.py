"""Runes Network - Elder Futhark Oracle.

Inspired by: Norse Runes
"""

import torch
import torch.nn as nn


RUNES = [
    'Fehu', 'Uruz', 'Thurisaz', 'Ansuz', 'Raido',
    'Kenaz', 'Gebo', 'Wunjo', 'Hagalaz', 'Nauthiz',
    'Isa', 'Jera', 'Eihwaz', 'Perthro', 'Algiz',
    'Sowilo', 'Tiwaz', 'Berkano', 'Ehwaz', 'Mannaz',
    'Laguz', 'Inguz', 'Dagaz', 'Othala'
]


class RunesNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.runes = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(24)
        ])
        self.spread = nn.Linear(embed_dim * 24, 3)  # 3-rune spread
        
    def forward(self, x: torch.Tensor) -> dict:
        rune_embs = [r(x) for r in self.runes]
        rune_scores = torch.stack([r.mean(dim=-1) for r in rune_embs], -1)
        top_3 = rune_scores.topk(3, dim=-1).indices
        return {
            'runes': dict(zip(RUNES, rune_embs)),
            'rune_scores': torch.sigmoid(rune_scores),
            'three_rune_spread': [RUNES[i] for i in top_3[0]],
            'reading': torch.sigmoid(self.spread(torch.cat(rune_embs, -1)))
        }


def create_runes_network(input_dim: int = 128, embed_dim: int = 256):
    return RunesNetwork(input_dim, embed_dim)
