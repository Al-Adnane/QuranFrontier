"""Climate Network - Weather Patterns.

Inspired by: Climate Science
"""

import torch
import torch.nn as nn


class ClimateNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.temperature = nn.Linear(input_dim, embed_dim)
        self.pressure = nn.Linear(input_dim, embed_dim)
        self.humidity = nn.Linear(input_dim, embed_dim)
        self.climate = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        t = self.temperature(x)
        p = self.pressure(x)
        h = self.humidity(x)
        return {'temperature': t, 'pressure': p, 'humidity': h, 'climate': torch.sigmoid(self.climate(torch.cat([t, p, h], -1)))}


def create_climate_network(input_dim: int = 128, embed_dim: int = 256):
    return ClimateNetwork(input_dim, embed_dim)
