"""
ReservoirSubstrate — Echo State Network / Reservoir Computing
Exploits chaotic dynamics of recurrent networks for computation.

Math:
  x(t+1) = (1-a)*x(t) + a*tanh(W_in*u(t+1) + W*x(t))   (leaky ESN)
  y(t) = W_out * x(t)                                      (linear readout)
  Spectral Radius rho(W) < 1  ⟹  Echo State Property       (stability)

Zero training cost for reservoir — only readout layer is trained.
"""

import asyncio
import numpy as np
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate, SubstrateState


@dataclass
class ReservoirParams:
    reservoir_size: int = 200
    spectral_radius: float = 0.95
    input_dim: int = 1
    output_dim: int = 1
    leak_rate: float = 0.3
    connectivity: float = 0.1   # Sparse connections
    input_scaling: float = 1.0
    noise_level: float = 0.001


class ReservoirSubstrate(BaseSubstrate):
    """
    Echo State Network exploiting high-dimensional chaotic dynamics.
    The reservoir is a fixed random recurrent network.
    Only the readout weights are trained (linear regression).
    """

    def __init__(self, config: Dict[str, Any], substrate_id: str = "reservoir"):
        super().__init__(config, substrate_id)
        p = config.get('reservoir', {})
        self.params = ReservoirParams(
            reservoir_size=p.get('reservoir_size', 200),
            spectral_radius=p.get('spectral_radius', 0.95),
            input_dim=p.get('input_dim', 1),
            output_dim=p.get('output_dim', 1),
            leak_rate=p.get('leak_rate', 0.3),
            connectivity=p.get('connectivity', 0.1),
            input_scaling=p.get('input_scaling', 1.0),
            noise_level=p.get('noise_level', 0.001),
        )
        self.W = None       # Reservoir weight matrix
        self.W_in = None    # Input weight matrix
        self.W_out = None   # Readout weight matrix
        self.x = None       # Reservoir state vector
        self._lyapunov_est = 0.0  # Lyapunov exponent estimate
        self._prev_x = None

    async def initialize(self) -> None:
        N = self.params.reservoir_size
        d_in = self.params.input_dim
        d_out = self.params.output_dim

        # Generate sparse random reservoir
        self.W = np.random.randn(N, N)
        # Apply sparsity mask
        mask = np.random.rand(N, N) < self.params.connectivity
        self.W *= mask
        # Scale to desired spectral radius
        eigenvalues = np.linalg.eigvals(self.W)
        current_rho = np.max(np.abs(eigenvalues))
        if current_rho > 0:
            self.W *= self.params.spectral_radius / current_rho

        # Input weights (dense, scaled)
        self.W_in = np.random.randn(N, d_in) * self.params.input_scaling

        # Readout weights (random init, would be trained)
        self.W_out = np.random.randn(d_out, N) * 0.01

        # Initial state
        self.x = np.zeros(N)
        self._prev_x = np.zeros(N)
        self.is_active = True

    def _compute_lyapunov(self) -> float:
        """Estimate largest Lyapunov exponent from state divergence."""
        if self._prev_x is None:
            return 0.0
        delta = np.linalg.norm(self.x - self._prev_x)
        if delta < 1e-15:
            return 0.0
        return float(np.log(delta + 1e-15))

    async def step(self, dt: float) -> SubstrateState:
        if not self.is_active:
            raise RuntimeError("Substrate not initialized")

        self._prev_x = self.x.copy()

        # Generate input (could be external signal; here random for autonomous mode)
        u = np.random.randn(self.params.input_dim) * 0.1

        # Leaky ESN update
        pre_activation = self.W_in @ u + self.W @ self.x
        noise = np.random.randn(self.params.reservoir_size) * self.params.noise_level
        new_x = (1 - self.params.leak_rate) * self.x + \
                self.params.leak_rate * np.tanh(pre_activation) + noise
        self.x = new_x

        # Readout
        output = self.W_out @ self.x

        # Compute metrics
        self._lyapunov_est = self._compute_lyapunov()
        activation_sparsity = float(np.mean(np.abs(self.x) < 0.1))
        mean_activation = float(np.mean(np.abs(self.x)))

        self._internal_clock += dt

        self.state = SubstrateState(
            tensor_data=output,
            metadata={
                'lyapunov_exponent': self._lyapunov_est,
                'activation_sparsity': activation_sparsity,
                'mean_activation': mean_activation,
                'reservoir_size': self.params.reservoir_size,
                'spectral_radius': self.params.spectral_radius,
                'state_norm': float(np.linalg.norm(self.x)),
            },
            timestamp=time.time(),
            substrate_origin=self.substrate_id,
        )
        return self.state

    def get_metrics(self) -> Dict[str, float]:
        if self.state is None:
            return {}
        m = self.state.metadata
        return {
            'lyapunov_exponent': m.get('lyapunov_exponent', 0),
            'activation_sparsity': m.get('activation_sparsity', 0),
            'mean_activation': m.get('mean_activation', 0),
            'state_norm': m.get('state_norm', 0),
        }

    def train_readout(self, states: np.ndarray, targets: np.ndarray,
                      ridge_alpha: float = 1e-6):
        """
        Train readout weights via ridge regression.
        states: (T, N) reservoir states collected during driven mode.
        targets: (T, d_out) desired outputs.
        """
        # W_out = targets^T @ states @ (states^T @ states + alpha*I)^{-1}
        R = states.T @ states + ridge_alpha * np.eye(states.shape[1])
        self.W_out = (np.linalg.solve(R, states.T @ targets)).T
