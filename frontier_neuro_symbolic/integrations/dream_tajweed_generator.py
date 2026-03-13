"""Dream Tajweed Generator — Novel Pattern Discovery via Noise Perturbation.

Generates novel tajweed pronunciation patterns by "dreaming" — perturbing
the initial conditions of the Gray-Scott / Turing PDE vocal tract model
with amplified noise and scoring the resulting patterns for novelty.

Inspired by dream/sleep-phase creativity in biological neural systems:
  1. Amplify noise in the morphogenetic field PDE (high noise_level).
  2. Evolve the field to produce novel Turing patterns.
  3. Score novelty by comparing against a library of known patterns.
  4. Filter: only patterns that are both novel AND phonetically valid
     (verified by TajweedPhonetics) are kept.

Cross-subsystem integration:
  frontier_neuro_symbolic/embodied_tajweed/vocal_tract.py
    (MorphogeneticField, VocalTractManifold)
  frontier_neuro_symbolic/embodied_tajweed/articulatory_features.py
    (TajweedPhonetics)
"""

import sys
import os
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import hashlib

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _project_root)

from frontier_neuro_symbolic.embodied_tajweed.vocal_tract import (
    MorphogeneticField,
    VocalTractManifold,
)
from frontier_neuro_symbolic.embodied_tajweed.articulatory_features import (
    TajweedPhonetics,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class DreamPattern:
    """A novel tajweed pattern discovered through dream generation."""
    pattern_id: str                          # Hash-based unique ID
    field: np.ndarray                        # Final activation field (grid_size,)
    trajectory: List[np.ndarray]             # Evolution trajectory
    tajweed_rule: str                        # Base rule used for PDE params
    novelty_score: float                     # How different from known patterns [0, 1]
    energy: float                            # Lyapunov energy of final pattern
    order_parameter: float                   # Pattern formation strength
    phonetic_validity: float                 # TajweedPhonetics verification score
    noise_amplitude: float                   # Noise level used in generation
    makharij_activations: Dict[str, float]   # Per-makharij activation strengths
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DreamSession:
    """Results of a full dream generation session."""
    total_dreams: int
    novel_patterns: List[DreamPattern]       # Patterns passing novelty threshold
    rejected_count: int                      # Patterns below novelty threshold
    phonetically_invalid_count: int          # Patterns failing phonetic check
    mean_novelty: float
    max_novelty: float
    dream_diversity: float                   # Inter-pattern variance


# ---------------------------------------------------------------------------
# Main integration class
# ---------------------------------------------------------------------------

class TajweedDreamGenerator:
    """Generate novel tajweed patterns via noise-amplified PDE evolution.

    Architecture:
        1. Start with a base tajweed rule (idgham, ikhfaa, iqlab, izhar).
        2. Create a MorphogeneticField with amplified noise (dream mode).
        3. Perturb initial conditions with structured noise:
           - Gaussian bumps at random makharij positions
           - Sinusoidal perturbations at random frequencies
           - White noise floor
        4. Evolve the PDE to produce a novel Turing pattern.
        5. Score novelty against a library of known patterns.
        6. Verify phonetic validity using TajweedPhonetics.
        7. Store novel, valid patterns.

    Parameters:
        grid_size: Spatial resolution of the vocal tract field.
        base_noise_level: Noise level for the PDE solver (amplified in dream mode).
        dream_amplification: How much to amplify noise in dream mode.
        novelty_threshold: Minimum novelty score to accept a pattern.
        phonetic_threshold: Minimum phonetic validity to accept.
    """

    def __init__(
        self,
        grid_size: int = 64,
        base_noise_level: float = 0.01,
        dream_amplification: float = 5.0,
        novelty_threshold: float = 0.3,
        phonetic_threshold: float = 0.3,
    ):
        self.grid_size = grid_size
        self.base_noise_level = base_noise_level
        self.dream_amplification = dream_amplification
        self.novelty_threshold = novelty_threshold
        self.phonetic_threshold = phonetic_threshold

        # Phonetic validator
        self.phonetics = TajweedPhonetics()

        # Vocal tract manifold (shared geometry)
        self.manifold = VocalTractManifold(grid_size)

        # Library of known patterns (for novelty comparison)
        self._known_patterns: List[np.ndarray] = []

        # All accepted dream patterns
        self.dream_library: List[DreamPattern] = []

        # Pre-generate baseline patterns for each rule
        self._baselines: Dict[str, np.ndarray] = {}
        self._generate_baselines()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dream(
        self,
        base_rule: str = "idgham",
        num_dreams: int = 10,
        evolution_steps: int = 200,
        seed: Optional[int] = None,
    ) -> DreamSession:
        """Run a dream session, generating novel tajweed patterns.

        Args:
            base_rule: Base tajweed rule for PDE parameters.
            num_dreams: Number of dream patterns to generate.
            evolution_steps: PDE evolution steps per dream.
            seed: Random seed for reproducibility.

        Returns:
            DreamSession with novel patterns and statistics.
        """
        if seed is not None:
            np.random.seed(seed)

        novel_patterns: List[DreamPattern] = []
        rejected = 0
        phonetically_invalid = 0
        all_novelties: List[float] = []

        for i in range(num_dreams):
            # Generate perturbed initial conditions
            u_init = self._create_dream_initial_conditions()

            # Create PDE solver with amplified noise
            dream_noise = self.base_noise_level * self.dream_amplification
            field_solver = MorphogeneticField(
                grid_size=self.grid_size,
                diffusion_coeff=0.01,
                reaction_strength=1.0,
                time_step=0.001,
                noise_level=dream_noise,
                tajweed_rule=base_rule,
            )

            # Evolve the field
            result = field_solver.evolve_to_pattern(
                u_init,
                num_steps=evolution_steps,
                record_every=max(1, evolution_steps // 10),
            )

            final_field = result["field"]
            trajectory = result["trajectory"]

            # Score novelty
            novelty = self._compute_novelty(final_field)
            all_novelties.append(novelty)

            # Compute energy and order parameter
            energy = field_solver.compute_pattern_energy(final_field)
            order_param = field_solver.compute_order_parameter(final_field)

            # Verify phonetic validity
            phonetic_score = self._check_phonetic_validity(final_field, base_rule)

            if novelty < self.novelty_threshold:
                rejected += 1
                continue

            if phonetic_score < self.phonetic_threshold:
                phonetically_invalid += 1
                continue

            # Compute makharij activations
            makharij_activations = self._extract_makharij_activations(final_field)

            # Generate pattern ID
            pattern_hash = hashlib.sha256(final_field.tobytes()).hexdigest()[:12]
            pattern_id = f"dream_{base_rule}_{pattern_hash}"

            pattern = DreamPattern(
                pattern_id=pattern_id,
                field=final_field,
                trajectory=trajectory,
                tajweed_rule=base_rule,
                novelty_score=novelty,
                energy=energy,
                order_parameter=order_param,
                phonetic_validity=phonetic_score,
                noise_amplitude=dream_noise,
                makharij_activations=makharij_activations,
                metadata={
                    "evolution_steps": evolution_steps,
                    "dream_index": i,
                },
            )

            novel_patterns.append(pattern)
            self.dream_library.append(pattern)
            self._known_patterns.append(final_field)

        # Compute session statistics
        mean_novelty = float(np.mean(all_novelties)) if all_novelties else 0.0
        max_novelty = float(np.max(all_novelties)) if all_novelties else 0.0

        # Dream diversity: mean pairwise distance between novel patterns
        diversity = self._compute_diversity(novel_patterns)

        return DreamSession(
            total_dreams=num_dreams,
            novel_patterns=novel_patterns,
            rejected_count=rejected,
            phonetically_invalid_count=phonetically_invalid,
            mean_novelty=mean_novelty,
            max_novelty=max_novelty,
            dream_diversity=diversity,
        )

    def dream_all_rules(
        self,
        num_dreams_per_rule: int = 5,
        evolution_steps: int = 200,
    ) -> Dict[str, DreamSession]:
        """Dream across all four tajweed rules.

        Args:
            num_dreams_per_rule: Dreams per rule.
            evolution_steps: PDE steps per dream.

        Returns:
            Dict mapping rule name to DreamSession.
        """
        results = {}
        for rule in ["idgham", "ikhfaa", "iqlab", "izhar"]:
            results[rule] = self.dream(
                base_rule=rule,
                num_dreams=num_dreams_per_rule,
                evolution_steps=evolution_steps,
            )
        return results

    def interpolate_patterns(
        self,
        pattern_a: DreamPattern,
        pattern_b: DreamPattern,
        num_steps: int = 5,
    ) -> List[np.ndarray]:
        """Linearly interpolate between two dream patterns.

        Useful for exploring the "dream space" between two novel patterns.

        Args:
            pattern_a: First pattern.
            pattern_b: Second pattern.
            num_steps: Number of interpolation steps.

        Returns:
            List of interpolated fields.
        """
        alphas = np.linspace(0, 1, num_steps)
        interpolated = []
        for alpha in alphas:
            field = (1 - alpha) * pattern_a.field + alpha * pattern_b.field
            interpolated.append(field)
        return interpolated

    def get_top_dreams(
        self,
        n: int = 5,
        sort_by: str = "novelty_score",
    ) -> List[DreamPattern]:
        """Get top-N dream patterns by a metric.

        Args:
            n: Number of patterns to return.
            sort_by: Metric to sort by (novelty_score, energy, phonetic_validity).

        Returns:
            Sorted list of top patterns.
        """
        return sorted(
            self.dream_library,
            key=lambda p: getattr(p, sort_by, 0),
            reverse=True,
        )[:n]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_baselines(self):
        """Generate baseline patterns for each tajweed rule (no dream noise)."""
        for rule in ["idgham", "ikhfaa", "iqlab", "izhar"]:
            solver = MorphogeneticField(
                grid_size=self.grid_size,
                noise_level=self.base_noise_level,
                tajweed_rule=rule,
            )
            u_init = np.random.randn(self.grid_size) * 0.01
            result = solver.evolve_to_pattern(u_init, num_steps=200)
            self._baselines[rule] = result["field"]
            self._known_patterns.append(result["field"])

    def _create_dream_initial_conditions(self) -> np.ndarray:
        """Create perturbed initial conditions for dreaming.

        Combines three noise sources:
            1. Gaussian bumps at random makharij positions.
            2. Sinusoidal perturbation at random frequency.
            3. White noise floor.
        """
        u = np.zeros(self.grid_size)

        # 1. Random makharij bumps (select 2-5 random makharij points)
        num_bumps = np.random.randint(2, 6)
        bump_positions = np.random.choice(
            self.manifold.makharij,
            size=min(num_bumps, len(self.manifold.makharij)),
            replace=False,
        )
        for pos in bump_positions:
            amplitude = np.random.uniform(0.1, 0.5)
            sigma = np.random.uniform(0.02, 0.08)
            u += amplitude * np.exp(-((self.manifold.x - pos) ** 2) / (2 * sigma ** 2))

        # 2. Sinusoidal perturbation
        freq = np.random.uniform(2, 10)
        phase = np.random.uniform(0, 2 * np.pi)
        amplitude = np.random.uniform(0.05, 0.2)
        u += amplitude * np.sin(2 * np.pi * freq * self.manifold.x + phase)

        # 3. White noise floor
        u += np.random.randn(self.grid_size) * 0.05

        # Clip to valid range
        u = np.clip(u, -1.0, 1.0)

        return u

    def _compute_novelty(self, field: np.ndarray) -> float:
        """Compute novelty score by comparing against known patterns.

        Novelty = 1 - max_similarity to any known pattern.
        Similarity is measured by normalized correlation.

        Args:
            field: Candidate pattern.

        Returns:
            Novelty score in [0, 1].
        """
        if not self._known_patterns:
            return 1.0

        max_sim = 0.0
        field_norm = np.linalg.norm(field)
        if field_norm < 1e-8:
            return 0.0

        for known in self._known_patterns:
            known_norm = np.linalg.norm(known)
            if known_norm < 1e-8:
                continue
            correlation = np.abs(np.dot(field, known) / (field_norm * known_norm))
            max_sim = max(max_sim, correlation)

        return float(1.0 - max_sim)

    def _check_phonetic_validity(self, field: np.ndarray, rule: str) -> float:
        """Check whether a pattern is phonetically valid for the given rule.

        Maps the activation field to acoustic features at the dominant makharij
        position and verifies the tajweed rule template.

        Args:
            field: Activation pattern.
            rule: Tajweed rule name.

        Returns:
            Validity score in [0, 1].
        """
        # Find dominant activation region
        abs_field = np.abs(field)
        peak_idx = np.argmax(abs_field)
        peak_pos = self.manifold.x[peak_idx]

        # Map peak position to approximate acoustic features
        # Position along vocal tract correlates with formant frequencies
        pitch = 100 + 200 * peak_pos   # Higher position -> higher pitch
        f1 = 200 + 600 * (1 - peak_pos)  # Lower position -> higher F1
        duration = 0.05 + 0.3 * abs_field[peak_idx]  # Stronger activation -> longer

        features = {
            "pitch": float(pitch),
            "formants": (float(f1), 1500.0, 2500.0),
            "duration": float(duration),
        }

        # Classify makharij from features
        makharij_probs = self.phonetics.classify_makharij(features)
        max_makharij_prob = float(np.max(makharij_probs))

        # Verify rule
        is_valid, rule_conf = self.phonetics.verify_rule(
            features, rule, phonemes=["م", "م"]  # Placeholder phonemes
        )

        # Combined validity: strong makharij classification + rule verification
        validity = 0.5 * max_makharij_prob + 0.5 * rule_conf

        return float(np.clip(validity, 0, 1))

    def _extract_makharij_activations(self, field: np.ndarray) -> Dict[str, float]:
        """Extract activation strength at each makharij position.

        Args:
            field: Activation pattern.

        Returns:
            Dict mapping makharij name to activation strength.
        """
        activations = {}
        for i, pos in enumerate(self.manifold.makharij):
            # Find nearest grid point
            idx = np.argmin(np.abs(self.manifold.x - pos))
            name = self.phonetics.makharij_names[i] if i < len(self.phonetics.makharij_names) else f"makharij_{i}"
            activations[name] = float(np.abs(field[idx]))
        return activations

    def _compute_diversity(self, patterns: List[DreamPattern]) -> float:
        """Compute diversity among a set of patterns.

        Diversity = mean pairwise L2 distance between normalized patterns.
        """
        if len(patterns) < 2:
            return 0.0

        distances = []
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                fi = patterns[i].field / (np.linalg.norm(patterns[i].field) + 1e-8)
                fj = patterns[j].field / (np.linalg.norm(patterns[j].field) + 1e-8)
                distances.append(float(np.linalg.norm(fi - fj)))

        return float(np.mean(distances))

    def get_metrics(self) -> Dict[str, Any]:
        """Return dream generator metrics."""
        novelties = [p.novelty_score for p in self.dream_library]
        energies = [p.energy for p in self.dream_library]
        validities = [p.phonetic_validity for p in self.dream_library]

        return {
            "total_dreams_accepted": len(self.dream_library),
            "known_patterns": len(self._known_patterns),
            "mean_novelty": float(np.mean(novelties)) if novelties else 0.0,
            "mean_energy": float(np.mean(energies)) if energies else 0.0,
            "mean_phonetic_validity": float(np.mean(validities)) if validities else 0.0,
            "rules_covered": list(set(p.tajweed_rule for p in self.dream_library)),
            "dream_amplification": self.dream_amplification,
        }
