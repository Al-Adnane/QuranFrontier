"""Meteorology Network - Weather Patterns.

Inspired by: Meteorology
"""

import torch
import torch.nn as nn


class MeteorologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Weather elements
        self.temperature = nn.Linear(input_dim, embed_dim)
        self.pressure = nn.Linear(input_dim, embed_dim)
        self.humidity = nn.Linear(input_dim, embed_dim)
        self.wind = nn.Linear(input_dim, embed_dim)
        self.precipitation = nn.Linear(input_dim, embed_dim)
        # Weather systems
        self.front = nn.Linear(input_dim, embed_dim)
        self.storm = nn.Linear(input_dim, embed_dim)
        # Forecast
        self.forecast = nn.Linear(embed_dim * 7, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        elements = [self.temperature(x), self.pressure(x), self.humidity(x), 
                   self.wind(x), self.precipitation(x), self.front(x), self.storm(x)]
        return {
            'elements': {
                'temperature': self.temperature(x),
                'pressure': self.pressure(x),
                'humidity': self.humidity(x),
                'wind': self.wind(x),
                'precipitation': self.precipitation(x)
            },
            'systems': {
                'front': self.front(x),
                'storm': self.storm(x)
            },
            'forecast': torch.sigmoid(self.forecast(torch.cat(elements, -1)))
        }


def create_meteorology_network(input_dim: int = 128, embed_dim: int = 256):
    return MeteorologyNetwork(input_dim, embed_dim)
