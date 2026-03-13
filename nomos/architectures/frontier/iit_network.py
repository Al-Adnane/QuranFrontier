"""Integrated Information Network (IIT) - Consciousness Metrics.

Inspired by: Tononi's Integrated Information Theory

Key insights:
- Φ (phi) measures integrated information
- Consciousness = capacity to integrate information
- Whole > sum of parts (irreducibility)
- Cause-effect structure matters

Architecture:
    Partition Network: Split system into parts
    Cause-Effect Repertoire: Compute cause/effect probabilities
    Φ Computation: Measure integrated information
    Maximization: Optimize for integration
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class IntegratedInfoResult:
    """Result of integrated information computation."""
    phi: torch.Tensor  # Integrated information
    cause_info: torch.Tensor  # Information in cause repertoire
    effect_info: torch.Tensor  # Information in effect repertoire
    irreducibility: torch.Tensor  # How irreducible is the system


def compute_effective_connectivity(
    activations: torch.Tensor,
    time_lag: int = 1
) -> torch.Tensor:
    """Compute effective connectivity from time series."""
    batch_size, seq_len, num_units = activations.shape
    
    if seq_len <= time_lag:
        return torch.zeros(batch_size, num_units, num_units, device=activations.device)
    
    # Granger-style causality estimation
    past = activations[:, :-time_lag, :]
    future = activations[:, time_lag:, :]
    
    # Simple correlation-based connectivity
    connectivity = torch.bmm(past.transpose(1, 2), future) / (seq_len - time_lag)
    
    return connectivity


class PartitionModule(nn.Module):
    """Partition system into parts for Φ computation."""
    
    def __init__(self, num_units: int, num_partitions: int = 2):
        super().__init__()
        
        self.num_units = num_units
        self.num_partitions = num_partitions
        
        # Learnable partition assignment
        self.partition_weights = nn.Parameter(torch.randn(num_partitions, num_units))
        
    def forward(
        self,
        activations: torch.Tensor
    ) -> List[torch.Tensor]:
        """Partition activations into parts."""
        batch_size, seq_len, num_units = activations.shape
        
        # Get partition assignments
        partition_assignments = F.softmax(self.partition_weights, dim=-1)
        
        # Partition activations
        partitions = []
        for p in range(self.num_partitions):
            weights = partition_assignments[p].unsqueeze(0).unsqueeze(0)
            partitioned = activations * weights
            partitions.append(partitioned)
        
        return partitions


class CauseEffectRepertoire(nn.Module):
    """Compute cause and effect repertoires."""
    
    def __init__(self, num_units: int, hidden_dim: int = 128):
        super().__init__()
        
        # Cause repertoire (what states could have caused this)
        self.cause_network = nn.Sequential(
            nn.Linear(num_units, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, num_units),
            nn.Sigmoid()
        )
        
        # Effect repertoire (what states this will cause)
        self.effect_network = nn.Sequential(
            nn.Linear(num_units, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, num_units),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        current_state: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute cause and effect repertoires."""
        cause_repertoire = self.cause_network(current_state)
        effect_repertoire = self.effect_network(current_state)
        
        return cause_repertoire, effect_repertoire


class PhiComputer(nn.Module):
    """Compute integrated information (Φ)."""
    
    def __init__(self, num_units: int):
        super().__init__()
        
        self.num_units = num_units
        
        # Information loss from partitioning
        self.partition_loss = nn.MSELoss(reduction='none')
        
    def forward(
        self,
        whole_cause: torch.Tensor,
        whole_effect: torch.Tensor,
        partitioned_causes: List[torch.Tensor],
        partitioned_effects: List[torch.Tensor]
    ) -> IntegratedInfoResult:
        """Compute Φ from whole vs partitioned repertoires."""
        batch_size = whole_cause.size(0)
        
        # Compute information loss from partitioning
        cause_loss = 0
        effect_loss = 0
        
        for partitioned_cause in partitioned_causes:
            loss = self.partition_loss(whole_cause, partitioned_cause).mean(dim=-1)
            cause_loss = cause_loss + loss
        
        for partitioned_effect in partitioned_effects:
            loss = self.partition_loss(whole_effect, partitioned_effect).mean(dim=-1)
            effect_loss = effect_loss + loss
        
        # Average over partitions
        num_partitions = len(partitioned_causes)
        cause_loss = cause_loss / num_partitions
        effect_loss = effect_loss / num_partitions
        
        # Φ = min(cause_info, effect_info) - integrated information
        phi = torch.minimum(cause_loss, effect_loss)
        
        # Irreducibility (how much the whole exceeds parts)
        irreducibility = phi / (cause_loss + effect_loss + 1e-9)
        
        return IntegratedInfoResult(
            phi=phi,
            cause_info=cause_loss,
            effect_info=effect_loss,
            irreducibility=irreducibility
        )


class IntegratedInformationNetwork(nn.Module):
    """Network that maximizes integrated information.
    
    Applications:
    - Consciousness metrics
    - System integration analysis
    - Irreducibility measurement
    - Complex system modeling
    """
    
    def __init__(
        self,
        input_dim: int = 128,
        hidden_dim: int = 256,
        num_units: int = 64,
        num_partitions: int = 2
    ):
        super().__init__()
        
        self.num_units = num_units
        
        # Input projection to recurrent units
        self.input_proj = nn.Linear(input_dim, num_units)
        
        # Recurrent dynamics
        self.recurrent = nn.RNN(num_units, num_units, num_layers=2, batch_first=True)
        
        # Partition module
        self.partition = PartitionModule(num_units, num_partitions)
        
        # Cause-effect repertoire
        self.cause_effect = CauseEffectRepertoire(num_units)
        
        # Φ computation
        self.phi_computer = PhiComputer(num_units)
        
        # Integration maximization head
        self.integration_head = nn.Sequential(
            nn.Linear(num_units, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1)
        )
        
    def forward(
        self,
        x: torch.Tensor,
        compute_phi: bool = True
    ) -> Dict:
        """Process and compute integrated information.
        
        Args:
            x: [batch, seq_len, input_dim] input sequence
            compute_phi: Whether to compute Φ
        Returns:
            Dict with activations and integrated information metrics
        """
        batch_size, seq_len, _ = x.shape
        
        # Project to recurrent units
        h = self.input_proj(x)
        
        # Recurrent dynamics
        recurrent_out, _ = self.recurrent(h)
        
        # Get final state
        final_state = recurrent_out[:, -1, :]
        
        # Compute effective connectivity
        connectivity = compute_effective_connectivity(recurrent_out)
        
        # Compute Φ if requested
        phi_result = None
        if compute_phi:
            # Whole system cause-effect
            whole_cause, whole_effect = self.cause_effect(final_state)
            
            # Partitioned cause-effect
            partitions = self.partition(recurrent_out)
            partitioned_states = [p[:, -1, :] for p in partitions]
            
            partitioned_causes = []
            partitioned_effects = []
            for partitioned_state in partitioned_states:
                cause, effect = self.cause_effect(partitioned_state)
                partitioned_causes.append(cause)
                partitioned_effects.append(effect)
            
            # Compute Φ
            phi_result = self.phi_computer(
                whole_cause, whole_effect,
                partitioned_causes, partitioned_effects
            )
        
        # Integration score
        integration_score = self.integration_head(final_state)
        
        return {
            'activations': recurrent_out,
            'final_state': final_state,
            'connectivity': connectivity,
            'phi_result': phi_result,
            'integration_score': integration_score,
            'phi': phi_result.phi if phi_result else None
        }
    
    def compute_phi_only(
        self,
        activations: torch.Tensor
    ) -> torch.Tensor:
        """Compute Φ for given activations."""
        batch_size, seq_len, num_units = activations.shape
        
        final_state = activations[:, -1, :]
        
        # Whole system
        whole_cause, whole_effect = self.cause_effect(final_state)
        
        # Partitioned
        partitions = self.partition(activations)
        partitioned_states = [p[:, -1, :] for p in partitions]
        
        partitioned_causes = []
        partitioned_effects = []
        for partitioned_state in partitioned_states:
            cause, effect = self.cause_effect(partitioned_state)
            partitioned_causes.append(cause)
            partitioned_effects.append(effect)
        
        # Compute Φ
        phi_result = self.phi_computer(
            whole_cause, whole_effect,
            partitioned_causes, partitioned_effects
        )
        
        return phi_result.phi


def create_iit_network(
    input_dim: int = 128,
    hidden_dim: int = 256,
    num_units: int = 64
) -> IntegratedInformationNetwork:
    """Create IntegratedInformationNetwork."""
    return IntegratedInformationNetwork(input_dim, hidden_dim, num_units)
