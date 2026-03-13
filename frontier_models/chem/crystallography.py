"""Crystallography Network - Crystal Structure.

Inspired by: Crystallography
"""

import torch
import torch.nn as nn


class CrystallographyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.lattice = nn.Linear(input_dim, embed_dim)
        self.basis = nn.Linear(input_dim, embed_dim)
        self.crystal = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        lat = self.lattice(x)
        basis = self.basis(x)
        return {'lattice': lat, 'basis': basis, 'crystal': torch.sigmoid(self.crystal(torch.cat([lat, basis], -1)))}


def create_crystallography_network(input_dim: int = 128, embed_dim: int = 256):
    return CrystallographyNetwork(input_dim, embed_dim)
