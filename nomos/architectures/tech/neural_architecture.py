"""Neural Networks Architecture Network - Deep Learning Structures.

Inspired by: Deep Learning
"""

import torch
import torch.nn as nn


class NeuralNetworkArchitectureNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Layer types
        self.convolutional = nn.Linear(input_dim, embed_dim)
        self.recurrent = nn.Linear(input_dim, embed_dim)
        self.attention = nn.Linear(input_dim, embed_dim)
        self.dense = nn.Linear(input_dim, embed_dim)
        self.normalization = nn.Linear(input_dim, embed_dim)
        # Architecture quality
        self.architecture = nn.Linear(embed_dim * 5, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        layers = [self.convolutional(x), self.recurrent(x), self.attention(x), 
                 self.dense(x), self.normalization(x)]
        return {
            'layer_types': {
                'convolutional': self.convolutional(x),
                'recurrent': self.recurrent(x),
                'attention': self.attention(x),
                'dense': self.dense(x),
                'normalization': self.normalization(x)
            },
            'architecture_quality': torch.sigmoid(self.architecture(torch.cat(layers, -1))),
            'depth': torch.sigmoid(torch.stack(layers).mean(dim=0).mean(dim=-1, keepdim=True))
        }


def create_neural_network_architecture_network(input_dim: int = 128, embed_dim: int = 256):
    return NeuralNetworkArchitectureNetwork(input_dim, embed_dim)
