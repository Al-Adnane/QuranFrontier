"""Urban Planning Network - City Design.

Inspired by: Urban Planning
"""

import torch
import torch.nn as nn


class UrbanPlanningNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Urban zones
        self.residential = nn.Linear(input_dim, embed_dim)
        self.commercial = nn.Linear(input_dim, embed_dim)
        self.industrial = nn.Linear(input_dim, embed_dim)
        self.green_space = nn.Linear(input_dim, embed_dim)
        # Infrastructure
        self.transportation = nn.Linear(input_dim, embed_dim)
        self.utilities = nn.Linear(input_dim, embed_dim)
        # City livability
        self.livability = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        zones = [self.residential(x), self.commercial(x), self.industrial(x), self.green_space(x)]
        infrastructure = [self.transportation(x), self.utilities(x)]
        return {
            'urban_zones': {
                'residential': self.residential(x),
                'commercial': self.commercial(x),
                'industrial': self.industrial(x),
                'green_space': self.green_space(x)
            },
            'infrastructure': {
                'transportation': self.transportation(x),
                'utilities': self.utilities(x)
            },
            'city_livability': torch.sigmoid(self.livability(torch.cat(zones + infrastructure, -1)))
        }


def create_urban_planning_network(input_dim: int = 128, embed_dim: int = 256):
    return UrbanPlanningNetwork(input_dim, embed_dim)
