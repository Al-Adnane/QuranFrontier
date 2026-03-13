"""Geology Network - Plate Tectonics and Rock Cycles.

Inspired by: Geology
"""

import torch
import torch.nn as nn


class GeologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Rock types
        self.igneous = nn.Linear(input_dim, embed_dim)
        self.sedimentary = nn.Linear(input_dim, embed_dim)
        self.metamorphic = nn.Linear(input_dim, embed_dim)
        # Plate tectonics
        self.tectonic = nn.Linear(input_dim, embed_dim)
        self.earthquake = nn.Linear(input_dim, embed_dim)
        self.volcano = nn.Linear(input_dim, embed_dim)
        # Rock cycle
        self.cycle = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        return {
            'rock_types': {
                'igneous': self.igneous(x),
                'sedimentary': self.sedimentary(x),
                'metamorphic': self.metamorphic(x)
            },
            'tectonics': {
                'plate_movement': self.tectonic(x),
                'earthquake_risk': torch.sigmoid(self.earthquake(x)),
                'volcanic_activity': torch.sigmoid(self.volcano(x))
            },
            'rock_cycle': torch.sigmoid(self.cycle(torch.cat([
                self.igneous(x), self.sedimentary(x), self.metamorphic(x),
                self.tectonic(x), self.earthquake(x), self.volcano(x)
            ], -1)))
        }


def create_geology_network(input_dim: int = 128, embed_dim: int = 256):
    return GeologyNetwork(input_dim, embed_dim)
