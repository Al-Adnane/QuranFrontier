"""
MorphogeneticSubstrate — Turing Reaction-Diffusion Computation
Gray-Scott model: activator-inhibitor dynamics yield emergent pattern logic gates.

Math:
  dA/dt = Da * laplace(A) - A*B^2 + f*(1-A)
  dB/dt = Db * laplace(B) + A*B^2 - (k+f)*B

Pattern classification (spots/stripes/labyrinth) serves as computational output.
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
class GrayScottParams:
    Da: float = 1.0        # Activator diffusion rate
    Db: float = 0.5        # Inhibitor diffusion rate
    f: float = 0.055       # Feed rate
    k: float = 0.062       # Kill rate
    grid_size: int = 100   # Spatial resolution


class MorphogeneticSubstrate(BaseSubstrate):
    """
    Turing reaction-diffusion patterns as logic gates.
    Pattern emergence encodes computational output:
      - Spots → binary 1
      - Stripes → binary 0
      - Labyrinth → superposition (undecided)
    """

    def __init__(self, config: Dict[str, Any], substrate_id: str = "morphogenetic"):
        super().__init__(config, substrate_id)
        p = config.get('gray_scott', {})
        self.params = GrayScottParams(
            Da=p.get('Da', 1.0),
            Db=p.get('Db', 0.5),
            f=p.get('f', 0.055),
            k=p.get('k', 0.062),
            grid_size=p.get('grid_size', 100),
        )
        self.A = None  # Activator field
        self.B = None  # Inhibitor field
        self._pattern_class = "uninitialized"

    async def initialize(self) -> None:
        n = self.params.grid_size
        self.A = np.ones((n, n))
        self.B = np.zeros((n, n))
        # Seed center with inhibitor
        cx, cy = n // 2, n // 2
        r = max(3, n // 20)
        self.B[cx - r:cx + r, cy - r:cy + r] = 1.0
        # Random perturbations for symmetry breaking
        self.A += np.random.uniform(-0.01, 0.01, (n, n))
        self.B += np.random.uniform(-0.01, 0.01, (n, n))
        self.is_active = True

    def _laplacian(self, field: np.ndarray) -> np.ndarray:
        """Discrete 2D Laplacian via finite differences (periodic boundary)."""
        return (
            np.roll(field, 1, axis=0) + np.roll(field, -1, axis=0) +
            np.roll(field, 1, axis=1) + np.roll(field, -1, axis=1) -
            4 * field
        )

    def _classify_pattern(self) -> str:
        """Classify current B-field pattern by spatial frequency analysis."""
        fft = np.fft.fft2(self.B)
        power = np.abs(fft) ** 2
        # Radial power spectrum
        n = self.params.grid_size
        cx, cy = n // 2, n // 2
        Y, X = np.ogrid[:n, :n]
        R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2).astype(int)
        max_r = min(cx, cy)
        radial_power = np.zeros(max_r)
        for r in range(max_r):
            mask = R == r
            if mask.any():
                radial_power[r] = power[mask].mean()

        peak_freq = np.argmax(radial_power[1:]) + 1  # Skip DC
        total_power = radial_power[1:].sum()
        peak_ratio = radial_power[peak_freq] / (total_power + 1e-12)

        if peak_ratio > 0.3 and peak_freq > max_r * 0.3:
            return "spots"
        elif peak_ratio > 0.2:
            return "stripes"
        else:
            return "labyrinth"

    def _shannon_entropy(self, field: np.ndarray, bins: int = 20) -> float:
        hist, _ = np.histogram(field.flatten(), bins=bins, range=(0, 1))
        prob = hist / hist.sum()
        prob = prob[prob > 0]
        return -np.sum(prob * np.log2(prob))

    async def step(self, dt: float) -> SubstrateState:
        if not self.is_active:
            raise RuntimeError("Substrate not initialized")

        # Reaction-diffusion update (Euler forward)
        LA = self._laplacian(self.A)
        LB = self._laplacian(self.B)
        reaction = self.A * (self.B ** 2)

        self.A += dt * (self.params.Da * LA - reaction + self.params.f * (1 - self.A))
        self.B += dt * (self.params.Db * LB + reaction - (self.params.k + self.params.f) * self.B)

        self.A = np.clip(self.A, 0, 1)
        self.B = np.clip(self.B, 0, 1)

        self._internal_clock += dt
        self._pattern_class = self._classify_pattern()

        entropy = self._shannon_entropy(self.B)
        energy = float(np.sum(self.A ** 2 + self.B ** 2))

        self.state = SubstrateState(
            tensor_data=self.B.copy(),
            metadata={
                'pattern_class': self._pattern_class,
                'entropy': entropy,
                'energy': energy,
                'mean_A': float(self.A.mean()),
                'mean_B': float(self.B.mean()),
                'grid_size': self.params.grid_size,
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
            'entropy': m.get('entropy', 0),
            'energy': m.get('energy', 0),
            'mean_activator': m.get('mean_A', 0),
            'mean_inhibitor': m.get('mean_B', 0),
            'pattern_class_hash': hash(self._pattern_class) % 100,
        }

    def get_logic_output(self) -> int:
        """Binary logic gate output: spots=1, stripes=0, labyrinth=-1 (undecided)."""
        mapping = {'spots': 1, 'stripes': 0, 'labyrinth': -1, 'uninitialized': -1}
        return mapping.get(self._pattern_class, -1)
