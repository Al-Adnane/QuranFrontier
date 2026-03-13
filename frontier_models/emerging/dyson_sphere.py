"""Dyson Sphere Network - Megastructure Engineering.

Inspired by: Megastructure Engineering
"""

import torch
import torch.nn as nn


class DysonSphereNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Dyson structure types
        self.swarm = nn.Linear(input_dim, embed_dim)
        self.bubble = nn.Linear(input_dim, embed_dim)
        self.shell = nn.Linear(input_dim, embed_dim)
        self.ring = nn.Linear(input_dim, embed_dim)
        # Energy collection
        self.solar_collection = nn.Linear(input_dim, embed_dim)
        self.energy_storage = nn.Linear(input_dim, embed_dim)
        # Construction feasibility
        self.feasibility = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        types = [self.swarm(x), self.bubble(x), self.shell(x), self.ring(x)]
        energy = [self.solar_collection(x), self.energy_storage(x)]
        return {
            'structure_types': {
                'dyson_swarm': self.swarm(x),
                'dyson_bubble': self.bubble(x),
                'dyson_shell': self.shell(x),
                'dyson_ring': self.ring(x)
            },
            'energy_systems': {
                'solar_collection': self.solar_collection(x),
                'energy_storage': self.energy_storage(x)
            },
            'construction_feasibility': torch.sigmoid(self.feasibility(torch.cat(types + energy, -1)))
        }


def create_dyson_sphere_network(input_dim: int = 128, embed_dim: int = 256):
    return DysonSphereNetwork(input_dim, embed_dim)
