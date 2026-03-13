"""Abstract Art Network - Non-Representational.

Inspired by: Abstract Art
"""

import torch
import torch.nn as nn


class AbstractArtNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.form = nn.Linear(input_dim, embed_dim)
        self.color_field = nn.Linear(input_dim, embed_dim)
        self.gesture = nn.Linear(input_dim, embed_dim)
        self.abstract = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        f = self.form(x)
        c = self.color_field(x)
        g = self.gesture(x)
        return {'form': f, 'color_field': c, 'gesture': g, 'abstract': torch.sigmoid(self.abstract(torch.cat([f, c, g], -1)))}


def create_abstract_art_network(input_dim: int = 128, embed_dim: int = 256):
    return AbstractArtNetwork(input_dim, embed_dim)
