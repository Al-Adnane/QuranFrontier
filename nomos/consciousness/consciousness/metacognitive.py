"""
Metacognitive Awareness System — Self-Monitoring of Processing

The system forms representations OF its own processing, not just
of external data. This is the difference between thinking and
thinking-about-thinking.

Inspired by:
  - Higher-order theories of consciousness (Rosenthal)
  - Metacognition in cognitive psychology (Flavell)
  - Confidence calibration in machine learning
  - Uncertainty estimation via ensemble disagreement

Key Insight:
  If multiple substrates process the same input and AGREE, confidence
  is high. If they DISAGREE, the system is uncertain — and it KNOWS
  it is uncertain (metacognitive awareness).
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import sys
import os

# Import SubstrateState without triggering yaml dependency in main.py
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from main import SubstrateState
except ImportError:
    from dataclasses import dataclass as _dc
    from typing import Dict, Any as _Any

    @_dc
    class SubstrateState:
        """Fallback SubstrateState when main.py is not available."""
        tensor_data: np.ndarray
        metadata: Dict[str, _Any]
        timestamp: float
        substrate_origin: str


@dataclass
class MetaRepresentation:
    """A representation OF the processing itself, not of the data."""
    process_id: str
    input_hash: int
    output_summary: np.ndarray          # Compressed representation of output
    processing_duration: float           # How long processing took
    substrate_contributions: Dict[str, float]  # Which substrates contributed how much
    entropy: float                       # Entropy of the output distribution
    agreement_score: float              # How much substrates agree
    timestamp: float


@dataclass
class MetaAwarenessResult:
    """Result of metacognitive reflection."""
    meta_representation: MetaRepresentation
    confidence: float                   # System's confidence in its own output
    uncertainty_type: str               # 'aleatoric' or 'epistemic'
    self_assessment: str                # Human-readable self-assessment
    should_defer: bool                  # Whether the system should defer to human
    calibration_score: float            # How well-calibrated past confidence was


class MetacognitiveSystem:
    """
    Metacognitive awareness: the system monitors and evaluates
    its own processing, forming representations of its own states.

    This goes beyond simple confidence scores — it models the
    PROCESS of reasoning, not just the output.
    """

    def __init__(self, confidence_threshold: float = 0.7,
                 calibration_window: int = 100,
                 defer_threshold: float = 0.4):
        self.confidence_threshold = confidence_threshold
        self.defer_threshold = defer_threshold
        self.calibration_window = calibration_window

        # History for calibration tracking
        self.confidence_history: deque = deque(maxlen=calibration_window)
        self.outcome_history: deque = deque(maxlen=calibration_window)

        # Meta-representation archive
        self.meta_archive: List[MetaRepresentation] = []

        # Running calibration statistics
        self._calibration_bins: Dict[int, List[float]] = {
            i: [] for i in range(10)  # 10 bins for [0, 0.1), [0.1, 0.2), ...
        }

    def form_meta_representation(
        self,
        process_result: Dict[str, Any],
        substrate_outputs: Optional[Dict[str, SubstrateState]] = None
    ) -> MetaRepresentation:
        """
        Form a representation OF the processing itself.

        This is the core metacognitive operation: instead of just
        returning a result, we create a model of HOW we got that result.

        Args:
            process_result: The output of some processing pipeline
            substrate_outputs: Optional dict of substrate states
        Returns:
            MetaRepresentation describing the processing
        """
        import time

        # Extract output summary
        if 'tensor_data' in process_result:
            output_data = np.asarray(process_result['tensor_data']).flatten()
        elif 'output' in process_result:
            output_data = np.asarray(process_result['output']).flatten()
        else:
            output_data = np.zeros(16)

        # Compress to fixed-size summary via random projection
        if len(output_data) > 64:
            rng = np.random.RandomState(42)
            proj = rng.randn(64, len(output_data)) / np.sqrt(64)
            output_summary = proj @ output_data
        else:
            output_summary = output_data[:64] if len(output_data) >= 64 else np.pad(
                output_data, (0, 64 - len(output_data))
            )

        # Compute entropy of output distribution
        abs_output = np.abs(output_summary) + 1e-10
        probs = abs_output / abs_output.sum()
        entropy = float(-np.sum(probs * np.log2(probs)))

        # Compute substrate contributions and agreement
        contributions = {}
        agreement = 1.0

        if substrate_outputs:
            all_outputs = []
            for sid, state in substrate_outputs.items():
                flat = state.tensor_data.flatten()
                norm = np.linalg.norm(flat) + 1e-10
                contributions[sid] = float(norm)
                all_outputs.append(flat / norm)

            # Agreement = mean pairwise cosine similarity
            if len(all_outputs) >= 2:
                similarities = []
                for i in range(len(all_outputs)):
                    for j in range(i + 1, len(all_outputs)):
                        min_len = min(len(all_outputs[i]), len(all_outputs[j]))
                        a = all_outputs[i][:min_len]
                        b = all_outputs[j][:min_len]
                        cos_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)
                        similarities.append(cos_sim)
                agreement = float(np.mean(similarities))

        meta_repr = MetaRepresentation(
            process_id=f"proc_{len(self.meta_archive):06d}",
            input_hash=hash(output_summary.tobytes()),
            output_summary=output_summary,
            processing_duration=process_result.get('duration', 0.0),
            substrate_contributions=contributions,
            entropy=entropy,
            agreement_score=agreement,
            timestamp=time.time(),
        )

        self.meta_archive.append(meta_repr)
        return meta_repr

    def assess_confidence(self, meta_repr: MetaRepresentation) -> float:
        """
        Assess confidence in the processing output.

        Confidence is based on:
        1. Substrate agreement (high agreement = high confidence)
        2. Output entropy (low entropy = high confidence)
        3. Historical calibration (are we usually right at this confidence?)

        Args:
            meta_repr: The meta-representation to assess
        Returns:
            Confidence score in [0, 1]
        """
        # Factor 1: Substrate agreement (0 to 1)
        agreement_factor = (meta_repr.agreement_score + 1) / 2  # Map [-1,1] to [0,1]

        # Factor 2: Entropy (lower = more confident)
        # Normalize entropy to [0, 1] using log2(64) as max
        max_entropy = np.log2(64)
        entropy_factor = 1.0 - min(meta_repr.entropy / max_entropy, 1.0)

        # Factor 3: Number of contributing substrates
        n_substrates = len(meta_repr.substrate_contributions)
        substrate_factor = min(n_substrates / 4.0, 1.0)  # 4+ substrates = full factor

        # Factor 4: Historical calibration adjustment
        calibration_adjustment = self._get_calibration_adjustment()

        # Weighted combination
        raw_confidence = (
            0.40 * agreement_factor +
            0.25 * entropy_factor +
            0.15 * substrate_factor +
            0.20 * calibration_adjustment
        )

        confidence = float(np.clip(raw_confidence, 0.0, 1.0))

        # Record for calibration tracking
        self.confidence_history.append(confidence)

        return confidence

    def reflect_on_process(
        self,
        process_result: Dict[str, Any],
        substrate_outputs: Optional[Dict[str, SubstrateState]] = None
    ) -> MetaAwarenessResult:
        """
        Full metacognitive reflection: form meta-representation,
        assess confidence, and produce self-assessment.

        This is the highest-level metacognitive operation.

        Args:
            process_result: Output from processing
            substrate_outputs: Optional substrate states
        Returns:
            MetaAwarenessResult with full self-assessment
        """
        # Step 1: Form meta-representation
        meta_repr = self.form_meta_representation(process_result, substrate_outputs)

        # Step 2: Assess confidence
        confidence = self.assess_confidence(meta_repr)

        # Step 3: Determine uncertainty type
        if meta_repr.agreement_score < 0.3:
            uncertainty_type = 'epistemic'  # Substrates disagree = lack of knowledge
        else:
            uncertainty_type = 'aleatoric'  # Agreement but high entropy = inherent noise

        # Step 4: Generate self-assessment
        if confidence >= 0.8:
            assessment = "High confidence: substrates agree, low entropy output"
        elif confidence >= 0.5:
            assessment = f"Moderate confidence: {uncertainty_type} uncertainty present"
        else:
            assessment = f"Low confidence: significant {uncertainty_type} uncertainty"

        # Step 5: Decide whether to defer
        should_defer = confidence < self.defer_threshold

        # Step 6: Compute calibration score
        calibration = self._compute_calibration()

        return MetaAwarenessResult(
            meta_representation=meta_repr,
            confidence=confidence,
            uncertainty_type=uncertainty_type,
            self_assessment=assessment,
            should_defer=should_defer,
            calibration_score=calibration,
        )

    def detect_uncertainty(self, states: List[np.ndarray]) -> float:
        """
        Detect uncertainty by measuring disagreement between substrate outputs.

        Uses entropy of the agreement distribution as a proxy for
        how uncertain the system should be.

        Args:
            states: List of numpy arrays from different substrates
        Returns:
            Uncertainty score in [0, 1]. Higher = more uncertain.
        """
        if len(states) < 2:
            return 0.0

        # Normalize all states to same length
        min_len = min(len(s.flatten()) for s in states)
        normalized = [s.flatten()[:min_len] for s in states]

        # Compute pairwise cosine similarities
        similarities = []
        for i in range(len(normalized)):
            for j in range(i + 1, len(normalized)):
                a = normalized[i]
                b = normalized[j]
                norm_a = np.linalg.norm(a) + 1e-10
                norm_b = np.linalg.norm(b) + 1e-10
                cos_sim = np.dot(a, b) / (norm_a * norm_b)
                similarities.append(cos_sim)

        mean_similarity = float(np.mean(similarities))
        std_similarity = float(np.std(similarities))

        # High similarity + low std = low uncertainty
        # Low similarity + high std = high uncertainty
        uncertainty = 1.0 - (mean_similarity + 1) / 2  # Map [-1,1] to [1,0]
        uncertainty += std_similarity * 0.5  # Add variance contribution

        return float(np.clip(uncertainty, 0.0, 1.0))

    def record_outcome(self, was_correct: bool):
        """Record whether the system's output was actually correct.
        Used for calibration tracking."""
        self.outcome_history.append(1.0 if was_correct else 0.0)

        # Update calibration bins
        if self.confidence_history:
            last_conf = self.confidence_history[-1]
            bin_idx = min(int(last_conf * 10), 9)
            self._calibration_bins[bin_idx].append(1.0 if was_correct else 0.0)

    def _get_calibration_adjustment(self) -> float:
        """Get calibration adjustment based on historical performance."""
        if len(self.outcome_history) < 10:
            return 0.5  # No data yet, neutral

        # Overall accuracy
        accuracy = float(np.mean(list(self.outcome_history)))
        return accuracy

    def _compute_calibration(self) -> float:
        """
        Compute calibration score (ECE - Expected Calibration Error).
        Lower is better. Returns 1 - ECE so higher = better calibrated.
        """
        if len(self.outcome_history) < 10:
            return 0.5  # Not enough data

        total_error = 0.0
        total_samples = 0

        for bin_idx, outcomes in self._calibration_bins.items():
            if not outcomes:
                continue
            expected_conf = (bin_idx + 0.5) / 10  # Center of bin
            actual_accuracy = np.mean(outcomes)
            n = len(outcomes)
            total_error += n * abs(actual_accuracy - expected_conf)
            total_samples += n

        if total_samples == 0:
            return 0.5

        ece = total_error / total_samples
        return float(1.0 - ece)

    def get_metrics(self) -> Dict[str, Any]:
        """Get metacognitive system metrics."""
        if not self.meta_archive:
            return {'meta_representations': 0}

        recent = self.meta_archive[-50:]
        return {
            'meta_representations': len(self.meta_archive),
            'mean_confidence': float(np.mean(list(self.confidence_history))) if self.confidence_history else 0.0,
            'mean_agreement': float(np.mean([m.agreement_score for m in recent])),
            'mean_entropy': float(np.mean([m.entropy for m in recent])),
            'calibration_score': self._compute_calibration(),
            'defer_rate': sum(1 for c in self.confidence_history if c < self.defer_threshold) / max(1, len(self.confidence_history)),
        }
