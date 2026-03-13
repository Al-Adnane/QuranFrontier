"""Chakra Network - 7 Energy Centers.

Inspired by: Hindu/Yogic Chakra System
"""

import torch
import torch.nn as nn


CHAKRAS = [
    ('Root', 'Muladhara', 'Red'),
    ('Sacral', 'Svadhisthana', 'Orange'),
    ('Solar_Plexus', 'Manipura', 'Yellow'),
    ('Heart', 'Anahata', 'Green'),
    ('Throat', 'Vishuddha', 'Blue'),
    ('Third_Eye', 'Ajna', 'Indigo'),
    ('Crown', 'Sahasrara', 'Violet')
]


class ChakraNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.chakras = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(7)
        ])
        self.kundalini = nn.Linear(embed_dim * 7, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        chakra_embs = [c(x) for c in self.chakras]
        chakra_scores = torch.stack([c.mean(dim=-1) for c in chakra_embs], -1)
        balanced = torch.sigmoid(1 - chakra_scores.std(dim=-1, keepdim=True))
        return {
            'chakras': {name: {'sanskrit': san, 'color': col, 'activation': ch} 
                       for (name, san, col), ch in zip(CHAKRAS, chakra_embs)},
            'chakra_scores': torch.sigmoid(chakra_scores),
            'kundalini_rising': torch.sigmoid(self.kundalini(torch.cat(chakra_embs, -1))),
            'balance': balanced
        }


def create_chakra_network(input_dim: int = 128, embed_dim: int = 256):
    return ChakraNetwork(input_dim, embed_dim)
