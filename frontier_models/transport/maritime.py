"""Maritime Network - Shipping and Navigation.

Inspired by: Maritime Industry
"""

import torch
import torch.nn as nn


class MaritimeNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Vessel types
        self.cargo = nn.Linear(input_dim, embed_dim)
        self.tanker = nn.Linear(input_dim, embed_dim)
        self.passenger = nn.Linear(input_dim, embed_dim)
        # Navigation
        self.navigation = nn.Linear(input_dim, embed_dim)
        self.port = nn.Linear(input_dim, embed_dim)
        # Shipping efficiency
        self.efficiency = nn.Linear(embed_dim * 5, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        vessels = [self.cargo(x), self.tanker(x), self.passenger(x)]
        navigation = [self.navigation(x), self.port(x)]
        return {
            'vessel_types': {
                'cargo': self.cargo(x),
                'tanker': self.tanker(x),
                'passenger': self.passenger(x)
            },
            'navigation': {
                'navigation': self.navigation(x),
                'port': self.port(x)
            },
            'shipping_efficiency': torch.sigmoid(self.efficiency(torch.cat(vessels + navigation, -1)))
        }


def create_maritime_network(input_dim: int = 128, embed_dim: int = 256):
    return MaritimeNetwork(input_dim, embed_dim)
