"""Space Colonization Network - Off-World Settlements.

Inspired by: Space Colonization
"""

import torch
import torch.nn as nn


class SpaceColonizationNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Colony locations
        self.moon = nn.Linear(input_dim, embed_dim)
        self.mars = nn.Linear(input_dim, embed_dim)
        self.asteroid = nn.Linear(input_dim, embed_dim)
        self.orbital = nn.Linear(input_dim, embed_dim)
        # Life support
        self.life_support = nn.Linear(input_dim, embed_dim)
        self.isru = nn.Linear(input_dim, embed_dim)  # In-situ resource utilization
        # Colony viability
        self.viability = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        locations = [self.moon(x), self.mars(x), self.asteroid(x), self.orbital(x)]
        support = [self.life_support(x), self.isru(x)]
        return {
            'locations': {
                'moon': self.moon(x),
                'mars': self.mars(x),
                'asteroid_belt': self.asteroid(x),
                'orbital_station': self.orbital(x)
            },
            'life_support': {
                'life_support': self.life_support(x),
                'isru': self.isru(x)
            },
            'colony_viability': torch.sigmoid(self.viability(torch.cat(locations + support, -1)))
        }


def create_space_colonization_network(input_dim: int = 128, embed_dim: int = 256):
    return SpaceColonizationNetwork(input_dim, embed_dim)
