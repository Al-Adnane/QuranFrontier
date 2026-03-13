"""Periodic Network - Element Properties.

Inspired by: Periodic Table
"""

import torch
import torch.nn as nn


class PeriodicNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, num_elements: int = 18):
        super().__init__()
        self.groups = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(num_elements)])
        self.period = nn.Linear(embed_dim * num_elements, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        group_outputs = [g(x) for g in self.groups]
        return {'groups': group_outputs, 'period': torch.sigmoid(self.period(torch.cat(group_outputs, -1)))}


def create_periodic_network(input_dim: int = 128, embed_dim: int = 256):
    return PeriodicNetwork(input_dim, embed_dim)
