"""Diffusion Models - Score-Based Generative Modeling.

Implements Denoising Diffusion Probabilistic Models (DDPM):
- Forward: gradually add noise
- Reverse: learn to denoise
- Generate by reversing diffusion process

Architecture:
    Forward Process: q(x_t | x_{t-1})
    Reverse Process: p_θ(x_{t-1} | x_t)
    Applications: Generation, inpainting, super-resolution

Based on Ho et al. "Denoising Diffusion Probabilistic Models" (2020).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DiffusionOutput:
    """Diffusion model output."""
    sample: torch.Tensor
    trajectory: List[torch.Tensor]
    final_noise: torch.Tensor


class UNet1D(nn.Module):
    """Simple 1D UNet for diffusion."""
    
    def __init__(
        self,
        input_dim: int = 128,
        hidden_dim: int = 128,
        time_emb_dim: int = 32
    ):
        super().__init__()
        
        self.input_dim = input_dim
        
        # Time embedding
        self.time_embed = nn.Sequential(
            nn.Linear(1, time_emb_dim),
            nn.SiLU(),
            nn.Linear(time_emb_dim, hidden_dim)
        )
        
        # Encoder
        self.enc1 = nn.Linear(input_dim, hidden_dim)
        self.enc2 = nn.Linear(hidden_dim, hidden_dim * 2)
        
        # Bottleneck
        self.bottleneck = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim * 2),
            nn.SiLU(),
            nn.Linear(hidden_dim * 2, hidden_dim * 2)
        )
        
        # Decoder
        self.dec1 = nn.Linear(hidden_dim * 4, hidden_dim)
        self.dec2 = nn.Linear(hidden_dim * 2, input_dim)
        
    def forward(
        self,
        x: torch.Tensor,
        t: torch.Tensor
    ) -> torch.Tensor:
        """Predict noise given noisy input and timestep."""
        # Time embedding
        t_emb = self.time_embed(t.view(-1, 1))
        
        # Encoder
        e1 = F.silu(self.enc1(x) + t_emb)
        e2 = F.silu(self.enc2(e1))
        
        # Bottleneck
        b = self.bottleneck(e2)
        
        # Decoder with skip connections
        d1 = F.silu(self.dec1(torch.cat([b, e2], dim=-1)))
        out = self.dec2(torch.cat([d1, e1], dim=-1))
        
        return out


class DiffusionSchedule:
    """Noise schedule for diffusion process."""
    
    def __init__(
        self,
        num_steps: int = 1000,
        beta_start: float = 1e-4,
        beta_end: float = 0.02
    ):
        self.num_steps = num_steps
        
        # Linear schedule
        self.betas = torch.linspace(beta_start, beta_end, num_steps)
        
        # Precompute alphas
        self.alphas = 1 - self.betas
        self.alpha_bars = torch.cumprod(self.alphas, dim=0)
        
    def add_noise(
        self,
        x0: torch.Tensor,
        t: torch.Tensor,
        noise: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Add noise to data: x_t = sqrt(ᾱ_t) * x_0 + sqrt(1-ᾱ_t) * ε"""
        if noise is None:
            noise = torch.randn_like(x0)
        
        batch_size = x0.size(0)
        
        # Get alpha_bar for each timestep
        alpha_bar = self.alpha_bars[t].view(batch_size, -1)
        
        # Sample
        xt = torch.sqrt(alpha_bar) * x0 + torch.sqrt(1 - alpha_bar) * noise
        
        return xt, noise
    
    def sample_prior(self, shape: torch.Size, device: torch.device) -> torch.Tensor:
        """Sample from prior (pure noise)."""
        return torch.randn(shape, device=device)


class DiffusionModel(nn.Module):
    """Denoising Diffusion Probabilistic Model.
    
    Applications:
    - Data generation
    - Image synthesis
    - Data augmentation
    """
    
    def __init__(
        self,
        data_dim: int = 128,
        hidden_dim: int = 128,
        num_steps: int = 1000
    ):
        super().__init__()
        
        self.data_dim = data_dim
        self.num_steps = num_steps
        
        # UNet for noise prediction
        self.unet = UNet1D(data_dim, hidden_dim)
        
        # Diffusion schedule
        self.schedule = DiffusionSchedule(num_steps)
        
    def forward(
        self,
        x0: torch.Tensor,
        t: Optional[torch.Tensor] = None
    ) -> Dict:
        """Forward pass (training)."""
        batch_size = x0.size(0)
        
        # Sample random timestep
        if t is None:
            t = torch.randint(0, self.num_steps, (batch_size,), device=x0.device)
        
        # Add noise
        xt, noise = self.schedule.add_noise(x0, t)
        
        # Predict noise
        predicted_noise = self.unet(xt, t.float())
        
        # Compute loss
        loss = F.mse_loss(predicted_noise, noise)
        
        return {
            'loss': loss,
            'predicted_noise': predicted_noise,
            'true_noise': noise
        }
    
    @torch.no_grad()
    def sample(
        self,
        batch_size: int,
        num_steps: Optional[int] = None
    ) -> DiffusionOutput:
        """Generate samples by reversing diffusion."""
        device = next(self.parameters()).device
        
        if num_steps is None:
            num_steps = self.num_steps
        
        # Start from pure noise
        x = self.schedule.sample_prior((batch_size, self.data_dim), device)
        
        trajectory = [x.clone()]
        
        # Reverse diffusion
        for t in reversed(range(num_steps)):
            t_batch = torch.full((batch_size,), t, device=device, dtype=torch.float)
            
            # Predict noise
            predicted_noise = self.unet(x, t_batch)
            
            # Compute alpha values
            alpha = self.schedule.alphas[t].to(device)
            alpha_bar = self.schedule.alpha_bars[t].to(device)
            
            if t > 0:
                alpha_bar_prev = self.schedule.alpha_bars[t-1].to(device)
            else:
                alpha_bar_prev = torch.ones_like(alpha_bar)
            
            # Compute mean
            beta = self.schedule.betas[t].to(device)
            sigma = torch.sqrt(beta)
            
            # Reverse step
            pred_x0 = (x - torch.sqrt(1 - alpha_bar) * predicted_noise) / torch.sqrt(alpha_bar)
            direction = torch.sqrt(1 - alpha_bar_prev) * predicted_noise
            
            x = torch.sqrt(alpha_bar_prev) * pred_x0 + direction
            
            # Add noise (except last step)
            if t > 0:
                x = x + sigma * torch.randn_like(x)
            
            trajectory.append(x.clone())
        
        return DiffusionOutput(
            sample=x,
            trajectory=trajectory,
            final_noise=predicted_noise
        )
    
    @torch.no_grad()
    def interpolate(
        self,
        x0_start: torch.Tensor,
        x0_end: torch.Tensor,
        num_steps: int = 50
    ) -> List[torch.Tensor]:
        """Interpolate between two samples in latent space."""
        batch_size = x0_start.size(0)
        device = x0_start.device
        
        # Add same noise to both
        noise = torch.randn_like(x0_start)
        xt_start, _ = self.schedule.add_noise(x0_start, torch.full((batch_size,), num_steps-1, device=device), noise)
        xt_end, _ = self.schedule.add_noise(x0_end, torch.full((batch_size,), num_steps-1, device=device), noise)
        
        # Interpolate and reverse
        results = []
        for alpha in torch.linspace(0, 1, 10):
            xt_interp = alpha * xt_start + (1 - alpha) * xt_end
            output = self.sample_with_initial(xt_interp, num_steps)
            results.append(output.sample)
        
        return results
    
    def sample_with_initial(
        self,
        initial: torch.Tensor,
        num_steps: int
    ) -> DiffusionOutput:
        """Sample starting from given initial state."""
        device = next(self.parameters()).device
        x = initial
        
        trajectory = [x.clone()]
        
        for t in reversed(range(num_steps)):
            t_batch = torch.full((x.size(0),), t, device=device, dtype=torch.float)
            predicted_noise = self.unet(x, t_batch)
            
            alpha = self.schedule.alphas[t].to(device)
            alpha_bar = self.schedule.alpha_bars[t].to(device)
            alpha_bar_prev = self.schedule.alpha_bars[t-1].to(device) if t > 0 else torch.ones_like(alpha_bar)
            
            beta = self.schedule.betas[t].to(device)
            
            pred_x0 = (x - torch.sqrt(1 - alpha_bar) * predicted_noise) / torch.sqrt(alpha_bar)
            x = torch.sqrt(alpha_bar_prev) * pred_x0 + torch.sqrt(1 - alpha_bar_prev) * predicted_noise
            
            if t > 0:
                x = x + torch.sqrt(beta) * torch.randn_like(x)
            
            trajectory.append(x.clone())
        
        return DiffusionOutput(sample=x, trajectory=trajectory, final_noise=predicted_noise)


def create_diffusion_model(
    data_dim: int = 128,
    hidden_dim: int = 128
) -> DiffusionModel:
    """Create DiffusionModel."""
    return DiffusionModel(data_dim, hidden_dim)
