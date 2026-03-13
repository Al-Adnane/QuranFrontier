"""Architecture Network - Structural Design.

Inspired by: Architecture
"""

import torch
import torch.nn as nn


class ArchitectureNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.foundation = nn.Linear(input_dim, embed_dim)
        self.structure = nn.Linear(embed_dim, embed_dim)
        self.form = nn.Linear(embed_dim, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        foundation = self.foundation(x)
        structure = self.structure(foundation)
        return {'foundation': foundation, 'structure': structure, 'form': torch.sigmoid(self.form(structure))}


def create_architecture_network(input_dim: int = 128, embed_dim: int = 256):
    return ArchitectureNetwork(input_dim, embed_dim)
