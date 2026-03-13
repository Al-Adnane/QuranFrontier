"""Alchemy Network - Great Work Stages.

Inspired by: Western Alchemy
"""

import torch
import torch.nn as nn


class AlchemyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Four stages of Great Work
        self.nigredo = nn.Sequential(nn.Linear(input_dim, embed_dim), nn.ReLU())  # Blackening
        self.albedo = nn.Sequential(nn.Linear(input_dim, embed_dim), nn.Sigmoid())  # Whitening
        self.citrinitas = nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())  # Yellowing
        self.rubedo = nn.Sequential(nn.Linear(input_dim, embed_dim), nn.Tanh())  # Reddening
        # Three primes
        self.salt = nn.Linear(input_dim, embed_dim)  # Body
        self.sulfur = nn.Linear(input_dim, embed_dim)  # Soul
        self.mercury = nn.Linear(input_dim, embed_dim)  # Spirit
        # Philosopher's stone
        self.stone = nn.Linear(embed_dim * 7, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        nigredo = self.nigredo(x)
        albedo = self.albedo(x)
        citrinitas = self.citrinitas(x)
        rubedo = self.rubedo(x)
        salt = self.salt(x)
        sulfur = self.sulfur(x)
        mercury = self.mercury(x)
        return {
            'four_stages': {
                'nigredo': nigredo,
                'albedo': albedo,
                'citrinitas': citrinitas,
                'rubedo': rubedo
            },
            'three_primes': {'salt': salt, 'sulfur': sulfur, 'mercury': mercury},
            'magnum_opus': torch.sigmoid(self.stone(torch.cat([nigredo, albedo, citrinitas, rubedo, salt, sulfur, mercury], -1))),
            'transmutation_progress': torch.sigmoid((rubedo + mercury).mean(dim=-1, keepdim=True))
        }


def create_alchemy_network(input_dim: int = 128, embed_dim: int = 256):
    return AlchemyNetwork(input_dim, embed_dim)
