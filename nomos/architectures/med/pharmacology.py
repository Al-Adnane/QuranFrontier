"""Pharmacology Network - Drug Interaction.

Inspired by: Pharmacology
"""

import torch
import torch.nn as nn


class PharmacologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.absorption = nn.Linear(input_dim, embed_dim)
        self.distribution = nn.Linear(input_dim, embed_dim)
        self.metabolism = nn.Linear(input_dim, embed_dim)
        self.excretion = nn.Linear(input_dim, embed_dim)
        self.adme = nn.Linear(embed_dim * 4, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        a = self.absorption(x)
        d = self.distribution(x)
        m = self.metabolism(x)
        e = self.excretion(x)
        return {'absorption': a, 'distribution': d, 'metabolism': m, 'excretion': e, 'adme': torch.sigmoid(self.adme(torch.cat([a, d, m, e], -1)))}


def create_pharmacology_network(input_dim: int = 128, embed_dim: int = 256):
    return PharmacologyNetwork(input_dim, embed_dim)
