"""IoT Network - Internet of Things.

Inspired by: IoT Systems
"""

import torch
import torch.nn as nn


class IoTNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # IoT layers
        self.sensors = nn.Linear(input_dim, embed_dim)
        self.connectivity = nn.Linear(input_dim, embed_dim)
        self.edge = nn.Linear(input_dim, embed_dim)
        self.cloud = nn.Linear(input_dim, embed_dim)
        # IoT protocols
        self.mqtt = nn.Linear(input_dim, embed_dim)
        self.coap = nn.Linear(input_dim, embed_dim)
        # IoT efficiency
        self.efficiency = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        layers = [self.sensors(x), self.connectivity(x), self.edge(x), self.cloud(x)]
        protocols = [self.mqtt(x), self.coap(x)]
        return {
            'iot_layers': {
                'sensors': self.sensors(x),
                'connectivity': self.connectivity(x),
                'edge_computing': self.edge(x),
                'cloud': self.cloud(x)
            },
            'protocols': {
                'mqtt': self.mqtt(x),
                'coap': self.coap(x)
            },
            'iot_efficiency': torch.sigmoid(self.efficiency(torch.cat(layers + protocols, -1)))
        }


def create_iot_network(input_dim: int = 128, embed_dim: int = 256):
    return IoTNetwork(input_dim, embed_dim)
