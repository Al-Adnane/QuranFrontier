"""Organic Chemistry Network - Carbon Bonds.

Inspired by: Organic Chemistry
"""

import torch
import torch.nn as nn


class OrganicChemistryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.single_bond = nn.Linear(input_dim, embed_dim)
        self.double_bond = nn.Linear(input_dim, embed_dim)
        self.triple_bond = nn.Linear(input_dim, embed_dim)
        self.molecule = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        s = self.single_bond(x)
        d = self.double_bond(x)
        t = self.triple_bond(x)
        return {'single_bond': s, 'double_bond': d, 'triple_bond': t, 'molecule': torch.sigmoid(self.molecule(torch.cat([s, d, t], -1)))}


def create_organic_chemistry_network(input_dim: int = 128, embed_dim: int = 256):
    return OrganicChemistryNetwork(input_dim, embed_dim)
