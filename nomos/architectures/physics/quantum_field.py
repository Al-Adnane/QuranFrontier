"""Quantum Field Network - Particle Physics Inspired.

Inspired by: Quantum Field Theory
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class QuantumFieldNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.field = nn.Sequential(
            nn.Linear(input_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        self.particle = nn.Linear(embed_dim, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        field_state = self.field(x)
        return {'field': field_state, 'particle': torch.sigmoid(self.particle(field_state))}


def create_quantum_field_network(input_dim: int = 128, embed_dim: int = 256):
    return QuantumFieldNetwork(input_dim, embed_dim)
