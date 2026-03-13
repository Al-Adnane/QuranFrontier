"""Network Science Network - Complex Networks.

Inspired by: Network Science
"""

import torch
import torch.nn as nn


class NetworkScienceNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.hub = nn.Linear(input_dim, embed_dim)
        self.periphery = nn.Linear(input_dim, embed_dim)
        self.small_world = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        h = self.hub(x)
        p = self.periphery(x)
        return {'hub': h, 'periphery': p, 'small_world': torch.sigmoid(self.small_world(torch.cat([h, p], -1)))}


def create_network_science_network(input_dim: int = 128, embed_dim: int = 256):
    return NetworkScienceNetwork(input_dim, embed_dim)
