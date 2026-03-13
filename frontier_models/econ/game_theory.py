"""Game Theory Network - Strategic Decision.

Inspired by: Game Theory
"""

import torch
import torch.nn as nn


class GameTheoryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, players: int = 2):
        super().__init__()
        self.players = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(players)])
        self.nash = nn.Linear(embed_dim * players, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        strategies = [p(x) for p in self.players]
        return {'strategies': strategies, 'nash_equilibrium': torch.sigmoid(self.nash(torch.cat(strategies, -1)))}


def create_game_theory_network(input_dim: int = 128, embed_dim: int = 256):
    return GameTheoryNetwork(input_dim, embed_dim)
