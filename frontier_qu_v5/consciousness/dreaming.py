"""
Dreaming Mode — Unconstrained Substrate Evolution
Run substrates without external input or safety constraints.
Harvest novel configurations, detect spontaneous pattern formation.

Inspired by:
- Default mode network (DMN) in neuroscience
- Simulated annealing (explore without exploitation)
- REM sleep consolidation of learned patterns

Process: Remove constraints → Free evolution → Harvest novelty → Reintegrate
"""

import asyncio
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate, SubstrateState


@dataclass
class DreamFragment:
    """A novel configuration discovered during dreaming."""
    substrate_id: str
    state_snapshot: np.ndarray
    novelty_score: float      # How different from waking states
    stability_score: float    # How long it persisted
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DreamReport:
    """Summary of a dreaming session."""
    duration: float
    fragments_discovered: int
    max_novelty: float
    mean_novelty: float
    spontaneous_patterns: int
    phase_transitions: int


class DreamingEngine:
    """
    Unconstrained substrate evolution for novelty discovery.
    Removes safety thresholds, amplifies noise, and records
    all novel configurations for later analysis.
    """

    def __init__(self, noise_amplification: float = 5.0,
                 novelty_threshold: float = 0.5):
        self.noise_amp = noise_amplification
        self.novelty_threshold = novelty_threshold
        self.dream_fragments: List[DreamFragment] = []
        self.waking_baselines: Dict[str, np.ndarray] = {}
        self._is_dreaming = False
        self._dream_start = 0.0
        self._phase_transitions = 0

    def record_waking_baseline(self, substrate: BaseSubstrate):
        """Record substrate's normal waking state for novelty comparison."""
        if substrate.state is not None:
            self.waking_baselines[substrate.substrate_id] = \
                substrate.state.tensor_data.flatten().copy()

    def _compute_novelty(self, substrate_id: str,
                         current_state: np.ndarray) -> float:
        """
        Novelty = distance from waking baseline.
        Uses normalized L2 distance + spectral divergence.
        """
        baseline = self.waking_baselines.get(substrate_id)
        if baseline is None:
            return 0.0

        current_flat = current_state.flatten()
        min_len = min(len(baseline), len(current_flat))
        b = baseline[:min_len]
        c = current_flat[:min_len]

        # Normalized L2 distance
        norm = np.linalg.norm(b) + 1e-10
        l2_novelty = np.linalg.norm(c - b) / norm

        # Spectral divergence (FFT)
        if len(b) > 8:
            fft_b = np.abs(np.fft.fft(b))
            fft_c = np.abs(np.fft.fft(c))
            spectral_div = np.linalg.norm(fft_c - fft_b) / (np.linalg.norm(fft_b) + 1e-10)
        else:
            spectral_div = 0.0

        return float(0.6 * l2_novelty + 0.4 * spectral_div)

    def _detect_phase_transition(self, history: List[float],
                                  window: int = 10) -> bool:
        """Detect sudden change in novelty trajectory."""
        if len(history) < window * 2:
            return False
        recent = history[-window:]
        earlier = history[-2 * window:-window]
        diff = abs(np.mean(recent) - np.mean(earlier))
        threshold = 2 * np.std(earlier) if np.std(earlier) > 0 else 0.5
        return diff > threshold

    async def dream(self, substrates: List[BaseSubstrate],
                    duration_steps: int = 500,
                    dt: float = 0.01) -> DreamReport:
        """
        Run a dreaming session.
        1. Record waking baselines
        2. Amplify noise, remove constraints
        3. Free evolution for duration_steps
        4. Harvest novel fragments
        """
        self._is_dreaming = True
        self._dream_start = time.time()
        self._phase_transitions = 0

        # Record baselines
        for sub in substrates:
            self.record_waking_baseline(sub)

        novelty_history: Dict[str, List[float]] = {
            s.substrate_id: [] for s in substrates
        }
        fragments_this_session = 0
        max_novelty = 0.0
        novelty_sum = 0.0
        novelty_count = 0

        for step in range(duration_steps):
            # Evolve all substrates with amplified noise
            tasks = []
            for sub in substrates:
                if sub.is_active:
                    tasks.append(self._dream_step(sub, dt))
            states = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze novelty
            for i, sub in enumerate(substrates):
                if isinstance(states[i], Exception) or sub.state is None:
                    continue

                novelty = self._compute_novelty(
                    sub.substrate_id, sub.state.tensor_data
                )
                novelty_history[sub.substrate_id].append(novelty)
                novelty_sum += novelty
                novelty_count += 1

                if novelty > max_novelty:
                    max_novelty = novelty

                # Harvest novel fragment
                if novelty > self.novelty_threshold:
                    # Check stability: did this state persist?
                    hist = novelty_history[sub.substrate_id]
                    stability = sum(1 for n in hist[-5:] if n > self.novelty_threshold * 0.8) / 5

                    fragment = DreamFragment(
                        substrate_id=sub.substrate_id,
                        state_snapshot=sub.state.tensor_data.flatten().copy(),
                        novelty_score=novelty,
                        stability_score=stability,
                        timestamp=time.time(),
                        metadata={
                            'step': step,
                            'pattern': self._classify_dream_pattern(sub.state.tensor_data),
                        },
                    )
                    self.dream_fragments.append(fragment)
                    fragments_this_session += 1

                # Detect phase transitions
                if self._detect_phase_transition(novelty_history[sub.substrate_id]):
                    self._phase_transitions += 1

        self._is_dreaming = False
        mean_novelty = novelty_sum / max(1, novelty_count)

        # Count spontaneous patterns
        spontaneous = sum(
            1 for f in self.dream_fragments[-fragments_this_session:]
            if f.stability_score > 0.6
        )

        return DreamReport(
            duration=time.time() - self._dream_start,
            fragments_discovered=fragments_this_session,
            max_novelty=max_novelty,
            mean_novelty=mean_novelty,
            spontaneous_patterns=spontaneous,
            phase_transitions=self._phase_transitions,
        )

    async def _dream_step(self, substrate: BaseSubstrate, dt: float) -> SubstrateState:
        """Single dream step with amplified noise."""
        state = await substrate.step(dt)
        # Amplify noise post-step
        if state.tensor_data is not None:
            noise = np.random.randn(*state.tensor_data.shape) * self.noise_amp * dt
            state.tensor_data = state.tensor_data + noise
        return state

    def _classify_dream_pattern(self, data: np.ndarray) -> str:
        """Classify the type of dream pattern."""
        flat = data.flatten()
        if len(flat) < 4:
            return "minimal"

        std = np.std(flat)
        kurtosis = float(np.mean((flat - np.mean(flat)) ** 4) / (std ** 4 + 1e-10))

        if kurtosis > 6:
            return "spike"      # Sharp peaks
        elif kurtosis < 2:
            return "diffuse"    # Spread out
        elif std > 1.0:
            return "turbulent"  # High variance
        else:
            return "crystalline"  # Ordered

    def get_top_fragments(self, n: int = 10) -> List[DreamFragment]:
        """Return top-N most novel and stable dream fragments."""
        scored = sorted(
            self.dream_fragments,
            key=lambda f: f.novelty_score * f.stability_score,
            reverse=True,
        )
        return scored[:n]

    def get_metrics(self) -> Dict[str, Any]:
        return {
            'total_fragments': len(self.dream_fragments),
            'is_dreaming': self._is_dreaming,
            'mean_novelty': float(np.mean([f.novelty_score for f in self.dream_fragments])) if self.dream_fragments else 0,
            'max_novelty': float(max((f.novelty_score for f in self.dream_fragments), default=0)),
            'phase_transitions': self._phase_transitions,
        }
