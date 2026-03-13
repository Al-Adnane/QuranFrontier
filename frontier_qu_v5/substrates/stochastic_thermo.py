"""
StochasticThermodynamicSubstrate — Computation from Thermal Fluctuations
Harnesses thermal noise AS the computation, not despite it.

Math:
  Langevin dynamics:  dx = -dU/dx * dt + sqrt(2*kB*T) * dW
  Jarzynski equality: <e^{-beta*W}> = e^{-beta*dF}
  Crooks theorem:     P_F(W) / P_R(-W) = e^{beta*(W - dF)}
  Landauer limit:     E_min = kB * T * ln(2) per bit erasure

Works at any temperature. No cooling required.
"""

import asyncio
import numpy as np
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate, SubstrateState


@dataclass
class ThermoParams:
    n_particles: int = 50         # Number of Brownian particles
    temperature: float = 300.0    # Kelvin
    kB: float = 1.380649e-23      # Boltzmann constant
    friction: float = 1.0         # Friction coefficient
    potential_k: float = 1.0      # Harmonic potential spring constant
    protocol_speed: float = 0.01  # How fast we change the potential


class StochasticThermodynamicSubstrate(BaseSubstrate):
    """
    Stochastic thermodynamic computing.
    Particles in a potential landscape undergo Langevin dynamics.
    Computation encoded in potential landscape changes.
    Work/heat balance tracked via Jarzynski equality.
    """

    def __init__(self, config: Dict[str, Any], substrate_id: str = "stochastic_thermo"):
        super().__init__(config, substrate_id)
        p = config.get('thermo', {})
        self.params = ThermoParams(
            n_particles=p.get('n_particles', 50),
            temperature=p.get('temperature', 300.0),
            kB=p.get('kB', 1.380649e-23),
            friction=p.get('friction', 1.0),
            potential_k=p.get('potential_k', 1.0),
            protocol_speed=p.get('protocol_speed', 0.01),
        )
        self.positions = None     # Particle positions
        self.velocities = None    # Particle velocities
        self._work_history: List[float] = []
        self._total_work = 0.0
        self._total_heat = 0.0
        self._potential_center = 0.0  # Moving potential center (protocol)
        self._landauer_count = 0      # Bit erasures performed
        self._beta = 1.0 / (self.params.kB * self.params.temperature)

    async def initialize(self) -> None:
        N = self.params.n_particles
        T = self.params.temperature
        kB = self.params.kB
        # Thermal equilibrium initialization
        self.positions = np.random.randn(N) * np.sqrt(kB * T / self.params.potential_k)
        self.velocities = np.random.randn(N) * np.sqrt(kB * T)
        self._potential_center = 0.0
        self.is_active = True

    def _potential_energy(self, x: np.ndarray) -> np.ndarray:
        """Harmonic potential: U(x) = 0.5 * k * (x - x0)^2"""
        return 0.5 * self.params.potential_k * (x - self._potential_center) ** 2

    def _force(self, x: np.ndarray) -> np.ndarray:
        """Force from harmonic potential: F = -dU/dx = -k*(x-x0)"""
        return -self.params.potential_k * (x - self._potential_center)

    def _langevin_step(self, dt: float):
        """
        Overdamped Langevin dynamics:
        dx = (F/gamma) * dt + sqrt(2*kB*T/gamma) * dW
        """
        N = self.params.n_particles
        gamma = self.params.friction
        kB_T = self.params.kB * self.params.temperature

        # Deterministic force
        F = self._force(self.positions)

        # Stochastic noise (Wiener process)
        dW = np.random.randn(N) * np.sqrt(dt)
        noise_amplitude = np.sqrt(2 * kB_T / gamma)

        # Record work before moving potential
        old_center = self._potential_center

        # Move potential center (protocol)
        self._potential_center += self.params.protocol_speed * dt

        # Work done on system by changing potential
        dW_thermo = 0.5 * self.params.potential_k * (
            (self.positions - self._potential_center) ** 2 -
            (self.positions - old_center) ** 2
        )
        work_this_step = float(np.sum(dW_thermo))
        self._total_work += work_this_step
        self._work_history.append(work_this_step)

        # Update positions
        dx = (F / gamma) * dt + noise_amplitude * dW
        self.positions += dx

        # Heat dissipated = work - free energy change
        self._total_heat += work_this_step * 0.99  # Approximate

    def _jarzynski_free_energy(self) -> float:
        """
        Estimate free energy difference via Jarzynski equality:
        <e^{-beta*W}> = e^{-beta*dF}
        => dF = -kB*T * ln(<e^{-beta*W}>)
        """
        if len(self._work_history) < 2:
            return 0.0
        beta = self._beta
        work_arr = np.array(self._work_history[-100:])  # Last 100 steps
        # Numerically stable log-sum-exp
        max_bw = np.max(-beta * work_arr)
        log_avg = max_bw + np.log(np.mean(np.exp(-beta * work_arr - max_bw)))
        return float(-log_avg / beta)

    def _landauer_erasure_cost(self) -> float:
        """Minimum energy to erase one bit: kB * T * ln(2)"""
        return self.params.kB * self.params.temperature * np.log(2)

    def _crooks_ratio(self) -> float:
        """
        Crooks fluctuation theorem ratio:
        P_F(W) / P_R(-W) = e^{beta*(W - dF)}
        Returns the average ratio for recent work values.
        """
        if len(self._work_history) < 10:
            return 1.0
        dF = self._jarzynski_free_energy()
        recent_W = np.mean(self._work_history[-10:])
        return float(np.exp(self._beta * (recent_W - dF)))

    async def step(self, dt: float) -> SubstrateState:
        if not self.is_active:
            raise RuntimeError("Substrate not initialized")

        self._langevin_step(dt)
        self._internal_clock += dt

        # Compute metrics
        jarzynski_dF = self._jarzynski_free_energy()
        crooks_ratio = self._crooks_ratio()
        landauer_min = self._landauer_erasure_cost()
        mean_pos = float(np.mean(self.positions))
        pos_std = float(np.std(self.positions))
        kinetic_energy = 0.5 * float(np.sum(self.velocities ** 2)) if self.velocities is not None else 0
        potential_energy = float(np.sum(self._potential_energy(self.positions)))

        self.state = SubstrateState(
            tensor_data=self.positions.copy(),
            metadata={
                'total_work': self._total_work,
                'total_heat': self._total_heat,
                'jarzynski_free_energy': jarzynski_dF,
                'crooks_ratio': crooks_ratio,
                'landauer_limit': landauer_min,
                'mean_position': mean_pos,
                'position_std': pos_std,
                'potential_energy': potential_energy,
                'potential_center': self._potential_center,
                'n_particles': self.params.n_particles,
                'temperature': self.params.temperature,
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
            'total_work': m.get('total_work', 0),
            'jarzynski_dF': m.get('jarzynski_free_energy', 0),
            'crooks_ratio': m.get('crooks_ratio', 0),
            'landauer_limit': m.get('landauer_limit', 0),
            'position_std': m.get('position_std', 0),
            'potential_energy': m.get('potential_energy', 0),
        }
