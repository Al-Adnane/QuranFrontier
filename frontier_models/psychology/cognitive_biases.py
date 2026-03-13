"""Cognitive Biases Network - 20+ Common Biases.

Inspired by: Behavioral Psychology
"""

import torch
import torch.nn as nn


class CognitiveBiasesNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.biases = nn.ModuleDict({
            'confirmation': nn.Linear(input_dim, 1),
            'anchoring': nn.Linear(input_dim, 1),
            'availability': nn.Linear(input_dim, 1),
            'dunning_kruger': nn.Linear(input_dim, 1),
            'sunk_cost': nn.Linear(input_dim, 1),
            'framing': nn.Linear(input_dim, 1),
            'hindsight': nn.Linear(input_dim, 1),
            'optimism': nn.Linear(input_dim, 1),
            'pessimism': nn.Linear(input_dim, 1),
            'status_quo': nn.Linear(input_dim, 1),
        })
        
    def forward(self, x: torch.Tensor) -> dict:
        return {name: torch.sigmoid(bias(x)) for name, bias in self.biases.items()}


def create_cognitive_biases_network(input_dim: int = 128, embed_dim: int = 256):
    return CognitiveBiasesNetwork(input_dim, embed_dim)
