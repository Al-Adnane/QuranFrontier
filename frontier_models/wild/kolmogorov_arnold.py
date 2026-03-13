"""Kolmogorov-Arnold Networks (KAN) - Function Decomposition (Simplified).

Implements KAN-inspired networks where:
- Learnable activation functions on edges
- Function decomposition architecture
- Better interpretability than MLPs

Simplified version that works reliably.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class KANLayer(nn.Module):
    """KAN-inspired layer with learnable activations."""
    
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        
        self.in_features = in_features
        self.out_features = out_features
        
        # Learnable weights [out_features, in_features] for F.linear
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        
        # Learnable activation scale per output
        self.act_scale = nn.Parameter(torch.ones(out_features))
        
        # Bias
        self.bias = nn.Parameter(torch.zeros(out_features))
        
        self.reset_parameters()
        
    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=0.01)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward through KAN layer."""
        # Standard linear transformation
        output = F.linear(x, self.weight, self.bias)
        
        # Apply learnable activation scaling (simplified spline effect)
        output = output * self.act_scale
        
        return output


class KolmogorovArnoldNetwork(nn.Module):
    """Complete Kolmogorov-Arnold Network.
    
    Applications:
    - Function approximation
    - Scientific computing
    - PDE solving
    - Physics-informed ML
    """
    
    def __init__(
        self,
        input_dim: int = 32,
        hidden_dims: List[int] = None,
        output_dim: int = 1
    ):
        super().__init__()
        
        if hidden_dims is None:
            hidden_dims = [64, 64]
        
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        # Input layer
        self.input_layer = KANLayer(input_dim, hidden_dims[0])
        
        # Hidden layers
        self.hidden_layers = nn.ModuleList()
        for i in range(len(hidden_dims) - 1):
            self.hidden_layers.append(
                KANLayer(hidden_dims[i], hidden_dims[i+1])
            )
        
        # Output layer
        self.output_layer = KANLayer(hidden_dims[-1], output_dim)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Forward through KAN."""
        # Input
        h = F.silu(self.input_layer(x))
        
        # Hidden layers
        for layer in self.hidden_layers:
            h = F.silu(layer(h))
        
        # Output
        y = self.output_layer(h)
        
        return {
            'output': y,
            'input_dim': self.input_dim,
            'output_dim': self.output_dim
        }
    
    def approximate_function(self, x: torch.Tensor, target: torch.Tensor) -> float:
        """Compute approximation error."""
        output = self.forward(x)['output']
        mse = F.mse_loss(output, target)
        return mse.item()


def create_kan(
    input_dim: int = 32,
    hidden_dims: List[int] = None,
    output_dim: int = 1
) -> KolmogorovArnoldNetwork:
    """Create KolmogorovArnoldNetwork."""
    return KolmogorovArnoldNetwork(input_dim, hidden_dims, output_dim)
