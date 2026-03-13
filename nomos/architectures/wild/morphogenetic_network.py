"""Morphogenetic Network - Biological Development-Inspired Learning.

Implements morphogenetic principles from developmental biology:
- Morphogen gradients guide cell differentiation
- Reaction-diffusion creates patterns
- Growth follows genetic programs
- Self-organization from simple rules

Architecture:
    Morphogen Field: Diffusing signaling molecules
    Cell Network: Differentiable cell units
    Genetic Program: Learnable development rules
    Pattern Formation: Emergent structure

Applications:
- Neural architecture search
- Self-organizing systems
- Pattern generation
- Growth-based optimization
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MorphogenState:
    """State of morphogenetic field."""
    morphogen_concentration: torch.Tensor
    cell_types: torch.Tensor
    pattern: torch.Tensor
    developmental_stage: int


class MorphogenField(nn.Module):
    """Simulates morphogen diffusion and gradient formation."""
    
    def __init__(
        self,
        grid_size: Tuple[int, int] = (32, 32),
        num_morphogens: int = 4
    ):
        super().__init__()
        self.grid_size = grid_size
        self.num_morphogens = num_morphogens
        
        # Morphogen sources (learnable)
        self.sources = nn.Parameter(torch.randn(num_morphogens, 2, grid_size[0], grid_size[1]) * 0.1)
        
        # Diffusion rates (learnable per morphogen)
        self.diffusion_rates = nn.Parameter(torch.ones(num_morphogens) * 0.1)
        
        # Decay rates
        self.decay_rates = nn.Parameter(torch.ones(num_morphogens) * 0.01)
        
    def forward(
        self,
        initial: Optional[torch.Tensor] = None,
        steps: int = 10
    ) -> torch.Tensor:
        """Simulate morphogen diffusion over time."""
        device = self.sources.device
        
        if initial is None:
            # Start from sources
            concentration = self.sources.sum(dim=0, keepdim=True)
        else:
            concentration = initial
        
        # Diffusion simulation (simplified Laplacian)
        for _ in range(steps):
            # Laplacian (discrete approximation)
            laplacian = self._compute_laplacian(concentration)
            
            # Reaction-diffusion update
            for m in range(self.num_morphogens):
                diff = self.diffusion_rates[m] * laplacian[:, m:m+1]
                decay = self.decay_rates[m] * concentration[:, m:m+1]
                concentration[:, m:m+1] = concentration[:, m:m+1] + diff - decay
        
        return concentration
    
    def _compute_laplacian(self, x: torch.Tensor) -> torch.Tensor:
        """Compute discrete Laplacian."""
        # Simple 3x3 Laplacian kernel approximation
        batch, channels, h, w = x.shape
        
        # Shift operations for Laplacian
        left = F.pad(x[:, :, :, :-1], (1, 0, 0, 0), mode='replicate')
        right = F.pad(x[:, :, :, 1:], (0, 1, 0, 0), mode='replicate')
        up = F.pad(x[:, :, :-1, :], (0, 0, 1, 0), mode='replicate')
        down = F.pad(x[:, :, 1:, :], (0, 0, 0, 1), mode='replicate')
        
        laplacian = left + right + up + down - 4 * x
        return laplacian


class CellNetwork(nn.Module):
    """Network of differentiable cells that respond to morphogens."""
    
    def __init__(
        self,
        num_cell_types: int = 8,
        num_morphogens: int = 4,
        hidden_dim: int = 64
    ):
        super().__init__()
        self.num_cell_types = num_cell_types
        self.num_morphogens = num_morphogens
        
        # Cell response to morphogens
        self.response_net = nn.Sequential(
            nn.Linear(num_morphogens, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, num_cell_types)
        )
        
        # Cell-cell communication
        self.communication = nn.Conv2d(num_cell_types, num_cell_types, 3, padding=1)
        
    def forward(
        self,
        morphogen_field: torch.Tensor,
        cell_state: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Update cell states based on morphogen concentrations."""
        batch, channels, h, w = morphogen_field.shape
        
        # Reshape for per-cell processing
        morph_flat = morphogen_field.permute(0, 2, 3, 1).reshape(batch * h * w, channels)
        
        # Cell type determination
        cell_logits = self.response_net(morph_flat)
        cell_probs = F.softmax(cell_logits, dim=-1)
        
        # Reshape back
        cell_types = cell_probs.reshape(batch, h, w, self.num_cell_types)
        cell_types = cell_types.permute(0, 3, 1, 2)
        
        # Cell communication
        if cell_state is not None:
            if cell_state.shape[1] != self.communication.in_channels:
                # Resize communication layer
                old_weight = self.communication.weight.data
                self.communication = nn.Conv2d(cell_state.shape[1], self.num_cell_types, 3, padding=1).to(cell_state.device)
            cell_types = cell_types + self.communication(cell_state)
        
        return cell_types


class GeneticProgram(nn.Module):
    """Learnable genetic program controlling development."""
    
    def __init__(
        self,
        input_dim: int = 64,
        hidden_dim: int = 128,
        output_dim: int = 32
    ):
        super().__init__()
        
        # Gene regulatory network
        self.grn = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # Gene expression thresholds
        self.thresholds = nn.Parameter(torch.randn(output_dim) * 0.5)
        
    def forward(self, cell_state: torch.Tensor) -> torch.Tensor:
        """Execute genetic program on cell state."""
        expression = self.grn(cell_state)
        
        # Apply thresholds (genes turn on/off)
        activated = (expression > self.thresholds.unsqueeze(0)).float()
        
        return activated


class MorphogeneticNetwork(nn.Module):
    """Main morphogenetic development network.
    
    Simulates biological development for:
    - Self-organizing pattern formation
    - Neural architecture search
    - Growth-based optimization
    """
    
    def __init__(
        self,
        grid_size: Tuple[int, int] = (32, 32),
        num_morphogens: int = 4,
        num_cell_types: int = 8
    ):
        super().__init__()
        
        self.grid_size = grid_size
        self.num_morphogens = num_morphogens
        self.num_cell_types = num_cell_types
        
        self.morphogen_field = MorphogenField(grid_size, num_morphogens)
        self.cell_network = CellNetwork(num_cell_types, num_morphogens)
        self.genetic_program = GeneticProgram(num_cell_types, 128, num_cell_types)
        
        # Developmental stage tracking
        self.stage = 0
        
    def develop(
        self,
        initial_condition: Optional[torch.Tensor] = None,
        num_steps: int = 20
    ) -> List[MorphogenState]:
        """Simulate developmental process."""
        device = next(self.parameters()).device
        batch_size = 1 if initial_condition is None else initial_condition.size(0)
        
        states = []
        cell_state = None
        
        for step in range(num_steps):
            # Update morphogen field - ensure correct number of morphogens
            morphogens = self.morphogen_field(initial_condition, steps=2)
            
            # Ensure morphogens has correct channel count
            if morphogens.size(1) != self.num_morphogens:
                # Adjust morphogen output to match expected
                if morphogens.size(1) < self.num_morphogens:
                    # Pad with zeros
                    padding = torch.zeros(batch_size, self.num_morphogens - morphogens.size(1), 
                                         morphogens.size(2), morphogens.size(3), device=device)
                    morphogens = torch.cat([morphogens, padding], dim=1)
                else:
                    # Truncate
                    morphogens = morphogens[:, :self.num_morphogens]
            
            # Update cell states
            cell_state = self.cell_network(morphogens, cell_state)
            
            # Execute genetic program
            cell_flat = cell_state.permute(0, 2, 3, 1).reshape(-1, self.num_cell_types)
            gene_expression = self.genetic_program(cell_flat)
            
            # Record state
            state = MorphogenState(
                morphogen_concentration=morphogens,
                cell_types=cell_state,
                pattern=gene_expression.reshape(batch_size, self.grid_size[0], self.grid_size[1], -1).permute(0, 3, 1, 2),
                developmental_stage=step
            )
            states.append(state)
        
        self.stage = num_steps
        return states
    
    def extract_architecture(self, final_state: MorphogenState) -> Dict:
        """Extract neural architecture from final pattern."""
        pattern = final_state.pattern
        
        # Analyze pattern complexity
        complexity = pattern.std(dim=(2, 3)).mean().item()
        
        # Cell type distribution
        cell_dist = final_state.cell_types.mean(dim=(2, 3)).squeeze(0)
        
        # Suggested architecture
        layer_sizes = []
        for i in range(min(self.num_cell_types, len(cell_dist))):
            if cell_dist[i].item() > 0.1:
                layer_sizes.append(int(cell_dist[i].item() * 512) + 64)
        
        num_layers = len(layer_sizes) + 2 if layer_sizes else 3
        
        return {
            'num_layers': num_layers,
            'layer_sizes': layer_sizes,
            'complexity': complexity,
            'pattern_entropy': self._compute_entropy(pattern).item()
        }
    
    def _compute_entropy(self, x: torch.Tensor) -> torch.Tensor:
        """Compute pattern entropy."""
        probs = F.softmax(x, dim=1)
        return -(probs * torch.log(probs + 1e-9)).sum(dim=1).mean()
    
    def forward(
        self,
        initial: Optional[torch.Tensor] = None,
        developmental_time: int = 20
    ) -> Dict:
        """Run morphogenetic development."""
        states = self.develop(initial, developmental_time)
        final_state = states[-1]
        
        architecture = self.extract_architecture(final_state)
        
        return {
            'final_state': final_state,
            'all_states': states,
            'architecture': architecture,
            'developmental_stage': self.stage
        }


def create_morphogenetic_network(
    grid_size: Tuple[int, int] = (32, 32),
    num_morphogens: int = 4,
    num_cell_types: int = 8
) -> MorphogeneticNetwork:
    """Create MorphogeneticNetwork."""
    return MorphogeneticNetwork(grid_size, num_morphogens, num_cell_types)
