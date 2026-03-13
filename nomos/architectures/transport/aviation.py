"""Aviation Network - Flight and Aircraft.

Inspired by: Aviation
"""

import torch
import torch.nn as nn


class AviationNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Flight forces
        self.lift = nn.Linear(input_dim, embed_dim)
        self.weight = nn.Linear(input_dim, embed_dim)
        self.thrust = nn.Linear(input_dim, embed_dim)
        self.drag = nn.Linear(input_dim, embed_dim)
        # Aircraft types
        self.fixed_wing = nn.Linear(input_dim, embed_dim)
        self.rotary_wing = nn.Linear(input_dim, embed_dim)
        # Flight efficiency
        self.efficiency = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        forces = [self.lift(x), self.weight(x), self.thrust(x), self.drag(x)]
        aircraft = [self.fixed_wing(x), self.rotary_wing(x)]
        return {
            'flight_forces': {
                'lift': self.lift(x),
                'weight': self.weight(x),
                'thrust': self.thrust(x),
                'drag': self.drag(x)
            },
            'aircraft_types': {
                'fixed_wing': self.fixed_wing(x),
                'rotary_wing': self.rotary_wing(x)
            },
            'flight_efficiency': torch.sigmoid(self.efficiency(torch.cat(forces + aircraft, -1)))
        }


def create_aviation_network(input_dim: int = 128, embed_dim: int = 256):
    return AviationNetwork(input_dim, embed_dim)
