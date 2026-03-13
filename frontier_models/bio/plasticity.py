"""Neural Plasticity Network - Synaptic Learning and Adaptation.

Inspired by: Brain plasticity and synaptic pruning

Architecture:
    Synaptic Weights: Learnable connections
    Hebbian Learning: Fire together, wire together
    Synaptic Pruning: Remove weak connections
    Neurogenesis: Create new neurons
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional


class NeuralPlasticityNetwork(nn.Module):
    """Neural network with biological plasticity mechanisms."""
    
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, num_neurons: int = 128):
        super().__init__()
        self.num_neurons = num_neurons
        
        # Synaptic weights (plastic)
        self.synaptic_weights = nn.Parameter(torch.randn(input_dim, num_neurons) * 0.1)
        
        # Neuron activation thresholds
        self.thresholds = nn.Parameter(torch.ones(num_neurons) * 0.5)
        
        # Neurotransmitter systems
        self.excitatory = nn.Linear(num_neurons, embed_dim)
        self.inhibitory = nn.Linear(num_neurons, embed_dim)
        
        # Plasticity regulators
        self.ltp_rate = nn.Parameter(torch.tensor(0.1))  # Long-term potentiation
        self.ltd_rate = nn.Parameter(torch.tensor(0.05))  # Long-term depression
        
        # Output
        self.output = nn.Linear(embed_dim, embed_dim)
        
    def hebbian_update(self, pre: torch.Tensor, post: torch.Tensor) -> None:
        """Apply Hebbian learning: fire together, wire together."""
        with torch.no_grad():
            # Δw = η * pre * post
            hebbian = torch.matmul(pre.unsqueeze(-1), post.unsqueeze(-2))
            self.synaptic_weights += self.ltp_rate * hebbian
            self.synaptic_weights.clamp_(-1, 1)
    
    def prune_synapses(self, threshold: float = 0.1) -> int:
        """Prune weak synaptic connections."""
        with torch.no_grad():
            weak = (self.synaptic_weights.abs() < threshold).float()
            num_pruned = weak.sum().item()
            self.synaptic_weights *= (1 - weak)
            return int(num_pruned)
    
    def forward(self, x: torch.Tensor, training: bool = True) -> Dict:
        """Forward pass with plasticity."""
        # Synaptic transmission
        synaptic_input = torch.matmul(x, self.synaptic_weights)
        
        # Apply threshold (activation function)
        activated = (synaptic_input > self.thresholds).float()
        
        # Neurotransmitter release
        excitatory_out = self.excitatory(activated)
        inhibitory_out = self.inhibitory(activated)
        
        # Balance excitation and inhibition
        balanced = excitatory_out - inhibitory_out
        balanced = F.gelu(balanced)
        
        # Output
        output = self.output(balanced)
        
        # Apply plasticity during training
        if training:
            self.hebbian_update(x, activated.mean(dim=0))
            pruned = self.prune_synapses()
        else:
            pruned = 0
        
        return {
            'output': output,
            'activation': activated,
            'synaptic_weights': self.synaptic_weights,
            'synapses_pruned': pruned,
            'plasticity': self.ltp_rate.item()
        }


def create_neural_plasticity_network(input_dim: int = 128, embed_dim: int = 256):
    """Create NeuralPlasticityNetwork."""
    return NeuralPlasticityNetwork(input_dim, embed_dim)
