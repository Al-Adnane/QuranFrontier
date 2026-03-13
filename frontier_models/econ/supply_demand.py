"""Supply Demand Network - Market Economics.

Inspired by: Economics
"""

import torch
import torch.nn as nn


class SupplyDemandNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.supply = nn.Linear(input_dim, embed_dim)
        self.demand = nn.Linear(input_dim, embed_dim)
        self.equilibrium = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        s = self.supply(x)
        d = self.demand(x)
        return {'supply': s, 'demand': d, 'equilibrium': torch.sigmoid(self.equilibrium(torch.cat([s, d], -1)))}


def create_supply_demand_network(input_dim: int = 128, embed_dim: int = 256):
    return SupplyDemandNetwork(input_dim, embed_dim)
