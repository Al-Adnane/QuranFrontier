"""Reaction Network - Chemical Reactions.

Inspired by: Chemical Kinetics
"""

import torch
import torch.nn as nn


class ReactionNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.reactants = nn.Linear(input_dim, embed_dim)
        self.catalyst = nn.Parameter(torch.randn(embed_dim) * 0.1)
        self.products = nn.Linear(embed_dim, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        reactants = self.reactants(x) + self.catalyst
        return {'reactants': reactants, 'products': torch.sigmoid(self.products(reactants))}


def create_reaction_network(input_dim: int = 128, embed_dim: int = 256):
    return ReactionNetwork(input_dim, embed_dim)
