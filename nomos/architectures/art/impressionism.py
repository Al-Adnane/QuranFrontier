"""Impressionism Network - Light and Color.

Inspired by: Impressionist Art
"""

import torch
import torch.nn as nn


class ImpressionismNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.light = nn.Linear(input_dim, embed_dim)
        self.color = nn.Linear(input_dim, embed_dim)
        self.impression = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        light = self.light(x)
        color = self.color(x)
        return {'light': light, 'color': color, 'impression': torch.sigmoid(self.impression(torch.cat([light, color], -1)))}


def create_impressionism_network(input_dim: int = 128, embed_dim: int = 256):
    return ImpressionismNetwork(input_dim, embed_dim)
