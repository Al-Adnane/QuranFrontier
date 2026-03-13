"""Agroforestry Network - Tree-Based Agriculture.

Inspired by: Agroforestry
"""

import torch
import torch.nn as nn


class AgroforestryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Agroforestry systems
        self.silvopasture = nn.Linear(input_dim, embed_dim)
        self.alley_cropping = nn.Linear(input_dim, embed_dim)
        self.windbreak = nn.Linear(input_dim, embed_dim)
        self.riparian = nn.Linear(input_dim, embed_dim)
        # Benefits
        self.carbon_sequestration = nn.Linear(input_dim, embed_dim)
        self.biodiversity = nn.Linear(input_dim, embed_dim)
        # System sustainability
        self.sustainability = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        systems = [self.silvopasture(x), self.alley_cropping(x), self.windbreak(x), self.riparian(x)]
        benefits = [self.carbon_sequestration(x), self.biodiversity(x)]
        return {
            'systems': {
                'silvopasture': self.silvopasture(x),
                'alley_cropping': self.alley_cropping(x),
                'windbreak': self.windbreak(x),
                'riparian_buffer': self.riparian(x)
            },
            'benefits': {
                'carbon_sequestration': self.carbon_sequestration(x),
                'biodiversity': self.biodiversity(x)
            },
            'sustainability': torch.sigmoid(self.sustainability(torch.cat(systems + benefits, -1)))
        }


def create_agroforestry_network(input_dim: int = 128, embed_dim: int = 256):
    return AgroforestryNetwork(input_dim, embed_dim)
