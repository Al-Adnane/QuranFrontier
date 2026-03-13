"""Clausewitz Network - On War Theory.

Inspired by: Carl von Clausewitz
"""

import torch
import torch.nn as nn


class ClausewitzNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Trinity
        self.people = nn.Linear(input_dim, embed_dim)  # Primordial violence
        self.army = nn.Linear(input_dim, embed_dim)  # Chance and probability
        self.government = nn.Linear(input_dim, embed_dim)  # Political aim
        # Fog of war
        self.fog = nn.Linear(input_dim, embed_dim)
        self.friction = nn.Linear(input_dim, embed_dim)
        # Center of gravity
        self.cog = nn.Linear(embed_dim * 5, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        people = self.people(x)
        army = self.army(x)
        government = self.government(x)
        fog = self.fog(x)
        friction = self.friction(x)
        return {
            'trinity': {'people': people, 'army': army, 'government': government},
            'fog_of_war': torch.sigmoid(fog.mean(dim=-1, keepdim=True)),
            'friction': torch.sigmoid(friction.mean(dim=-1, keepdim=True)),
            'center_of_gravity': torch.sigmoid(self.cog(torch.cat([people, army, government, fog, friction], -1))),
            'war_politics_alignment': torch.sigmoid((government + people).mean(dim=-1, keepdim=True))
        }


def create_clausewitz_network(input_dim: int = 128, embed_dim: int = 256):
    return ClausewitzNetwork(input_dim, embed_dim)
