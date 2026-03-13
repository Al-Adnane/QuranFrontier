"""
TextProfiler — Quranic Text Analysis & Profiling Engine
========================================================
Analyzes Quranic text across multiple dimensions:

- Emotional analysis: sentiment valence/arousal using 10 Quranic categories
- Confidence estimation: how certain the analysis is
- Attention routing: salience-based competition for thematic focus
- Complexity scoring: information-theoretic text complexity

Replaces the former ConsciousnessMetrics module with rigorous,
scientifically grounded text analysis terminology.
"""

from __future__ import annotations

import sys
import os
import time
from dataclasses import dataclass, field
from typing import Union, List, Optional, Dict, Tuple

import numpy as np

# ── Path setup ───────────────────────────────────────────────────────────────
_HERE = os.path.abspath(os.path.dirname(__file__))
_NOMOS = os.path.abspath(os.path.join(_HERE, "..", ".."))
_CONSCIOUSNESS_PKG = os.path.join(_NOMOS, "consciousness")

for _p in [_NOMOS, _CONSCIOUSNESS_PKG]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from consciousness.global_workspace import GlobalWorkspace  # noqa: E402
from consciousness.emotional_valence import EmotionalValence  # noqa: E402
from consciousness.metacognitive import MetacognitiveSystem  # noqa: E402


# ── Quranic emotional categories (from EmotionalValence) ────────────────────

QURANIC_CATEGORIES: List[str] = [
    "mercy",      # رحمة
    "justice",    # عدل
    "warning",    # إنذار
    "promise",    # وعد
    "narrative",  # قصص
    "worship",    # عبادة
    "guidance",   # هداية
    "creation",   # خلق
    "judgment",   # حساب
    "patience",   # صبر
]

# ── Theme keywords for detection ────────────────────────────────────────────

_THEME_KEYWORDS: Dict[str, List[str]] = {
    "mercy": ["mercy", "رحمة", "compassion", "forgiveness", "grace", "kind"],
    "justice": ["justice", "عدل", "fair", "right", "equity", "judge"],
    "warning": ["warning", "إنذار", "punishment", "wrath", "hellfire", "doom", "warn"],
    "promise": ["promise", "وعد", "paradise", "reward", "garden", "heaven", "bless"],
    "narrative": ["story", "قصص", "prophet", "people", "nation", "said", "told"],
    "worship": ["worship", "عبادة", "pray", "prayer", "bow", "prostrate", "glorify"],
    "guidance": ["guidance", "هداية", "guide", "path", "straight", "light", "truth"],
    "creation": ["creation", "خلق", "create", "heaven", "earth", "sky", "water", "life"],
    "judgment": ["judgment", "حساب", "day", "reckoning", "account", "scale", "weigh"],
    "patience": ["patience", "صبر", "patient", "endure", "steadfast", "persevere"],
}


# ── Report dataclass ─────────────────────────────────────────────────────────

@dataclass
class ProfileReport:
    """Output of TextProfiler.profile()."""

    emotional_category: str       # Primary Quranic emotional category
    valence: float                # Emotional valence: -1 (negative) to +1 (positive)
    arousal: float                # Emotional arousal: 0 (calm) to 1 (excited)
    complexity_score: float       # Information-theoretic text complexity: 0 to 1
    confidence: float             # Analysis confidence: 0 to 1
    attention_salience: float     # Attention routing salience: 0 to 1
    themes: List[str]             # Detected thematic elements

    # Optional extras
    secondary_category: str = ""
    attention_active: bool = False
    information_flow: float = 0.0
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "emotional_category": self.emotional_category,
            "valence": self.valence,
            "arousal": self.arousal,
            "complexity_score": self.complexity_score,
            "confidence": self.confidence,
            "attention_salience": self.attention_salience,
            "themes": self.themes,
            "secondary_category": self.secondary_category,
            "attention_active": self.attention_active,
            "information_flow": self.information_flow,
            "duration_ms": self.duration_ms,
        }


# ── Helper functions ─────────────────────────────────────────────────────────

def _text_to_vector(text: str, dim: int = 256) -> np.ndarray:
    """
    Convert text to a numeric vector via character-level statistics.
    Deterministic — no model required.
    """
    if not text:
        return np.zeros(dim, dtype=np.float32)

    seed = sum(ord(c) * (i + 1) for i, c in enumerate(text[:100]))
    rng = np.random.default_rng(seed % (2**32))

    chars = np.array([ord(c) for c in text[:512]], dtype=np.float32)
    chars = chars / 127.5 - 1.0

    if len(chars) >= dim:
        vec = chars[:dim]
    else:
        repeats = (dim // len(chars)) + 1
        vec = np.tile(chars, repeats)[:dim]
        noise = rng.standard_normal(dim).astype(np.float32) * 0.05
        vec = vec + noise

    complexity = min(1.0, len(set(text)) / 95.0)
    length_factor = min(1.0, len(text) / 500.0)
    boost = complexity * 0.5 + length_factor * 0.5
    vec = vec * boost

    return vec.astype(np.float32)


def _compute_complexity(state: np.ndarray) -> float:
    """
    Compute text complexity score using information-theoretic measures.
    Uses entropy of the state distribution normalized to [0, 1].
    """
    if state is None or np.all(state == 0):
        return 0.0

    state_abs = np.abs(state) + 1e-10
    state_norm = state_abs / state_abs.sum()
    entropy = float(-np.sum(state_norm * np.log(state_norm)))
    max_entropy = np.log(len(state_norm))
    if max_entropy == 0:
        return 0.0

    # Bipartition analysis for structural complexity
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
    entropy_score = float(entropy / max_entropy)
    structure_score = float(np.clip(kl, 0.0, 1.0))
    complexity = 0.6 * entropy_score + 0.4 * structure_score

    return float(np.clip(complexity, 0.0, 1.0))


def _detect_themes(text: str) -> List[str]:
    """Detect thematic elements from text using keyword matching."""
    text_lower = text.lower()
    detected = []
    for theme, keywords in _THEME_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            detected.append(theme)
    return detected if detected else ["general"]


# ── Main API class ───────────────────────────────────────────────────────────

class TextProfiler:
    """
    Quranic Text Profiling Engine.

    Analyzes text across emotional, complexity, confidence, and
    thematic dimensions using the 10 Quranic emotional categories.

    Usage:
        tp = TextProfiler()
        report = tp.profile("In the name of God, the Most Merciful.")
        print(report.emotional_category, report.valence, report.themes)
    """

    def __init__(
        self,
        workspace_dim: int = 256,
        feature_dim: int = 128,
        ignition_threshold: float = 0.5,
        decay_rate: float = 0.95,
        n_steps: int = 5,
        confidence_threshold: float = 0.7,
    ):
        self.n_steps = n_steps
        self._workspace_dim = workspace_dim

        # Attention router (GWT-based salience competition)
        self._attention = GlobalWorkspace(
            workspace_dim=workspace_dim,
            ignition_threshold=ignition_threshold,
            decay_rate=decay_rate,
        )

        # Emotional analyzer (circumplex model with Quranic categories)
        self._emotion = EmotionalValence(
            feature_dim=feature_dim,
            modulation_strength=0.3,
        )

        # Confidence estimator (metacognitive system)
        self._confidence = MetacognitiveSystem(
            confidence_threshold=confidence_threshold,
        )

    def profile(
        self,
        text: str,
        context: Optional[str] = None,
    ) -> ProfileReport:
        """
        Profile a text input across all analysis dimensions.

        Args:
            text: The text to analyze.
            context: Optional contextual information to inform analysis.

        Returns:
            ProfileReport with emotional category, valence, arousal,
            complexity, confidence, salience, and detected themes.
        """
        t0 = time.time()

        # Convert text to vector representation
        vec = _text_to_vector(text, dim=self._workspace_dim)

        # If context provided, blend it in
        if context:
            ctx_vec = _text_to_vector(context, dim=self._workspace_dim)
            vec = 0.8 * vec + 0.2 * ctx_vec

        # ── 1. Emotional analysis ────────────────────────────────────
        emotion_vec = vec[:self._emotion.feature_dim]
        valence, arousal = self._emotion.compute_valence(emotion_vec)
        # Map arousal from [-1, 1] to [0, 1]
        arousal_normalized = float(np.clip((arousal + 1) / 2, 0.0, 1.0))

        # Get emotional category from the emotion system's memory
        if self._emotion.emotional_memory:
            last_state = self._emotion.emotional_memory[-1]
            emotional_category = last_state.category
            secondary_category = last_state.secondary_category
        else:
            emotional_category = "general"
            secondary_category = ""

        # ── 2. Attention routing (salience competition) ──────────────
        norm = float(np.linalg.norm(vec))
        salience = float(np.tanh(norm / max(1.0, self._workspace_dim ** 0.5)))

        rng = np.random.default_rng(int(abs(vec.sum() * 1e6)) % (2 ** 32))
        ignitions = 0

        for step in range(self.n_steps):
            jitter = float(rng.normal(0, 0.03))
            step_salience = float(np.clip(salience + jitter, 0.0, 1.0))
            self._attention.submit_candidate(
                content=vec,
                source="text_input",
                salience=step_salience,
            )
            result = self._attention.compete_for_access()
            if result is not None:
                ignitions += 1

        attention_active = ignitions > 0
        attention_salience = float(np.clip(salience, 0.0, 1.0))

        # ── 3. Complexity scoring ────────────────────────────────────
        ws_state = self._attention.get_workspace_state()
        if ws_state is not None:
            complexity_score = _compute_complexity(ws_state)
        else:
            complexity_score = float(np.clip(salience * 0.25, 0.0, 0.29))

        # ── 4. Confidence estimation ─────────────────────────────────
        process_result = {
            "output": vec,
            "duration": time.time() - t0,
        }
        meta_repr = self._confidence.form_meta_representation(process_result)
        confidence = self._confidence.assess_confidence(meta_repr)

        # ── 5. Theme detection ───────────────────────────────────────
        themes = _detect_themes(text)

        # ── 6. Information flow ──────────────────────────────────────
        information_flow = self._attention.compute_information_flow()

        duration_ms = (time.time() - t0) * 1000

        return ProfileReport(
            emotional_category=emotional_category,
            valence=float(np.clip(valence, -1.0, 1.0)),
            arousal=arousal_normalized,
            complexity_score=complexity_score,
            confidence=confidence,
            attention_salience=attention_salience,
            themes=themes,
            secondary_category=secondary_category,
            attention_active=attention_active,
            information_flow=information_flow,
            duration_ms=duration_ms,
        )

    def get_emotional_categories(self) -> Dict[str, Tuple[float, float]]:
        """Return the 10 Quranic emotional categories with prototypical values."""
        return self._emotion.emotional_categories

    def reset(self) -> None:
        """Reset all internal state."""
        self._attention.workspace_state = None
        self._attention._candidates.clear()
        self._attention.access_history.clear()
        self._attention._broadcast_count = 0
        self._attention._competition_count = 0
        self._attention._ignition_failures = 0


__all__ = ["TextProfiler", "ProfileReport", "QURANIC_CATEGORIES"]
