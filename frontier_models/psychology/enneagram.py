"""Enneagram Network - 9 Personality Types.

Inspired by: Enneagram of Personality
"""

import torch
import torch.nn as nn


TYPES = ['Reformer', 'Helper', 'Achiever', 'Individualist', 
         'Investigator', 'Loyalist', 'Enthusiast', 'Challenger', 'Peacemaker']


class EnneagramNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.types = nn.ModuleList([nn.Sequential(
            nn.Linear(input_dim, embed_dim), nn.GELU(), nn.Linear(embed_dim, 1)
        ) for _ in range(9)])
        self.wings = nn.Linear(9, 18)  # Each type has 2 wings
        
    def forward(self, x: torch.Tensor) -> dict:
        scores = torch.cat([t(x) for t in self.types], -1)
        probs = torch.softmax(scores, -1)
        dominant_idx = probs.argmax(dim=-1)
        return {
            'type_scores': dict(zip(TYPES, scores.unbind(-1))),
            'dominant_type': TYPES[dominant_idx],
            'probabilities': probs,
            'wings': self.wings(probs)
        }


def create_enneagram_network(input_dim: int = 128, embed_dim: int = 256):
    return EnneagramNetwork(input_dim, embed_dim)
