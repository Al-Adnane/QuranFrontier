"""Energy-Based Network - Learning Energy Landscapes.

Implements energy-based models (EBMs) where:
- Low energy = high probability
- Learning shapes the energy landscape
- Inference via sampling or optimization

Architecture:
    Energy Network: Maps input to scalar energy
    Langevin Dynamics: MCMC sampling
    Contrastive Divergence: Training objective
    Applications: Anomaly detection, generation

Based on LeCun's energy-based models framework.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EnergyOutput:
    """Energy-based model output."""
    energy: torch.Tensor
    probability: torch.Tensor
    samples: Optional[torch.Tensor]
    convergence: float


class EnergyNetwork(nn.Module):
    """Neural network that outputs scalar energy."""
    
    def __init__(self, input_dim: int = 128, hidden_dims: List[int] = None):
        super().__init__()
        
        if hidden_dims is None:
            hidden_dims = [256, 256, 128]
        
        layers = []
        prev_dim = input_dim
        for h in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, h),
                nn.LeakyReLU(0.2),
                nn.LayerNorm(h)
            ])
            prev_dim = h
        
        # Final layer outputs scalar energy
        layers.append(nn.Linear(prev_dim, 1))
        
        self.network = nn.Sequential(*layers)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Compute energy for input."""
        return self.network(x).squeeze(-1)
    
    def probability(self, x: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        """Convert energy to probability (Boltzmann distribution)."""
        energy = self.forward(x)
        return F.softmax(-energy / temperature, dim=-1)


class LangevinDynamics:
    """MCMC sampling via Langevin dynamics."""
    
    def __init__(
        self,
        energy_fn: nn.Module,
        step_size: float = 0.01,
        noise: float = 0.1,
        num_steps: int = 50
    ):
        self.energy_fn = energy_fn
        self.step_size = step_size
        self.noise = noise
        self.num_steps = num_steps
        
    def sample(
        self,
        initial: torch.Tensor,
        return_trajectory: bool = False
    ) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """Generate samples via Langevin MCMC.
        
        x_{t+1} = x_t - step_size * ∇E(x_t) + noise * ε
        """
        x = initial.clone().requires_grad_(True)
        trajectory = [x.clone()] if return_trajectory else []
        
        for step in range(self.num_steps):
            # Compute energy gradient
            energy = self.energy_fn(x).sum()
            grad = torch.autograd.grad(energy, x, create_graph=True)[0]
            
            # Langevin update
            with torch.no_grad():
                x = x - self.step_size * grad
                x = x + self.noise * torch.randn_like(x)
            
            if return_trajectory and step % 10 == 0:
                trajectory.append(x.clone())
        
        return x, trajectory


class ContrastiveDivergence:
    """Training via contrastive divergence."""
    
    def __init__(self, energy_fn: nn.Module, k: int = 5):
        self.energy_fn = energy_fn
        self.k = k  # Number of Gibbs steps
        
    def compute_loss(
        self,
        positive_samples: torch.Tensor,
        negative_samples: torch.Tensor
    ) -> torch.Tensor:
        """Contrastive divergence loss.
        
        L = E(x_positive) - E(x_negative)
        """
        pos_energy = self.energy_fn(positive_samples).mean()
        neg_energy = self.energy_fn(negative_samples).mean()
        
        return pos_energy - neg_energy


class EnergyBasedNetwork(nn.Module):
    """Main energy-based network.
    
    Applications:
    - Anomaly detection (high energy = anomaly)
    - Generative modeling (sample from low energy)
    - Classification (energy per class)
    """
    
    def __init__(
        self,
        input_dim: int = 128,
        hidden_dims: List[int] = None,
        temperature: float = 1.0
    ):
        super().__init__()
        
        self.energy_fn = EnergyNetwork(input_dim, hidden_dims)
        self.sampler = LangevinDynamics(self.energy_fn)
        self.cd = ContrastiveDivergence(self.energy_fn)
        
        self.temperature = temperature
        self.input_dim = input_dim
        
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """Compute energy of input."""
        return self.energy_fn(x)
    
    def probability(self, x: torch.Tensor) -> torch.Tensor:
        """Compute probability via Boltzmann distribution."""
        energy = self.energy_fn(x)
        return torch.exp(-energy / self.temperature)
    
    def sample(
        self,
        batch_size: int,
        steps: int = 50
    ) -> torch.Tensor:
        """Generate samples from the model."""
        # Start from random noise
        initial = torch.randn(batch_size, self.input_dim, device=next(self.parameters()).device)
        
        # Update sampler steps
        self.sampler.num_steps = steps
        
        samples, _ = self.sampler.sample(initial)
        return samples
    
    def detect_anomaly(
        self,
        x: torch.Tensor,
        threshold: Optional[float] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Detect anomalies based on energy.
        
        High energy = anomaly
        """
        energy = self.energy_fn(x)
        
        if threshold is None:
            # Use learned threshold (mean + 2*std from training)
            threshold = energy.mean() + 2 * energy.std()
        
        is_anomaly = (energy > threshold).float()
        
        return is_anomaly, energy
    
    def classify(
        self,
        x: torch.Tensor,
        class_energies: nn.ModuleDict
    ) -> torch.Tensor:
        """Classify by comparing energies across classes.
        
        Lower energy = more likely class
        """
        energies = {}
        for class_name, class_fn in class_energies.items():
            energies[class_name] = class_fn(x)
        
        # Stack and convert to probabilities
        energy_stack = torch.stack(list(energies.values()), dim=-1)
        probs = F.softmax(-energy_stack / self.temperature, dim=-1)
        
        return probs.argmax(dim=-1), probs
    
    def train_step(
        self,
        data: torch.Tensor,
        optimizer: torch.optim.Optimizer
    ) -> Dict:
        """Single training step with contrastive divergence."""
        self.train()
        
        # Generate negative samples
        with torch.no_grad():
            negative = self.sample(data.size(0), steps=10)
        
        # Compute CD loss
        loss = self.cd.compute_loss(data, negative)
        
        # Add regularization
        reg_loss = 0.01 * sum(p.pow(2).sum() for p in self.parameters())
        total_loss = loss + reg_loss
        
        # Optimize
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
        
        return {
            'loss': total_loss.item(),
            'cd_loss': loss.item(),
            'positive_energy': self.energy_fn(data).mean().item(),
            'negative_energy': self.energy_fn(negative).mean().item()
        }
    
    def forward(
        self,
        x: torch.Tensor,
        mode: str = 'energy'
    ) -> Dict:
        """Forward pass."""
        if mode == 'energy':
            return {'energy': self.energy_fn(x)}
        elif mode == 'probability':
            return {'probability': self.probability(x)}
        elif mode == 'sample':
            samples = self.sample(x.size(0))
            return {'samples': samples}
        elif mode == 'anomaly':
            is_anomaly, energy = self.detect_anomaly(x)
            return {'is_anomaly': is_anomaly, 'energy': energy}
        else:
            return {'energy': self.energy_fn(x)}


def create_energy_based_network(
    input_dim: int = 128,
    hidden_dims: List[int] = None
) -> EnergyBasedNetwork:
    """Create EnergyBasedNetwork."""
    return EnergyBasedNetwork(input_dim, hidden_dims)
