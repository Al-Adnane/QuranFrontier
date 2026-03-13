"""
MemristiveSubstrate — Resistance-Based Analog Crossbar Computation
HP Labs memristor model with conductance-based matrix multiplication.

Math:
  I = M(w) * V           (Ohm's law with state-dependent conductance)
  dw/dt = mu_v * (R_on / D^2) * V   (state variable dynamics)
  G(w) = 1 / (w * R_off + (1-w) * R_on)  (conductance interpolation)

10,000x energy efficiency for matrix multiplication vs digital.
"""

import asyncio
import numpy as np
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate, SubstrateState


@dataclass
class MemristorParams:
    crossbar_rows: int = 16
    crossbar_cols: int = 16
    R_on: float = 100.0       # Minimum resistance (ohms)
    R_off: float = 10000.0    # Maximum resistance (ohms)
    mu_v: float = 1e-14       # Dopant mobility (m^2/V*s)
    D: float = 10e-9          # Device thickness (m)
    V_threshold: float = 0.5  # Switching threshold (V)


class MemristiveSubstrate(BaseSubstrate):
    """
    Analog crossbar array using HP Labs memristor model.
    Matrix-vector multiplication is O(1) in hardware (single voltage pulse).
    Weight updates via voltage pulse programming.
    """

    def __init__(self, config: Dict[str, Any], substrate_id: str = "memristive"):
        super().__init__(config, substrate_id)
        p = config.get('memristor', {})
        self.params = MemristorParams(
            crossbar_rows=p.get('crossbar_rows', 16),
            crossbar_cols=p.get('crossbar_cols', 16),
            R_on=p.get('R_on', 100.0),
            R_off=p.get('R_off', 10000.0),
            mu_v=p.get('mu_v', 1e-14),
            D=p.get('D', 10e-9),
            V_threshold=p.get('V_threshold', 0.5),
        )
        # State variable w in [0, 1] for each memristor
        self.w = None
        # Conductance matrix
        self.G = None
        # Energy accumulator
        self._total_energy = 0.0
        self._operations = 0

    async def initialize(self) -> None:
        rows, cols = self.params.crossbar_rows, self.params.crossbar_cols
        # Random initial state
        self.w = np.random.uniform(0.3, 0.7, (rows, cols))
        self.G = self._compute_conductance()
        self.is_active = True

    def _compute_conductance(self) -> np.ndarray:
        """G(w) = 1 / (w * R_off + (1-w) * R_on)"""
        R = self.w * self.params.R_off + (1 - self.w) * self.params.R_on
        return 1.0 / R

    def _apply_voltage_pulse(self, V: np.ndarray, dt: float):
        """
        Update state variable w based on applied voltage.
        dw/dt = mu_v * (R_on / D^2) * V
        Only updates where |V| > threshold.
        """
        rate = self.params.mu_v * (self.params.R_on / self.params.D ** 2)
        mask = np.abs(V) > self.params.V_threshold
        dw = np.zeros_like(self.w)
        dw[mask] = rate * V[mask] * dt
        self.w = np.clip(self.w + dw, 0, 1)
        self.G = self._compute_conductance()

    def matrix_vector_multiply(self, input_vec: np.ndarray) -> np.ndarray:
        """
        Analog matrix-vector multiplication: I = G * V
        This is O(1) in hardware — single voltage application.
        """
        cols = self.params.crossbar_cols
        if len(input_vec) < cols:
            input_vec = np.pad(input_vec, (0, cols - len(input_vec)))
        elif len(input_vec) > cols:
            input_vec = input_vec[:cols]

        output = self.G @ input_vec
        # Track energy: P = V^2 / R summed over all elements
        energy = float(np.sum(input_vec ** 2 * self.G.sum(axis=0)))
        self._total_energy += energy
        self._operations += 1
        return output

    def hebbian_update(self, pre: np.ndarray, post: np.ndarray, lr: float = 0.01):
        """
        Hebbian learning: update weights based on pre/post correlation.
        V_update = lr * outer(post, pre)
        """
        V_update = lr * np.outer(post[:self.params.crossbar_rows],
                                  pre[:self.params.crossbar_cols])
        self._apply_voltage_pulse(V_update, dt=1e-6)

    async def step(self, dt: float) -> SubstrateState:
        if not self.is_active:
            raise RuntimeError("Substrate not initialized")

        # Generate random input signal for this step
        input_signal = np.random.randn(self.params.crossbar_cols) * 0.5
        output = self.matrix_vector_multiply(input_signal)

        # Small random drift in state (simulates thermal noise)
        noise = np.random.normal(0, 0.001, self.w.shape)
        self.w = np.clip(self.w + noise, 0, 1)
        self.G = self._compute_conductance()

        self._internal_clock += dt

        # Conductance statistics
        g_mean = float(self.G.mean())
        g_std = float(self.G.std())
        w_mean = float(self.w.mean())

        self.state = SubstrateState(
            tensor_data=output,
            metadata={
                'conductance_mean': g_mean,
                'conductance_std': g_std,
                'state_mean': w_mean,
                'total_energy_joules': self._total_energy,
                'operations': self._operations,
                'energy_per_op': self._total_energy / max(1, self._operations),
                'crossbar_size': (self.params.crossbar_rows, self.params.crossbar_cols),
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
            'conductance_mean': m.get('conductance_mean', 0),
            'conductance_std': m.get('conductance_std', 0),
            'state_mean': m.get('state_mean', 0),
            'total_energy': m.get('total_energy_joules', 0),
            'energy_per_op': m.get('energy_per_op', 0),
        }
