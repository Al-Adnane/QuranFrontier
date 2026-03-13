"""Astronomy Network - Stellar Evolution.

Inspired by: Astronomy
"""

import torch
import torch.nn as nn


STellar_TYPES = ['Protostar', 'Main_Sequence', 'Red_Giant', 'White_Dwarf', 
                 'Neutron_Star', 'Black_Hole', 'Supergiant']


class AstronomyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.star_types = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(7)])
        self.stellar_evolution = nn.Linear(embed_dim * 7, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        type_embs = [s(x) for s in self.star_types]
        return {
            'stellar_types': dict(zip(STellar_TYPES, type_embs)),
            'current_stage': STellar_TYPES[torch.stack(type_embs).mean(dim=0).argmax(dim=-1).item()],
            'evolution_progress': torch.sigmoid(self.stellar_evolution(torch.cat(type_embs, -1)))
        }


def create_astronomy_network(input_dim: int = 128, embed_dim: int = 256):
    return AstronomyNetwork(input_dim, embed_dim)
