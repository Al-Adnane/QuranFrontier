"""Cosmology Network - Universe Structure.

Inspired by: Cosmology
"""

import torch
import torch.nn as nn


class CosmologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Universe components
        self.dark_energy = nn.Linear(input_dim, embed_dim)
        self.dark_matter = nn.Linear(input_dim, embed_dim)
        self.baryonic = nn.Linear(input_dim, embed_dim)
        # Cosmic structures
        self.galaxy = nn.Linear(input_dim, embed_dim)
        self.cluster = nn.Linear(input_dim, embed_dim)
        self.supercluster = nn.Linear(input_dim, embed_dim)
        # Big Bang
        self.big_bang = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        components = [self.dark_energy(x), self.dark_matter(x), self.baryonic(x)]
        structures = [self.galaxy(x), self.cluster(x), self.supercluster(x)]
        return {
            'universe_composition': {
                'dark_energy': torch.sigmoid(self.dark_energy(x)),
                'dark_matter': torch.sigmoid(self.dark_matter(x)),
                'baryonic_matter': torch.sigmoid(self.baryonic(x))
            },
            'structures': {
                'galaxy': self.galaxy(x),
                'cluster': self.cluster(x),
                'supercluster': self.supercluster(x)
            },
            'cosmic_evolution': torch.sigmoid(self.big_bang(torch.cat(components + structures, -1)))
        }


def create_cosmology_network(input_dim: int = 128, embed_dim: int = 256):
    return CosmologyNetwork(input_dim, embed_dim)
