"""Epidemiology Network - Disease Spread.

Inspired by: Epidemiology
"""

import torch
import torch.nn as nn


class EpidemiologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.susceptible = nn.Linear(input_dim, embed_dim)
        self.infected = nn.Linear(input_dim, embed_dim)
        self.recovered = nn.Linear(input_dim, embed_dim)
        self.sir_model = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        s = self.susceptible(x)
        i = self.infected(x)
        r = self.recovered(x)
        return {'susceptible': s, 'infected': i, 'recovered': r, 'sir_model': torch.sigmoid(self.sir_model(torch.cat([s, i, r], -1)))}


def create_epidemiology_network(input_dim: int = 128, embed_dim: int = 256):
    return EpidemiologyNetwork(input_dim, embed_dim)
