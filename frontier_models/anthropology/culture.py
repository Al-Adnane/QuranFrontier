"""Anthropology Network - Cultural Patterns.

Inspired by: Anthropology
"""

import torch
import torch.nn as nn


class AnthropologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.kinship = nn.Linear(input_dim, embed_dim)
        self.ritual = nn.Linear(input_dim, embed_dim)
        self.myth = nn.Linear(input_dim, embed_dim)
        self.culture = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        k = self.kinship(x)
        r = self.ritual(x)
        m = self.myth(x)
        return {'kinship': k, 'ritual': r, 'myth': m, 'culture': torch.sigmoid(self.culture(torch.cat([k, r, m], -1)))}


def create_anthropology_network(input_dim: int = 128, embed_dim: int = 256):
    return AnthropologyNetwork(input_dim, embed_dim)
