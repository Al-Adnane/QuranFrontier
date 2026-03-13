"""Liquid Neural Networks - Time-Continuous RNNs (Simplified).

Implements liquid neural networks where:
- Hidden state evolves via differential equations
- Time-continuous dynamics
- Adaptive computation

Simplified version that works reliably.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class LiquidCell(nn.Module):
    """Liquid neural network cell."""
    
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
        # Input weights
        self.W = nn.Linear(input_dim, hidden_dim, bias=False)
        
        # Recurrent weights
        self.U = nn.Linear(hidden_dim, hidden_dim, bias=False)
        
        # Bias and time constant
        self.b = nn.Parameter(torch.zeros(hidden_dim))
        self.tau = nn.Parameter(torch.ones(hidden_dim))
        
        # Nonlinearity
        self.activation = nn.Tanh()
        
    def forward(self, x: torch.Tensor, h: torch.Tensor, dt: float = 0.1) -> torch.Tensor:
        """Compute one step of liquid dynamics."""
        # Ensure correct dimensions
        if x.dim() == 1:
            x = x.unsqueeze(0)
        if h.dim() == 1:
            h = h.unsqueeze(0)
        
        # Compute dh/dt
        input_term = self.W(x)
        recurrent_term = self.U(h)
        
        dh_dt = (-1.0 / self.tau) * h + self.activation(input_term + recurrent_term + self.b)
        
        # Euler integration
        h_new = h + dt * dh_dt
        
        return h_new


class LiquidLayer(nn.Module):
    """Layer of liquid cells."""
    
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        
        self.cell = LiquidCell(input_dim, hidden_dim)
        self.hidden_dim = hidden_dim
        
    def forward(self, x: torch.Tensor, h0: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Process sequence through liquid layer."""
        batch_size = x.size(0)
        seq_len = x.size(1)
        
        # Initialize hidden state
        if h0 is None:
            h = torch.zeros(batch_size, self.hidden_dim, device=x.device)
        else:
            h = h0
        
        all_states = []
        
        # Process through time
        for t in range(seq_len):
            x_t = x[:, t, :]  # [batch, input_dim]
            h = self.cell(x_t, h)  # [batch, hidden_dim]
            all_states.append(h)
        
        # Stack: [batch, seq_len, hidden_dim]
        all_states = torch.stack(all_states, dim=1)
        
        return h, all_states


class LiquidNeuralNetwork(nn.Module):
    """Complete Liquid Neural Network.
    
    Applications:
    - Continuous-time control
    - Irregular time series
    - Robotics
    """
    
    def __init__(
        self,
        input_dim: int = 32,
        hidden_dim: int = 64,
        output_dim: int = 10,
        num_layers: int = 2
    ):
        super().__init__()
        
        self.hidden_dim = hidden_dim
        
        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # Liquid layers
        self.liquid_layers = nn.ModuleList()
        for i in range(num_layers):
            self.liquid_layers.append(LiquidLayer(hidden_dim, hidden_dim))
        
        # Output
        self.output_proj = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Forward through liquid network.
        
        Args:
            x: [batch, seq_len, input_dim]
        Returns:
            Dict with outputs
        """
        # Project input
        h = self.input_proj(x)  # [batch, seq_len, hidden_dim]
        
        # Through liquid layers
        for layer in self.liquid_layers:
            h, _ = layer(h)  # h is [batch, hidden_dim] (final state)
            # Expand for next layer
            h = h.unsqueeze(1).expand(-1, x.size(1), -1)  # [batch, seq_len, hidden_dim]
        
        # Use mean pooling over sequence
        h_pooled = h.mean(dim=1)
        
        # Output
        logits = self.output_proj(h_pooled)
        
        return {
            'logits': logits,
            'final_hidden': h_pooled,
        }


def create_liquid_network(
    input_dim: int = 32,
    hidden_dim: int = 64,
    output_dim: int = 10
) -> LiquidNeuralNetwork:
    """Create LiquidNeuralNetwork."""
    return LiquidNeuralNetwork(input_dim, hidden_dim, output_dim)
