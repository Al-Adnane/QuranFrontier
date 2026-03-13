"""Astrology Network - Zodiac Signs and Planets.

Inspired by: Western Astrology
"""

import torch
import torch.nn as nn


SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
           'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

HOUSES = list(range(1, 13))


class AstrologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.signs = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(12)])
        self.planets = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(10)])
        self.houses = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(12)])
        self.chart = nn.Linear(embed_dim * 34, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        sign_embs = [s(x) for s in self.signs]
        planet_embs = [p(x) for p in self.planets]
        house_embs = [h(x) for h in self.houses]
        sign_scores = torch.stack([s.mean(dim=-1) for s in sign_embs], -1)
        return {
            'signs': dict(zip(SIGNS, sign_embs)),
            'planets': dict(zip(PLANETS, planet_embs)),
            'houses': dict(zip(HOUSES, house_embs)),
            'sun_sign': SIGNS[sign_scores.argmax(dim=-1).item()],
            'chart_synthesis': torch.sigmoid(self.chart(torch.cat(sign_embs + planet_embs + house_embs, -1)))
        }


def create_astrology_network(input_dim: int = 128, embed_dim: int = 256):
    return AstrologyNetwork(input_dim, embed_dim)
