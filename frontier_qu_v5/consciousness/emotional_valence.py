"""
Emotional Valence System — Affective Processing for Quranic Analysis

Maps Quranic themes to emotional dimensions using the circumplex
model of affect (Russell, 1980):
  - Valence: positive ←→ negative (-1 to +1)
  - Arousal: calm ←→ excited (-1 to +1)

Quranic Emotional Categories:
  - Mercy (رحمة): high valence, moderate arousal
  - Justice (عدل): neutral valence, high arousal
  - Warning (إنذار): negative valence, high arousal
  - Promise (وعد): high valence, high arousal
  - Narrative (قصص): variable valence, moderate arousal

Why this matters:
  Emotional content modulates attention, memory consolidation, and
  decision-making. A system that processes the Quran without
  emotional awareness misses a fundamental dimension of meaning.

Inspired by:
  - Affective computing (Picard, 1997)
  - Somatic marker hypothesis (Damasio, 1994)
  - Emotional prosody in Tajweed recitation
"""

import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import sys
import os

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
class EmotionalState:
    """Emotional state of the processing system."""
    valence: float          # -1 (negative) to +1 (positive)
    arousal: float          # -1 (calm) to +1 (excited)
    category: str           # Primary emotional category
    secondary_category: str # Secondary emotional category
    intensity: float        # Overall intensity [0, 1]
    timestamp: float


@dataclass
class AffectModulationResult:
    """Result of emotional modulation on processing."""
    original_state: np.ndarray
    modulated_state: np.ndarray
    valence: float
    arousal: float
    modulation_strength: float
    category: str


class EmotionalValence:
    """
    Emotional valence system for Quranic verse processing.

    Computes emotional dimensions (valence, arousal) from verse
    features and uses them to modulate processing — mimicking
    how emotions shape cognition in biological systems.
    """

    # Quranic emotional categories with prototypical (valence, arousal) values
    EMOTIONAL_CATEGORIES = {
        'mercy':     (0.8, 0.3),    # رحمة — positive, calm-moderate
        'justice':   (0.0, 0.7),    # عدل — neutral, high arousal
        'warning':   (-0.7, 0.8),   # إنذار — negative, high arousal
        'promise':   (0.9, 0.7),    # وعد — very positive, excited
        'narrative': (0.2, 0.4),    # قصص — slightly positive, moderate
        'worship':   (0.6, 0.5),    # عبادة — positive, moderate arousal
        'guidance':  (0.5, 0.3),    # هداية — positive, calm
        'creation':  (0.4, 0.6),    # خلق — positive, moderate-high
        'judgment':  (-0.4, 0.9),   # حساب — negative, very high arousal
        'patience':  (0.3, -0.2),   # صبر — slightly positive, calm
    }

    def __init__(self, feature_dim: int = 128,
                 modulation_strength: float = 0.3,
                 emotional_memory_size: int = 200):
        self.feature_dim = feature_dim
        self.modulation_strength = modulation_strength

        # Learned category prototypes (random init, refined by usage)
        self._category_prototypes: Dict[str, np.ndarray] = {}
        rng = np.random.RandomState(42)
        for cat in self.EMOTIONAL_CATEGORIES:
            self._category_prototypes[cat] = rng.randn(feature_dim) * 0.1

        # Emotional memory (recent emotional states)
        self.emotional_memory: deque = deque(maxlen=emotional_memory_size)

        # Mood (running average of emotional states — slower-changing)
        self._mood_valence = 0.0
        self._mood_arousal = 0.0
        self._mood_momentum = 0.95

    @property
    def emotional_categories(self) -> Dict[str, Tuple[float, float]]:
        """Get the emotional category definitions."""
        return dict(self.EMOTIONAL_CATEGORIES)

    def compute_valence(self, verse_features: np.ndarray) -> Tuple[float, float]:
        """
        Compute emotional valence and arousal from verse features.

        Uses similarity to emotional category prototypes weighted
        by the categories' prototypical (valence, arousal) values.

        Args:
            verse_features: Feature vector for a verse/passage
        Returns:
            Tuple of (valence, arousal), each in [-1, 1]
        """
        flat = verse_features.flatten()
        if len(flat) > self.feature_dim:
            flat = flat[:self.feature_dim]
        elif len(flat) < self.feature_dim:
            flat = np.pad(flat, (0, self.feature_dim - len(flat)))

        # Compute similarity to each category prototype
        similarities = {}
        for cat, prototype in self._category_prototypes.items():
            cos_sim = np.dot(flat, prototype) / (
                np.linalg.norm(flat) * np.linalg.norm(prototype) + 1e-10
            )
            similarities[cat] = cos_sim

        # Softmax over similarities
        sim_values = np.array(list(similarities.values()))
        exp_sims = np.exp(sim_values - sim_values.max())  # Numerical stability
        softmax_sims = exp_sims / (exp_sims.sum() + 1e-10)

        # Weighted sum of category (valence, arousal) values
        valence = 0.0
        arousal = 0.0
        for idx, (cat, (v, a)) in enumerate(self.EMOTIONAL_CATEGORIES.items()):
            weight = softmax_sims[idx]
            valence += weight * v
            arousal += weight * a

        # Clip to [-1, 1]
        valence = float(np.clip(valence, -1.0, 1.0))
        arousal = float(np.clip(arousal, -1.0, 1.0))

        # Update mood (exponential moving average)
        self._mood_valence = self._mood_momentum * self._mood_valence + \
                             (1 - self._mood_momentum) * valence
        self._mood_arousal = self._mood_momentum * self._mood_arousal + \
                             (1 - self._mood_momentum) * arousal

        # Determine primary and secondary categories
        sorted_cats = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_cats[0][0]
        secondary = sorted_cats[1][0] if len(sorted_cats) > 1 else primary

        # Compute intensity
        intensity = float(np.sqrt(valence ** 2 + arousal ** 2) / np.sqrt(2))

        # Record emotional state
        state = EmotionalState(
            valence=valence,
            arousal=arousal,
            category=primary,
            secondary_category=secondary,
            intensity=intensity,
            timestamp=time.time(),
        )
        self.emotional_memory.append(state)

        return (valence, arousal)

    def affect_processing(self, state: np.ndarray, valence: float,
                          arousal: Optional[float] = None) -> np.ndarray:
        """
        Modulate processing state based on emotional content.

        Positive valence → amplify constructive patterns
        Negative valence → amplify warning/attention patterns
        High arousal → sharpen contrasts (increase variance)
        Low arousal → smooth (decrease variance)

        This mimics how emotions shape neural processing in the brain:
        fear sharpens attention, joy broadens it.

        Args:
            state: Current processing state
            valence: Emotional valence [-1, 1]
            arousal: Optional arousal [-1, 1], defaults to abs(valence)
        Returns:
            Emotionally modulated state
        """
        if arousal is None:
            arousal = abs(valence)

        modulated = state.copy()
        strength = self.modulation_strength

        # Valence modulation: shift the mean
        # Positive valence → boost positive components
        # Negative valence → boost negative components
        mean_val = np.mean(modulated)
        modulated = modulated + strength * valence * np.abs(mean_val + 1e-10)

        # Arousal modulation: adjust variance
        # High arousal → increase contrast (amplify deviations from mean)
        # Low arousal → decrease contrast (smooth toward mean)
        current_mean = np.mean(modulated)
        deviation = modulated - current_mean
        arousal_factor = 1.0 + strength * arousal
        modulated = current_mean + deviation * arousal_factor

        return modulated

    def get_mood(self) -> Tuple[float, float]:
        """Get current mood (slow-changing emotional baseline)."""
        return (self._mood_valence, self._mood_arousal)

    def get_emotional_trajectory(self, window: int = 20) -> Dict[str, List[float]]:
        """Get recent emotional trajectory."""
        recent = list(self.emotional_memory)[-window:]
        if not recent:
            return {'valence': [], 'arousal': [], 'intensity': []}

        return {
            'valence': [s.valence for s in recent],
            'arousal': [s.arousal for s in recent],
            'intensity': [s.intensity for s in recent],
            'categories': [s.category for s in recent],
        }

    def detect_emotional_shift(self, window: int = 10,
                                threshold: float = 0.3) -> Optional[str]:
        """
        Detect significant emotional shifts in recent processing.

        Returns description of shift if detected, None otherwise.
        """
        if len(self.emotional_memory) < window * 2:
            return None

        recent = list(self.emotional_memory)
        earlier = recent[-window * 2:-window]
        later = recent[-window:]

        earlier_v = np.mean([s.valence for s in earlier])
        later_v = np.mean([s.valence for s in later])
        earlier_a = np.mean([s.arousal for s in earlier])
        later_a = np.mean([s.arousal for s in later])

        v_shift = later_v - earlier_v
        a_shift = later_a - earlier_a

        if abs(v_shift) > threshold or abs(a_shift) > threshold:
            direction_v = "more positive" if v_shift > 0 else "more negative"
            direction_a = "higher arousal" if a_shift > 0 else "lower arousal"
            return f"Emotional shift detected: {direction_v} (dv={v_shift:.2f}), {direction_a} (da={a_shift:.2f})"

        return None

    def get_metrics(self) -> Dict[str, Any]:
        """Get emotional system metrics."""
        if not self.emotional_memory:
            return {'emotional_states_recorded': 0}

        recent = list(self.emotional_memory)[-50:]
        return {
            'emotional_states_recorded': len(self.emotional_memory),
            'current_mood_valence': self._mood_valence,
            'current_mood_arousal': self._mood_arousal,
            'mean_valence': float(np.mean([s.valence for s in recent])),
            'mean_arousal': float(np.mean([s.arousal for s in recent])),
            'mean_intensity': float(np.mean([s.intensity for s in recent])),
            'dominant_category': max(
                set(s.category for s in recent),
                key=lambda c: sum(1 for s in recent if s.category == c)
            ),
            'emotional_shift': self.detect_emotional_shift(),
        }
