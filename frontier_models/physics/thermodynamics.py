"""Thermodynamics Network - Entropy and Energy.

Inspired by: Thermodynamics
"""

import torch
import torch.nn as nn


class ThermodynamicsNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.energy = nn.Linear(input_dim, embed_dim)
        self.entropy = nn.Linear(embed_dim, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        energy = self.energy(x)
        entropy = self.entropy(energy)
        return {'energy': energy, 'entropy': torch.sigmoid(entropy)}


def create_thermodynamics_network(input_dim: int = 128, embed_dim: int = 256):
    return ThermodynamicsNetwork(input_dim, embed_dim)
