"""Gothic Network - Cathedral Architecture.

Inspired by: Gothic Architecture
"""

import torch
import torch.nn as nn


class GothicNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.arch = nn.Linear(input_dim, embed_dim)
        self.vault = nn.Linear(input_dim, embed_dim)
        self.flying_buttress = nn.Linear(input_dim, embed_dim)
        self.cathedral = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        a = self.arch(x)
        v = self.vault(x)
        f = self.flying_buttress(x)
        return {'arch': a, 'vault': v, 'flying_buttress': f, 'cathedral': torch.sigmoid(self.cathedral(torch.cat([a, v, f], -1)))}


def create_gothic_network(input_dim: int = 128, embed_dim: int = 256):
    return GothicNetwork(input_dim, embed_dim)
