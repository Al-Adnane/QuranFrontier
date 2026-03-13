"""Semantics Network - Meaning Representation.

Inspired by: Semantics
"""

import torch
import torch.nn as nn


class SemanticsNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.literal = nn.Linear(input_dim, embed_dim)
        self.figurative = nn.Linear(input_dim, embed_dim)
        self.meaning = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        lit = self.literal(x)
        fig = self.figurative(x)
        return {'literal': lit, 'figurative': fig, 'meaning': torch.sigmoid(self.meaning(torch.cat([lit, fig], -1)))}


def create_semantics_network(input_dim: int = 128, embed_dim: int = 256):
    return SemanticsNetwork(input_dim, embed_dim)
