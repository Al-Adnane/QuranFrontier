"""Calculus Network - Continuous Change.

Inspired by: Calculus
"""

import torch
import torch.nn as nn


class CalculusNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.derivative = nn.Linear(input_dim, embed_dim)
        self.integral = nn.Linear(input_dim, embed_dim)
        self.limit = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        d = self.derivative(x)
        i = self.integral(x)
        return {'derivative': d, 'integral': i, 'limit': torch.sigmoid(self.limit(torch.cat([d, i], -1)))}


def create_calculus_network(input_dim: int = 128, embed_dim: int = 256):
    return CalculusNetwork(input_dim, embed_dim)
