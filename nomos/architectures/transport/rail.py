"""Rail Systems Network - Train Transportation.

Inspired by: Rail Transportation
"""

import torch
import torch.nn as nn


class RailSystemsNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Rail types
        self.high_speed = nn.Linear(input_dim, embed_dim)
        self.commuter = nn.Linear(input_dim, embed_dim)
        self.freight = nn.Linear(input_dim, embed_dim)
        self.metro = nn.Linear(input_dim, embed_dim)
        # Rail infrastructure
        self.track = nn.Linear(input_dim, embed_dim)
        self.signaling = nn.Linear(input_dim, embed_dim)
        # Rail efficiency
        self.efficiency = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        types = [self.high_speed(x), self.commuter(x), self.freight(x), self.metro(x)]
        infrastructure = [self.track(x), self.signaling(x)]
        return {
            'rail_types': {
                'high_speed': self.high_speed(x),
                'commuter': self.commuter(x),
                'freight': self.freight(x),
                'metro': self.metro(x)
            },
            'infrastructure': {
                'track': self.track(x),
                'signaling': self.signaling(x)
            },
            'rail_efficiency': torch.sigmoid(self.efficiency(torch.cat(types + infrastructure, -1)))
        }


def create_rail_systems_network(input_dim: int = 128, embed_dim: int = 256):
    return RailSystemsNetwork(input_dim, embed_dim)
