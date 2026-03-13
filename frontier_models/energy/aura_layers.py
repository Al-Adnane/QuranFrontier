"""Aura Layers Network - 7 Energy Body Layers.

Inspired by: Aura/Energy Healing
"""

import torch
import torch.nn as nn


AURA_LAYERS = [
    ('Physical', 'Red', 'Survival'),
    ('Emotional', 'Orange', 'Feelings'),
    ('Mental', 'Yellow', 'Thoughts'),
    ('Astral', 'Green', 'Love'),
    ('Etheric', 'Blue', 'Truth'),
    ('Celestial', 'Indigo', 'Intuition'),
    ('Ketheric', 'Violet', 'Spirituality')
]


class AuraLayersNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(7)
        ])
        self.aura_field = nn.Linear(embed_dim * 7, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        layer_embs = [l(x) for l in self.layers]
        layer_scores = torch.stack([l.mean(dim=-1) for l in layer_embs], -1)
        return {
            'aura_layers': {name: {'color': color, 'theme': theme, 'activation': layer} 
                          for (name, color, theme), layer in zip(AURA_LAYERS, layer_embs)},
            'layer_scores': torch.sigmoid(layer_scores),
            'aura_field_strength': torch.sigmoid(self.aura_field(torch.cat(layer_embs, -1))),
            'dominant_layer': AURA_LAYERS[layer_scores.argmax(dim=-1).item()][0]
        }


def create_aura_layers_network(input_dim: int = 128, embed_dim: int = 256):
    return AuraLayersNetwork(input_dim, embed_dim)
