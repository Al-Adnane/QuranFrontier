"""Mixture of Experts (MoE) - Sparse Expert Routing.

Implements Mixture of Experts where:
- Multiple expert networks process inputs
- Gating network routes to appropriate experts
- Sparse activation (only top-k experts used)
- Scales model capacity without compute cost

Architecture:
    Expert Network: Specialized sub-network
    Gating Network: Routes inputs to experts
    Top-k Selection: Sparse expert activation
    Applications: Large-scale models, efficient scaling

Based on Shazeer et al. "Outrageously Large Neural Networks" (2017).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MoEOutput:
    """Mixture of Experts output."""
    output: torch.Tensor
    expert_weights: torch.Tensor
    selected_experts: torch.Tensor
    load_balancing_loss: torch.Tensor


class ExpertNetwork(nn.Module):
    """Single expert network."""
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_dim: Optional[int] = None
    ):
        super().__init__()
        
        if hidden_dim is None:
            hidden_dim = input_dim * 4
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class GatingNetwork(nn.Module):
    """Routes inputs to appropriate experts."""
    
    def __init__(
        self,
        input_dim: int,
        num_experts: int,
        top_k: int = 2,
        noise_epsilon: float = 1e-2
    ):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.noise_epsilon = noise_epsilon
        
        # Gating weights
        self.gate = nn.Linear(input_dim, num_experts, bias=False)
        
        # Load balancing auxiliary loss
        self.register_buffer('expert_usage', torch.zeros(num_experts))
        
    def forward(
        self,
        x: torch.Tensor,
        training: bool = True
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Compute expert weights and select top-k experts.
        
        Returns:
            weights: [batch, num_experts] - softmax weights
            selected: [batch, top_k] - indices of selected experts
            load_loss: auxiliary load balancing loss
        """
        batch_size = x.size(0)
        
        # Compute gating scores
        gate_logits = self.gate(x)  # [batch, num_experts]
        
        # Add noise for exploration during training
        if training and self.noise_epsilon > 0:
            noise = torch.randn_like(gate_logits) * self.noise_epsilon
            gate_logits = gate_logits + noise
        
        # Softmax to get weights
        weights = F.softmax(gate_logits, dim=-1)  # [batch, num_experts]
        
        # Select top-k experts
        top_values, top_indices = torch.topk(weights, self.top_k, dim=-1)  # [batch, top_k]
        
        # Create sparse weights (only top-k non-zero)
        sparse_weights = torch.zeros_like(weights)
        sparse_weights.scatter_(1, top_indices, top_values)
        
        # Renormalize
        sparse_weights = sparse_weights / (sparse_weights.sum(dim=-1, keepdim=True) + 1e-9)
        
        # Compute load balancing loss
        load_loss = self._compute_load_balancing_loss(weights)
        
        # Update expert usage tracking
        if training:
            with torch.no_grad():
                self.expert_usage = 0.99 * self.expert_usage + 0.01 * weights.mean(dim=0)
        
        return sparse_weights, top_indices, load_loss
    
    def _compute_load_balancing_loss(self, weights: torch.Tensor) -> torch.Tensor:
        """Compute auxiliary load balancing loss.
        
        Encourages uniform expert usage.
        """
        # Fraction of total capacity used by each expert
        expert_fraction = weights.mean(dim=0)  # [num_experts]
        
        # Target: uniform usage
        target = 1.0 / self.num_experts
        
        # Loss: squared deviation from uniform
        load_loss = ((expert_fraction - target) ** 2).sum()
        
        return load_loss * self.num_experts  # Scale by num_experts


class MoELayer(nn.Module):
    """Single Mixture of Experts layer."""
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        num_experts: int = 8,
        top_k: int = 2,
        hidden_dim: Optional[int] = None,
        capacity_factor: float = 1.0
    ):
        super().__init__()
        
        self.num_experts = num_experts
        self.top_k = top_k
        self.capacity_factor = capacity_factor
        
        # Create experts
        self.experts = nn.ModuleList([
            ExpertNetwork(input_dim, output_dim, hidden_dim)
            for _ in range(num_experts)
        ])
        
        # Gating network
        self.gate = GatingNetwork(input_dim, num_experts, top_k)
        
    def forward(
        self,
        x: torch.Tensor,
        training: bool = True
    ) -> MoEOutput:
        """Forward through MoE layer."""
        batch_size = x.size(0)
        
        # Get expert weights and selections
        weights, selected_experts, load_loss = self.gate(x, training)
        
        # Process through selected experts
        outputs = torch.zeros(
            batch_size, x.size(-1),
            device=x.device, dtype=x.dtype
        )
        
        for expert_idx, expert in enumerate(self.experts):
            # Find samples that selected this expert
            mask = (selected_experts == expert_idx).any(dim=-1)
            
            if mask.any():
                # Get weights for this expert
                expert_weights = weights[mask, expert_idx].unsqueeze(-1)
                
                # Process through expert
                expert_output = expert(x[mask])
                
                # Weight and accumulate
                outputs[mask] = outputs[mask] + expert_weights * expert_output
        
        return MoEOutput(
            output=outputs,
            expert_weights=weights,
            selected_experts=selected_experts,
            load_balancing_loss=load_loss
        )


class MoENetwork(nn.Module):
    """Complete Mixture of Experts network.
    
    Applications:
    - Large-scale language models
    - Efficient model scaling
    - Multi-task learning
    """
    
    def __init__(
        self,
        input_dim: int = 512,
        hidden_dim: int = 1024,
        output_dim: int = 10,
        num_experts: int = 8,
        top_k: int = 2,
        num_moe_layers: int = 4,
        capacity_factor: float = 1.0
    ):
        super().__init__()
        
        self.num_experts = num_experts
        self.top_k = top_k
        
        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # MoE layers
        self.moe_layers = nn.ModuleList()
        for i in range(num_moe_layers):
            self.moe_layers.append(MoELayer(
                hidden_dim,
                hidden_dim,
                num_experts,
                top_k,
                hidden_dim * 4,
                capacity_factor
            ))
        
        # Output projection
        self.output_proj = nn.Linear(hidden_dim, output_dim)
        
        # Track total load balancing loss
        self.total_load_loss = torch.tensor(0.0)
        
    def forward(
        self,
        x: torch.Tensor,
        training: bool = True
    ) -> Dict:
        """Forward through MoE network."""
        # Input projection
        h = self.input_proj(x)
        
        # Track load balancing loss
        total_load_loss = 0.0
        
        # Through MoE layers
        for moe_layer in self.moe_layers:
            moe_output = moe_layer(h, training)
            h = moe_output.output
            total_load_loss = total_load_loss + moe_output.load_balancing_loss
        
        self.total_load_loss = total_load_loss
        
        # Output projection
        logits = self.output_proj(h)
        
        return {
            'logits': logits,
            'load_balancing_loss': total_load_loss,
            'num_experts': self.num_experts,
            'top_k': self.top_k
        }
    
    def train_step(
        self,
        x: torch.Tensor,
        target: torch.Tensor,
        optimizer: torch.optim.Optimizer,
        load_loss_weight: float = 0.01
    ) -> Dict:
        """Training step with load balancing."""
        self.train()
        
        # Forward
        output = self.forward(x, training=True)
        
        # Compute loss
        ce_loss = F.cross_entropy(output['logits'], target)
        total_loss = ce_loss + load_loss_weight * output['load_balancing_loss']
        
        # Backward
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
        
        return {
            'total_loss': total_loss.item(),
            'ce_loss': ce_loss.item(),
            'load_loss': output['load_balancing_loss'].item()
        }


def create_moe_network(
    input_dim: int = 512,
    hidden_dim: int = 1024,
    output_dim: int = 10,
    num_experts: int = 8,
    top_k: int = 2
) -> MoENetwork:
    """Create MoENetwork."""
    return MoENetwork(input_dim, hidden_dim, output_dim, num_experts, top_k)
