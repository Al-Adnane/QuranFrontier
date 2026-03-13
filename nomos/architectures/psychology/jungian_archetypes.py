"""Jungian Archetypes Network - 12 Universal Archetypes.

Inspired by: Carl Jung's Analytical Psychology
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


ARCHETYPES = [
    'Innocent', 'Orphan', 'Hero', 'Caregiver',
    'Explorer', 'Rebel', 'Lover', 'Creator',
    'Jester', 'Sage', 'Magician', 'Ruler'
]


class JungianArchetypesNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.archetypes = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(12)
        ])
        self.integration = nn.Linear(embed_dim * 12, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        activations = [a(x) for a in self.archetypes]
        mean_acts = torch.stack([a.mean(dim=-1) for a in activations], -1)
        dominant_idx = mean_acts.argmax(dim=-1)
        return {
            'archetypes': dict(zip(ARCHETYPES, activations)),
            'dominant': ARCHETYPES[dominant_idx],
            'integration': torch.sigmoid(self.integration(torch.cat(activations, -1)))
        }


def create_jungian_archetypes_network(input_dim: int = 128, embed_dim: int = 256):
    return JungianArchetypesNetwork(input_dim, embed_dim)
