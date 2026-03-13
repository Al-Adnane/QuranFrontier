"""Music Theory Network - Harmony and Melody.

Inspired by: Music Theory
"""

import torch
import torch.nn as nn


class MusicTheoryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.harmony = nn.Linear(input_dim, embed_dim)
        self.melody = nn.Linear(input_dim, embed_dim)
        self.rhythm = nn.Linear(input_dim, embed_dim)
        self.composition = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        h = self.harmony(x)
        m = self.melody(x)
        r = self.rhythm(x)
        return {'harmony': h, 'melody': m, 'rhythm': r, 'composition': torch.sigmoid(self.composition(torch.cat([h, m, r], -1)))}


def create_music_theory_network(input_dim: int = 128, embed_dim: int = 256):
    return MusicTheoryNetwork(input_dim, embed_dim)
