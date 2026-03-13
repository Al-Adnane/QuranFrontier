"""Surrealism Network - Dream Logic.

Inspired by: Surrealist Art
"""

import torch
import torch.nn as nn


class SurrealismNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.conscious = nn.Linear(input_dim, embed_dim)
        self.unconscious = nn.Linear(input_dim, embed_dim)
        self.dream = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        con = self.conscious(x)
        uncon = self.unconscious(x)
        return {'conscious': con, 'unconscious': uncon, 'dream': torch.sigmoid(self.dream(torch.cat([con, uncon], -1)))}


def create_surrealism_network(input_dim: int = 128, embed_dim: int = 256):
    return SurrealismNetwork(input_dim, embed_dim)
