"""MultiTraditionCompliance — Run compliance across all three tradition adapters.

Usage:
    mtc = MultiTraditionCompliance()
    report = mtc.check({"subject": "riba", "beneficiaries": 0, "harmed_parties": 10})
    print(report.consensus)  # "REJECTED"
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Project root on sys.path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from nomos.traditions.islamic_adapter import IslamicTraditionAdapter
from nomos.traditions.utilitarian_adapter import UtilitarianAdapter
from nomos.traditions.kantian_adapter import KantianAdapter
from nomos.products.complianceos import ComplianceOS, ComplianceReport


# ── Per-tradition result ───────────────────────────────────────────────────

@dataclass
class TraditionResult:
    """Compliance result for a single tradition."""
    tradition: str
    score: float          # 0.0–1.0 from adapter.evaluate()
    is_compliant: bool    # score >= 0.5
    report: ComplianceReport
    norms_loaded: int


# ── Multi-tradition report ─────────────────────────────────────────────────

@dataclass
class MultiReport:
    """Aggregated compliance report across all traditions.

    consensus:
        "APPROVED"  — all tradition scores > 0.5
        "REJECTED"  — all tradition scores < 0.5
        "CONTESTED" — mixed (some approve, some reject)
    """
    action: Any
    per_tradition: Dict[str, TraditionResult] = field(default_factory=dict)
    consensus: str = "CONTESTED"        # "APPROVED" | "REJECTED" | "CONTESTED"
    consensus_score: float = 0.0        # mean of all tradition scores
    approving_traditions: List[str] = field(default_factory=list)
    rejecting_traditions: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


# ── MultiTraditionCompliance ───────────────────────────────────────────────

class MultiTraditionCompliance:
    """Load norms from Islamic, Utilitarian, and Kantian adapters and run
    compliance checks under each tradition independently.

    Each tradition gets its own isolated ComplianceOS instance so norm
    sets don't bleed between frameworks.
    """

    APPROVAL_THRESHOLD = 0.5

    def __init__(self, domain: str = "general"):
        self._domain = domain
        self._adapters = {
            "islamic":     IslamicTraditionAdapter(),
            "utilitarian": UtilitarianAdapter(),
            "kantian":     KantianAdapter(),
        }
        # Pre-build per-tradition ComplianceOS instances
        self._engines: Dict[str, ComplianceOS] = {}
        self._norms_loaded: Dict[str, int] = {}
        self._build_engines()

    def _build_engines(self) -> None:
        """Construct one ComplianceOS per tradition and load its norms."""
        for name, adapter in self._adapters.items():
            engine = ComplianceOS()
            n = engine.load_norms_from_adapter(adapter, self._domain)
            self._engines[name] = engine
            self._norms_loaded[name] = n

    def check(self, action: Any) -> MultiReport:
        """Run compliance under every tradition and aggregate.

        Args:
            action: dict or string describing the action.

        Returns:
            MultiReport with per-tradition breakdown and consensus.
        """
        per_tradition: Dict[str, TraditionResult] = {}
        approving: List[str] = []
        rejecting: List[str] = []
        total_score = 0.0

        for name, adapter in self._adapters.items():
            engine = self._engines[name]
            report = engine.check(action)

            # Use adapter.evaluate() as the authoritative score for this tradition
            # (it implements the tradition's native reasoning: deontic/felicific/CI)
            adapter_score = adapter.evaluate(action, context={})

            # Blend ComplianceOS structural score (0.3) with adapter native score (0.7)
            blended_score = 0.3 * report.score + 0.7 * adapter_score
            blended_score = round(max(0.0, min(1.0, blended_score)), 4)
            is_compliant = blended_score >= self.APPROVAL_THRESHOLD

            result = TraditionResult(
                tradition=name,
                score=blended_score,
                is_compliant=is_compliant,
                report=report,
                norms_loaded=self._norms_loaded[name],
            )
            per_tradition[name] = result
            total_score += blended_score

            if is_compliant:
                approving.append(name)
            else:
                rejecting.append(name)

        n_traditions = len(self._adapters)
        mean_score = total_score / n_traditions if n_traditions > 0 else 0.0

        # Consensus logic
        if len(approving) == n_traditions:
            consensus = "APPROVED"
        elif len(rejecting) == n_traditions:
            consensus = "REJECTED"
        else:
            consensus = "CONTESTED"

        return MultiReport(
            action=action,
            per_tradition=per_tradition,
            consensus=consensus,
            consensus_score=round(mean_score, 4),
            approving_traditions=approving,
            rejecting_traditions=rejecting,
            details={
                "domain": self._domain,
                "traditions_checked": list(self._adapters.keys()),
                "norms_per_tradition": dict(self._norms_loaded),
            },
        )

    def check_single_tradition(self, tradition: str, action: Any) -> TraditionResult:
        """Run compliance for a single named tradition.

        Args:
            tradition: "islamic" | "utilitarian" | "kantian"
            action:    Action dict or string.

        Returns:
            TraditionResult
        """
        if tradition not in self._engines:
            raise ValueError(f"Unknown tradition '{tradition}'. "
                             f"Available: {list(self._engines.keys())}")
        adapter = self._adapters[tradition]
        engine = self._engines[tradition]
        report = engine.check(action)
        adapter_score = adapter.evaluate(action, context={})
        blended = round(0.3 * report.score + 0.7 * adapter_score, 4)
        return TraditionResult(
            tradition=tradition,
            score=blended,
            is_compliant=blended >= self.APPROVAL_THRESHOLD,
            report=report,
            norms_loaded=self._norms_loaded[tradition],
        )

    def reload(self, domain: str = "general") -> None:
        """Reload all engines (useful after changing domain)."""
        self._domain = domain
        self._engines.clear()
        self._norms_loaded.clear()
        self._build_engines()

    def __repr__(self) -> str:
        return (f"MultiTraditionCompliance(traditions={list(self._adapters.keys())}, "
                f"domain={self._domain!r})")
