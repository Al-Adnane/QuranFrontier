"""Topology Network - Shape Properties.

Inspired by: Topology
"""

import torch
import torch.nn as nn


class TopologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.continuous = nn.Linear(input_dim, embed_dim)
        self.homeomorphism = nn.Linear(embed_dim, embed_dim)
        self.invariant = nn.Linear(embed_dim, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        cont = self.continuous(x)
        homeo = self.homeomorphism(cont)
        return {'continuous': cont, 'homeomorphism': homeo, 'invariant': torch.sigmoid(self.invariant(homeo))}


def create_topology_network(input_dim: int = 128, embed_dim: int = 256):
    return TopologyNetwork(input_dim, embed_dim)
