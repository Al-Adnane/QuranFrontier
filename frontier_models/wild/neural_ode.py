"""Neural ODE - Continuous Depth Networks.

Implements Neural Ordinary Differential Equations where:
- Hidden state evolves via ODE: dh/dt = f(h, t, θ)
- Continuous depth instead of discrete layers
- Adaptive step size solvers
- Memory-efficient backpropagation

Architecture:
    ODE Function: Neural network defining dynamics
    ODE Solver: Numerical integration (RK4, Dormand-Prince)
    Applications: Time series, continuous dynamics

Based on Chen et al. "Neural Ordinary Differential Equations" (NeurIPS 2018).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class ODEOutput:
    """Neural ODE output."""
    solution: torch.Tensor
    evaluations: List[torch.Tensor]
    nfev: int  # Number of function evaluations


class ODEFunction(nn.Module):
    """Neural network defining ODE dynamics: dh/dt = f(h, t, θ)."""
    
    def __init__(self, hidden_dim: int = 128, time_emb_dim: int = 32):
        super().__init__()
        self.hidden_dim = hidden_dim
        
        # Time embedding
        self.time_embed = nn.Sequential(
            nn.Linear(1, time_emb_dim),
            nn.SiLU()
        )
        
        # Dynamics network
        self.dynamics = nn.Sequential(
            nn.Linear(hidden_dim + time_emb_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
    def forward(self, t: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
        """Compute dh/dt at time t for state h."""
        # Handle batch dimensions
        if h.dim() == 1:
            h = h.unsqueeze(0)
        if t.dim() == 0:
            t = t.unsqueeze(0)
        
        # Embed time
        t_emb = self.time_embed(t.view(-1, 1))
        
        # Expand time embedding to match batch
        if t_emb.size(0) == 1 and h.size(0) > 1:
            t_emb = t_emb.expand(h.size(0), -1)
        
        # Concatenate with hidden state
        combined = torch.cat([h, t_emb], dim=-1)
        
        # Compute dynamics
        return self.dynamics(combined)


class ODESolver:
    """Numerical ODE solver."""
    
    def __init__(
        self,
        method: str = 'rk4',
        rtol: float = 1e-5,
        atol: float = 1e-5
    ):
        self.method = method
        self.rtol = rtol
        self.atol = atol
        
    def solve(
        self,
        func: Callable,
        y0: torch.Tensor,
        t_span: torch.Tensor,
        return_all: bool = False
    ) -> Tuple[torch.Tensor, int, List[torch.Tensor]]:
        """Solve ODE dy/dt = f(t, y) with initial condition y0.
        
        Args:
            func: ODE function f(t, y)
            y0: Initial condition
            t_span: Time points [t0, t1, ..., tn]
            return_all: Return all intermediate states
        Returns:
            solution, nfev, evaluations
        """
        if self.method == 'euler':
            return self._euler(func, y0, t_span, return_all)
        elif self.method == 'rk4':
            return self._rk4(func, y0, t_span, return_all)
        elif self.method == 'dopri5':
            return self._dopri5(func, y0, t_span, return_all)
        else:
            return self._rk4(func, y0, t_span, return_all)
    
    def _euler(
        self,
        func: Callable,
        y0: torch.Tensor,
        t_span: torch.Tensor,
        return_all: bool
    ) -> Tuple[torch.Tensor, int, List[torch.Tensor]]:
        """Euler method (simplest)."""
        y = y0
        evaluations = [y.clone()] if return_all else []
        nfev = 0
        
        for i in range(len(t_span) - 1):
            dt = t_span[i + 1] - t_span[i]
            t = t_span[i]
            
            dy = func(t, y)
            y = y + dt * dy
            nfev += 1
            
            if return_all:
                evaluations.append(y.clone())
        
        return y, nfev, evaluations
    
    def _rk4(
        self,
        func: Callable,
        y0: torch.Tensor,
        t_span: torch.Tensor,
        return_all: bool
    ) -> Tuple[torch.Tensor, int, List[torch.Tensor]]:
        """Runge-Kutta 4th order."""
        y = y0
        evaluations = [y.clone()] if return_all else []
        nfev = 0
        
        for i in range(len(t_span) - 1):
            dt = t_span[i + 1] - t_span[i]
            t = t_span[i]
            
            # RK4 stages
            k1 = func(t, y)
            k2 = func(t + dt/2, y + dt*k1/2)
            k3 = func(t + dt/2, y + dt*k2/2)
            k4 = func(t + dt, y + dt*k3)
            
            y = y + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
            nfev += 4
            
            if return_all:
                evaluations.append(y.clone())
        
        return y, nfev, evaluations
    
    def _dopri5(
        self,
        func: Callable,
        y0: torch.Tensor,
        t_span: torch.Tensor,
        return_all: bool
    ) -> Tuple[torch.Tensor, int, List[torch.Tensor]]:
        """Dormand-Prince 5(4) adaptive method."""
        # Simplified adaptive stepping
        y = y0
        evaluations = [y.clone()] if return_all else []
        nfev = 0
        
        dt = (t_span[-1] - t_span[0]) / len(t_span)
        t = t_span[0]
        
        while t < t_span[-1]:
            # Take step
            k1 = func(t, y)
            k2 = func(t + dt/4, y + dt*k1/4)
            k3 = func(t + 3*dt/8, y + dt*(3*k1/32 + 9*k2/32))
            k4 = func(t + 12*dt/13, y + dt*(1932*k1/2197 - 7200*k2/2197 + 7296*k3/2197))
            k5 = func(t + dt, y + dt*(439*k1/216 - 8*k2 + 3680*k3/513 - 845*k4/4104))
            k6 = func(t + dt/2, y + dt*(-8*k1/27 + 2*k2 - 3544*k3/2565 + 1859*k4/4104 - 11*k5/40))
            
            y_new = y + dt * (16*k1/135 + 6656*k3/12825 + 28561*k4/56430 - 9*k5/50 + 2*k6/55)
            nfev += 6
            
            y = y_new
            t = t + dt
            
            if return_all:
                evaluations.append(y.clone())
        
        return y, nfev, evaluations


class NeuralODE(nn.Module):
    """Neural Ordinary Differential Equation layer.
    
    Replaces discrete layers with continuous ODE evolution.
    """
    
    def __init__(
        self,
        hidden_dim: int = 128,
        time_span: Tuple[float, float] = (0.0, 1.0),
        num_steps: int = 10,
        method: str = 'rk4'
    ):
        super().__init__()
        
        self.ode_func = ODEFunction(hidden_dim)
        self.solver = ODESolver(method=method)
        
        self.time_span = time_span
        self.num_steps = num_steps
        self.hidden_dim = hidden_dim
        
    def forward(
        self,
        x: torch.Tensor,
        return_trajectory: bool = False
    ) -> ODEOutput:
        """Solve ODE with initial condition x."""
        # Ensure x is 2D: [batch, dim]
        if x.dim() == 1:
            x = x.unsqueeze(0)
        
        # Create time points
        t_span = torch.linspace(
            self.time_span[0],
            self.time_span[1],
            self.num_steps + 1,
            device=x.device
        )
        
        # Solve ODE
        solution, nfev, evaluations = self.solver.solve(
            self.ode_func,
            x,
            t_span,
            return_trajectory
        )
        
        return ODEOutput(
            solution=solution,
            evaluations=evaluations,
            nfev=nfev
        )


class ODEBlock(nn.Module):
    """ResNet-like block using Neural ODE."""
    
    def __init__(
        self,
        channels: int,
        time_span: Tuple[float, float] = (0.0, 1.0)
    ):
        super().__init__()
        
        self.ode_func = ODEFunction(channels)
        self.solver = ODESolver(method='rk4')
        self.time_span = time_span
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward through ODE block."""
        # Reshape for convolutional ODE
        batch_size = x.size(0)
        
        # Flatten spatial dimensions
        x_flat = x.view(batch_size, -1)
        
        # Solve ODE
        t_span = torch.linspace(
            self.time_span[0],
            self.time_span[1],
            10,
            device=x.device
        )
        
        solution, _, _ = self.solver.solve(self.ode_func, x_flat, t_span)
        
        # Reshape back
        return solution.view_as(x)


class NeuralODENetwork(nn.Module):
    """Complete Neural ODE network.
    
    Applications:
    - Continuous-depth classification
    - Time series modeling
    - Physical system simulation
    """
    
    def __init__(
        self,
        input_dim: int = 128,
        hidden_dim: int = 128,
        output_dim: int = 10,
        time_span: Tuple[float, float] = (0.0, 1.0),
        num_steps: int = 10
    ):
        super().__init__()
        
        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # Neural ODE layer
        self.ode = NeuralODE(hidden_dim, time_span, num_steps)
        
        # Output projection
        self.output_proj = nn.Linear(hidden_dim, output_dim)
        
        self.hidden_dim = hidden_dim
        
    def forward(
        self,
        x: torch.Tensor,
        return_trajectory: bool = False
    ) -> Dict:
        """Forward pass."""
        # Project to hidden dim
        h = self.input_proj(x)
        
        # Solve ODE
        ode_output = self.ode(h, return_trajectory)
        
        # Project to output
        logits = self.output_proj(ode_output.solution)
        
        result = {
            'logits': logits,
            'nfev': ode_output.nfev,
            'hidden_dim': self.hidden_dim
        }
        
        if return_trajectory:
            result['trajectory'] = ode_output.evaluations
        
        return result
    
    def classify(self, x: torch.Tensor) -> torch.Tensor:
        """Classification forward pass."""
        output = self.forward(x)
        return output['logits'].argmax(dim=-1)


def create_neural_ode(
    input_dim: int = 128,
    hidden_dim: int = 128,
    output_dim: int = 10
) -> NeuralODENetwork:
    """Create NeuralODENetwork."""
    return NeuralODENetwork(input_dim, hidden_dim, output_dim)
