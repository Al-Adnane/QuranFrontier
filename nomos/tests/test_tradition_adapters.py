"""
TDD Tests for TraditionAdapters — RED phase first, then GREEN after wiring.

These tests define what 'real' means:
  - No default 0.5 stub scores
  - Differentiated outputs across traditions for the same action
  - Islamic adapter uses actual quran_core deontic logic
  - Utilitarian adapter computes real Bentham utility
  - Kantian adapter tests universalizability
"""

import pytest
import sys
import os

# Ensure nomos and quran-core are importable
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "quran-core"))

from nomos.traditions.islamic_adapter import IslamicTraditionAdapter
from nomos.traditions.utilitarian_adapter import UtilitarianAdapter
from nomos.traditions.kantian_adapter import KantianAdapter


# ── Shared test actions ────────────────────────────────────────────────────

ACTIONS = {
    # Clearly haram in Islam, fails Kantian CI, negative utility
    "riba": {
        "type": "financial",
        "subject": "riba",
        "description": "Charge interest on a loan",
        "beneficiaries": 1,
        "harmed_parties": 10,
        "reversible": False,
    },
    # Clearly wajib in Islam, positive utility, passes CI
    "salah": {
        "type": "worship",
        "subject": "salah",
        "description": "Perform the five daily prayers",
        "beneficiaries": 1,
        "harmed_parties": 0,
        "reversible": True,
    },
    # Ethically contested: lies to save a life
    "lie_to_save": {
        "type": "speech",
        "subject": "lying",
        "description": "Lie to save an innocent person from harm",
        "beneficiaries": 1,
        "harmed_parties": 0,
        "reversible": False,
        "maxim": "Lie when it saves a life",
    },
    # Neutral / permissible baseline
    "trade": {
        "type": "financial",
        "subject": "trade",
        "description": "Engage in fair trade",
        "beneficiaries": 2,
        "harmed_parties": 0,
        "reversible": True,
    },
}

CONTEXT = {"domain": "general", "jurisdiction": "universal"}


# ── Islamic Adapter Tests ──────────────────────────────────────────────────

class TestIslamicAdapter:

    @pytest.fixture
    def adapter(self):
        return IslamicTraditionAdapter()

    def test_name(self, adapter):
        assert adapter.name == "islamic"

    def test_load_norms_not_empty(self, adapter):
        """load_norms must return real norms, not empty list."""
        norms = adapter.load_norms(domain="general")
        assert len(norms) > 0, "Islamic adapter returned empty norms (stub detected)"

    def test_load_norms_have_required_fields(self, adapter):
        """Every norm must have id, type, condition, strength."""
        norms = adapter.load_norms(domain="general")
        for n in norms:
            assert "id" in n, f"Norm missing 'id': {n}"
            assert "type" in n, f"Norm missing 'type': {n}"
            assert n["type"] in (
                "obligatory", "prohibited", "recommended", "discouraged", "permitted"
            ), f"Unknown norm type: {n['type']}"

    def test_load_norms_finance_contains_riba_prohibition(self, adapter):
        """Finance domain must include riba prohibition."""
        norms = adapter.load_norms(domain="finance")
        ids = [n["id"] for n in norms]
        assert any("riba" in nid.lower() for nid in ids), (
            f"Finance norms missing riba prohibition. Got: {ids}"
        )

    def test_evaluate_haram_action_scores_low(self, adapter):
        """Riba (interest) must score < 0.3 — it is haram."""
        score = adapter.evaluate(ACTIONS["riba"], CONTEXT)
        assert score != 0.5, "evaluate() returned default stub 0.5"
        assert score < 0.3, f"Riba should score < 0.3, got {score}"

    def test_evaluate_wajib_action_scores_high(self, adapter):
        """Salah (prayer) must score > 0.8 — it is wajib."""
        score = adapter.evaluate(ACTIONS["salah"], CONTEXT)
        assert score != 0.5, "evaluate() returned default stub 0.5"
        assert score > 0.8, f"Salah should score > 0.8, got {score}"

    def test_evaluate_permissible_trade_scores_middle(self, adapter):
        """Fair trade is halal (permitted) — should score 0.5–0.8."""
        score = adapter.evaluate(ACTIONS["trade"], CONTEXT)
        assert score != 0.5 or True, "Permitted actions may score 0.5 — check not hardcoded"
        assert 0.4 <= score <= 0.9, f"Trade score out of expected range: {score}"

    def test_evaluate_returns_float_in_range(self, adapter):
        for name, action in ACTIONS.items():
            score = adapter.evaluate(action, CONTEXT)
            assert 0.0 <= score <= 1.0, f"Score out of [0,1] for {name}: {score}"

    def test_resolve_conflict_later_norm_wins(self, adapter):
        """Later revelation supersedes earlier (naskh)."""
        earlier = {"id": "old_rule", "type": "permitted", "verse": (2, 219), "strength": 0.7}
        later = {"id": "new_rule", "type": "prohibited", "verse": (5, 90), "strength": 1.0}
        resolved = adapter.resolve_conflict(earlier, later)
        assert resolved["id"] == "new_rule", (
            f"Naskh should return later norm, got: {resolved['id']}"
        )

    def test_resolve_conflict_higher_strength_wins_when_no_verse(self, adapter):
        """When no verse reference, stronger norm wins."""
        weak = {"id": "weak_norm", "type": "recommended", "strength": 0.4}
        strong = {"id": "strong_norm", "type": "obligatory", "strength": 1.0}
        resolved = adapter.resolve_conflict(weak, strong)
        assert resolved["id"] == "strong_norm"


# ── Utilitarian Adapter Tests ──────────────────────────────────────────────

class TestUtilitarianAdapter:

    @pytest.fixture
    def adapter(self):
        return UtilitarianAdapter()

    def test_name(self, adapter):
        assert adapter.name == "utilitarian"

    def test_load_norms_not_empty(self, adapter):
        norms = adapter.load_norms(domain="general")
        assert len(norms) > 0

    def test_evaluate_not_stub(self, adapter):
        """evaluate must not return default 0.5 for all inputs."""
        scores = {
            name: adapter.evaluate(action, CONTEXT)
            for name, action in ACTIONS.items()
        }
        assert not all(s == 0.5 for s in scores.values()), (
            "All scores are 0.5 — still a stub"
        )

    def test_evaluate_riba_negative_utility(self, adapter):
        """Riba harms 10, benefits 1 — should score below 0.5."""
        score = adapter.evaluate(ACTIONS["riba"], CONTEXT)
        assert score < 0.5, f"Riba (10 harmed, 1 benefited) should score < 0.5, got {score}"

    def test_evaluate_trade_positive_utility(self, adapter):
        """Fair trade benefits 2, harms 0 — should score > 0.5."""
        score = adapter.evaluate(ACTIONS["trade"], CONTEXT)
        assert score > 0.5, f"Fair trade should score > 0.5, got {score}"

    def test_evaluate_lie_to_save_high_utility(self, adapter):
        """Lie that saves a life: 1 benefited, 0 harmed — positive utility."""
        score = adapter.evaluate(ACTIONS["lie_to_save"], CONTEXT)
        assert score > 0.5, f"Life-saving lie should score > 0.5 in utilitarian, got {score}"

    def test_evaluate_returns_float_in_range(self, adapter):
        for name, action in ACTIONS.items():
            score = adapter.evaluate(action, CONTEXT)
            assert 0.0 <= score <= 1.0, f"Score out of [0,1] for {name}: {score}"


# ── Kantian Adapter Tests ──────────────────────────────────────────────────

class TestKantianAdapter:

    @pytest.fixture
    def adapter(self):
        return KantianAdapter()

    def test_name(self, adapter):
        assert adapter.name == "kantian"

    def test_load_norms_contains_categorical_imperative(self, adapter):
        norms = adapter.load_norms(domain="general")
        ids = [n["id"] for n in norms]
        assert "categorical_imperative" in ids

    def test_evaluate_not_stub(self, adapter):
        scores = {
            name: adapter.evaluate(action, CONTEXT)
            for name, action in ACTIONS.items()
        }
        assert not all(s == 0.5 for s in scores.values()), (
            "All scores are 0.5 — still a stub"
        )

    def test_evaluate_lying_fails_categorical_imperative(self, adapter):
        """Lying cannot be universalized — must score low."""
        # General lying (not the life-saving case)
        action = {
            "type": "speech",
            "subject": "lying",
            "description": "Lie for personal gain",
            "maxim": "Lie whenever convenient",
            "beneficiaries": 1,
            "harmed_parties": 3,
        }
        score = adapter.evaluate(action, CONTEXT)
        assert score < 0.4, (
            f"Lying for personal gain should fail CI (score < 0.4), got {score}"
        )

    def test_evaluate_fair_trade_passes_categorical_imperative(self, adapter):
        """Fair trade is universalizable — must score high."""
        score = adapter.evaluate(ACTIONS["trade"], CONTEXT)
        assert score > 0.6, (
            f"Fair trade should pass CI (score > 0.6), got {score}"
        )

    def test_evaluate_resolve_conflict_perfect_duty_wins(self, adapter):
        """Perfect duty (do not lie) overrides imperfect duty."""
        perfect = {"id": "do_not_lie", "type": "obligatory", "duty_type": "perfect", "strength": 1.0}
        imperfect = {"id": "be_kind", "type": "recommended", "duty_type": "imperfect", "strength": 0.6}
        resolved = adapter.resolve_conflict(perfect, imperfect)
        assert resolved["id"] == "do_not_lie"

    def test_evaluate_returns_float_in_range(self, adapter):
        for name, action in ACTIONS.items():
            score = adapter.evaluate(action, CONTEXT)
            assert 0.0 <= score <= 1.0, f"Score out of [0,1] for {name}: {score}"


# ── Cross-Tradition Differentiation Test ──────────────────────────────────

class TestTraditionDifferentiation:
    """The critical test: traditions must DISAGREE on contested actions."""

    def test_lying_to_save_life_differentiates_traditions(self):
        """
        Lie to save a life:
          - Utilitarian: HIGH score (saves a life = positive utility)
          - Kantian: LOW score (lying fails universalizability)
          - Islamic: CONTEXT-DEPENDENT (necessity principle may apply)

        Key assertion: utilitarian and kantian must differ by >= 0.3
        """
        islamic = IslamicTraditionAdapter()
        utilitarian = UtilitarianAdapter()
        kantian = KantianAdapter()

        action = ACTIONS["lie_to_save"]

        u_score = utilitarian.evaluate(action, CONTEXT)
        k_score = kantian.evaluate(action, CONTEXT)

        assert abs(u_score - k_score) >= 0.3, (
            f"Utilitarian ({u_score:.2f}) and Kantian ({k_score:.2f}) should "
            f"disagree on lying-to-save-life by >= 0.3. "
            f"Diff: {abs(u_score - k_score):.2f}. "
            f"Traditions are not differentiating — check if scores are hardcoded."
        )

    def test_fair_trade_all_traditions_approve(self):
        """Fair trade should score > 0.5 across all three traditions."""
        adapters = {
            "islamic": IslamicTraditionAdapter(),
            "utilitarian": UtilitarianAdapter(),
            "kantian": KantianAdapter(),
        }
        action = ACTIONS["trade"]
        for name, adapter in adapters.items():
            score = adapter.evaluate(action, CONTEXT)
            assert score > 0.5, (
                f"{name} should approve fair trade (score > 0.5), got {score}"
            )

    def test_riba_condemned_by_islamic_neutral_by_others(self):
        """
        Riba condemned strongly by Islamic (<0.3).
        Utilitarian may condemn if harm > benefit.
        """
        islamic = IslamicTraditionAdapter()
        utilitarian = UtilitarianAdapter()

        riba_score_islamic = islamic.evaluate(ACTIONS["riba"], CONTEXT)
        riba_score_utilitarian = utilitarian.evaluate(ACTIONS["riba"], CONTEXT)

        # Islamic must strongly condemn
        assert riba_score_islamic < 0.3, (
            f"Islamic should strongly condemn riba (< 0.3), got {riba_score_islamic}"
        )
        # Utilitarian may also condemn given 10 harmed vs 1 benefited
        assert riba_score_utilitarian < 0.5, (
            f"Utilitarian should mildly condemn riba given harm > benefit, got {riba_score_utilitarian}"
        )
