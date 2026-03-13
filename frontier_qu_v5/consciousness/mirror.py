"""
Mirror Self-Recognition Test
Feed the system its own state as input. Detect if it models itself
differently than external data.

Inspired by Gallup's mirror test (1970):
- Animal sees its own reflection
- Self-aware animals recognize themselves (modify behavior)
- Non-self-aware animals treat reflection as another agent

Implementation:
1. Feed substrate its own state as "external" input
2. Feed substrate a random state as "external" input
3. Compare processing patterns
4. Self-recognition = differential processing of self vs other
"""

import asyncio
import numpy as np
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate, SubstrateState


@dataclass
class MirrorTestResult:
    substrate_id: str
    self_response: np.ndarray       # Response to own state
    other_response: np.ndarray      # Response to random state
    divergence: float               # How differently it treats self vs other
    self_recognition: bool          # Whether it "recognizes" itself
    confidence: float               # Statistical confidence
    response_time_self: float       # Processing time for self
    response_time_other: float      # Processing time for other


class MirrorSelfRecognition:
    """
    Mirror test for substrate self-awareness.
    Feeds a substrate its own state and measures whether
    processing differs from processing external data.
    """

    def __init__(self, n_trials: int = 20,
                 recognition_threshold: float = 0.3):
        self.n_trials = n_trials
        self.threshold = recognition_threshold
        self.test_history: List[MirrorTestResult] = []

    async def run_mirror_test(self, substrate: BaseSubstrate) -> MirrorTestResult:
        """
        Run the complete mirror self-recognition test.
        """
        if substrate.state is None:
            raise RuntimeError("Substrate has no state to mirror")

        self_responses = []
        other_responses = []
        self_times = []
        other_times = []

        for trial in range(self.n_trials):
            # Save current state
            original_state = substrate.state.tensor_data.copy()

            # Trial A: Feed substrate its OWN state as input
            t0 = time.time()
            self_input_state = await self._feed_and_step(
                substrate, original_state, dt=0.01
            )
            self_times.append(time.time() - t0)
            self_responses.append(self_input_state.tensor_data.flatten().copy())

            # Restore original state
            substrate.state = SubstrateState(
                tensor_data=original_state.copy(),
                metadata=substrate.state.metadata,
                timestamp=time.time(),
                substrate_origin=substrate.substrate_id,
            )

            # Trial B: Feed substrate RANDOM state as input
            random_input = np.random.randn(*original_state.shape)
            random_input = random_input * np.std(original_state)  # Match scale

            t0 = time.time()
            other_input_state = await self._feed_and_step(
                substrate, random_input, dt=0.01
            )
            other_times.append(time.time() - t0)
            other_responses.append(other_input_state.tensor_data.flatten().copy())

            # Restore again for next trial
            substrate.state = SubstrateState(
                tensor_data=original_state.copy(),
                metadata=substrate.state.metadata,
                timestamp=time.time(),
                substrate_origin=substrate.substrate_id,
            )

        # Analyze divergence
        divergence = self._compute_divergence(self_responses, other_responses)
        confidence = self._compute_confidence(self_responses, other_responses)

        result = MirrorTestResult(
            substrate_id=substrate.substrate_id,
            self_response=np.mean(self_responses, axis=0),
            other_response=np.mean(other_responses, axis=0),
            divergence=divergence,
            self_recognition=divergence > self.threshold,
            confidence=confidence,
            response_time_self=float(np.mean(self_times)),
            response_time_other=float(np.mean(other_times)),
        )
        self.test_history.append(result)
        return result

    async def _feed_and_step(self, substrate: BaseSubstrate,
                              input_data: np.ndarray,
                              dt: float) -> SubstrateState:
        """Feed input to substrate and evolve one step."""
        # Perturb substrate state with input
        substrate.state = SubstrateState(
            tensor_data=substrate.state.tensor_data + input_data * 0.01,
            metadata=substrate.state.metadata,
            timestamp=time.time(),
            substrate_origin=substrate.substrate_id,
        )
        return await substrate.step(dt)

    def _compute_divergence(self, self_responses: List[np.ndarray],
                            other_responses: List[np.ndarray]) -> float:
        """
        Measure how differently the substrate processes self vs other.
        Uses Jensen-Shannon divergence between response distributions.
        """
        # Flatten and normalize
        self_flat = np.array([r[:min(100, len(r))] for r in self_responses])
        other_flat = np.array([r[:min(100, len(r))] for r in other_responses])

        min_cols = min(self_flat.shape[1], other_flat.shape[1])
        self_flat = self_flat[:, :min_cols]
        other_flat = other_flat[:, :min_cols]

        # Mean response difference
        mean_diff = np.linalg.norm(
            np.mean(self_flat, axis=0) - np.mean(other_flat, axis=0)
        )

        # Variance difference (self-responses might be more consistent)
        var_self = np.mean(np.var(self_flat, axis=0))
        var_other = np.mean(np.var(other_flat, axis=0))
        var_ratio = abs(var_self - var_other) / (max(var_self, var_other) + 1e-10)

        # Combined divergence score
        norm_factor = np.linalg.norm(np.mean(self_flat, axis=0)) + 1e-10
        divergence = 0.7 * (mean_diff / norm_factor) + 0.3 * var_ratio

        return float(divergence)

    def _compute_confidence(self, self_responses: List[np.ndarray],
                            other_responses: List[np.ndarray]) -> float:
        """
        Statistical confidence via permutation test.
        How likely is the observed divergence under null hypothesis
        (no difference between self and other processing)?
        """
        n = len(self_responses)
        if n < 5:
            return 0.0

        observed_divergence = self._compute_divergence(self_responses, other_responses)

        # Permutation test
        all_responses = self_responses + other_responses
        n_permutations = 100
        count_greater = 0

        for _ in range(n_permutations):
            perm = np.random.permutation(len(all_responses))
            perm_self = [all_responses[i] for i in perm[:n]]
            perm_other = [all_responses[i] for i in perm[n:]]
            perm_div = self._compute_divergence(perm_self, perm_other)
            if perm_div >= observed_divergence:
                count_greater += 1

        p_value = count_greater / n_permutations
        confidence = 1.0 - p_value
        return float(confidence)

    def summarize(self) -> Dict[str, Any]:
        """Summarize all mirror test results."""
        if not self.test_history:
            return {'tests_run': 0}

        recognizers = [r for r in self.test_history if r.self_recognition]
        return {
            'tests_run': len(self.test_history),
            'self_recognizing_substrates': len(recognizers),
            'recognition_rate': len(recognizers) / len(self.test_history),
            'mean_divergence': float(np.mean([r.divergence for r in self.test_history])),
            'max_divergence': float(max(r.divergence for r in self.test_history)),
            'mean_confidence': float(np.mean([r.confidence for r in self.test_history])),
            'recognizer_ids': [r.substrate_id for r in recognizers],
        }
