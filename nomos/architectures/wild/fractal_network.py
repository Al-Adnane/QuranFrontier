"""Fractal Neural Network - Self-Similar Hierarchical Architecture.

Implements fractal/self-similar neural architectures where:
- Same computation pattern repeats at different scales
- Each level is a transformed copy of levels above/below
- Scale-invariant representations
- Infinite depth limit (in theory)

Architecture:
    Fractal Block: Self-similar computational unit
    Scale Transform: Maps between resolution levels
    Recursive Processing: Apply same function at each scale
    Aggregation: Combine information across scales

Applications:
- Multi-scale image analysis
- Hierarchical reasoning
- Recursive problem solving
- Scale-invariant pattern recognition
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class FractalBlock(nn.Module):
    """Self-similar computational block.
    
    Same structure at every scale, with scale-specific parameters.
    """
    
    def __init__(self, dim: int, scale: int = 0):
        super().__init__()
        self.dim = dim
        self.scale = scale
        
        # Core computation (same at all scales)
        self.transform = nn.Sequential(
            nn.Linear(dim, dim * 2),
            nn.GELU(),
            nn.Linear(dim * 2, dim)
        )
        
        # Scale-specific modulation
        self.scale_modulation = nn.Parameter(torch.randn(dim) * 0.1)
        
        # Gating (controls information flow between scales)
        self.gate = nn.Sequential(
            nn.Linear(dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        x: torch.Tensor,
        from_coarse: Optional[torch.Tensor] = None,
        from_fine: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Process with fractal computation."""
        # Base transformation
        h = self.transform(x)
        
        # Scale modulation
        h = h * (1 + self.scale_modulation.unsqueeze(0))
        
        # Integrate from other scales
        if from_coarse is not None:
            h = h + self.gate(from_coarse) * from_coarse
        if from_fine is not None:
            h = h + self.gate(from_fine) * from_fine
        
        # Residual connection
        return x + h


class ScaleTransform(nn.Module):
    """Transforms between scale levels."""
    
    def __init__(self, dim: int, direction: str = 'up'):
        super().__init__()
        self.direction = direction
        
        if direction == 'up':
            # Coarse to fine: expand
            self.transform = nn.Linear(dim, dim)
        else:
            # Fine to coarse: pool
            self.transform = nn.Linear(dim, dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.transform(x)


class FractalLayer(nn.Module):
    """Complete fractal layer with recursive processing."""
    
    def __init__(
        self,
        dim: int,
        depth: int = 4,
        scale_range: Tuple[int, int] = (0, 3)
    ):
        super().__init__()
        self.depth = depth
        self.scale_range = scale_range
        
        # Fractal blocks at each scale
        self.blocks = nn.ModuleList([
            FractalBlock(dim, scale=i)
            for i in range(scale_range[1] - scale_range[0] + 1)
        ])
        
        # Scale transforms
        self.up_transforms = nn.ModuleList([
            ScaleTransform(dim, 'up')
            for _ in range(len(self.blocks) - 1)
        ])
        self.down_transforms = nn.ModuleList([
            ScaleTransform(dim, 'down')
            for _ in range(len(self.blocks) - 1)
        ])
        
    def forward(self, x: torch.Tensor) -> List[torch.Tensor]:
        """Process through fractal hierarchy.
        
        Returns outputs at each scale level.
        """
        outputs = []
        
        # Initialize all scales
        scale_states = [x.clone() for _ in range(len(self.blocks))]
        
        # Iterative refinement (could also be recursive)
        for _ in range(self.depth):
            new_states = []
            
            for i, block in enumerate(self.blocks):
                # Get inputs from adjacent scales
                from_coarse = self.up_transforms[i-1](scale_states[i-1]) if i > 0 else None
                from_fine = self.down_transforms[i](scale_states[i+1]) if i < len(self.blocks) - 1 else None
                
                # Process at this scale
                new_state = block(scale_states[i], from_coarse, from_fine)
                new_states.append(new_state)
            
            scale_states = new_states
        
        return scale_states


class FractalNeuralNetwork(nn.Module):
    """Main fractal neural network.
    
    Self-similar architecture with scale-invariant processing.
    """
    
    def __init__(
        self,
        input_dim: int = 256,
        hidden_dim: int = 512,
        num_fractal_layers: int = 4,
        fractal_depth: int = 4
    ):
        super().__init__()
        
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # Stacked fractal layers
        self.fractal_layers = nn.ModuleList([
            FractalLayer(hidden_dim, fractal_depth)
            for _ in range(num_fractal_layers)
        ])
        
        # Scale aggregation
        self.aggregation = nn.MultiheadAttention(hidden_dim, num_heads=8)
        
        # Output
        self.output_proj = nn.Linear(hidden_dim, input_dim)
        
        self.hidden_dim = hidden_dim
        self.num_fractal_layers = num_fractal_layers
        
    def forward(
        self,
        x: torch.Tensor,
        return_all_scales: bool = False
    ) -> Dict:
        """Forward through fractal network."""
        # Project to hidden dim
        h = self.input_proj(x)
        
        all_scale_outputs = []
        
        # Process through fractal layers
        for layer in self.fractal_layers:
            scale_outputs = layer(h)
            all_scale_outputs.append(scale_outputs)
            
            # Aggregate across scales
            aggregated = self._aggregate_scales(scale_outputs)
            h = aggregated
        
        # Output
        output = self.output_proj(h)
        
        result = {
            'output': output,
            'final_hidden': h
        }
        
        if return_all_scales:
            result['all_scales'] = all_scale_outputs
        
        return result
    
    def _aggregate_scales(
        self,
        scale_outputs: List[torch.Tensor]
    ) -> torch.Tensor:
        """Aggregate information across scales."""
        # Stack and attend
        stacked = torch.stack(scale_outputs, dim=0)
        
        # Self-attention across scales
        batch_size = stacked.size(1)
        stacked_flat = stacked.view(-1, stacked.size(-1))
        
        attended, _ = self.aggregation(
            stacked_flat.unsqueeze(0),
            stacked_flat.unsqueeze(0),
            stacked_flat.unsqueeze(0)
        )
        
        # Mean across scales
        attended = attended.view(len(scale_outputs), batch_size, -1)
        return attended.mean(dim=0)
    
    def compute_fractal_dimension(
        self,
        x: torch.Tensor
    ) -> float:
        """Estimate fractal dimension of representation.
        
        Uses box-counting approximation.
        """
        with torch.no_grad():
            h = self.input_proj(x)
            
            # Get representations at different scales
            scale_outputs = self.fractal_layers[0](h)
            
            # Compute variance at each scale
            variances = [s.var().item() for s in scale_outputs]
            
            # Fractal dimension from variance scaling
            # log(var) ~ -D * log(scale)
            scales = list(range(1, len(variances) + 1))
            
            if len(variances) > 1 and variances[0] > 0:
                # Simple estimate from first two scales
                ratio = variances[0] / (variances[1] + 1e-9)
                dimension = 2 - torch.log(torch.tensor(ratio)).item() / torch.log(torch.tensor(2.0)).item()
            else:
                dimension = 2.0
            
            return max(0, min(3, dimension))


def create_fractal_network(
    input_dim: int = 256,
    hidden_dim: int = 512,
    num_layers: int = 4
) -> FractalNeuralNetwork:
    """Create FractalNeuralNetwork."""
    return FractalNeuralNetwork(input_dim, hidden_dim, num_layers)
