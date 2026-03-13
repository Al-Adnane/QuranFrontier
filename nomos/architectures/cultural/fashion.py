"""Fashion Network - Style and Design.

Inspired by: Fashion Industry
"""

import torch
import torch.nn as nn


class FashionNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Fashion elements
        self.color = nn.Linear(input_dim, embed_dim)
        self.fabric = nn.Linear(input_dim, embed_dim)
        self.silhouette = nn.Linear(input_dim, embed_dim)
        self.pattern = nn.Linear(input_dim, embed_dim)
        # Style types
        self.casual = nn.Linear(input_dim, embed_dim)
        self.formal = nn.Linear(input_dim, embed_dim)
        # Style coherence
        self.coherence = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        elements = [self.color(x), self.fabric(x), self.silhouette(x), self.pattern(x)]
        styles = [self.casual(x), self.formal(x)]
        return {
            'elements': {
                'color': self.color(x),
                'fabric': self.fabric(x),
                'silhouette': self.silhouette(x),
                'pattern': self.pattern(x)
            },
            'styles': {
                'casual': self.casual(x),
                'formal': self.formal(x)
            },
            'style_coherence': torch.sigmoid(self.coherence(torch.cat(elements + styles, -1)))
        }


def create_fashion_network(input_dim: int = 128, embed_dim: int = 256):
    return FashionNetwork(input_dim, embed_dim)
