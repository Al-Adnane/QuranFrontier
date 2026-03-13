"""Discourse Coherence Analyzer for Quranic Text.

Models inter-verse coherence using:
    - Character n-gram cosine similarity
    - Thematic transition detection via sliding-window divergence
    - Munasabat (contextual relevance) scoring between verse pairs

The classical discipline of 'ilm al-munasabat studies the wisdom behind
verse and surah ordering. This module provides computational measures
that approximate coherence as understood in Quranic discourse analysis.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math
import re


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Transition:
    """A detected thematic transition between verses."""
    position: int          # index in the verse list where transition occurs
    verse_before: str
    verse_after: str
    divergence: float      # how sharp the topic shift is (0.0 = smooth, 1.0 = abrupt)
    transition_type: str   # 'gradual', 'sharp', 'parenthetical'

    def __repr__(self) -> str:
        return (f"Transition(pos={self.position}, type={self.transition_type!r}, "
                f"div={self.divergence:.3f})")


@dataclass
class CoherenceReport:
    """Full coherence report for a surah or passage."""
    num_verses: int
    mean_coherence: float
    min_coherence: float
    max_coherence: float
    transitions: List[Transition]
    pairwise_scores: List[float]


# ============================================================================
# Internal Utilities
# ============================================================================

_TASHKEEL_RE = re.compile(r'[\u064B-\u065F\u0670]')


def _strip_tashkeel(text: str) -> str:
    """Remove Arabic diacritical marks."""
    return _TASHKEEL_RE.sub('', text)


def _char_ngrams(text: str, n: int = 3) -> Dict[str, int]:
    """Extract character n-gram frequency vector.

    Args:
        text: Input text (diacritics stripped).
        n: n-gram size (default 3).

    Returns:
        Dict mapping n-gram string to count.
    """
    cleaned = _strip_tashkeel(text).replace(' ', '')
    grams: Dict[str, int] = {}
    for i in range(len(cleaned) - n + 1):
        gram = cleaned[i:i + n]
        grams[gram] = grams.get(gram, 0) + 1
    return grams


def _cosine_similarity(vec_a: Dict[str, int], vec_b: Dict[str, int]) -> float:
    """Compute cosine similarity between two sparse frequency vectors.

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 if either vector is zero.
    """
    if not vec_a or not vec_b:
        return 0.0

    keys = set(vec_a.keys()) | set(vec_b.keys())

    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot / (mag_a * mag_b)


def _word_overlap(text_a: str, text_b: str) -> float:
    """Compute Jaccard word overlap between two texts.

    Returns:
        Float in [0.0, 1.0].
    """
    words_a = set(_strip_tashkeel(text_a).split())
    words_b = set(_strip_tashkeel(text_b).split())

    if not words_a and not words_b:
        return 1.0
    union = words_a | words_b
    if not union:
        return 0.0
    return len(words_a & words_b) / len(union)


# Thematic keyword clusters for Quranic discourse
_THEME_KEYWORDS: Dict[str, List[str]] = {
    'tawhid': ['الله', 'رب', 'إله', 'واحد', 'أحد', 'سبحان', 'تعالى'],
    'akhirah': ['يوم', 'القيامة', 'الآخرة', 'جنة', 'نار', 'حساب', 'بعث'],
    'risalah': ['رسول', 'نبي', 'كتاب', 'آية', 'وحي', 'أنزل', 'بلغ'],
    'ahkam': ['حلال', 'حرام', 'فرض', 'واجب', 'أقيموا', 'آتوا', 'صلاة', 'زكاة'],
    'qisas': ['قال', 'قوم', 'أرسلنا', 'فرعون', 'موسى', 'إبراهيم', 'نوح'],
    'creation': ['خلق', 'سماوات', 'أرض', 'ماء', 'جعل', 'أنبت'],
}


def _theme_vector(text: str) -> Dict[str, float]:
    """Compute theme affinity vector for a text.

    Returns:
        Dict mapping theme name to affinity score.
    """
    stripped = _strip_tashkeel(text)
    result: Dict[str, float] = {}
    for theme, keywords in _THEME_KEYWORDS.items():
        score = 0.0
        for kw in keywords:
            kw_s = _strip_tashkeel(kw)
            if kw_s in stripped:
                score += 1.0
        result[theme] = score / max(len(keywords), 1)
    return result


def _theme_divergence(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Jensen-Shannon-like divergence between theme vectors.

    Returns:
        Float in [0.0, 1.0]. 0 = identical themes, 1 = completely different.
    """
    all_themes = set(vec_a.keys()) | set(vec_b.keys())
    if not all_themes:
        return 0.0

    total_diff = 0.0
    for theme in all_themes:
        a = vec_a.get(theme, 0.0)
        b = vec_b.get(theme, 0.0)
        total_diff += abs(a - b)

    max_possible = len(all_themes)  # each theme can differ by at most 1.0
    return total_diff / max_possible if max_possible > 0 else 0.0


# ============================================================================
# Discourse Analyzer
# ============================================================================

class DiscourseAnalyzer:
    """Analyzer for discourse coherence in Quranic text.

    Provides three core operations:
        1. Pairwise verse coherence via n-gram cosine similarity
        2. Thematic transition detection across verse sequences
        3. Munasabat scoring for contextual relevance
    """

    def __init__(self, ngram_size: int = 3, transition_threshold: float = 0.4):
        """Initialize analyzer.

        Args:
            ngram_size: Character n-gram size for similarity (default 3).
            transition_threshold: Divergence above which a transition is flagged.
        """
        self.ngram_size = ngram_size
        self.transition_threshold = transition_threshold

    def compute_coherence(self, verse1: str, verse2: str) -> float:
        """Compute coherence between two verses using character n-gram cosine similarity.

        Combines character-level n-gram similarity with word-level overlap
        for a blended coherence measure.

        Args:
            verse1: First verse text.
            verse2: Second verse text.

        Returns:
            Float in [0.0, 1.0] where 1.0 = maximally coherent.
        """
        # Character n-gram similarity (primary signal)
        ngrams_a = _char_ngrams(verse1, self.ngram_size)
        ngrams_b = _char_ngrams(verse2, self.ngram_size)
        ngram_sim = _cosine_similarity(ngrams_a, ngrams_b)

        # Word overlap (secondary signal)
        word_sim = _word_overlap(verse1, verse2)

        # Blend: 70% n-gram, 30% word overlap
        return 0.7 * ngram_sim + 0.3 * word_sim

    def find_thematic_transitions(self, surah_verses: List[str]) -> List[Transition]:
        """Detect thematic transitions (topic shifts) in a sequence of verses.

        Uses a sliding window to compare consecutive verse-pair coherence
        against the running average. A significant drop signals a transition.

        Args:
            surah_verses: Ordered list of verse texts from a surah.

        Returns:
            List of Transition objects where topic shifts are detected.
        """
        if len(surah_verses) < 2:
            return []

        transitions: List[Transition] = []

        # Compute pairwise theme vectors
        theme_vecs = [_theme_vector(v) for v in surah_verses]

        # Compute consecutive divergences
        divergences: List[float] = []
        for i in range(len(surah_verses) - 1):
            div = _theme_divergence(theme_vecs[i], theme_vecs[i + 1])
            divergences.append(div)

        # Running mean for adaptive thresholding
        if divergences:
            running_mean = sum(divergences) / len(divergences)
        else:
            running_mean = 0.0

        adaptive_threshold = max(self.transition_threshold, running_mean * 1.5)

        for i, div in enumerate(divergences):
            if div >= adaptive_threshold:
                # Classify transition type
                if div >= 0.8:
                    ttype = 'sharp'
                elif div >= 0.5:
                    ttype = 'gradual'
                else:
                    ttype = 'parenthetical'

                transitions.append(Transition(
                    position=i + 1,
                    verse_before=surah_verses[i],
                    verse_after=surah_verses[i + 1],
                    divergence=div,
                    transition_type=ttype,
                ))

        return transitions

    def munasabat_score(self, verse_a: int, verse_b: int,
                        surah_verses: Optional[List[str]] = None) -> float:
        """Compute munasabat (contextual relevance) between two verse positions.

        If surah_verses is provided, uses actual text similarity.
        Otherwise falls back to a proximity-based heuristic where adjacent
        verses score higher than distant ones.

        Args:
            verse_a: Index of first verse (0-based).
            verse_b: Index of second verse (0-based).
            surah_verses: Optional list of verse texts for content-based scoring.

        Returns:
            Float in [0.0, 1.0] where 1.0 = maximum contextual relevance.
        """
        if surah_verses is not None:
            if 0 <= verse_a < len(surah_verses) and 0 <= verse_b < len(surah_verses):
                # Content-based: n-gram coherence + theme similarity
                coherence = self.compute_coherence(
                    surah_verses[verse_a], surah_verses[verse_b]
                )
                theme_a = _theme_vector(surah_verses[verse_a])
                theme_b = _theme_vector(surah_verses[verse_b])
                theme_sim = 1.0 - _theme_divergence(theme_a, theme_b)

                # Proximity weight: closer verses are more likely munasib
                distance = abs(verse_a - verse_b)
                proximity = 1.0 / (1.0 + 0.1 * distance)

                # Blend all signals
                return 0.4 * coherence + 0.3 * theme_sim + 0.3 * proximity

        # Fallback: pure proximity heuristic
        distance = abs(verse_a - verse_b)
        return 1.0 / (1.0 + 0.2 * distance)

    def analyze_surah(self, surah_verses: List[str]) -> CoherenceReport:
        """Full coherence analysis for a surah.

        Args:
            surah_verses: Ordered list of verse texts.

        Returns:
            CoherenceReport with statistics and detected transitions.
        """
        if len(surah_verses) < 2:
            return CoherenceReport(
                num_verses=len(surah_verses),
                mean_coherence=1.0,
                min_coherence=1.0,
                max_coherence=1.0,
                transitions=[],
                pairwise_scores=[],
            )

        # Compute consecutive pairwise coherences
        pairwise: List[float] = []
        for i in range(len(surah_verses) - 1):
            score = self.compute_coherence(surah_verses[i], surah_verses[i + 1])
            pairwise.append(score)

        transitions = self.find_thematic_transitions(surah_verses)

        return CoherenceReport(
            num_verses=len(surah_verses),
            mean_coherence=sum(pairwise) / len(pairwise),
            min_coherence=min(pairwise),
            max_coherence=max(pairwise),
            transitions=transitions,
            pairwise_scores=pairwise,
        )
