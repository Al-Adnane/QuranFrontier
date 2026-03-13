"""Interior Design Network - Space Aesthetics.

Inspired by: Interior Design
"""

import torch
import torch.nn as nn


class InteriorDesignNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Design elements
        self.color_scheme = nn.Linear(input_dim, embed_dim)
        self.furniture = nn.Linear(input_dim, embed_dim)
        self.lighting = nn.Linear(input_dim, embed_dim)
        self.texture = nn.Linear(input_dim, embed_dim)
        # Design styles
        self.modern = nn.Linear(input_dim, embed_dim)
        self.traditional = nn.Linear(input_dim, embed_dim)
        # Room harmony
        self.harmony = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        elements = [self.color_scheme(x), self.furniture(x), self.lighting(x), self.texture(x)]
        styles = [self.modern(x), self.traditional(x)]
        return {
            'elements': {
                'color_scheme': self.color_scheme(x),
                'furniture': self.furniture(x),
                'lighting': self.lighting(x),
                'texture': self.texture(x)
            },
            'styles': {
                'modern': self.modern(x),
                'traditional': self.traditional(x)
            },
            'room_harmony': torch.sigmoid(self.harmony(torch.cat(elements + styles, -1)))
        }


def create_interior_design_network(input_dim: int = 128, embed_dim: int = 256):
    return InteriorDesignNetwork(input_dim, embed_dim)
