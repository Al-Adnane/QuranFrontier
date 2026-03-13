"""Behavioral Economics Network - Irrational Decisions.

Inspired by: Behavioral Economics
"""

import torch
import torch.nn as nn


class BehavioralEconomicsNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.rational = nn.Linear(input_dim, embed_dim)
        self.emotional = nn.Linear(input_dim, embed_dim)
        self.bias = nn.Linear(input_dim, embed_dim)
        self.decision = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        r = self.rational(x)
        e = self.emotional(x)
        b = self.bias(x)
        return {'rational': r, 'emotional': e, 'bias': b, 'decision': torch.sigmoid(self.decision(torch.cat([r, e, b], -1)))}


def create_behavioral_economics_network(input_dim: int = 128, embed_dim: int = 256):
    return BehavioralEconomicsNetwork(input_dim, embed_dim)
