"""Flow State Network - Optimal Experience.

Inspired by: Mihaly Csikszentmihalyi's Flow Theory
"""

import torch
import torch.nn as nn


class FlowStateNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.challenge = nn.Linear(input_dim, embed_dim)
        self.skill = nn.Linear(input_dim, embed_dim)
        self.flow_conditions = nn.Linear(embed_dim * 2, 9)  # 9 flow dimensions
        self.flow_state = nn.Linear(9, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        challenge = self.challenge(x)
        skill = self.skill(x)
        balance = torch.abs(challenge - skill)
        conditions = torch.sigmoid(self.flow_conditions(torch.cat([challenge, skill, balance], -1)))
        return {
            'challenge': challenge,
            'skill': skill,
            'balance': torch.exp(-balance),
            'flow_dimensions': conditions,
            'flow_state': torch.sigmoid(self.flow_state(conditions))
        }


def create_flow_state_network(input_dim: int = 128, embed_dim: int = 256):
    return FlowStateNetwork(input_dim, embed_dim)
