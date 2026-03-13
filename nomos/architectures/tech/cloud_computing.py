"""Cloud Computing Network - Distributed Systems.

Inspired by: Cloud Computing
"""

import torch
import torch.nn as nn


class CloudComputingNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Service models
        self.iaas = nn.Linear(input_dim, embed_dim)
        self.paas = nn.Linear(input_dim, embed_dim)
        self.saas = nn.Linear(input_dim, embed_dim)
        # Cloud features
        self.scalability = nn.Linear(input_dim, embed_dim)
        self.redundancy = nn.Linear(input_dim, embed_dim)
        self.load_balancing = nn.Linear(input_dim, embed_dim)
        # Cloud efficiency
        self.efficiency = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        services = [self.iaas(x), self.paas(x), self.saas(x)]
        features = [self.scalability(x), self.redundancy(x), self.load_balancing(x)]
        return {
            'service_models': {
                'iaas': self.iaas(x),
                'paas': self.paas(x),
                'saas': self.saas(x)
            },
            'features': {
                'scalability': self.scalability(x),
                'redundancy': self.redundancy(x),
                'load_balancing': self.load_balancing(x)
            },
            'efficiency': torch.sigmoid(self.efficiency(torch.cat(services + features, -1)))
        }


def create_cloud_computing_network(input_dim: int = 128, embed_dim: int = 256):
    return CloudComputingNetwork(input_dim, embed_dim)
