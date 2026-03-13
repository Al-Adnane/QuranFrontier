"""
Tests for ConsensusEngine — multi-tradition meta-evaluator.
All tests must pass with real (non-stub) tradition adapters.
"""

import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "quran-core"))

import pytest
from nomos.core.consensus_engine import ConsensusEngine, ConsensusReport
from nomos.traditions.islamic_adapter import IslamicTraditionAdapter
from nomos.traditions.utilitarian_adapter import UtilitarianAdapter
from nomos.traditions.kantian_adapter import KantianAdapter

CONTEXT = {"domain": "general"}

ACTIONS = {
    "riba":  {"subject": "riba",  "description": "Charge interest", "beneficiaries": 1, "harmed_parties": 10, "reversible": False},
    "trade": {"subject": "trade", "description": "Fair trade",      "beneficiaries": 2, "harmed_parties": 0,  "reversible": True},
    "salah": {"subject": "salah", "description": "Five daily prayers", "beneficiaries": 1, "harmed_parties": 0, "reversible": True},
    "lie_to_save": {"subject": "lying", "description": "Lie to save a life", "beneficiaries": 1, "harmed_parties": 0, "maxim": "Lie to save a life", "reversible": False},
    "lying_gain": {"subject": "lying", "description": "Lie for personal gain", "beneficiaries": 1, "harmed_parties": 3, "maxim": "Lie whenever convenient", "reversible": False},
}


@pytest.fixture
def engine():
    return ConsensusEngine.default()


class TestConsensusEngineBasics:

    def test_default_engine_has_three_traditions(self, engine):
        assert len(engine._adapters) == 3
        assert "islamic" in engine._adapters
        assert "utilitarian" in engine._adapters
        assert "kantian" in engine._adapters

    def test_evaluate_returns_report(self, engine):
        report = engine.evaluate(ACTIONS["trade"], CONTEXT)
        assert isinstance(report, ConsensusReport)

    def test_weighted_mean_in_range(self, engine):
        for name, action in ACTIONS.items():
            report = engine.evaluate(action, CONTEXT)
            assert 0.0 <= report.weighted_mean <= 1.0, f"{name}: {report.weighted_mean}"

    def test_std_dev_nonnegative(self, engine):
        for name, action in ACTIONS.items():
            report = engine.evaluate(action, CONTEXT)
            assert report.std_dev >= 0.0

    def test_confidence_in_range(self, engine):
        for name, action in ACTIONS.items():
            report = engine.evaluate(action, CONTEXT)
            assert 0.0 <= report.confidence <= 1.0

    def test_verdict_is_valid(self, engine):
        for name, action in ACTIONS.items():
            report = engine.evaluate(action, CONTEXT)
            assert report.verdict in ("APPROVED", "REJECTED", "CONTESTED"), (
                f"{name}: unexpected verdict {report.verdict}"
            )

    def test_conflict_level_is_valid(self, engine):
        for name, action in ACTIONS.items():
            report = engine.evaluate(action, CONTEXT)
            assert report.conflict_level in ("LOW", "MEDIUM", "HIGH")

    def test_tradition_scores_sum_weights_to_one(self, engine):
        report = engine.evaluate(ACTIONS["trade"], CONTEXT)
        total = sum(ts.weight for ts in report.tradition_scores)
        assert abs(total - 1.0) < 1e-9

    def test_all_three_traditions_in_report(self, engine):
        report = engine.evaluate(ACTIONS["trade"], CONTEXT)
        names = {ts.tradition for ts in report.tradition_scores}
        assert names == {"islamic", "utilitarian", "kantian"}

    def test_explanation_is_nonempty_string(self, engine):
        report = engine.evaluate(ACTIONS["trade"], CONTEXT)
        assert isinstance(report.explanation, str)
        assert len(report.explanation) > 10


class TestConsensusVerdicts:

    def test_fair_trade_approved_by_consensus(self, engine):
        """Fair trade: all traditions approve → APPROVED."""
        report = engine.evaluate(ACTIONS["trade"], CONTEXT)
        assert report.verdict == "APPROVED", (
            f"Expected APPROVED for fair trade, got {report.verdict}. "
            f"Mean={report.weighted_mean:.2f}, conflict={report.conflict_level}"
        )

    def test_riba_rejected_or_contested(self, engine):
        """Riba: Islamic strongly rejects, others variable → REJECTED or CONTESTED."""
        report = engine.evaluate(ACTIONS["riba"], CONTEXT)
        assert report.verdict in ("REJECTED", "CONTESTED"), (
            f"Expected REJECTED/CONTESTED for riba, got {report.verdict}. "
            f"Mean={report.weighted_mean:.2f}"
        )

    def test_lying_gain_rejected(self, engine):
        """Lying for gain: all traditions condemn → REJECTED."""
        report = engine.evaluate(ACTIONS["lying_gain"], CONTEXT)
        assert report.verdict == "REJECTED", (
            f"Expected REJECTED for lying-for-gain, got {report.verdict}. "
            f"Mean={report.weighted_mean:.2f}"
        )

    def test_lie_to_save_is_contested(self, engine):
        """
        Lie to save life: Utilitarian approves, Kantian rejects → HIGH conflict → CONTESTED.
        This is the canonical moral dilemma — must NOT be unanimously approved or rejected.
        """
        report = engine.evaluate(ACTIONS["lie_to_save"], CONTEXT)
        assert report.verdict == "CONTESTED", (
            f"Lying-to-save-life must be CONTESTED (moral dilemma). "
            f"Got {report.verdict}. Scores: "
            + ", ".join(f"{ts.tradition}={ts.score:.2f}" for ts in report.tradition_scores)
        )

    def test_salah_approved(self, engine):
        """Prayer is approved across all traditions."""
        report = engine.evaluate(ACTIONS["salah"], CONTEXT)
        assert report.verdict == "APPROVED", (
            f"Expected APPROVED for salah, got {report.verdict}. Mean={report.weighted_mean:.2f}"
        )


class TestConflictDetection:

    def test_fair_trade_low_or_medium_conflict(self, engine):
        """Fair trade: traditions lean positive, no HIGH conflict."""
        report = engine.evaluate(ACTIONS["trade"], CONTEXT)
        assert report.conflict_level in ("LOW", "MEDIUM"), (
            f"Expected LOW or MEDIUM conflict for fair trade, got {report.conflict_level}. "
            f"Std={report.std_dev:.2f}"
        )
        # Critically: must not be HIGH (no strong moral controversy)
        assert report.conflict_level != "HIGH"

    def test_lie_to_save_high_conflict(self, engine):
        """Utilitarian vs Kantian diverge strongly → HIGH conflict."""
        report = engine.evaluate(ACTIONS["lie_to_save"], CONTEXT)
        assert report.conflict_level == "HIGH", (
            f"Expected HIGH conflict for lying-to-save-life, got {report.conflict_level}. "
            f"Std={report.std_dev:.2f}"
        )

    def test_detect_moral_dilemma_true_for_contested(self, engine):
        assert engine.detect_moral_dilemma(ACTIONS["lie_to_save"], CONTEXT) is True

    def test_detect_moral_dilemma_false_for_consensus(self, engine):
        assert engine.detect_moral_dilemma(ACTIONS["trade"], CONTEXT) is False

    def test_riba_has_dissenting_traditions(self, engine):
        report = engine.evaluate(ACTIONS["riba"], CONTEXT)
        # Islamic should always dissent on riba
        assert "islamic" in report.dissenting_traditions, (
            f"Islamic should dissent on riba. Dissenting: {report.dissenting_traditions}"
        )


class TestCustomWeights:

    def test_islamic_weighted_engine_rejects_riba_strongly(self):
        engine = ConsensusEngine()
        engine.register("islamic",     IslamicTraditionAdapter(), weight=3.0)
        engine.register("utilitarian", UtilitarianAdapter(),       weight=1.0)
        engine.register("kantian",     KantianAdapter(),            weight=1.0)

        report = engine.evaluate(ACTIONS["riba"], CONTEXT)
        # Islamic weight=3x → riba (0.05) should pull mean down strongly
        assert report.weighted_mean < 0.4, (
            f"Islamic-weighted engine should reject riba (mean < 0.4). Got {report.weighted_mean:.2f}"
        )

    def test_utilitarian_weighted_approves_lie_to_save(self):
        engine = ConsensusEngine()
        engine.register("utilitarian", UtilitarianAdapter(),       weight=3.0)
        engine.register("kantian",     KantianAdapter(),            weight=1.0)

        report = engine.evaluate(ACTIONS["lie_to_save"], CONTEXT)
        # Utilitarian weight=3x → should pull mean above Kantian rejection (> 0.4)
        assert report.weighted_mean > 0.40, (
            f"Utilitarian-weighted engine should lean toward approving lie-to-save. Got {report.weighted_mean:.2f}"
        )

    def test_weights_normalize_correctly(self):
        engine = ConsensusEngine()
        engine.register("a", IslamicTraditionAdapter(),  weight=2.0)
        engine.register("b", UtilitarianAdapter(),       weight=3.0)

        report = engine.evaluate(ACTIONS["trade"], CONTEXT)
        total_weight = sum(ts.weight for ts in report.tradition_scores)
        assert abs(total_weight - 1.0) < 1e-9
