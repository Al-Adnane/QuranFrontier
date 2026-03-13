"""Relativity Network - Spacetime Curvature.

Inspired by: General Relativity
"""

import torch
import torch.nn as nn


class RelativityNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.spacetime = nn.Linear(input_dim, embed_dim * 4)  # 4D spacetime
        self.curvature = nn.Linear(embed_dim * 4, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        spacetime = self.spacetime(x)
        return {'spacetime': spacetime, 'curvature': torch.tanh(self.curvature(spacetime))}


def create_relativity_network(input_dim: int = 128, embed_dim: int = 256):
    return RelativityNetwork(input_dim, embed_dim)
