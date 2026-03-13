"""Spiral Dynamics Network - Value Systems Evolution.

Inspired by: Spiral Dynamics (Beck & Cowan)
"""

import torch
import torch.nn as nn


LEVELS = ['Beige', 'Purple', 'Red', 'Blue', 'Orange', 'Green', 'Yellow', 'Turquoise']


class SpiralDynamicsNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.levels = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(8)
        ])
        self.evolution = nn.Linear(embed_dim * 8, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        activations = [l(x) for l in self.levels]
        dominant = torch.stack(activations).mean(dim=0).argmax(dim=-1)
        return {
            'level_activations': dict(zip(LEVELS, activations)),
            'dominant_level': LEVELS[dominant],
            'evolution_stage': torch.sigmoid(self.evolution(torch.cat(activations, -1))),
            'spiral_position': dominant.float() / 7  # Normalized 0-1
        }


def create_spiral_dynamics_network(input_dim: int = 128, embed_dim: int = 256):
    return SpiralDynamicsNetwork(input_dim, embed_dim)
