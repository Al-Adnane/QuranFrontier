"""Glaciology Network - Ice and Glaciers.

Inspired by: Glaciology
"""

import torch
import torch.nn as nn


class GlaciologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Ice types
        self.glacier = nn.Linear(input_dim, embed_dim)
        self.ice_sheet = nn.Linear(input_dim, embed_dim)
        self.sea_ice = nn.Linear(input_dim, embed_dim)
        # Glacier dynamics
        self.accumulation = nn.Linear(input_dim, embed_dim)
        self.ablation = nn.Linear(input_dim, embed_dim)
        self.flow = nn.Linear(input_dim, embed_dim)
        # Ice stability
        self.stability = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        ice_types = [self.glacier(x), self.ice_sheet(x), self.sea_ice(x)]
        dynamics = [self.accumulation(x), self.ablation(x), self.flow(x)]
        return {
            'ice_types': {
                'glacier': self.glacier(x),
                'ice_sheet': self.ice_sheet(x),
                'sea_ice': self.sea_ice(x)
            },
            'glacier_dynamics': {
                'accumulation': self.accumulation(x),
                'ablation': self.ablation(x),
                'flow': self.flow(x)
            },
            'ice_stability': torch.sigmoid(self.stability(torch.cat(ice_types + dynamics, -1)))
        }


def create_glaciology_network(input_dim: int = 128, embed_dim: int = 256):
    return GlaciologyNetwork(input_dim, embed_dim)
