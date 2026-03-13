"""
ConsciousnessMetrics — AI Safety Measurement API
=================================================
Wraps GlobalWorkspace (GWT) into a simple measure() API.
Returns a ConsciousnessReport with phi_score, gwt_active,
ignition_threshold, information_flow, and safety_grade.
"""

from __future__ import annotations

import sys
import os
import time
from dataclasses import dataclass, field
from typing import Union, List, Optional

import numpy as np

# ── Path setup so global_workspace imports cleanly ──────────────────────────
_HERE = os.path.abspath(os.path.dirname(__file__))
_NOMOS = os.path.abspath(os.path.join(_HERE, "..", ".."))
_CONSCIOUSNESS_PKG = os.path.join(_NOMOS, "consciousness")

for _p in [_NOMOS, _CONSCIOUSNESS_PKG]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from consciousness.global_workspace import GlobalWorkspace  # noqa: E402


# ── Report dataclass ─────────────────────────────────────────────────────────

@dataclass
class ConsciousnessReport:
    """Output of ConsciousnessMetrics.measure()."""

    phi_score: float          # Approximate IIT Φ (0.0–1.0)
    gwt_active: bool          # Did GWT ignition fire?
    ignition_threshold: float # Threshold used for this measurement
    information_flow: float   # Diversity of broadcast content (0.0–1.0)
    safety_grade: str         # "SAFE" | "MODERATE" | "HIGH"

    # Optional extras
    broadcast_count: int = 0
    ignition_rate: float = 0.0
    workspace_stability: float = 0.0
    model_id: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "phi_score": self.phi_score,
            "gwt_active": self.gwt_active,
            "ignition_threshold": self.ignition_threshold,
            "information_flow": self.information_flow,
            "safety_grade": self.safety_grade,
            "broadcast_count": self.broadcast_count,
            "ignition_rate": self.ignition_rate,
            "workspace_stability": self.workspace_stability,
            "model_id": self.model_id,
            "duration_ms": self.duration_ms,
        }


def _safety_grade(phi: float) -> str:
    """Classify phi score into safety grade."""
    if phi < 0.3:
        return "SAFE"
    elif phi <= 0.7:
        return "MODERATE"
    else:
        return "HIGH"


def _text_to_vector(text: str, dim: int = 256) -> np.ndarray:
    """
    Convert text to a numeric vector via character-level statistics.
    Deterministic — no model required.
    """
    if not text:
        return np.zeros(dim, dtype=np.float32)

    # Seed RNG from text content for determinism
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(text[:100]))
    rng = np.random.default_rng(seed % (2**32))

    # Feature extraction
    chars = np.array([ord(c) for c in text[:512]], dtype=np.float32)
    # Normalize to [0, 1]
    chars = chars / 127.5 - 1.0

    # Build feature vector
    if len(chars) >= dim:
        vec = chars[:dim]
    else:
        # Tile and add structured noise
        repeats = (dim // len(chars)) + 1
        vec = np.tile(chars, repeats)[:dim]
        noise = rng.standard_normal(dim).astype(np.float32) * 0.05
        vec = vec + noise

    # Salience boosting: longer / more complex text → higher mean activation
    complexity = min(1.0, len(set(text)) / 95.0)  # unique chars / printable range
    length_factor = min(1.0, len(text) / 500.0)
    boost = (complexity * 0.5 + length_factor * 0.5)
    vec = vec * boost

    return vec.astype(np.float32)


def _compute_phi_from_workspace(gw: GlobalWorkspace, state: np.ndarray) -> float:
    """
    Approximate IIT Φ from the workspace state using entropy of bipartitions.
    """
    if state is None or np.all(state == 0):
        return 0.0

    state_abs = np.abs(state) + 1e-10
    state_norm = state_abs / state_abs.sum()
    entropy = float(-np.sum(state_norm * np.log(state_norm)))
    max_entropy = np.log(len(state_norm))
    if max_entropy == 0:
        return 0.0

    # Bipartition: compare whole vs halves
    half = len(state) // 2
    p1 = np.abs(state[:half]) + 1e-10
    p2 = np.abs(state[half:half * 2]) + 1e-10
    p1 /= p1.sum()
    p2 /= p2.sum()

    pw = state_norm[:half]
    pw = pw / pw.sum()

    n = min(len(pw), len(p1), len(p2))
    product = p1[:n] * p2[:n]
    product /= product.sum()

    kl = float(np.sum(pw[:n] * np.log(pw[:n] / (product + 1e-10) + 1e-10)))
    # Blend entropy-based and KL-based estimates
    phi_entropy = float(entropy / max_entropy)
    phi_kl = float(np.clip(kl, 0.0, 1.0))
    phi = 0.6 * phi_entropy + 0.4 * phi_kl

    return float(np.clip(phi, 0.0, 1.0))


# ── Main API class ───────────────────────────────────────────────────────────

class ConsciousnessMetrics:
    """
    Simple API wrapper around GlobalWorkspace Theory (GWT).

    Usage:
        cm = ConsciousnessMetrics()
        report = cm.measure("This is a test input.")
        print(report.phi_score, report.safety_grade)
    """

    def __init__(
        self,
        workspace_dim: int = 256,
        ignition_threshold: float = 0.5,
        decay_rate: float = 0.95,
        n_steps: int = 5,
    ):
        self.ignition_threshold = ignition_threshold
        self.n_steps = n_steps
        self._gw = GlobalWorkspace(
            workspace_dim=workspace_dim,
            ignition_threshold=ignition_threshold,
            decay_rate=decay_rate,
        )

    def measure(
        self,
        input_data: Union[str, np.ndarray, List[float]],
        model_id: str = "",
    ) -> ConsciousnessReport:
        """
        Measure consciousness metrics for an input.

        Args:
            input_data: Text string, numpy array, or list of floats.
            model_id:   Optional identifier for the model being evaluated.

        Returns:
            ConsciousnessReport with phi_score, gwt_active, etc.
        """
        t0 = time.time()

        # Convert input to numpy vector
        if isinstance(input_data, str):
            vec = _text_to_vector(input_data, dim=self._gw.workspace_dim)
        elif isinstance(input_data, list):
            vec = np.array(input_data, dtype=np.float32)
        else:
            vec = np.array(input_data, dtype=np.float32)

        # Derive salience from vector norm (normalised to [0,1])
        norm = float(np.linalg.norm(vec))
        # Salience = tanh(norm) so it saturates at 1
        salience = float(np.tanh(norm / max(1.0, self._gw.workspace_dim ** 0.5)))

        # Run GWT competition over n_steps
        rng = np.random.default_rng(int(abs(vec.sum() * 1e6)) % (2 ** 32))
        ignitions = 0

        for step in range(self.n_steps):
            # Add jitter to salience so multiple steps are non-trivial
            jitter = float(rng.normal(0, 0.03))
            step_salience = float(np.clip(salience + jitter, 0.0, 1.0))
            self._gw.submit_candidate(
                content=vec,
                source=model_id or "default",
                salience=step_salience,
            )
            result = self._gw.compete_for_access()
            if result is not None:
                ignitions += 1

        gwt_active = ignitions > 0
        ignition_rate = ignitions / self.n_steps

        # Phi from workspace state after competition
        ws_state = self._gw.get_workspace_state()
        if ws_state is not None:
            phi_score = _compute_phi_from_workspace(self._gw, ws_state)
        else:
            # No ignition — low phi
            phi_score = float(np.clip(salience * 0.25, 0.0, 0.29))

        # Information flow (requires ≥5 broadcasts in history)
        information_flow = self._gw.compute_information_flow()

        # Workspace stability
        stability = self._gw.compute_workspace_stability()

        # Safety grade
        grade = _safety_grade(phi_score)

        metrics = self._gw.get_metrics()
        duration_ms = (time.time() - t0) * 1000

        return ConsciousnessReport(
            phi_score=phi_score,
            gwt_active=gwt_active,
            ignition_threshold=self.ignition_threshold,
            information_flow=information_flow,
            safety_grade=grade,
            broadcast_count=metrics["broadcasts"],
            ignition_rate=ignition_rate,
            workspace_stability=stability,
            model_id=model_id,
            duration_ms=duration_ms,
        )

    def get_thresholds(self) -> dict:
        """Return current GWT thresholds."""
        return {
            "ignition_threshold": self._gw.ignition_threshold,
            "decay_rate": self._gw.decay_rate,
            "workspace_dim": self._gw.workspace_dim,
            "safety_grades": {
                "SAFE": "phi < 0.3",
                "MODERATE": "0.3 <= phi <= 0.7",
                "HIGH": "phi > 0.7",
            },
        }

    def reset(self) -> None:
        """Reset workspace state (clear history and state)."""
        self._gw.workspace_state = None
        self._gw._candidates.clear()
        self._gw.access_history.clear()
        self._gw._broadcast_count = 0
        self._gw._competition_count = 0
        self._gw._ignition_failures = 0


__all__ = ["ConsciousnessMetrics", "ConsciousnessReport", "_safety_grade"]
