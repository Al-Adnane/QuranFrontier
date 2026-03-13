"""Environmental Science Network - Ecosystem Health.

Inspired by: Environmental Science
"""

import torch
import torch.nn as nn


class EnvironmentalScienceNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Environmental factors
        self.air_quality = nn.Linear(input_dim, embed_dim)
        self.water_quality = nn.Linear(input_dim, embed_dim)
        self.soil_health = nn.Linear(input_dim, embed_dim)
        self.biodiversity = nn.Linear(input_dim, embed_dim)
        # Climate impact
        self.carbon = nn.Linear(input_dim, embed_dim)
        self.climate = nn.Linear(input_dim, embed_dim)
        # Ecosystem health
        self.health = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        factors = [self.air_quality(x), self.water_quality(x), self.soil_health(x), 
                  self.biodiversity(x), self.carbon(x), self.climate(x)]
        return {
            'environmental_factors': {
                'air_quality': self.air_quality(x),
                'water_quality': self.water_quality(x),
                'soil_health': self.soil_health(x),
                'biodiversity': self.biodiversity(x),
                'carbon_footprint': self.carbon(x),
                'climate_impact': self.climate(x)
            },
            'ecosystem_health': torch.sigmoid(self.health(torch.cat(factors, -1)))
        }


def create_environmental_science_network(input_dim: int = 128, embed_dim: int = 256):
    return EnvironmentalScienceNetwork(input_dim, embed_dim)
