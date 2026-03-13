"""Ecosystem Network - Food Web.

Inspired by: Ecology
"""

import torch
import torch.nn as nn


class EcosystemNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, trophic_levels: int = 5):
        super().__init__()
        self.trophic = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(trophic_levels)])
        self.web = nn.Linear(embed_dim * trophic_levels, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        levels = [t(x) for t in self.trophic]
        return {'trophic_levels': levels, 'ecosystem': torch.sigmoid(self.web(torch.cat(levels, -1)))}


def create_ecosystem_network(input_dim: int = 128, embed_dim: int = 256):
    return EcosystemNetwork(input_dim, embed_dim)
