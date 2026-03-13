"""Sun Tzu Network - Art of War Strategy.

Inspired by: The Art of War
"""

import torch
import torch.nn as nn


class SunTzuNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Five fundamentals
        self.way = nn.Linear(input_dim, embed_dim)  # Moral law
        self.heaven = nn.Linear(input_dim, embed_dim)  # Weather/timing
        self.earth = nn.Linear(input_dim, embed_dim)  # Terrain
        self.commander = nn.Linear(input_dim, embed_dim)  # Leadership
        self.method = nn.Linear(input_dim, embed_dim)  # Discipline
        # Strategic principles
        self.know_enemy = nn.Linear(input_dim, embed_dim)
        self.know_self = nn.Linear(input_dim, embed_dim)
        self.victory_without_battle = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        way = self.way(x)
        heaven = self.heaven(x)
        earth = self.earth(x)
        commander = self.commander(x)
        method = self.method(x)
        know_enemy = self.know_enemy(x)
        know_self = self.know_self(x)
        return {
            'five_fundamentals': {'way': way, 'heaven': heaven, 'earth': earth, 'commander': commander, 'method': method},
            'know_enemy': know_enemy,
            'know_self': know_self,
            'victory_probability': torch.sigmoid(self.victory_without_battle(torch.cat([know_enemy, know_self], -1))),
            'strategic_advantage': torch.sigmoid((way + commander + method).mean(dim=-1, keepdim=True))
        }


def create_sun_tzu_network(input_dim: int = 128, embed_dim: int = 256):
    return SunTzuNetwork(input_dim, embed_dim)
