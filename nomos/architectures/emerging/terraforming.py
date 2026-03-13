"""Terraforming Network - Planet Engineering.

Inspired by: Planetary Engineering
"""

import torch
import torch.nn as nn


class TerraformingNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Terraforming methods
        self.atmosphere = nn.Linear(input_dim, embed_dim)
        self.temperature = nn.Linear(input_dim, embed_dim)
        self.water = nn.Linear(input_dim, embed_dim)
        self.biosphere = nn.Linear(input_dim, embed_dim)
        # Planetary engineering
        self.magnetic_field = nn.Linear(input_dim, embed_dim)
        self.orbital_adjustment = nn.Linear(input_dim, embed_dim)
        # Terraforming success
        self.success = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        methods = [self.atmosphere(x), self.temperature(x), self.water(x), self.biosphere(x)]
        engineering = [self.magnetic_field(x), self.orbital_adjustment(x)]
        return {
            'terraforming_methods': {
                'atmosphere_generation': self.atmosphere(x),
                'temperature_control': self.temperature(x),
                'water_introduction': self.water(x),
                'biosphere_establishment': self.biosphere(x)
            },
            'planetary_engineering': {
                'magnetic_field': self.magnetic_field(x),
                'orbital_adjustment': self.orbital_adjustment(x)
            },
            'terraforming_success': torch.sigmoid(self.success(torch.cat(methods + engineering, -1)))
        }


def create_terraforming_network(input_dim: int = 128, embed_dim: int = 256):
    return TerraformingNetwork(input_dim, embed_dim)
