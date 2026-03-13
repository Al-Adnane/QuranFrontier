"""Big Five Personality Network - OCEAN Model.

Inspired by: Five Factor Model of Personality
"""

import torch
import torch.nn as nn


class BigFiveNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.openness = nn.Linear(input_dim, 1)
        self.conscientiousness = nn.Linear(input_dim, 1)
        self.extraversion = nn.Linear(input_dim, 1)
        self.agreeableness = nn.Linear(input_dim, 1)
        self.neuroticism = nn.Linear(input_dim, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        return {
            'openness': torch.sigmoid(self.openness(x)),
            'conscientiousness': torch.sigmoid(self.conscientiousness(x)),
            'extraversion': torch.sigmoid(self.extraversion(x)),
            'agreeableness': torch.sigmoid(self.agreeableness(x)),
            'neuroticism': torch.sigmoid(self.neuroticism(x))
        }


def create_big_five_network(input_dim: int = 128, embed_dim: int = 256):
    return BigFiveNetwork(input_dim, embed_dim)
