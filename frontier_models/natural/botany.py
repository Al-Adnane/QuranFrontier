"""Botany Network - Plant Systems.

Inspired by: Botany
"""

import torch
import torch.nn as nn


class BotanyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Plant parts
        self.root = nn.Linear(input_dim, embed_dim)
        self.stem = nn.Linear(input_dim, embed_dim)
        self.leaf = nn.Linear(input_dim, embed_dim)
        self.flower = nn.Linear(input_dim, embed_dim)
        # Photosynthesis
        self.photosynthesis = nn.Linear(embed_dim * 4, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        parts = [self.root(x), self.stem(x), self.leaf(x), self.flower(x)]
        return {
            'plant_parts': {
                'root': self.root(x),
                'stem': self.stem(x),
                'leaf': self.leaf(x),
                'flower': self.flower(x)
            },
            'photosynthesis_rate': torch.sigmoid(self.photosynthesis(torch.cat(parts, -1)))
        }


def create_botany_network(input_dim: int = 128, embed_dim: int = 256):
    return BotanyNetwork(input_dim, embed_dim)
