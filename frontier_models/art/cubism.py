"""Cubism Network - Multiple Perspectives.

Inspired by: Cubist Art
"""

import torch
import torch.nn as nn


class CubismNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, perspectives: int = 5):
        super().__init__()
        self.views = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(perspectives)])
        self.cubist = nn.Linear(embed_dim * perspectives, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        views = [v(x) for v in self.views]
        return {'views': views, 'cubist': torch.sigmoid(self.cubist(torch.cat(views, -1)))}


def create_cubism_network(input_dim: int = 128, embed_dim: int = 256):
    return CubismNetwork(input_dim, embed_dim)
