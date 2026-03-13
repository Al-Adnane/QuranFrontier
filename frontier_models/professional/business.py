"""Business Strategy Network - Corporate Planning.

Inspired by: Business Strategy
"""

import torch
import torch.nn as nn


class BusinessStrategyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Strategy frameworks
        self.swot = nn.Linear(input_dim, embed_dim)
        self.porter_five = nn.Linear(input_dim, embed_dim)
        self.bcg_matrix = nn.Linear(input_dim, embed_dim)
        # Business functions
        self.marketing = nn.Linear(input_dim, embed_dim)
        self.operations = nn.Linear(input_dim, embed_dim)
        self.finance = nn.Linear(input_dim, embed_dim)
        # Strategy success
        self.success = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        frameworks = [self.swot(x), self.porter_five(x), self.bcg_matrix(x)]
        functions = [self.marketing(x), self.operations(x), self.finance(x)]
        return {
            'frameworks': {
                'swot': self.swot(x),
                'porter_five_forces': self.porter_five(x),
                'bcg_matrix': self.bcg_matrix(x)
            },
            'functions': {
                'marketing': self.marketing(x),
                'operations': self.operations(x),
                'finance': self.finance(x)
            },
            'strategy_success': torch.sigmoid(self.success(torch.cat(frameworks + functions, -1)))
        }


def create_business_strategy_network(input_dim: int = 128, embed_dim: int = 256):
    return BusinessStrategyNetwork(input_dim, embed_dim)
