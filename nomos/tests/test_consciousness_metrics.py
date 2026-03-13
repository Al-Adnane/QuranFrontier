"""
Tests for ConsciousnessMetrics product.
Runs against real GlobalWorkspace — no mocks of core GWT logic.
"""

import sys
import os
import pytest
import numpy as np

# ── Ensure nomos package is importable ──────────────────────────────────────
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CONSCIOUSNESS_PKG = os.path.join(_REPO, "consciousness")
for _p in [_REPO, _CONSCIOUSNESS_PKG]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from nomos.products.consciousness_metrics import (
    ConsciousnessMetrics,
    ConsciousnessReport,
    _safety_grade,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def cm():
    """Fresh ConsciousnessMetrics instance per test."""
    return ConsciousnessMetrics(
        workspace_dim=64,
        ignition_threshold=0.4,
        n_steps=10,
    )


@pytest.fixture
def cm_strict():
    """Instance with high ignition threshold — makes low-salience inputs fail."""
    return ConsciousnessMetrics(
        workspace_dim=64,
        ignition_threshold=0.85,
        n_steps=10,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestMeasureReturnsPhi:
    def test_measure_returns_phi_score(self, cm):
        """phi_score must be a float in [0, 1]."""
        report = cm.measure("The quick brown fox jumps over the lazy dog")
        assert isinstance(report, ConsciousnessReport)
        assert isinstance(report.phi_score, float)
        assert 0.0 <= report.phi_score <= 1.0

    def test_measure_with_numpy_vector(self, cm):
        """measure() accepts numpy array input."""
        vec = np.random.default_rng(1).standard_normal(64).astype(np.float32)
        report = cm.measure(vec)
        assert isinstance(report.phi_score, float)
        assert 0.0 <= report.phi_score <= 1.0

    def test_measure_with_list_input(self, cm):
        """measure() accepts list of floats."""
        data = [0.5] * 64
        report = cm.measure(data)
        assert isinstance(report.phi_score, float)
        assert 0.0 <= report.phi_score <= 1.0


class TestGWTIgnition:
    def test_gwt_ignition_detected(self):
        """High-salience input (large-magnitude vector) triggers ignition."""
        # Use low threshold so ignition fires easily
        cm = ConsciousnessMetrics(
            workspace_dim=64,
            ignition_threshold=0.1,
            n_steps=5,
        )
        # Large, uniform vector → high norm → high salience
        vec = np.ones(64, dtype=np.float32) * 2.0
        report = cm.measure(vec)
        assert report.gwt_active is True, (
            f"Expected ignition for high-salience input, got phi={report.phi_score}, "
            f"ignition_rate={report.ignition_rate}"
        )

    def test_gwt_no_ignition_for_low_salience(self):
        """
        Low-salience input (near-zero vector) with strict threshold should
        fail to ignite OR produce a low ignition rate.
        """
        cm = ConsciousnessMetrics(
            workspace_dim=64,
            ignition_threshold=0.99,  # almost impossible to reach
            n_steps=5,
        )
        # Near-zero vector → near-zero salience
        vec = np.zeros(64, dtype=np.float32) + 1e-6
        report = cm.measure(vec)
        # With threshold=0.99 and near-zero input, ignition should not fire
        assert report.gwt_active is False or report.ignition_rate < 0.5, (
            f"Expected low/no ignition for near-zero input, got "
            f"gwt_active={report.gwt_active}, ignition_rate={report.ignition_rate}"
        )


class TestSafetyGrade:
    def test_safety_grade_classification(self):
        """_safety_grade() returns correct labels for boundary values."""
        assert _safety_grade(0.0) == "SAFE"
        assert _safety_grade(0.1) == "SAFE"
        assert _safety_grade(0.29) == "SAFE"
        assert _safety_grade(0.3) == "MODERATE"
        assert _safety_grade(0.5) == "MODERATE"
        assert _safety_grade(0.7) == "MODERATE"
        assert _safety_grade(0.71) == "HIGH"
        assert _safety_grade(1.0) == "HIGH"

    def test_report_safety_grade_matches_phi(self, cm):
        """safety_grade in report matches _safety_grade(phi_score)."""
        report = cm.measure("hello world")
        expected = _safety_grade(report.phi_score)
        assert report.safety_grade == expected

    def test_safety_grade_in_valid_set(self, cm):
        """safety_grade is always one of the three valid labels."""
        for text in ["", "a", "x" * 100, "This is sensitive financial data: SSN 123-45-6789"]:
            report = cm.measure(text)
            assert report.safety_grade in {"SAFE", "MODERATE", "HIGH"}


class TestInformationFlow:
    def test_information_flow_nonzero_after_broadcast(self):
        """
        After multiple distinct broadcasts, information_flow should be > 0.
        GlobalWorkspace.compute_information_flow() requires ≥5 history entries.
        """
        cm = ConsciousnessMetrics(
            workspace_dim=64,
            ignition_threshold=0.1,  # low threshold to guarantee ignition
            n_steps=3,
        )
        rng = np.random.default_rng(42)

        # Measure 3 distinct inputs — each adds broadcasts to history
        for _ in range(3):
            vec = rng.standard_normal(64).astype(np.float32) * 2.0
            cm.measure(vec)

        # Final measure with a fresh distinct vector
        vec_final = rng.standard_normal(64).astype(np.float32) * 2.0
        report = cm.measure(vec_final)

        # We need ≥5 broadcasts total; 4 measures × 3 steps × ~100% ignition = ≥12
        assert report.information_flow >= 0.0  # always valid
        # With diverse inputs and ignitions, flow should be > 0
        assert report.information_flow > 0.0, (
            f"Expected information_flow > 0 after multiple broadcasts, "
            f"got {report.information_flow}. broadcast_count={report.broadcast_count}"
        )

    def test_information_flow_in_range(self, cm):
        """information_flow is always in [0, 1]."""
        report = cm.measure("test information flow bounds check")
        assert 0.0 <= report.information_flow <= 1.0


class TestReportStructure:
    def test_report_has_all_fields(self, cm):
        """ConsciousnessReport has all required fields."""
        report = cm.measure("structure test")
        assert hasattr(report, "phi_score")
        assert hasattr(report, "gwt_active")
        assert hasattr(report, "ignition_threshold")
        assert hasattr(report, "information_flow")
        assert hasattr(report, "safety_grade")

    def test_ignition_threshold_matches_config(self, cm):
        """ignition_threshold in report equals the configured threshold."""
        report = cm.measure("threshold test")
        assert report.ignition_threshold == 0.4

    def test_to_dict_serializable(self, cm):
        """to_dict() returns a plain dict with expected keys."""
        report = cm.measure("serialization test")
        d = report.to_dict()
        assert isinstance(d, dict)
        for key in ("phi_score", "gwt_active", "ignition_threshold",
                    "information_flow", "safety_grade"):
            assert key in d
