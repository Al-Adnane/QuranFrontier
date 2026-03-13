"""Sociology Network - Social Structures.

Inspired by: Sociology
"""

import torch
import torch.nn as nn


class SociologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Social institutions
        self.family = nn.Linear(input_dim, embed_dim)
        self.education = nn.Linear(input_dim, embed_dim)
        self.religion = nn.Linear(input_dim, embed_dim)
        self.government = nn.Linear(input_dim, embed_dim)
        self.economy = nn.Linear(input_dim, embed_dim)
        # Social class
        self.class_structure = nn.Linear(input_dim, embed_dim * 3)  # Upper, Middle, Lower
        
    def forward(self, x: torch.Tensor) -> dict:
        institutions = {
            'family': self.family(x),
            'education': self.education(x),
            'religion': self.religion(x),
            'government': self.government(x),
            'economy': self.economy(x)
        }
        class_emb = self.class_structure(x).view(x.size(0), 3, -1)
        return {
            'institutions': institutions,
            'class_structure': {'upper': class_emb[:, 0], 'middle': class_emb[:, 1], 'lower': class_emb[:, 2]},
            'social_cohesion': torch.sigmoid(torch.stack(list(institutions.values())).mean(dim=0).mean(dim=-1, keepdim=True))
        }


def create_sociology_network(input_dim: int = 128, embed_dim: int = 256):
    return SociologyNetwork(input_dim, embed_dim)
