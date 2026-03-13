"""Freudian Structure Network - Id, Ego, Superego.

Inspired by: Sigmund Freud's Structural Model
"""

import torch
import torch.nn as nn


class FreudianStructureNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.id = nn.Sequential(nn.Linear(input_dim, embed_dim), nn.ReLU())  # Pleasure principle
        self.ego = nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())  # Reality principle
        self.superego = nn.Sequential(nn.Linear(input_dim, embed_dim), nn.Sigmoid())  # Morality
        self.resolution = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        id_out = self.id(x)
        ego_out = self.ego(x)
        superego_out = self.superego(x)
        return {
            'id': id_out,
            'ego': ego_out,
            'superego': superego_out,
            'resolution': torch.sigmoid(self.resolution(torch.cat([id_out, ego_out, superego_out], -1)))
        }


def create_freudian_structure_network(input_dim: int = 128, embed_dim: int = 256):
    return FreudianStructureNetwork(input_dim, embed_dim)
