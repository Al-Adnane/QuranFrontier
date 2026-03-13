"""Blockchain Network - Distributed Ledger.

Inspired by: Blockchain Technology
"""

import torch
import torch.nn as nn


class BlockchainNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Blockchain components
        self.block = nn.Linear(input_dim, embed_dim)
        self.chain = nn.Linear(input_dim, embed_dim)
        self.consensus = nn.Linear(input_dim, embed_dim)
        self.smart_contract = nn.Linear(input_dim, embed_dim)
        # Mining/Validation
        self.mining = nn.Linear(input_dim, embed_dim)
        # Network health
        self.network = nn.Linear(embed_dim * 5, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        components = [self.block(x), self.chain(x), self.consensus(x),
                     self.smart_contract(x), self.mining(x)]
        return {
            'components': {
                'block': self.block(x),
                'chain': self.chain(x),
                'consensus': self.consensus(x),
                'smart_contract': self.smart_contract(x),
                'mining': self.mining(x)
            },
            'network_health': torch.sigmoid(self.network(torch.cat(components, -1))),
            'decentralization': torch.sigmoid(self.consensus(x).mean(dim=-1, keepdim=True))
        }


def create_blockchain_network(input_dim: int = 128, embed_dim: int = 256):
    return BlockchainNetwork(input_dim, embed_dim)
