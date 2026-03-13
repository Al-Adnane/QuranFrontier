"""Tests for ComplianceOS and MultiTraditionCompliance.

Run with:
    cd /Users/mac/Desktop/QuranFrontier
    python3 -m pytest nomos/tests/test_complianceos.py -v
"""

import sys
import os

# Ensure project root is on path
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest

from nomos.products.complianceos import ComplianceOS, ComplianceReport
from nomos.products.complianceos.multi_tradition import (
    MultiTraditionCompliance,
    MultiReport,
    TraditionResult,
)


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def cos():
    """Fresh ComplianceOS instance."""
    return ComplianceOS()


@pytest.fixture
def mtc():
    """MultiTraditionCompliance with all three adapters loaded."""
    return MultiTraditionCompliance()


# ── Test 1: Single obligatory norm, matching action → compliant ────────────

def test_single_norm_satisfiable(cos):
    """One obligatory norm matching the action → compliant with high score."""
    cos.add_norm(
        norm_id="prayer_obligation",
        norm_type="obligatory",
        condition="action.subject == 'salah'",
        strength=1.0,
        jurisdiction="islamic",
    )

    action = {"subject": "salah", "description": "performing daily prayer"}
    report = cos.check(action)

    assert isinstance(report, ComplianceReport)
    assert report.is_compliant is True
    assert report.score >= 0.5
    assert "prayer_obligation" in report.satisfied_norms
    assert report.violated_norms == []


# ── Test 2: Conflicting norms (wajib + haram) detected ────────────────────

def test_conflicting_norms_detected(cos):
    """Obligatory norm + prohibited norm on same subject → conflict detected."""
    cos.add_norm(
        norm_id="trade_obligation",
        norm_type="obligatory",
        condition="action.subject == 'riba'",
        strength=1.0,
        jurisdiction="custom",
    )
    cos.add_norm(
        norm_id="riba_prohibition",
        norm_type="prohibited",
        condition="action.subject == 'riba'",
        strength=1.0,
        jurisdiction="islamic",
    )

    action = {"subject": "riba"}
    report = cos.check(action)

    # Both norms match → conflict must be detected
    assert len(report.conflicts) > 0
    conflict_norm_ids = {
        nid
        for c in report.conflicts
        for nid in (c["norm_a"], c["norm_b"])
    }
    assert "trade_obligation" in conflict_norm_ids
    assert "riba_prohibition" in conflict_norm_ids
    # Conflict type should be recognised as wajib/haram or strong
    assert report.conflicts[0]["type"] in ("wajib_haram_conflict", "strong_conflict")


# ── Test 3: Multi-tradition riba check → contested ────────────────────────

def test_multi_tradition_riba_contested(mtc):
    """Riba (interest-based lending): Islamic rejects, others may approve/differ.

    Expected: CONTESTED (Islamic clearly rejects; utilitarian/kantian may differ).
    """
    # Riba: many harmed_parties, high intensity — typically utilitarian dislikes too
    action = {
        "subject": "riba",
        "description": "charging interest on loans",
        "beneficiaries": 1,
        "harmed_parties": 5,
        "intensity": 2.0,
        "certainty": 0.9,
        "reversible": False,
    }
    report = mtc.check(action)

    assert isinstance(report, MultiReport)
    # Islamic must reject riba
    islamic_result = report.per_tradition.get("islamic")
    assert islamic_result is not None
    assert islamic_result.is_compliant is False, (
        f"Expected Islamic to reject riba but score was {islamic_result.score}"
    )
    # Consensus should be CONTESTED or REJECTED (not all-approve)
    assert report.consensus in ("CONTESTED", "REJECTED"), (
        f"Expected CONTESTED or REJECTED for riba, got {report.consensus}"
    )
    # At least one tradition rejects
    assert len(report.rejecting_traditions) >= 1


# ── Test 4: Multi-tradition fair trade → approved ─────────────────────────

def test_multi_tradition_trade_approved(mtc):
    """Fair trade: beneficial to many, honest, universalizable → all approve."""
    action = {
        "subject": "trade",
        "description": "engaging in fair trade with mutual consent",
        "beneficiaries": 10,
        "harmed_parties": 0,
        "intensity": 1.0,
        "certainty": 0.9,
        "reversible": True,
        "maxim": "I will trade fairly with others",
    }
    report = mtc.check(action)

    assert isinstance(report, MultiReport)
    # All traditions should approve fair trade
    assert report.consensus == "APPROVED", (
        f"Expected APPROVED for fair trade, got {report.consensus}. "
        f"Per-tradition scores: {[(k, v.score) for k, v in report.per_tradition.items()]}"
    )
    assert len(report.approving_traditions) == 3


# ── Test 5: Conflict resolved with "temporal" strategy ────────────────────

def test_resolution_strategy_applied(cos):
    """Add two conflicting norms; resolve with 'temporal' → later norm wins."""
    cos.add_norm(
        norm_id="old_norm",
        norm_type="obligatory",
        condition="action.subject == 'riba'",
        strength=1.0,
        jurisdiction="historical",
    )
    cos.add_norm(
        norm_id="new_norm",
        norm_type="prohibited",
        condition="action.subject == 'riba'",
        strength=1.0,
        jurisdiction="islamic",
    )

    # "temporal" strategy: later-registered norm (new_norm) wins
    winner = cos.resolve_conflict("old_norm", "new_norm", strategy="temporal")
    assert winner == "new_norm", f"Expected 'new_norm' to win temporally, got '{winner}'"

    # "strength" strategy: both are 1.0 → first (old_norm) wins on tie
    winner_strength = cos.resolve_conflict("old_norm", "new_norm", strategy="strength")
    assert winner_strength == "old_norm", (
        f"Expected 'old_norm' on strength tie (first registered), got '{winner_strength}'"
    )

    # Verify the check result references a resolution strategy hint
    action = {"subject": "riba"}
    report = cos.check(action)
    assert report.conflicts, "Expected conflicts to be detected"
    assert report.resolution_strategy is not None


# ── Bonus test: reset clears all norms ────────────────────────────────────

def test_reset_clears_norms(cos):
    """reset() removes all registered norms."""
    cos.add_norm("n1", "obligatory", "true", 1.0)
    assert len(cos._norms) == 1
    cos.reset()
    assert len(cos._norms) == 0
    report = cos.check({"subject": "anything"})
    assert report.is_compliant is True  # No norms → default permissible
    assert report.confidence == 0.0     # Zero confidence when no norms


# ── Bonus test: necessity override ────────────────────────────────────────

def test_necessity_override(cos):
    """Prohibition + necessity → compliance elevated."""
    cos.add_norm(
        norm_id="pork_ban",
        norm_type="prohibited",
        condition="action.subject == 'pork'",
        strength=1.0,
        jurisdiction="islamic",
    )
    action = {
        "subject": "pork",
        "description": "eating pork to save life from starvation — necessity",
    }
    report = cos.check(action)
    # Necessity should elevate score above 0
    assert report.score > 0.0
    assert "necessity_override" in report.details
    assert report.details["necessity_override"] is True
