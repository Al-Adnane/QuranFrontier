"""Multiverse Network - Parallel Universes.

Inspired by: Multiverse Theory
"""

import torch
import torch.nn as nn


class MultiverseNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Universe types
        self.bubble = nn.Linear(input_dim, embed_dim)
        self.brane = nn.Linear(input_dim, embed_dim)
        self.quantum = nn.Linear(input_dim, embed_dim)
        self.mathematical = nn.Linear(input_dim, embed_dim)
        # Universe interaction
        self.interaction = nn.Linear(input_dim, embed_dim)
        # Multiverse probability
        self.multiverse = nn.Linear(embed_dim * 5, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        universes = [self.bubble(x), self.brane(x), self.quantum(x), self.mathematical(x)]
        return {
            'universe_types': {
                'bubble_universes': self.bubble(x),
                'brane_multiverse': self.brane(x),
                'quantum_many_worlds': self.quantum(x),
                'mathematical_universe': self.mathematical(x)
            },
            'universe_interaction': self.interaction(x),
            'multiverse_probability': torch.sigmoid(self.multiverse(torch.cat(universes + [self.interaction(x)], -1)))
        }


def create_multiverse_network(input_dim: int = 128, embed_dim: int = 256):
    return MultiverseNetwork(input_dim, embed_dim)
