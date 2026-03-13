"""Crop Rotation Network - Sustainable Farming.

Inspired by: Crop Rotation
"""

import torch
import torch.nn as nn


class CropRotationNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Crop types
        self.legumes = nn.Linear(input_dim, embed_dim)
        self.grains = nn.Linear(input_dim, embed_dim)
        self.vegetables = nn.Linear(input_dim, embed_dim)
        self.cover_crops = nn.Linear(input_dim, embed_dim)
        # Soil benefits
        self.nitrogen_fixation = nn.Linear(input_dim, embed_dim)
        self.pest_reduction = nn.Linear(input_dim, embed_dim)
        # Rotation effectiveness
        self.effectiveness = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        crops = [self.legumes(x), self.grains(x), self.vegetables(x), self.cover_crops(x)]
        benefits = [self.nitrogen_fixation(x), self.pest_reduction(x)]
        return {
            'crop_types': {
                'legumes': self.legumes(x),
                'grains': self.grains(x),
                'vegetables': self.vegetables(x),
                'cover_crops': self.cover_crops(x)
            },
            'soil_benefits': {
                'nitrogen_fixation': self.nitrogen_fixation(x),
                'pest_reduction': self.pest_reduction(x)
            },
            'rotation_effectiveness': torch.sigmoid(self.effectiveness(torch.cat(crops + benefits, -1)))
        }


def create_crop_rotation_network(input_dim: int = 128, embed_dim: int = 256):
    return CropRotationNetwork(input_dim, embed_dim)
