"""Qi Gong Network - Energy Cultivation.

Inspired by: Qi Gong / Chi Kung
"""

import torch
import torch.nn as nn


class QiGongNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Three treasures
        self.jing = nn.Linear(input_dim, embed_dim)  # Essence
        self.qi = nn.Linear(input_dim, embed_dim)    # Energy
        self.shen = nn.Linear(input_dim, embed_dim)  # Spirit
        # Dantians
        self.lower_dantian = nn.Linear(input_dim, embed_dim)
        self.middle_dantian = nn.Linear(input_dim, embed_dim)
        self.upper_dantian = nn.Linear(input_dim, embed_dim)
        # Microcosmic orbit
        self.orbit = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        jing = self.jing(x)
        qi = self.qi(x)
        shen = self.shen(x)
        lower = self.lower_dantian(x)
        middle = self.middle_dantian(x)
        upper = self.upper_dantian(x)
        return {
            'three_treasures': {'jing': jing, 'qi': qi, 'shen': shen},
            'dantians': {'lower': lower, 'middle': middle, 'upper': upper},
            'microcosmic_orbit': torch.sigmoid(self.orbit(torch.cat([jing, qi, shen, lower, middle, upper], -1))),
            'cultivation_progress': torch.sigmoid((qi + lower).mean(dim=-1, keepdim=True))
        }


def create_qi_gong_network(input_dim: int = 128, embed_dim: int = 256):
    return QiGongNetwork(input_dim, embed_dim)
