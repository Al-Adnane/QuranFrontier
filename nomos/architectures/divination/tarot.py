"""Tarot Network - 78 Card Oracle System.

Inspired by: Tarot Divination
"""

import torch
import torch.nn as nn


MAJOR_ARCANA = [
    'Fool', 'Magician', 'High_Priestess', 'Empress', 'Emperor',
    'Hierophant', 'Lovers', 'Chariot', 'Strength', 'Hermit',
    'Wheel_of_Fortune', 'Justice', 'Hanged_Man', 'Death',
    'Temperance', 'Devil', 'Tower', 'Star', 'Moon', 'Sun',
    'Judgment', 'World'
]


class TarotNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # 22 Major Arcana
        self.major_arcana = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(22)
        ])
        # Minor Arcana (4 suits x 14 cards = 56, simplified to suit-level)
        self.suits = nn.ModuleDict({
            'wands': nn.Linear(input_dim, embed_dim),
            'cups': nn.Linear(input_dim, embed_dim),
            'swords': nn.Linear(input_dim, embed_dim),
            'pentacles': nn.Linear(input_dim, embed_dim)
        })
        # Reading positions
        self.positions = nn.Linear(embed_dim * 26, 10)  # 10-card spread
        
    def forward(self, x: torch.Tensor) -> dict:
        major = [m(x) for m in self.major_arcana]
        minor = {suit: layer(x) for suit, layer in self.suits.items()}
        all_cards = major + list(minor.values())
        spread = self.positions(torch.cat(all_cards, -1))
        major_scores = torch.stack([m.mean(dim=-1) for m in major], -1)
        return {
            'major_arcana': dict(zip(MAJOR_ARCANA, major)),
            'minor_arcana': minor,
            'spread': torch.sigmoid(spread),
            'dominant_card': MAJOR_ARCANA[major_scores.argmax(dim=-1).item()]
        }


def create_tarot_network(input_dim: int = 128, embed_dim: int = 256):
    return TarotNetwork(input_dim, embed_dim)
