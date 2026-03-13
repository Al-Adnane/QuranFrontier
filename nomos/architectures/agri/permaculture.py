"""Permaculture Network - Sustainable Agriculture.

Inspired by: Permaculture Design
"""

import torch
import torch.nn as nn


class PermacultureNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Permaculture principles
        self.observe_interact = nn.Linear(input_dim, embed_dim)
        self.catch_store = nn.Linear(input_dim, embed_dim)
        self.obtain_yield = nn.Linear(input_dim, embed_dim)
        self.apply_regulate = nn.Linear(input_dim, embed_dim)
        self.use_renewable = nn.Linear(input_dim, embed_dim)
        self.produce_waste = nn.Linear(input_dim, embed_dim)
        # Sustainability
        self.sustainability = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        principles = [
            self.observe_interact(x), self.catch_store(x), self.obtain_yield(x),
            self.apply_regulate(x), self.use_renewable(x), self.produce_waste(x)
        ]
        return {
            'principles': {
                'observe_interact': self.observe_interact(x),
                'catch_store': self.catch_store(x),
                'obtain_yield': self.obtain_yield(x),
                'apply_regulate': self.apply_regulate(x),
                'use_renewable': self.use_renewable(x),
                'produce_waste': self.produce_waste(x)
            },
            'sustainability': torch.sigmoid(self.sustainability(torch.cat(principles, -1)))
        }


def create_permaculture_network(input_dim: int = 128, embed_dim: int = 256):
    return PermacultureNetwork(input_dim, embed_dim)
