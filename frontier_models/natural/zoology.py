"""Zoology Network - Animal Classification.

Inspired by: Zoology
"""

import torch
import torch.nn as nn


ANIMAL_CLASSES = ['Mammal', 'Bird', 'Reptile', 'Amphibian', 'Fish', 'Invertebrate']


class ZoologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.classes = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(6)])
        self.classification = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        class_embs = [c(x) for c in self.classes]
        return {
            'animal_classes': dict(zip(ANIMAL_CLASSES, class_embs)),
            'classification': ANIMAL_CLASSES[torch.stack(class_embs).mean(dim=0).argmax(dim=-1)],
            'confidence': torch.sigmoid(self.classification(torch.cat(class_embs, -1)))
        }


def create_zoology_network(input_dim: int = 128, embed_dim: int = 256):
    return ZoologyNetwork(input_dim, embed_dim)
