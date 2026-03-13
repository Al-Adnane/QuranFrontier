"""Culinary Network - Food and Cooking.

Inspired by: Culinary Arts
"""

import torch
import torch.nn as nn


class CulinaryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Taste profiles
        self.sweet = nn.Linear(input_dim, embed_dim)
        self.sour = nn.Linear(input_dim, embed_dim)
        self.salty = nn.Linear(input_dim, embed_dim)
        self.bitter = nn.Linear(input_dim, embed_dim)
        self.umami = nn.Linear(input_dim, embed_dim)
        # Cooking methods
        self.cooking = nn.Linear(input_dim, embed_dim)
        # Dish quality
        self.quality = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        tastes = [self.sweet(x), self.sour(x), self.salty(x), self.bitter(x), self.umami(x)]
        return {
            'taste_profile': {
                'sweet': self.sweet(x),
                'sour': self.sour(x),
                'salty': self.salty(x),
                'bitter': self.bitter(x),
                'umami': self.umami(x)
            },
            'cooking_method': self.cooking(x),
            'dish_quality': torch.sigmoid(self.quality(torch.cat(tastes + [self.cooking(x)], -1)))
        }


def create_culinary_network(input_dim: int = 128, embed_dim: int = 256):
    return CulinaryNetwork(input_dim, embed_dim)
