"""Hydrology Network - Water Systems.

Inspired by: Hydrology
"""

import torch
import torch.nn as nn


class HydrologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Water cycle
        self.evaporation = nn.Linear(input_dim, embed_dim)
        self.condensation = nn.Linear(input_dim, embed_dim)
        self.precipitation = nn.Linear(input_dim, embed_dim)
        self.runoff = nn.Linear(input_dim, embed_dim)
        # Water bodies
        self.groundwater = nn.Linear(input_dim, embed_dim)
        self.surface_water = nn.Linear(input_dim, embed_dim)
        # Water availability
        self.availability = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        cycle = [self.evaporation(x), self.condensation(x), self.precipitation(x), self.runoff(x)]
        bodies = [self.groundwater(x), self.surface_water(x)]
        return {
            'water_cycle': {
                'evaporation': self.evaporation(x),
                'condensation': self.condensation(x),
                'precipitation': self.precipitation(x),
                'runoff': self.runoff(x)
            },
            'water_bodies': {
                'groundwater': self.groundwater(x),
                'surface_water': self.surface_water(x)
            },
            'water_availability': torch.sigmoid(self.availability(torch.cat(cycle + bodies, -1)))
        }


def create_hydrology_network(input_dim: int = 128, embed_dim: int = 256):
    return HydrologyNetwork(input_dim, embed_dim)
