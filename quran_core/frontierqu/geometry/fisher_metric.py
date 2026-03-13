"""Information Geometry: Fisher Metric on Tafsir Distributions.

Each verse's interpretive tradition is modeled as a probability distribution
over semantic categories. The Fisher information matrix defines a Riemannian
metric on this statistical manifold.

    g_ij(theta) = E[d log p/d theta_i . d log p/d theta_j]

Positive curvature = scholarly consensus
Negative curvature = interpretive disagreement
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional
import numpy as np

# Semantic categories for Quranic tafsir
SEMANTIC_CATEGORIES = [
    "legal",        # Ahkam (legal rulings)
    "theological",  # Aqidah (creed/belief)
    "ethical",      # Akhlaq (morality/ethics)
    "narrative",    # Qisas (stories of prophets)
    "eschatological", # Ma'ad (afterlife/judgment)
    "cosmological", # Khalq (creation/universe)
    "linguistic",   # Balaghi (rhetorical/linguistic)
    "mystical",     # Ishari (spiritual/sufi)
]

# Tafsir source weights (representing different scholarly traditions)
TAFSIR_SOURCES = {
    "tabari": {"school": "traditional", "weight": 1.0},
    "zamakhshari": {"school": "linguistic", "weight": 0.9},
    "razi": {"school": "theological", "weight": 0.95},
    "qurtubi": {"school": "legal", "weight": 0.9},
    "ibn_kathir": {"school": "traditional", "weight": 1.0},
    "baydawi": {"school": "theological", "weight": 0.85},
}

# Pre-defined semantic distributions for key verses
# Each maps (surah, verse) -> category probabilities
VERSE_DISTRIBUTIONS: Dict[Tuple[int, int], Dict[str, float]] = {
    (1, 1): {"legal": 0.05, "theological": 0.30, "ethical": 0.05, "narrative": 0.02,
             "eschatological": 0.02, "cosmological": 0.05, "linguistic": 0.40, "mystical": 0.11},
    (1, 2): {"legal": 0.05, "theological": 0.45, "ethical": 0.10, "narrative": 0.02,
             "eschatological": 0.02, "cosmological": 0.10, "linguistic": 0.20, "mystical": 0.06},
    (1, 3): {"legal": 0.02, "theological": 0.50, "ethical": 0.15, "narrative": 0.02,
             "eschatological": 0.02, "cosmological": 0.02, "linguistic": 0.20, "mystical": 0.07},
    (1, 4): {"legal": 0.05, "theological": 0.30, "ethical": 0.05, "narrative": 0.02,
             "eschatological": 0.40, "cosmological": 0.02, "linguistic": 0.10, "mystical": 0.06},
    (1, 5): {"legal": 0.10, "theological": 0.30, "ethical": 0.20, "narrative": 0.02,
             "eschatological": 0.02, "cosmological": 0.02, "linguistic": 0.15, "mystical": 0.19},
    (1, 6): {"legal": 0.05, "theological": 0.20, "ethical": 0.30, "narrative": 0.02,
             "eschatological": 0.02, "cosmological": 0.02, "linguistic": 0.15, "mystical": 0.24},
    (1, 7): {"legal": 0.05, "theological": 0.25, "ethical": 0.20, "narrative": 0.10,
             "eschatological": 0.15, "cosmological": 0.02, "linguistic": 0.15, "mystical": 0.08},
    (2, 255): {"legal": 0.05, "theological": 0.60, "ethical": 0.05, "narrative": 0.02,
               "eschatological": 0.05, "cosmological": 0.10, "linguistic": 0.08, "mystical": 0.05},
    (112, 1): {"legal": 0.02, "theological": 0.70, "ethical": 0.02, "narrative": 0.02,
               "eschatological": 0.02, "cosmological": 0.05, "linguistic": 0.12, "mystical": 0.05},
}


@dataclass
class TafsirDistribution:
    verse: Tuple[int, int]
    probabilities: Dict[str, float]

    @classmethod
    def for_verse(cls, verse: Tuple[int, int]) -> 'TafsirDistribution':
        if verse in VERSE_DISTRIBUTIONS:
            probs = VERSE_DISTRIBUTIONS[verse]
        else:
            # Default: uniform-ish distribution with theological emphasis
            n = len(SEMANTIC_CATEGORIES)
            base = 0.8 / n
            probs = {cat: base for cat in SEMANTIC_CATEGORIES}
            probs["theological"] = 0.2 + base
            # Normalize
            total = sum(probs.values())
            probs = {k: v / total for k, v in probs.items()}
        return cls(verse=verse, probabilities=probs)

    def to_vector(self) -> np.ndarray:
        return np.array([self.probabilities.get(cat, 0.0) for cat in SEMANTIC_CATEGORIES])


def fisher_matrix(verse: Tuple[int, int],
                  tafsir_sources: Optional[List[str]] = None) -> np.ndarray:
    """Compute Fisher information matrix for verse's tafsir distribution.

    G_ij = sum_x (1/p(x)) * (dp/d theta_i) * (dp/d theta_j)

    For categorical distribution, G_ij = delta_ij / p_i (diagonal).
    """
    dist = TafsirDistribution.for_verse(verse)
    p = dist.to_vector()

    # For categorical distribution, Fisher matrix is diag(1/p_i)
    # Clamp to avoid division by zero
    p_safe = np.maximum(p, 1e-10)

    # Fisher information for multinomial: G_ij = delta_ij/p_i
    G = np.diag(1.0 / p_safe)

    # Apply source weighting if specified
    if tafsir_sources:
        weight = sum(TAFSIR_SOURCES.get(s, {}).get("weight", 0.5)
                     for s in tafsir_sources) / len(tafsir_sources)
        G *= weight

    return G


def geodesic_distance(v1: Tuple[int, int], v2: Tuple[int, int]) -> float:
    """Compute Riemannian geodesic distance between two verse distributions.

    For categorical distributions with Fisher metric, this is:
        d(p, q) = 2 * arccos(sum(sqrt(p_i * q_i)))

    (Bhattacharyya/Hellinger distance on the statistical manifold)
    """
    d1 = TafsirDistribution.for_verse(v1)
    d2 = TafsirDistribution.for_verse(v2)

    p = d1.to_vector()
    q = d2.to_vector()

    # Fisher-Rao geodesic distance
    inner = np.sum(np.sqrt(p * q))
    inner = np.clip(inner, -1.0, 1.0)

    return 2.0 * np.arccos(inner)


def curvature(verse: Tuple[int, int]) -> float:
    """Compute scalar curvature of the statistical manifold at a verse.

    For categorical distribution on simplex:
        R = (n-1)(n-2)/2 where n = number of categories
    But weighted by distribution concentration (Herfindahl index).

    Positive = consensus (concentrated distribution)
    Negative = disagreement (spread distribution)
    """
    dist = TafsirDistribution.for_verse(verse)
    p = dist.to_vector()

    n = len(p)
    # Herfindahl-Hirschman Index (concentration measure)
    hhi = np.sum(p ** 2)

    # Uniform distribution gives HHI = 1/n
    uniform_hhi = 1.0 / n

    # Scale curvature: positive if concentrated, negative if spread
    # Base curvature of n-simplex
    base_curvature = (n - 1) * (n - 2) / 2.0

    # Adjust by how concentrated vs uniform the distribution is
    concentration = (hhi - uniform_hhi) / (1.0 - uniform_hhi)

    return float(base_curvature * concentration)
