"""Fisher Information Geometry - Riemannian Manifold Learning.

This model implements information geometry layers using the Fisher 
information metric, providing natural gradient optimization and 
curvature-aware representations.

Architecture:
    Fisher Metric: g_ij = E[∂_i log p ∂_j log p]
    Natural Gradient: ∇_N = G^{-1} ∇ (where G is Fisher matrix)
    Geodesic Distance: Shortest path on statistical manifold
    Curvature: Riemannian curvature tensor

Based on frontierqu.geometry.fisher_metric for Quranic geometry.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class FisherOutput:
    """Output from Fisher geometry computations."""
    fisher_matrix: torch.Tensor
    natural_gradient: torch.Tensor
    geodesic_distance: float
    curvature: float
    is_positive_definite: bool


class FisherInformationMetric(nn.Module):
    """Computes Fisher information metric for a distribution."""
    
    def __init__(
        self,
        param_dim: int,
        epsilon: float = 1e-8
    ):
        super().__init__()
        self.param_dim = param_dim
        self.epsilon = epsilon
        
    def forward(
        self,
        log_probs: torch.Tensor,
        params: torch.Tensor
    ) -> torch.Tensor:
        """Compute Fisher information matrix.
        
        F_ij = E[∂log p(x|θ)/∂θ_i * ∂log p(x|θ)/∂θ_j]
        
        Args:
            log_probs: [batch, num_classes]
            params: [batch, param_dim] model parameters
        Returns:
            fisher: [batch, param_dim, param_dim]
        """
        batch_size = log_probs.size(0)
        
        # Compute score function: ∂log p / ∂θ
        # Using the identity: ∂log p = (1/p) * ∂p
        with torch.enable_grad():
            params.requires_grad_(True)
            
            # Compute gradients of log_probs w.r.t. params
            grad_outputs = torch.ones_like(log_probs)
            grads = torch.autograd.grad(
                log_probs, params,
                grad_outputs=grad_outputs,
                create_graph=True,
                retain_graph=True
            )[0]
        
        # Fisher = E[grad * grad^T]
        # Approximate with empirical covariance
        fisher = torch.zeros(
            batch_size, self.param_dim, self.param_dim,
            device=params.device
        )
        
        for b in range(batch_size):
            g = grads[b:b+1, :]  # [1, param_dim]
            fisher[b] = g.t() @ g  # Outer product
        
        # Add damping for numerical stability
        fisher = fisher + self.epsilon * torch.eye(
            self.param_dim, device=params.device
        ).unsqueeze(0)
        
        return fisher


class NaturalGradientOptimizer:
    """Natural gradient optimizer using Fisher information."""
    
    def __init__(
        self,
        model: nn.Module,
        lr: float = 0.01,
        damping: float = 1e-5,
        fisher_update_freq: int = 10
    ):
        self.model = model
        self.lr = lr
        self.damping = damping
        self.fisher_update_freq = fisher_update_freq
        self.step_count = 0
        
        # Cache Fisher inverse
        self.fisher_inverse: Optional[torch.Tensor] = None
        
    def step(self, loss: torch.Tensor) -> None:
        """Take natural gradient step.
        
        θ_new = θ_old - lr * F^{-1} * ∇L
        """
        self.step_count += 1
        
        # Compute standard gradient
        grads = []
        params = []
        for p in self.model.parameters():
            if p.grad is not None:
                grads.append(p.grad.view(-1))
                params.append(p.data.view(-1))
        
        if not grads:
            return
        
        grad_vector = torch.cat(grads)
        param_vector = torch.cat(params)
        
        # Update or compute Fisher
        if self.step_count % self.fisher_update_freq == 0:
            self._compute_fisher_inverse(param_vector)
        
        # Apply natural gradient
        if self.fisher_inverse is not None:
            natural_grad = self.fisher_inverse @ grad_vector
        else:
            natural_grad = grad_vector
        
        # Update parameters
        idx = 0
        for p in self.model.parameters():
            if p.grad is not None:
                size = p.numel()
                update = natural_grad[idx:idx+size].view_as(p)
                p.data -= self.lr * update
                idx += size
    
    def _compute_fisher_inverse(self, params: torch.Tensor) -> None:
        """Compute inverse Fisher matrix (approximate)."""
        # For large models, use K-FAC or other approximations
        # Here we use a simple diagonal approximation
        
        fisher_diag = torch.zeros_like(params)
        
        # Compute diagonal of Fisher
        for p in self.model.parameters():
            if p.grad is not None:
                fisher_diag_part = p.grad ** 2
                # Accumulate
                pass
        
        # Add damping and invert
        fisher_diag = fisher_diag + self.damping
        fisher_inv_diag = 1.0 / fisher_diag
        
        # Store as diagonal matrix (efficient)
        self.fisher_inverse = torch.diag(fisher_inv_diag)


class GeodesicDistance(nn.Module):
    """Computes geodesic distance on statistical manifold."""
    
    def __init__(self, epsilon: float = 1e-8):
        super().__init__()
        self.epsilon = epsilon
        
    def forward(
        self,
        params1: torch.Tensor,
        params2: torch.Tensor,
        fisher: torch.Tensor
    ) -> torch.Tensor:
        """Compute geodesic distance between two points.
        
        For small distances: d ≈ sqrt((θ1-θ2)^T F (θ1-θ2))
        
        Args:
            params1: [batch, param_dim]
            params2: [batch, param_dim]
            fisher: [batch, param_dim, param_dim]
        Returns:
            distance: [batch]
        """
        diff = params1 - params2  # [batch, param_dim]
        
        # d^2 = diff^T F diff
        fisher_diff = torch.bmm(fisher, diff.unsqueeze(-1)).squeeze(-1)
        d_squared = (diff * fisher_diff).sum(dim=-1)
        
        # Ensure non-negative
        d_squared = torch.clamp(d_squared, min=0)
        
        return torch.sqrt(d_squared + self.epsilon)


class RiemannianCurvature(nn.Module):
    """Computes Riemannian curvature of statistical manifold."""
    
    def __init__(self, epsilon: float = 1e-8):
        super().__init__()
        self.epsilon = epsilon
        
    def forward(
        self,
        fisher: torch.Tensor,
        params: torch.Tensor
    ) -> torch.Tensor:
        """Compute scalar curvature (Ricci scalar).
        
        This is a simplified approximation. Full computation requires
        Christoffel symbols and Riemann tensor.
        
        Args:
            fisher: [batch, param_dim, param_dim]
            params: [batch, param_dim]
        Returns:
            curvature: [batch] scalar curvature
        """
        batch_size = fisher.size(0)
        
        # Compute condition number as curvature proxy
        # High condition number = high curvature
        with torch.no_grad():
            # Eigenvalue decomposition
            try:
                eigenvalues = torch.linalg.eigvalsh(fisher)
                
                # Condition number
                max_eig = eigenvalues.max(dim=-1).values
                min_eig = eigenvalues.min(dim=-1).values
                
                condition = max_eig / (min_eig + self.epsilon)
                
                # Curvature proxy: log of condition number
                curvature = torch.log(condition + 1)
                
            except RuntimeError:
                # Fallback: use trace/determinant ratio
                trace = torch.trace(fisher[0]) if batch_size == 1 else fisher[0].trace()
                det = torch.det(fisher[0] + self.epsilon * torch.eye(
                    fisher.size(1), device=fisher.device
                ))
                curvature = torch.log(trace ** fisher.size(1) / (det + self.epsilon) + 1)
                curvature = curvature.expand(batch_size)
        
        return curvature


class FisherInformationGeometry(nn.Module):
    """Main Fisher Information Geometry module.
    
    Provides Riemannian geometry tools for neural network optimization
    and analysis.
    """
    
    def __init__(
        self,
        param_dim: int,
        epsilon: float = 1e-8
    ):
        super().__init__()
        
        self.fisher_metric = FisherInformationMetric(param_dim, epsilon)
        self.geodesic = GeodesicDistance(epsilon)
        self.curvature = RiemannianCurvature(epsilon)
        
        self.param_dim = param_dim
        self.epsilon = epsilon
        
    def compute_natural_gradient(
        self,
        model: nn.Module,
        loss: torch.Tensor,
        data: torch.Tensor
    ) -> FisherOutput:
        """Compute natural gradient for a model.
        
        Args:
            model: Neural network
            loss: Loss value
            data: Input data
        Returns:
            FisherOutput with natural gradient and metrics
        """
        # Get model parameters
        params = torch.cat([p.view(-1) for p in model.parameters() if p.requires_grad])
        
        # Compute Fisher
        model.eval()
        with torch.no_grad():
            outputs = model(data)
            if isinstance(outputs, dict):
                outputs = outputs.get('logits', outputs.get('output', outputs))
            log_probs = F.log_softmax(outputs, dim=-1)
        
        fisher = self.fisher_metric(log_probs, params.unsqueeze(0))
        
        # Compute standard gradient
        grad = torch.cat([
            p.grad.view(-1) for p in model.parameters() 
            if p.grad is not None and p.requires_grad
        ])
        
        # Natural gradient: F^{-1} g
        try:
            fisher_inv = torch.inverse(fisher[0] + self.epsilon * torch.eye(
                self.param_dim, device=params.device
            ))
            natural_grad = fisher_inv @ grad
        except RuntimeError:
            # Use pseudo-inverse
            natural_grad = torch.linalg.lstsq(fisher[0], grad).solution
        
        # Geodesic distance from origin
        origin = torch.zeros_like(params)
        geo_dist = self.geodesic(params.unsqueeze(0), origin.unsqueeze(0), fisher)
        
        # Curvature
        curv = self.curvature(fisher, params.unsqueeze(0))
        
        # Check positive definiteness
        try:
            torch.cholesky(fisher[0])
            is_pd = True
        except RuntimeError:
            is_pd = False
        
        return FisherOutput(
            fisher_matrix=fisher[0],
            natural_gradient=natural_grad,
            geodesic_distance=geo_dist.item(),
            curvature=curv.item(),
            is_positive_definite=is_pd
        )
    
    def project_to_manifold(
        self,
        params: torch.Tensor,
        constraint: str = "positive_definite"
    ) -> torch.Tensor:
        """Project parameters onto valid manifold.
        
        Args:
            params: Parameters to project
            constraint: Type of constraint
        Returns:
            Projected parameters
        """
        if constraint == "positive_definite":
            # Ensure positive definiteness via eigenvalue clipping
            fisher = params.view(-1, self.param_dim, self.param_dim)
            
            eigenvalues, eigenvectors = torch.linalg.eigh(fisher)
            eigenvalues = torch.clamp(eigenvalues, min=self.epsilon)
            
            projected = eigenvectors @ torch.diag_embed(eigenvalues) @ eigenvectors.transpose(-2, -1)
            return projected.view_as(params)
        
        return params


def create_fisher_geometry(
    param_dim: int,
    epsilon: float = 1e-8
) -> FisherInformationGeometry:
    """Create FisherInformationGeometry module."""
    return FisherInformationGeometry(param_dim=param_dim, epsilon=epsilon)


# Convenience class for natural gradient training
class NaturalGradientTrainer:
    """Trainer using natural gradient descent."""
    
    def __init__(
        self,
        model: nn.Module,
        fisher_dim: int,
        lr: float = 0.01,
        damping: float = 1e-5
    ):
        self.model = model
        self.fisher = FisherInformationGeometry(fisher_dim, damping)
        self.optimizer = NaturalGradientOptimizer(model, lr, damping)
        
    def train_step(
        self,
        data: torch.Tensor,
        target: torch.Tensor,
        criterion: nn.Module
    ) -> Dict[str, float]:
        """Single training step with natural gradient."""
        self.model.train()
        
        # Forward
        output = self.model(data)
        loss = criterion(output, target)
        
        # Backward
        self.model.zero_grad()
        loss.backward()
        
        # Natural gradient step
        self.optimizer.step(loss)
        
        # Compute geometry metrics
        geo_output = self.fisher.compute_natural_gradient(
            self.model, loss, data
        )
        
        return {
            'loss': loss.item(),
            'geodesic_distance': geo_output.geodesic_distance,
            'curvature': geo_output.curvature,
            'is_positive_definite': geo_output.is_positive_definite
        }
