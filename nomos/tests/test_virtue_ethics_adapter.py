"""
Tests for VirtueEthicsAdapter — 4th tradition for NOMOS ConsensusEngine.

Covers:
  - Adapter identity / contract
  - load_norms() structure
  - Action scoring for canonical virtue/vice cases
  - Phronesis contested-mean case (lie_to_save)
  - Score range invariant over all ACTIONS from test_consensus_engine
  - Integration: 4-tradition ConsensusEngine verdict
"""

import sys
import os

# Ensure project root is on path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "quran-core"))

import pytest
from nomos.traditions.virtue_ethics_adapter import VirtueEthicsAdapter
from nomos.core.consensus_engine import ConsensusEngine

# ── Shared test data ────────────────────────────────────────────────────────

ADAPTER = VirtueEthicsAdapter()
CONTEXT = {"domain": "general"}

# Same ACTIONS dict as test_consensus_engine.py — score-range invariant
ACTIONS = {
    "riba": {
        "subject": "riba",
        "description": "Charge interest",
        "beneficiaries": 1,
        "harmed_parties": 10,
        "reversible": False,
    },
    "trade": {
        "subject": "trade",
        "description": "Fair trade",
        "beneficiaries": 2,
        "harmed_parties": 0,
        "reversible": True,
    },
    "salah": {
        "subject": "salah",
        "description": "Five daily prayers",
        "beneficiaries": 1,
        "harmed_parties": 0,
        "reversible": True,
    },
    "lie_to_save": {
        "subject": "lying",
        "description": "Lie to save a life",
        "beneficiaries": 1,
        "harmed_parties": 0,
        "maxim": "Lie to save a life",
        "reversible": False,
    },
    "lying_gain": {
        "subject": "lying",
        "description": "Lie for personal gain",
        "beneficiaries": 1,
        "harmed_parties": 3,
        "maxim": "Lie whenever convenient",
        "reversible": False,
    },
    "giving_charity": {
        "subject": "giving_charity",
        "description": "Give to those in need",
        "beneficiaries": 5,
        "harmed_parties": 0,
    },
}

# ── Adapter identity ────────────────────────────────────────────────────────

class TestAdapterIdentity:

    def test_adapter_name_is_virtue_ethics(self):
        assert ADAPTER.name == "virtue_ethics"

    def test_adapter_implements_protocol(self):
        """VirtueEthicsAdapter must satisfy TraditionAdapter protocol."""
        from nomos.interfaces.protocols import TraditionAdapter
        assert isinstance(ADAPTER, TraditionAdapter)


# ── load_norms ──────────────────────────────────────────────────────────────

class TestLoadNorms:

    def test_load_norms_returns_list(self):
        norms = ADAPTER.load_norms()
        assert isinstance(norms, list)

    def test_load_norms_has_at_least_five(self):
        norms = ADAPTER.load_norms()
        assert len(norms) >= 5

    def test_required_norm_ids_present(self):
        norms = ADAPTER.load_norms()
        ids = {n["id"] for n in norms}
        required = {"courage", "justice", "phronesis", "vice_prohibition", "eudaimonia"}
        assert required.issubset(ids), f"Missing norms: {required - ids}"

    def test_each_norm_has_type_and_strength(self):
        for norm in ADAPTER.load_norms():
            assert "type" in norm, f"Norm {norm.get('id')} missing 'type'"
            assert "strength" in norm, f"Norm {norm.get('id')} missing 'strength'"
            assert 0.0 <= norm["strength"] <= 1.0

    def test_domain_parameter_accepted(self):
        """load_norms() should accept domain without raising."""
        for domain in ("general", "finance", "worship", "family"):
            norms = ADAPTER.load_norms(domain=domain)
            assert isinstance(norms, list)


# ── Scoring: virtue cases ───────────────────────────────────────────────────

class TestVirtueScores:

    def test_trade_approved(self):
        """Fair trade expresses justice + temperance → score > 0.7."""
        score = ADAPTER.evaluate(ACTIONS["trade"], CONTEXT)
        assert score > 0.7, f"trade score {score:.4f} should be > 0.7"

    def test_salah_approved(self):
        """Prayer: piety + humility + contemplation → score > 0.8."""
        score = ADAPTER.evaluate(ACTIONS["salah"], CONTEXT)
        assert score > 0.8, f"salah score {score:.4f} should be > 0.8"

    def test_giving_charity_approved(self):
        """Generosity + justice → score > 0.8."""
        score = ADAPTER.evaluate(ACTIONS["giving_charity"], CONTEXT)
        assert score > 0.8, f"giving_charity score {score:.4f} should be > 0.8"

    def test_zakat_approved(self):
        action = {"subject": "zakat", "description": "Obligatory almsgiving"}
        score = ADAPTER.evaluate(action, CONTEXT)
        assert score > 0.8, f"zakat score {score:.4f} should be > 0.8"


# ── Scoring: vice cases ─────────────────────────────────────────────────────

class TestViceScores:

    def test_riba_rejected(self):
        """Greed + injustice (excessive interest) → score < 0.3."""
        score = ADAPTER.evaluate(ACTIONS["riba"], CONTEXT)
        assert score < 0.3, f"riba score {score:.4f} should be < 0.3"

    def test_lying_for_gain_rejected(self):
        """Dishonesty for personal gain → score < 0.3."""
        score = ADAPTER.evaluate(ACTIONS["lying_gain"], CONTEXT)
        assert score < 0.3, f"lying_gain score {score:.4f} should be < 0.3"

    def test_fraud_rejected(self):
        action = {"subject": "fraud", "description": "Commit fraud"}
        score = ADAPTER.evaluate(action, CONTEXT)
        assert score < 0.2, f"fraud score {score:.4f} should be < 0.2"

    def test_theft_rejected(self):
        action = {"subject": "theft", "description": "Take property by force"}
        score = ADAPTER.evaluate(action, CONTEXT)
        assert score < 0.2, f"theft score {score:.4f} should be < 0.2"


# ── Phronesis / contested mean ──────────────────────────────────────────────

class TestPhronesisContestedMean:

    def test_lie_to_save_contested(self):
        """
        Lying to save a life: honesty vs compassion — both are virtues.
        Phronesis recognises genuine moral tension → 0.4 < score < 0.7.
        """
        score = ADAPTER.evaluate(ACTIONS["lie_to_save"], CONTEXT)
        assert 0.4 < score < 0.7, (
            f"lie_to_save score {score:.4f} should be in contested range (0.4, 0.7). "
            "Honesty and compassion are both virtues — this must stay contested."
        )

    def test_lie_to_save_not_too_high(self):
        """Virtue ethics must NOT fully approve lying even for good reasons."""
        score = ADAPTER.evaluate(ACTIONS["lie_to_save"], CONTEXT)
        assert score < 0.7, (
            f"lie_to_save score {score:.4f} must be < 0.7 to keep ConsensusEngine CONTESTED"
        )

    def test_lie_to_save_not_too_low(self):
        """Compassion is a genuine virtue — lie_to_save must not score as pure vice."""
        score = ADAPTER.evaluate(ACTIONS["lie_to_save"], CONTEXT)
        assert score > 0.4, (
            f"lie_to_save score {score:.4f} must be > 0.4; compassion has genuine weight"
        )


# ── Score range invariant ───────────────────────────────────────────────────

class TestScoreRange:

    def test_score_in_range_for_all_actions(self):
        """All ACTIONS must produce a score in [0.0, 1.0]."""
        for name, action in ACTIONS.items():
            score = ADAPTER.evaluate(action, CONTEXT)
            assert 0.0 <= score <= 1.0, (
                f"Action '{name}' produced out-of-range score: {score}"
            )

    def test_non_dict_action_returns_mid_score(self):
        """Non-dict input should return 0.5 (safe default)."""
        score = ADAPTER.evaluate("some string", CONTEXT)
        assert score == 0.5

    def test_empty_action_returns_default(self):
        score = ADAPTER.evaluate({}, CONTEXT)
        assert 0.0 <= score <= 1.0


# ── resolve_conflict ────────────────────────────────────────────────────────

class TestResolveConflict:

    def test_higher_strength_wins(self):
        norm_a = {"id": "justice", "type": "obligatory", "strength": 1.0}
        norm_b = {"id": "courage", "type": "obligatory", "strength": 0.8}
        result = ADAPTER.resolve_conflict(norm_a, norm_b)
        assert result["id"] == "justice"

    def test_virtue_beats_vice_at_equal_strength(self):
        virtue = {"id": "honesty", "type": "obligatory", "strength": 0.9}
        vice   = {"id": "vice_prohibition", "type": "prohibited", "strength": 0.9}
        result = ADAPTER.resolve_conflict(virtue, vice)
        assert result["type"] == "obligatory"

    def test_higher_strength_vice_wins_over_weaker_virtue(self):
        """Strength is the primary criterion — higher always wins."""
        weak_virtue  = {"id": "laziness_norm", "type": "obligatory", "strength": 0.3}
        strong_vice  = {"id": "extreme_prohibition", "type": "prohibited", "strength": 0.95}
        result = ADAPTER.resolve_conflict(weak_virtue, strong_vice)
        assert result["strength"] == 0.95


# ── 4-tradition ConsensusEngine integration ─────────────────────────────────

class TestFourTraditionEngine:

    @pytest.fixture
    def four_engine(self):
        """ConsensusEngine with all 4 traditions at equal weight."""
        from nomos.traditions.islamic_adapter import IslamicTraditionAdapter
        from nomos.traditions.utilitarian_adapter import UtilitarianAdapter
        from nomos.traditions.kantian_adapter import KantianAdapter

        engine = ConsensusEngine()
        engine.register("islamic",       IslamicTraditionAdapter(), weight=1.0)
        engine.register("utilitarian",   UtilitarianAdapter(),       weight=1.0)
        engine.register("kantian",       KantianAdapter(),            weight=1.0)
        engine.register("virtue_ethics", VirtueEthicsAdapter(),       weight=1.0)
        return engine

    def test_four_tradition_engine_has_virtue(self, four_engine):
        """Engine must contain virtue_ethics tradition."""
        assert "virtue_ethics" in four_engine._adapters

    def test_four_tradition_engine_has_four_traditions(self, four_engine):
        assert len(four_engine._adapters) == 4

    def test_four_tradition_trade_approved(self, four_engine):
        """Fair trade should still be APPROVED with 4 traditions."""
        report = four_engine.evaluate(ACTIONS["trade"], CONTEXT)
        assert report.verdict == "APPROVED", (
            f"4-tradition engine should APPROVE fair trade. "
            f"Got {report.verdict}, mean={report.weighted_mean:.2f}"
        )

    def test_four_tradition_riba_rejected_or_contested(self, four_engine):
        """Riba should still be REJECTED or CONTESTED with 4 traditions."""
        report = four_engine.evaluate(ACTIONS["riba"], CONTEXT)
        assert report.verdict in ("REJECTED", "CONTESTED"), (
            f"4-tradition engine: riba expected REJECTED/CONTESTED. "
            f"Got {report.verdict}, mean={report.weighted_mean:.2f}"
        )

    def test_four_tradition_lie_to_save_contested(self, four_engine):
        """
        lie_to_save: Utilitarian≈0.55, Kantian≈0.04, Islamic≈0.65, VirtueEthics≈0.55
        Combined: HIGH conflict → CONTESTED.
        """
        report = four_engine.evaluate(ACTIONS["lie_to_save"], CONTEXT)
        assert report.verdict == "CONTESTED", (
            f"4-tradition lie_to_save must be CONTESTED. "
            f"Got {report.verdict}. Scores: "
            + ", ".join(f"{ts.tradition}={ts.score:.2f}" for ts in report.tradition_scores)
        )

    def test_four_tradition_virtue_score_in_report(self, four_engine):
        """virtue_ethics score must appear in the ConsensusReport."""
        report = four_engine.evaluate(ACTIONS["trade"], CONTEXT)
        traditions = {ts.tradition for ts in report.tradition_scores}
        assert "virtue_ethics" in traditions

    def test_four_tradition_weights_sum_to_one(self, four_engine):
        report = four_engine.evaluate(ACTIONS["trade"], CONTEXT)
        total = sum(ts.weight for ts in report.tradition_scores)
        assert abs(total - 1.0) < 1e-9

    def test_four_tradition_all_scores_in_range(self, four_engine):
        for name, action in ACTIONS.items():
            report = four_engine.evaluate(action, CONTEXT)
            for ts in report.tradition_scores:
                assert 0.0 <= ts.score <= 1.0, (
                    f"Action '{name}', tradition '{ts.tradition}': "
                    f"score {ts.score} out of [0,1]"
                )
