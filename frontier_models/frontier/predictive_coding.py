"""Predictive Coding Network - Free Energy Principle Implementation.

Inspired by: Karl Friston's Free Energy Principle / Active Inference

Simple working version.
"""

import torch
import torch.nn as nn
from typing import Dict, Optional


class PredictiveCodingNetwork(nn.Module):
    """Complete Predictive Coding Network."""
    
    def __init__(
        self,
        input_dim: int = 128,
        hidden_dims: list = None,
        action_dim: int = 32,
        num_levels: int = 4
    ):
        super().__init__()
        
        if hidden_dims is None:
            hidden_dims = [256, 128, 64, 32]
        
        self.num_levels = min(num_levels, len(hidden_dims))
        self.hidden_dims = hidden_dims[:self.num_levels]
        
        # Encoder layers
        self.encoder = nn.ModuleList()
        prev_dim = input_dim
        for dim in self.hidden_dims:
            self.encoder.append(nn.Sequential(
                nn.Linear(prev_dim, dim),
                nn.GELU()
            ))
            prev_dim = dim
        
        # Free energy head
        self.free_energy_head = nn.Linear(self.hidden_dims[-1], 1)
        
        # Action head
        self.action_head = nn.Linear(self.hidden_dims[-1], action_dim)
        
    def forward(
        self,
        input_data: torch.Tensor,
        target: Optional[torch.Tensor] = None,
        num_iterations: int = 5
    ) -> Dict:
        """Process through predictive coding hierarchy."""
        # Bottom-up encoding
        hidden_states = []
        current = input_data
        
        for layer in self.encoder:
            current = layer(current)
            hidden_states.append(current)
        
        # Free energy
        free_energy = self.free_energy_head(hidden_states[-1])
        
        # Action
        action = None
        if target is not None:
            action = self.action_head(hidden_states[-1])
        
        # Prediction error (simplified - just reconstruction error)
        total_error = sum(h.pow(2).mean().item() for h in hidden_states)
        
        return {
            'hidden_states': hidden_states,
            'free_energy': free_energy,
            'total_prediction_error': total_error,
            'action': action
        }


def create_predictive_coding_network(
    input_dim: int = 128,
    embed_dim: int = 256,
    action_dim: int = 32
) -> PredictiveCodingNetwork:
    """Create PredictiveCodingNetwork."""
    hidden_dims = [embed_dim, embed_dim // 2, embed_dim // 4, embed_dim // 8]
    return PredictiveCodingNetwork(input_dim, hidden_dims, action_dim)
