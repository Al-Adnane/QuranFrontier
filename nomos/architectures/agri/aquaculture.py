"""Aquaculture Network - Fish Farming.

Inspired by: Aquaculture
"""

import torch
import torch.nn as nn


class AquacultureNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Aquaculture systems
        self.ponds = nn.Linear(input_dim, embed_dim)
        self.raceways = nn.Linear(input_dim, embed_dim)
        self.recirculating = nn.Linear(input_dim, embed_dim)
        # Water quality
        self.oxygen = nn.Linear(input_dim, embed_dim)
        self.ph = nn.Linear(input_dim, embed_dim)
        self.temperature = nn.Linear(input_dim, embed_dim)
        # Production
        self.production = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        systems = [self.ponds(x), self.raceways(x), self.recirculating(x)]
        water = [self.oxygen(x), self.ph(x), self.temperature(x)]
        return {
            'systems': {
                'ponds': self.ponds(x),
                'raceways': self.raceways(x),
                'recirculating': self.recirculating(x)
            },
            'water_quality': {
                'oxygen': self.oxygen(x),
                'ph': self.ph(x),
                'temperature': self.temperature(x)
            },
            'production': torch.sigmoid(self.production(torch.cat(systems + water, -1)))
        }


def create_aquaculture_network(input_dim: int = 128, embed_dim: int = 256):
    return AquacultureNetwork(input_dim, embed_dim)
