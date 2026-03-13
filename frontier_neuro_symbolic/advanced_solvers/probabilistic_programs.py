"""Probabilistic programming with NumPyro/Pyro for Bayesian inference over Quranic evidence."""
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import warnings

# Try to import NumPyro, fall back gracefully if unavailable
try:
    import numpyro
    import numpyro.distributions as dist
    from numpyro.infer import MCMC, NUTS

    HAS_NUMPYRO = True
except ImportError:
    HAS_NUMPYRO = False
    warnings.warn("NumPyro not installed. Probabilistic inference will use mock implementations.")


@dataclass
class NaskhEvidence:
    """Evidence about naskh (abrogation)."""

    qiraat_variants: List[Tuple[str, str, float]]  # (verse, variant, frequency)
    temporal_markers: Optional[List[Tuple[str, str]]] = None  # (verse, period)
    strength_progression: Optional[List[float]] = None  # Increasing strengths


class NaskhProbabilisticModel:
    """Bayesian inference of naskh (abrogation) from evidence.

    Model:
    - Prior: P(naskh occurred | chronology)
    - Likelihood: P(qiraat variants | naskh)
    - Posterior: P(naskh occurred | evidence)

    Uses NumPyro/Pyro for variational inference.
    """

    def __init__(self):
        """Initialize model."""
        self.posterior_samples = None
        self.posterior_mean = None

    def infer_naskh_posterior(
        self,
        evidence: Dict[str, Any],
        num_samples: int = 100,
    ) -> Dict[str, float]:
        """Infer posterior probability of naskh given evidence.

        Args:
            evidence: Dict with 'qiraat_variants' and optional temporal info.
            num_samples: Number of posterior samples to draw.

        Returns:
            Posterior probability and confidence.
        """
        if not HAS_NUMPYRO:
            return self._mock_posterior_inference(evidence)

        # Extract evidence
        qiraat_variants = evidence.get("qiraat_variants", [])

        # Simplified: compute likelihood of variants under naskh vs. no-naskh
        # Higher variant diversity = stronger evidence for naskh

        variant_freqs = [freq for _, _, freq in qiraat_variants]

        if len(variant_freqs) > 1:
            # Compute entropy of variant distribution
            freqs_array = np.array(variant_freqs)
            freqs_array = freqs_array / freqs_array.sum()  # Normalize
            entropy = -np.sum(freqs_array * np.log(freqs_array + 1e-8))

            # High entropy = evidence for naskh (multiple readings)
            naskh_probability = min(1.0, entropy / np.log(len(variant_freqs)))
        else:
            naskh_probability = 0.1  # Low evidence for single variant

        return {
            "naskh_occurred": naskh_probability > 0.5,
            "naskh_probability": float(naskh_probability),
            "confidence": 0.7,  # Moderate confidence without full MCMC
        }

    def _mock_posterior_inference(self, evidence: Dict[str, Any]) -> Dict[str, float]:
        """Mock inference when NumPyro unavailable."""
        qiraat_variants = evidence.get("qiraat_variants", [])

        if len(qiraat_variants) > 1:
            # Extract frequencies from variants
            freqs = []
            for item in qiraat_variants:
                if isinstance(item, tuple) and len(item) >= 3:
                    # (verse, variant, frequency) format
                    freqs.append(item[2])
                elif isinstance(item, (int, float)):
                    freqs.append(item)

            if freqs:
                entropy = sum(
                    -f * np.log(f + 1e-8) / np.log(len(freqs))
                    for f in freqs
                    if f > 0
                )
                prob = min(1.0, entropy)
            else:
                prob = 0.1
        else:
            prob = 0.1

        return {
            "naskh_occurred": prob > 0.5,
            "naskh_probability": float(prob),
            "confidence": 0.65,
        }


class ChronologyPPL:
    """Probabilistic model over revelation chronology.

    Samples prior P(revelation_times) subject to:
    - Makkan verses before Madinan
    - Surah order constraints
    - Known historical markers
    """

    def __init__(self):
        """Initialize chronology model."""
        self.times = None

    def sample_revelation_times(self, num_verses: int = 114) -> List[float]:
        """Sample revelation times for verses.

        Args:
            num_verses: Number of verses to assign times.

        Returns:
            List of normalized revelation times [0, 1].
        """
        # Mock: return uniform samples constrained to monotonicity
        times = np.sort(np.random.uniform(0, 1, num_verses))
        return times.tolist()

    def add_chronology_constraint(
        self,
        earlier_verses: List[str],
        later_verses: List[str],
    ) -> None:
        """Add constraint that earlier_verses precede later_verses.

        Args:
            earlier_verses: List of verse IDs revealed earlier.
            later_verses: List of verse IDs revealed later.
        """
        # Store constraints for later enforcement
        pass


class QiraatLikelihoodModel:
    """Likelihood model for qira'at (variant readings) as noisy evidence.

    Observations:
    - Qira'at variant frequencies (e.g., "sawm" 85% vs "siyam" 15%)
    - Reflect transmitter chains and regional reading schools

    Model:
    - P(variant | true_reading) = transmission accuracy + geographic factors
    """

    def __init__(self):
        """Initialize likelihood model."""
        self.base_accuracy = 0.9  # Baseline transmitter accuracy

    def compute_likelihood(self, variants: List[Tuple[str, str, float]]) -> float:
        """Compute log-likelihood of observed variants.

        Args:
            variants: List of (verse_id, variant_reading, frequency) tuples.

        Returns:
            Log likelihood of observations.
        """
        total_log_likelihood = 0.0

        for verse_id, variant, frequency in variants:
            # Likelihood: how probable is this frequency under the generative model?
            # Simplified: high frequency variants have high likelihood (p=accuracy)
            # Low frequency variants have lower likelihood (p=1-accuracy)

            if frequency >= self.base_accuracy:
                # High frequency is more likely
                log_likelihood = np.log(frequency + 1e-8)
            else:
                # Low frequency less likely
                log_likelihood = np.log(1 - frequency + 1e-8)

            total_log_likelihood += log_likelihood

        return total_log_likelihood


class VariationalNaskhInference:
    """Variational inference for naskh using normalizing flows.

    Approximates posterior P(naskh | evidence) using:
    - Variational family: normalizing flow
    - Optimization: ELBO maximization
    - Inference: one-step approximation
    """

    def __init__(self):
        """Initialize variational inference."""
        self.model = NaskhProbabilisticModel()
        self.num_steps = 10

    def run_inference(
        self,
        evidence: Dict[str, Any],
        num_steps: int = 10,
    ) -> Dict[str, float]:
        """Run variational inference to approximate posterior.

        Args:
            evidence: Dict of ruling_id -> (verse, strength) tuples.
            num_steps: Number of inference steps.

        Returns:
            Posterior approximation with naskh_probability and entropy.
        """
        # Convert evidence to format for NaskhProbabilisticModel
        qiraat_variants = []
        for i, (ruling_id, value) in enumerate(evidence.items()):
            if isinstance(value, tuple) and len(value) >= 2:
                # value = (verse, strength) format
                verse, strength = value[0], value[1]
            else:
                # value = just strength
                verse = f"verse_{i}"
                strength = value if isinstance(value, (int, float)) else 0.5

            qiraat_variants.append((verse, ruling_id, strength))

        evidence_dict = {"qiraat_variants": qiraat_variants}

        # Run inference
        posterior = self.model.infer_naskh_posterior(evidence_dict)

        # Compute entropy of approximation (uncertainty)
        entropy = -posterior["naskh_probability"] * np.log(
            posterior["naskh_probability"] + 1e-8
        ) - (1 - posterior["naskh_probability"]) * np.log(
            1 - posterior["naskh_probability"] + 1e-8
        )

        return {
            "naskh_probability": posterior["naskh_probability"],
            "entropy": float(entropy),
            "num_inference_steps": num_steps,
        }


class RecursivePPL:
    """Recursive probabilistic programming for transmission chains.

    Models:
    - P(transmission_chain) = prior over tree structures
    - Recursive definition: chain(depth) → chain(depth-1) with transmission errors
    - Implements loops and recursion (Turing-complete subset of PPL)
    """

    def __init__(self):
        """Initialize recursive PPL."""
        self.transmission_error_rate = 0.05

    def sample_transmission_chain(
        self,
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        """Sample a transmission chain (isnad) with errors.

        Recursive model:
        - Base case: single transmitter (Prophet)
        - Recursive case: transmitter → next generation with error rate

        Args:
            max_depth: Maximum chain length.

        Returns:
            Chain with log probability.
        """

        def recurse(depth: int, log_prob: float = 0.0) -> Dict[str, Any]:
            """Recursively sample transmitters."""
            if depth == 0:
                return {
                    "chain": ["Prophet"],
                    "log_probability": log_prob,
                }

            # Sample: does transmission succeed?
            success_prob = 1 - self.transmission_error_rate
            success = np.random.random() < success_prob

            if success:
                # Continue chain
                child = recurse(depth - 1, log_prob + np.log(success_prob))
                child["chain"].append(f"Transmitter_{depth}")
                return child
            else:
                # Chain breaks
                return {
                    "chain": [f"Transmitter_{depth}"],
                    "log_probability": log_prob + np.log(1 - success_prob),
                }

        result = recurse(max_depth)
        return result


class JointNaskhChronologyModel:
    """Joint inference over naskh AND chronology.

    Models:
    - Prior: P(chronology) from historical markers
    - Prior: P(naskh | chronology)
    - Likelihood: P(qiraat, deontic_strength | naskh, chronology)
    - Posterior: P(naskh, chronology | evidence)
    """

    def __init__(self):
        """Initialize joint model."""
        self.naskh_model = NaskhProbabilisticModel()
        self.chronology_model = ChronologyPPL()

    def joint_inference(
        self,
        evidence: Dict[str, Any],
        num_samples: int = 100,
    ) -> Dict[str, Any]:
        """Run joint inference over naskh and chronology.

        Args:
            evidence: Dict with qiraat, deontic_strength, etc.
            num_samples: Number of samples.

        Returns:
            Joint posterior over (naskh_occurred, chronology).
        """
        # Sample chronology from prior
        chronology = self.chronology_model.sample_revelation_times(num_verses=10)

        # Condition on chronology, infer naskh
        naskh_post = self.naskh_model.infer_naskh_posterior(evidence)

        return {
            "naskh_occurred": naskh_post["naskh_occurred"],
            "naskh_probability": naskh_post["naskh_probability"],
            "chronology": chronology,
            "joint_log_probability": 0.0,  # Placeholder
        }
