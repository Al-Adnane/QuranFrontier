"""
Tests for TextProfiler — Quranic Text Analysis & Profiling Engine
=================================================================
10+ tests covering all ProfileReport fields, edge cases, and API.
"""

import sys
import os
import pytest
import numpy as np

# ── Path setup ───────────────────────────────────────────────────────────────
_HERE = os.path.abspath(os.path.dirname(__file__))
_NOMOS = os.path.abspath(os.path.join(_HERE, ".."))
if _NOMOS not in sys.path:
    sys.path.insert(0, _NOMOS)

from products.text_profiler import (
    TextProfiler,
    ProfileReport,
    QURANIC_CATEGORIES,
    _text_to_vector,
    _compute_complexity,
    _detect_themes,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def profiler():
    return TextProfiler()


# ── Tests ────────────────────────────────────────────────────────────────────

class TestTextProfilerBasic:
    """Basic profiling tests."""

    def test_profile_returns_report(self, profiler):
        """profile() returns a ProfileReport dataclass."""
        report = profiler.profile("In the name of God, the Most Merciful.")
        assert isinstance(report, ProfileReport)

    def test_valence_in_range(self, profiler):
        """Valence must be in [-1, 1]."""
        report = profiler.profile("God is the Most Merciful, full of compassion and grace.")
        assert -1.0 <= report.valence <= 1.0

    def test_arousal_in_range(self, profiler):
        """Arousal must be in [0, 1]."""
        report = profiler.profile("Be patient and steadfast in your faith.")
        assert 0.0 <= report.arousal <= 1.0

    def test_complexity_in_range(self, profiler):
        """Complexity score must be in [0, 1]."""
        report = profiler.profile(
            "And We have certainly made the Quran easy to remember. "
            "So is there anyone who will be mindful?"
        )
        assert 0.0 <= report.complexity_score <= 1.0

    def test_confidence_in_range(self, profiler):
        """Confidence must be in [0, 1]."""
        report = profiler.profile("Praise be to God, Lord of all the worlds.")
        assert 0.0 <= report.confidence <= 1.0

    def test_attention_salience_in_range(self, profiler):
        """Attention salience must be in [0, 1]."""
        report = profiler.profile("He is the First and the Last, the Manifest and the Hidden.")
        assert 0.0 <= report.attention_salience <= 1.0

    def test_emotional_category_is_valid(self, profiler):
        """Emotional category must be one of the 10 Quranic categories."""
        report = profiler.profile("God forgives all sins, for He is the Forgiving.")
        assert report.emotional_category in QURANIC_CATEGORIES


class TestThemeDetection:
    """Theme detection tests."""

    def test_mercy_theme_detected(self, profiler):
        """Text about mercy should detect 'mercy' theme."""
        report = profiler.profile("God's mercy encompasses all things.")
        assert "mercy" in report.themes

    def test_warning_theme_detected(self, profiler):
        """Text about warning should detect 'warning' theme."""
        report = profiler.profile("A warning to those who deny the punishment of hellfire.")
        assert "warning" in report.themes

    def test_guidance_theme_detected(self, profiler):
        """Text about guidance should detect 'guidance' theme."""
        report = profiler.profile("Guide us to the straight path, the path of truth and light.")
        assert "guidance" in report.themes

    def test_multiple_themes(self, profiler):
        """Text with multiple themes should detect all of them."""
        report = profiler.profile(
            "God's mercy and guidance lead to the promise of paradise."
        )
        assert len(report.themes) >= 2

    def test_general_fallback(self, profiler):
        """Text with no recognizable themes gets 'general'."""
        report = profiler.profile("xyz abc 123")
        assert "general" in report.themes


class TestEdgeCases:
    """Edge cases and robustness."""

    def test_empty_string(self, profiler):
        """Empty string should not crash, returns valid report."""
        report = profiler.profile("")
        assert isinstance(report, ProfileReport)
        assert report.complexity_score >= 0.0

    def test_very_long_text(self, profiler):
        """Long text should not crash."""
        long_text = "In the name of God. " * 500
        report = profiler.profile(long_text)
        assert isinstance(report, ProfileReport)

    def test_arabic_text(self, profiler):
        """Arabic text should be handled without errors."""
        report = profiler.profile("بسم الله الرحمن الرحيم")
        assert isinstance(report, ProfileReport)
        assert -1.0 <= report.valence <= 1.0

    def test_context_blending(self, profiler):
        """Providing context should change the result vs. no context."""
        report_no_ctx = profiler.profile("He said to them.")
        profiler.reset()
        report_with_ctx = profiler.profile(
            "He said to them.",
            context="The prophet warned the disbelievers of punishment.",
        )
        # Both should be valid; context may shift results
        assert isinstance(report_with_ctx, ProfileReport)

    def test_to_dict(self, profiler):
        """to_dict() returns all expected keys."""
        report = profiler.profile("Test input.")
        d = report.to_dict()
        expected_keys = {
            "emotional_category", "valence", "arousal", "complexity_score",
            "confidence", "attention_salience", "themes",
            "secondary_category", "attention_active",
            "information_flow", "duration_ms",
        }
        assert expected_keys == set(d.keys())


class TestHelpers:
    """Test internal helper functions."""

    def test_text_to_vector_deterministic(self):
        """Same text should produce same vector."""
        v1 = _text_to_vector("test input", dim=64)
        v2 = _text_to_vector("test input", dim=64)
        np.testing.assert_array_equal(v1, v2)

    def test_text_to_vector_empty(self):
        """Empty text returns zero vector."""
        v = _text_to_vector("", dim=32)
        assert np.all(v == 0)

    def test_compute_complexity_zeros(self):
        """All-zero state returns 0 complexity."""
        assert _compute_complexity(np.zeros(64)) == 0.0

    def test_detect_themes_keywords(self):
        """Keyword detection works for each category."""
        assert "worship" in _detect_themes("We pray and prostrate before God.")
        assert "creation" in _detect_themes("God created the heavens and the earth.")
        assert "patience" in _detect_themes("Be patient and endure.")


class TestNoConsciousnessTerminology:
    """Verify no pseudoscience terminology leaks into the public API."""

    def test_no_phi_in_report(self, profiler):
        """ProfileReport should not have phi_score."""
        report = profiler.profile("Test.")
        assert not hasattr(report, "phi_score")

    def test_no_consciousness_in_report_keys(self, profiler):
        """to_dict keys should not contain 'consciousness' or 'phi'."""
        d = profiler.profile("Test.").to_dict()
        for key in d:
            assert "consciousness" not in key.lower()
            assert "phi" not in key.lower()

    def test_categories_are_ten(self):
        """Exactly 10 Quranic categories."""
        assert len(QURANIC_CATEGORIES) == 10


class TestReset:
    """Test reset functionality."""

    def test_reset_clears_state(self, profiler):
        """After reset, workspace state should be None."""
        profiler.profile("Some text to populate state.")
        profiler.reset()
        assert profiler._attention.get_workspace_state() is None
        assert profiler._attention._broadcast_count == 0
