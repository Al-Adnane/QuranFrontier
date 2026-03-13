"""Syntax Network - Grammatical Structure.

Inspired by: Linguistics
"""

import torch
import torch.nn as nn


class SyntaxNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.noun = nn.Linear(input_dim, embed_dim)
        self.verb = nn.Linear(input_dim, embed_dim)
        self.sentence = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        n = self.noun(x)
        v = self.verb(x)
        return {'noun': n, 'verb': v, 'sentence': torch.sigmoid(self.sentence(torch.cat([n, v], -1)))}


def create_syntax_network(input_dim: int = 128, embed_dim: int = 256):
    return SyntaxNetwork(input_dim, embed_dim)
