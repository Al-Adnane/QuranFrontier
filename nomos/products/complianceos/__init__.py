"""ComplianceOS — Universal Regulatory Compliance Engine.

Wraps SMTDeonticSolver + tradition adapters into a single compliance API.

Usage:
    cos = ComplianceOS()
    cos.add_norm("riba_ban", "prohibited", "action.subject == 'riba'", 1.0, "islamic")
    report = cos.check({"subject": "riba"})
    print(report.is_compliant)  # False
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Wire to project root so nomos.* imports work
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from nomos.reasoning.advanced_solvers.smt_solver import (
    SMTDeonticSolver,
    DeonticStatus,
)

# ── Deontic strength constants ─────────────────────────────────────────────
_TYPE_TO_STRENGTH: Dict[str, float] = {
    "obligatory":  1.0,
    "recommended": 0.75,
    "permitted":   0.5,
    "discouraged": 0.25,
    "prohibited":  0.0,
    # Islamic aliases
    "wajib":     1.0,
    "mustahabb": 0.75,
    "mubah":     0.5,
    "makruh":    0.25,
    "haram":     0.0,
}

_TYPE_TO_DEONTIC: Dict[str, DeonticStatus] = {
    "obligatory":  DeonticStatus.WAJIB,
    "wajib":       DeonticStatus.WAJIB,
    "recommended": DeonticStatus.MUSTAHABB,
    "mustahabb":   DeonticStatus.MUSTAHABB,
    "permitted":   DeonticStatus.MUBAH,
    "mubah":       DeonticStatus.MUBAH,
    "discouraged": DeonticStatus.MAKRUH,
    "makruh":      DeonticStatus.MAKRUH,
    "prohibited":  DeonticStatus.HARAM,
    "haram":       DeonticStatus.HARAM,
}

RESOLUTION_STRATEGIES = {
    "temporal",   # later norm supersedes earlier
    "strength",   # higher-strength norm wins
    "jurisdiction",  # local jurisdiction overrides general
    "necessity",  # necessity (darura) can override prohibition
}


@dataclass
class NormEntry:
    """An internal norm record."""
    norm_id: str
    norm_type: str          # "obligatory", "prohibited", etc.
    condition: str          # Condition expression string
    strength: float         # Deontic strength [0, 1]
    jurisdiction: str       # e.g., "islamic", "kantian", "general"
    topic: str = ""         # Derived topic key for conflict detection
    order: int = 0          # Insertion order (for temporal strategy)


@dataclass
class ComplianceReport:
    """Result of a compliance check."""
    is_compliant: bool
    score: float                        # 0.0 = fully non-compliant, 1.0 = fully compliant
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    resolution_strategy: Optional[str] = None
    confidence: float = 1.0
    violated_norms: List[str] = field(default_factory=list)
    satisfied_norms: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class ComplianceOS:
    """SMT-backed compliance engine for any normative framework.

    Lifecycle:
        1. add_norm(...) — register norms from any source
        2. check(action) — run SMT satisfiability + score
        3. resolve_conflict(a, b, strategy) — pick winning norm

    The SMTDeonticSolver detects wajib/haram conflicts (strength delta > 0.7)
    automatically.  ComplianceOS wraps that with higher-level scoring logic.
    """

    COMPLIANCE_THRESHOLD = 0.5  # score >= 0.5 → compliant

    def __init__(self):
        self._norms: Dict[str, NormEntry] = {}
        self._insertion_counter = 0
        self._solver = SMTDeonticSolver()

    # ── Norm Management ────────────────────────────────────────────────────

    def add_norm(
        self,
        norm_id: str,
        norm_type: str,
        condition: str,
        strength: float,
        jurisdiction: str = "general",
    ) -> None:
        """Register a norm.

        Args:
            norm_id:      Unique identifier (e.g. "riba_ban").
            norm_type:    "obligatory" | "prohibited" | "permitted" |
                          "recommended" | "discouraged" (or Islamic aliases).
            condition:    String condition expression (used for matching).
            strength:     Deontic strength override [0, 1]. If -1, inferred
                          from norm_type.
            jurisdiction: Tradition source (e.g. "islamic", "kantian").
        """
        if strength < 0:
            strength = _TYPE_TO_STRENGTH.get(norm_type.lower(), 0.5)

        # Derive topic key from condition (e.g. "action.subject == 'riba'" → "riba")
        topic = self._extract_topic(condition) or norm_id

        entry = NormEntry(
            norm_id=norm_id,
            norm_type=norm_type.lower(),
            condition=condition,
            strength=strength,
            jurisdiction=jurisdiction,
            topic=topic,
            order=self._insertion_counter,
        )
        self._norms[norm_id] = entry
        self._insertion_counter += 1

        # Register with SMT solver
        deontic_status = _TYPE_TO_DEONTIC.get(norm_type.lower(), DeonticStatus.MUBAH)
        self._solver.add_deontic_status(
            ruling=(norm_id, topic),
            status=deontic_status,
            confidence=min(1.0, strength),
        )

    def load_norms_from_adapter(self, adapter: Any, domain: str = "general") -> int:
        """Load all norms from a TraditionAdapter.

        Returns number of norms loaded.
        """
        norms = adapter.load_norms(domain)
        for n in norms:
            self.add_norm(
                norm_id=n["id"],
                norm_type=n.get("type", "permitted"),
                condition=n.get("condition", "true"),
                strength=n.get("strength", 0.5),
                jurisdiction=adapter.name,
            )
        return len(norms)

    # ── Compliance Check ───────────────────────────────────────────────────

    def check(self, action: Any) -> ComplianceReport:
        """Run compliance check for an action.

        Args:
            action: dict with at least {"subject": str} or a plain string.

        Returns:
            ComplianceReport
        """
        subject = self._get_subject(action)
        description = (action.get("description", "") if isinstance(action, dict) else "").lower()
        necessity = any(w in description for w in ("save", "necessity", "emergency", "life", "starving"))

        if not self._norms:
            return ComplianceReport(
                is_compliant=True,
                score=1.0,
                confidence=0.0,
                details={"reason": "No norms registered"},
            )

        violated: List[str] = []
        satisfied: List[str] = []
        conflicts: List[Dict[str, Any]] = []

        # Evaluate each norm against the action
        total_weight = 0.0
        compliance_score = 0.0

        for norm_id, norm in self._norms.items():
            matches = self._norm_matches(norm, subject, action)
            if not matches:
                continue

            weight = norm.strength
            total_weight += weight

            if norm.norm_type in ("prohibited", "haram"):
                if necessity:
                    # Darura: necessity elevates haram to mubah
                    compliance_score += 0.5 * weight
                    satisfied.append(f"{norm_id} (necessity override)")
                else:
                    violated.append(norm_id)
                    # Non-compliant contribution
                    compliance_score += 0.0
            elif norm.norm_type in ("obligatory", "wajib"):
                satisfied.append(norm_id)
                compliance_score += 1.0 * weight
            elif norm.norm_type in ("recommended", "mustahabb"):
                satisfied.append(norm_id)
                compliance_score += 0.85 * weight
            elif norm.norm_type in ("discouraged", "makruh"):
                violated.append(norm_id)
                compliance_score += 0.25 * weight
            else:
                # Permitted / mubah
                satisfied.append(norm_id)
                compliance_score += 0.65 * weight

        # Detect SMT-level conflicts among matched norms
        matched_norms = [n for n in self._norms.values() if self._norm_matches(n, subject, action)]
        conflicts = self._detect_conflicts(matched_norms)

        # Normalise score
        if total_weight > 0:
            final_score = compliance_score / total_weight
        else:
            # No norms matched → default permissible
            final_score = 0.65

        # SMT satisfiability check on the whole system
        smt_sat = self._solver.check_satisfiability()
        if not smt_sat and conflicts:
            # Unsatisfiable constraint system → lower confidence
            confidence = 0.6
        else:
            confidence = 0.95

        is_compliant = final_score >= self.COMPLIANCE_THRESHOLD

        # Determine resolution strategy hint
        resolution_strategy = None
        if conflicts:
            resolution_strategy = self._suggest_strategy(conflicts)

        return ComplianceReport(
            is_compliant=is_compliant,
            score=round(final_score, 4),
            conflicts=conflicts,
            resolution_strategy=resolution_strategy,
            confidence=confidence,
            violated_norms=violated,
            satisfied_norms=satisfied,
            details={
                "subject": subject,
                "total_norms_matched": len(matched_norms),
                "smt_satisfiable": smt_sat,
                "necessity_override": necessity,
            },
        )

    # ── Conflict Resolution ────────────────────────────────────────────────

    def resolve_conflict(
        self,
        norm_a_id: str,
        norm_b_id: str,
        strategy: str = "strength",
    ) -> Optional[str]:
        """Resolve a conflict between two norms.

        Args:
            norm_a_id: First norm ID.
            norm_b_id: Second norm ID.
            strategy:  "temporal" | "strength" | "jurisdiction" | "necessity"

        Returns:
            Winner norm ID, or None if both norms are unknown.
        """
        norm_a = self._norms.get(norm_a_id)
        norm_b = self._norms.get(norm_b_id)

        if norm_a is None and norm_b is None:
            return None
        if norm_a is None:
            return norm_b_id
        if norm_b is None:
            return norm_a_id

        if strategy == "temporal":
            # Later-registered norm wins (naskh: later abrogates earlier)
            return norm_b_id if norm_b.order >= norm_a.order else norm_a_id

        elif strategy == "strength":
            return norm_a_id if norm_a.strength >= norm_b.strength else norm_b_id

        elif strategy == "jurisdiction":
            # Islamic jurisdiction overrides general; otherwise first registered wins
            if norm_a.jurisdiction == "islamic" and norm_b.jurisdiction != "islamic":
                return norm_a_id
            if norm_b.jurisdiction == "islamic" and norm_a.jurisdiction != "islamic":
                return norm_b_id
            # Same jurisdiction: fallback to strength
            return norm_a_id if norm_a.strength >= norm_b.strength else norm_b_id

        elif strategy == "necessity":
            # Prohibition bows to necessity — find the less restrictive norm
            if norm_a.norm_type in ("prohibited", "haram"):
                return norm_b_id
            if norm_b.norm_type in ("prohibited", "haram"):
                return norm_a_id
            return norm_a_id if norm_a.strength >= norm_b.strength else norm_b_id

        else:
            raise ValueError(f"Unknown strategy '{strategy}'. "
                             f"Valid: {RESOLUTION_STRATEGIES}")

    # ── Reset ──────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear all norms and reset the solver."""
        self._norms.clear()
        self._insertion_counter = 0
        self._solver.reset()

    # ── Private Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _get_subject(action: Any) -> str:
        if isinstance(action, dict):
            return action.get("subject", "").lower().replace(" ", "_")
        return str(action).lower().replace(" ", "_")

    @staticmethod
    def _extract_topic(condition: str) -> str:
        """Extract topic keyword from condition string.

        e.g. "action.subject == 'riba'" → "riba"
        """
        import re
        m = re.search(r"['\"]([a-zA-Z_]+)['\"]", condition)
        if m:
            return m.group(1)
        return ""

    @staticmethod
    def _norm_matches(norm: NormEntry, subject: str, action: Any) -> bool:
        """Evaluate whether a norm applies to the given action."""
        # Universal norms always match
        if norm.condition.strip() in ("true", "True", "1", ""):
            return True

        # Subject equality check
        if norm.topic and subject:
            if norm.topic == subject:
                return True
            # Partial match: subject contains topic keyword
            if norm.topic in subject or subject in norm.topic:
                return True

        # aggregate_utility / felicific conditions: match anything
        if "aggregate_utility" in norm.condition or "net_harm" in norm.condition:
            return True
        if "universalizable" in norm.condition or "treats_persons" in norm.condition:
            return True
        if "consistent_with" in norm.condition or "all_interests" in norm.condition:
            return True

        return False

    def _detect_conflicts(self, norms: List[NormEntry]) -> List[Dict[str, Any]]:
        """Find pairs of norms with contradictory deontic types or strengths."""
        # Norm types that are directly contradictory when paired
        _OBLIGATORY_TYPES = {"obligatory", "wajib", "recommended", "mustahabb"}
        _PROHIBITED_TYPES = {"prohibited", "haram", "discouraged", "makruh"}

        conflicts = []
        for i, a in enumerate(norms):
            for b in norms[i + 1:]:
                # Case 1: semantic contradiction — one obligatory, one prohibited
                a_obligatory = a.norm_type in _OBLIGATORY_TYPES
                b_obligatory = b.norm_type in _OBLIGATORY_TYPES
                a_prohibited = a.norm_type in _PROHIBITED_TYPES
                b_prohibited = b.norm_type in _PROHIBITED_TYPES

                is_type_conflict = (a_obligatory and b_prohibited) or (a_prohibited and b_obligatory)

                # Case 2: strength-based conflict (deontic distance > 0.7)
                strength_delta = abs(a.strength - b.strength)
                is_strength_conflict = strength_delta > 0.7

                if is_type_conflict or is_strength_conflict:
                    # Classify conflict severity
                    strong = (
                        (a.norm_type in ("obligatory", "wajib") and b.norm_type in ("prohibited", "haram"))
                        or (b.norm_type in ("obligatory", "wajib") and a.norm_type in ("prohibited", "haram"))
                    )
                    conflicts.append({
                        "norm_a": a.norm_id,
                        "norm_b": b.norm_id,
                        "topic": a.topic or b.topic,
                        "strength_a": a.strength,
                        "strength_b": b.strength,
                        "type": "wajib_haram_conflict" if strong else "strong_conflict",
                    })
        return conflicts

    @staticmethod
    def _suggest_strategy(conflicts: List[Dict[str, Any]]) -> str:
        """Suggest a resolution strategy based on conflict types."""
        for c in conflicts:
            if c["type"] == "wajib_haram_conflict":
                return "temporal"
        return "strength"

    def __repr__(self) -> str:
        return f"ComplianceOS(norms={len(self._norms)})"
