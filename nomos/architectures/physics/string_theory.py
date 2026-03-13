"""String Theory Network - Vibrating Strings.

Inspired by: String Theory
"""

import torch
import torch.nn as nn


class StringTheoryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, num_dimensions: int = 11):
        super().__init__()
        self.strings = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(num_dimensions)])
        self.vibration = nn.Linear(embed_dim * num_dimensions, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        vibrations = [s(x) for s in self.strings]
        combined = torch.cat(vibrations, -1)
        return {'vibrations': vibrations, 'unified': torch.sigmoid(self.vibration(combined))}


def create_string_theory_network(input_dim: int = 128, embed_dim: int = 256):
    return StringTheoryNetwork(input_dim, embed_dim)
