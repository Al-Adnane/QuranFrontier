"""Film Theory Network - Cinematic Elements.

Inspired by: Film Studies
"""

import torch
import torch.nn as nn


class FilmTheoryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Cinematic elements
        self.cinematography = nn.Linear(input_dim, embed_dim)
        self.editing = nn.Linear(input_dim, embed_dim)
        self.sound = nn.Linear(input_dim, embed_dim)
        self.mise_en_scene = nn.Linear(input_dim, embed_dim)
        self.acting = nn.Linear(input_dim, embed_dim)
        # Shot types
        self.shots = nn.ModuleDict({
            'close_up': nn.Linear(input_dim, embed_dim // 2),
            'medium': nn.Linear(input_dim, embed_dim // 2),
            'long': nn.Linear(input_dim, embed_dim // 2),
            'extreme_close': nn.Linear(input_dim, embed_dim // 2),
            'extreme_long': nn.Linear(input_dim, embed_dim // 2)
        })
        # Film quality
        self.quality = nn.Linear(embed_dim * 10, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        shots = {k: v(x) for k, v in self.shots.items()}
        elements = [self.cinematography(x), self.editing(x), self.sound(x), 
                   self.mise_en_scene(x), self.acting(x)]
        shot_scores = torch.stack([s.mean(dim=-1) for s in shots.values()], -1)
        return {
            'elements': {
                'cinematography': self.cinematography(x),
                'editing': self.editing(x),
                'sound': self.sound(x),
                'mise_en_scene': self.mise_en_scene(x),
                'acting': self.acting(x)
            },
            'shots': shots,
            'preferred_shot': max(shots.keys(), key=lambda k: shot_scores.max(dim=-1).values[list(shots.keys()).index(k)].item()),
            'film_quality': torch.sigmoid(self.quality(torch.cat(elements + list(shots.values()), -1)))
        }


def create_film_theory_network(input_dim: int = 128, embed_dim: int = 256):
    return FilmTheoryNetwork(input_dim, embed_dim)
