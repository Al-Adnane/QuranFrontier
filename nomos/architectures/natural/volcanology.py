"""Volcanology Network - Volcano Science.

Inspired by: Volcanology
"""

import torch
import torch.nn as nn


class VolcanologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Volcano types
        self.shield = nn.Linear(input_dim, embed_dim)
        self.stratovolcano = nn.Linear(input_dim, embed_dim)
        self.cinder_cone = nn.Linear(input_dim, embed_dim)
        # Volcanic activity
        self.magma = nn.Linear(input_dim, embed_dim)
        self.eruption = nn.Linear(input_dim, embed_dim)
        self.pyroclastic = nn.Linear(input_dim, embed_dim)
        # Eruption prediction
        self.prediction = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        types = [self.shield(x), self.stratovolcano(x), self.cinder_cone(x)]
        activity = [self.magma(x), self.eruption(x), self.pyroclastic(x)]
        return {
            'volcano_types': {
                'shield': self.shield(x),
                'stratovolcano': self.stratovolcano(x),
                'cinder_cone': self.cinder_cone(x)
            },
            'volcanic_activity': {
                'magma_chamber': self.magma(x),
                'eruption': self.eruption(x),
                'pyroclastic_flow': self.pyroclastic(x)
            },
            'eruption_prediction': torch.sigmoid(self.prediction(torch.cat(types + activity, -1)))
        }


def create_volcanology_network(input_dim: int = 128, embed_dim: int = 256):
    return VolcanologyNetwork(input_dim, embed_dim)
