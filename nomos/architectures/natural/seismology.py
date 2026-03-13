"""Seismology Network - Earthquake Science.

Inspired by: Seismology
"""

import torch
import torch.nn as nn


class SeismologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Earthquake types
        self.tectonic = nn.Linear(input_dim, embed_dim)
        self.volcanic = nn.Linear(input_dim, embed_dim)
        self.induced = nn.Linear(input_dim, embed_dim)
        # Seismic waves
        self.p_wave = nn.Linear(input_dim, embed_dim)
        self.s_wave = nn.Linear(input_dim, embed_dim)
        self.surface_wave = nn.Linear(input_dim, embed_dim)
        # Earthquake prediction
        self.prediction = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        types = [self.tectonic(x), self.volcanic(x), self.induced(x)]
        waves = [self.p_wave(x), self.s_wave(x), self.surface_wave(x)]
        return {
            'earthquake_types': {
                'tectonic': self.tectonic(x),
                'volcanic': self.volcanic(x),
                'induced': self.induced(x)
            },
            'seismic_waves': {
                'p_wave': self.p_wave(x),
                's_wave': self.s_wave(x),
                'surface_wave': self.surface_wave(x)
            },
            'earthquake_prediction': torch.sigmoid(self.prediction(torch.cat(types + waves, -1)))
        }


def create_seismology_network(input_dim: int = 128, embed_dim: int = 256):
    return SeismologyNetwork(input_dim, embed_dim)
