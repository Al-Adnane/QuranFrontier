"""Edge Computing Network - Distributed Processing.

Inspired by: Edge Computing
"""

import torch
import torch.nn as nn


class EdgeComputingNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Edge layers
        self.device = nn.Linear(input_dim, embed_dim)
        self.gateway = nn.Linear(input_dim, embed_dim)
        self.fog = nn.Linear(input_dim, embed_dim)
        self.edge_server = nn.Linear(input_dim, embed_dim)
        # Edge features
        self.latency = nn.Linear(input_dim, embed_dim)
        self.bandwidth = nn.Linear(input_dim, embed_dim)
        # Edge efficiency
        self.efficiency = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        layers = [self.device(x), self.gateway(x), self.fog(x), self.edge_server(x)]
        features = [self.latency(x), self.bandwidth(x)]
        return {
            'edge_layers': {
                'device': self.device(x),
                'gateway': self.gateway(x),
                'fog': self.fog(x),
                'edge_server': self.edge_server(x)
            },
            'features': {
                'latency': self.latency(x),
                'bandwidth': self.bandwidth(x)
            },
            'edge_efficiency': torch.sigmoid(self.efficiency(torch.cat(layers + features, -1)))
        }


def create_edge_computing_network(input_dim: int = 128, embed_dim: int = 256):
    return EdgeComputingNetwork(input_dim, embed_dim)
