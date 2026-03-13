"""Urban Transit Network - Public Transportation.

Inspired by: Urban Planning
"""

import torch
import torch.nn as nn


class UrbanTransitNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Transit modes
        self.bus = nn.Linear(input_dim, embed_dim)
        self.train = nn.Linear(input_dim, embed_dim)
        self.subway = nn.Linear(input_dim, embed_dim)
        self.tram = nn.Linear(input_dim, embed_dim)
        # Transit features
        self.frequency = nn.Linear(input_dim, embed_dim)
        self.coverage = nn.Linear(input_dim, embed_dim)
        # Transit quality
        self.quality = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        modes = [self.bus(x), self.train(x), self.subway(x), self.tram(x)]
        features = [self.frequency(x), self.coverage(x)]
        return {
            'transit_modes': {
                'bus': self.bus(x),
                'train': self.train(x),
                'subway': self.subway(x),
                'tram': self.tram(x)
            },
            'features': {
                'frequency': self.frequency(x),
                'coverage': self.coverage(x)
            },
            'transit_quality': torch.sigmoid(self.quality(torch.cat(modes + features, -1)))
        }


def create_urban_transit_network(input_dim: int = 128, embed_dim: int = 256):
    return UrbanTransitNetwork(input_dim, embed_dim)
