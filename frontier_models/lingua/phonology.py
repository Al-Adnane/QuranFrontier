"""Phonology Network - Sound Patterns.

Inspired by: Phonology
"""

import torch
import torch.nn as nn


class PhonologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.vowel = nn.Linear(input_dim, embed_dim)
        self.consonant = nn.Linear(input_dim, embed_dim)
        self.prosody = nn.Linear(input_dim, embed_dim)
        self.phoneme = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        v = self.vowel(x)
        c = self.consonant(x)
        p = self.prosody(x)
        return {'vowel': v, 'consonant': c, 'prosody': p, 'phoneme': torch.sigmoid(self.phoneme(torch.cat([v, c, p], -1)))}


def create_phonology_network(input_dim: int = 128, embed_dim: int = 256):
    return PhonologyNetwork(input_dim, embed_dim)
