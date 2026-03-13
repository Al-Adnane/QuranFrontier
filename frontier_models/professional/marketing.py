"""Marketing Network - Consumer Behavior.

Inspired by: Marketing Theory
"""

import torch
import torch.nn as nn


class MarketingNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Marketing mix (4Ps)
        self.product = nn.Linear(input_dim, embed_dim)
        self.price = nn.Linear(input_dim, embed_dim)
        self.place = nn.Linear(input_dim, embed_dim)
        self.promotion = nn.Linear(input_dim, embed_dim)
        # Consumer behavior
        self.awareness = nn.Linear(input_dim, embed_dim)
        self.purchase = nn.Linear(input_dim, embed_dim)
        # Campaign success
        self.success = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        mix = [self.product(x), self.price(x), self.place(x), self.promotion(x)]
        behavior = [self.awareness(x), self.purchase(x)]
        return {
            'marketing_mix': {
                'product': self.product(x),
                'price': self.price(x),
                'place': self.place(x),
                'promotion': self.promotion(x)
            },
            'consumer_behavior': {
                'awareness': self.awareness(x),
                'purchase_intent': self.purchase(x)
            },
            'campaign_success': torch.sigmoid(self.success(torch.cat(mix + behavior, -1)))
        }


def create_marketing_network(input_dim: int = 128, embed_dim: int = 256):
    return MarketingNetwork(input_dim, embed_dim)
