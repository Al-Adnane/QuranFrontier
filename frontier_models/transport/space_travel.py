"""Space Travel Network - Rocketry and Spaceflight.

Inspired by: Aerospace Engineering
"""

import torch
import torch.nn as nn


class SpaceTravelNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Rocket stages
        self.first_stage = nn.Linear(input_dim, embed_dim)
        self.second_stage = nn.Linear(input_dim, embed_dim)
        self.payload = nn.Linear(input_dim, embed_dim)
        # Propulsion
        self.chemical = nn.Linear(input_dim, embed_dim)
        self.electric = nn.Linear(input_dim, embed_dim)
        self.nuclear = nn.Linear(input_dim, embed_dim)
        # Mission success
        self.success = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        stages = [self.first_stage(x), self.second_stage(x), self.payload(x)]
        propulsion = [self.chemical(x), self.electric(x), self.nuclear(x)]
        return {
            'rocket_stages': {
                'first_stage': self.first_stage(x),
                'second_stage': self.second_stage(x),
                'payload': self.payload(x)
            },
            'propulsion': {
                'chemical': self.chemical(x),
                'electric': self.electric(x),
                'nuclear': self.nuclear(x)
            },
            'mission_success': torch.sigmoid(self.success(torch.cat(stages + propulsion, -1)))
        }


def create_space_travel_network(input_dim: int = 128, embed_dim: int = 256):
    return SpaceTravelNetwork(input_dim, embed_dim)
