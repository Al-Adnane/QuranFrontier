"""Oceanography Network - Ocean Currents and Ecosystems.

Inspired by: Oceanography
"""

import torch
import torch.nn as nn


class OceanographyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Ocean zones
        self.epipelagic = nn.Linear(input_dim, embed_dim)
        self.mesopelagic = nn.Linear(input_dim, embed_dim)
        self.bathypelagic = nn.Linear(input_dim, embed_dim)
        self.abyssopelagic = nn.Linear(input_dim, embed_dim)
        # Currents
        self.gyre = nn.Linear(input_dim, embed_dim)
        self.thermohaline = nn.Linear(input_dim, embed_dim)
        # Marine life
        self.marine_ecosystem = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        zones = [self.epipelagic(x), self.mesopelagic(x), self.bathypelagic(x), self.abyssopelagic(x)]
        return {
            'zones': {
                'epipelagic': zones[0],
                'mesopelagic': zones[1],
                'bathypelagic': zones[2],
                'abyssopelagic': zones[3]
            },
            'currents': {
                'gyre': self.gyre(x),
                'thermohaline': self.thermohaline(x)
            },
            'ecosystem_health': torch.sigmoid(self.marine_ecosystem(torch.cat(zones + [self.gyre(x), self.thermohaline(x)], -1)))
        }


def create_oceanography_network(input_dim: int = 128, embed_dim: int = 256):
    return OceanographyNetwork(input_dim, embed_dim)
