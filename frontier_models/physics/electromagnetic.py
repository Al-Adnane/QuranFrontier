"""Electromagnetic Network - Wave Propagation.

Inspired by: Electromagnetism
"""

import torch
import torch.nn as nn


class ElectromagneticNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.electric = nn.Linear(input_dim, embed_dim)
        self.magnetic = nn.Linear(input_dim, embed_dim)
        self.wave = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        e = self.electric(x)
        m = self.magnetic(x)
        return {'electric': e, 'magnetic': m, 'wave': torch.sigmoid(self.wave(torch.cat([e, m], -1)))}


def create_electromagnetic_network(input_dim: int = 128, embed_dim: int = 256):
    return ElectromagneticNetwork(input_dim, embed_dim)
