"""Number Theory Network - Prime Patterns.

Inspired by: Number Theory
"""

import torch
import torch.nn as nn


class NumberTheoryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.prime = nn.Linear(input_dim, embed_dim)
        self.composite = nn.Linear(input_dim, embed_dim)
        self.distribution = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        p = self.prime(x)
        c = self.composite(x)
        return {'prime': p, 'composite': c, 'distribution': torch.sigmoid(self.distribution(torch.cat([p, c], -1)))}


def create_number_theory_network(input_dim: int = 128, embed_dim: int = 256):
    return NumberTheoryNetwork(input_dim, embed_dim)
