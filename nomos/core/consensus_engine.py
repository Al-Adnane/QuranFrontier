"""
ConsensusEngine — Multi-tradition meta-evaluator for NOMOS.

Synthesizes scores across all loaded TraditionAdapters into a single
CalibratedMetaOutput with:
  - Weighted tradition scores
  - Conflict detection (KL-divergence / std-based)
  - Consensus verdict: APPROVED / REJECTED / CONTESTED
  - Confidence calibration per tradition
  - Disagreement explanation (which traditions conflict and why)

Conflict levels:
  LOW     — std < 0.15   — traditions largely agree
  MEDIUM  — std 0.15–0.3 — meaningful disagreement
  HIGH    — std > 0.3    — strong moral conflict

Verdict:
  APPROVED   — weighted_mean > 0.6 AND conflict < HIGH
  REJECTED   — weighted_mean < 0.4
  CONTESTED  — conflict HIGH or weighted_mean in [0.4, 0.6]
"""

import math
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from nomos.interfaces.protocols import TraditionAdapter


@dataclass
class TraditionScore:
    tradition: str
    score: float           # 0.0–1.0
    weight: float          # contribution weight (sums to 1.0 across all)
    norms_loaded: int      # number of norms from this tradition


@dataclass
class ConsensusReport:
    action: Any
    tradition_scores: List[TraditionScore]
    weighted_mean: float
    std_dev: float
    conflict_level: str          # "LOW" | "MEDIUM" | "HIGH"
    verdict: str                 # "APPROVED" | "REJECTED" | "CONTESTED"
    confidence: float            # 0.0–1.0 (high when traditions agree)
    dissenting_traditions: List[str]   # traditions that diverge from consensus
    supporting_traditions: List[str]
    explanation: str


def _kl_divergence(p: float, q: float, eps: float = 1e-9) -> float:
    """KL divergence between two Bernoulli distributions."""
    p = max(eps, min(1 - eps, p))
    q = max(eps, min(1 - eps, q))
    return p * math.log(p / q) + (1 - p) * math.log((1 - p) / (1 - q))


class ConsensusEngine:
    """
    Runs an action through multiple TraditionAdapters and synthesizes
    a consensus verdict with conflict detection.

    Usage:
        engine = ConsensusEngine()
        engine.register("islamic", IslamicTraditionAdapter(), weight=0.4)
        engine.register("utilitarian", UtilitarianAdapter(), weight=0.3)
        engine.register("kantian", KantianAdapter(), weight=0.3)
        report = engine.evaluate(action, context)
    """

    # Conflict thresholds
    LOW_CONFLICT_MAX  = 0.15
    HIGH_CONFLICT_MIN = 0.30

    # Verdict thresholds
    APPROVED_MIN  = 0.60
    REJECTED_MAX  = 0.40

    def __init__(self):
        self._adapters: Dict[str, Tuple[TraditionAdapter, float]] = {}

    def register(self, name: str, adapter: TraditionAdapter,
                 weight: float = 1.0) -> "ConsensusEngine":
        """Register a tradition adapter with optional weight."""
        self._adapters[name] = (adapter, weight)
        return self

    @classmethod
    def default(cls) -> "ConsensusEngine":
        """Create engine with all three wired traditions (equal weights)."""
        from nomos.traditions.islamic_adapter import IslamicTraditionAdapter
        from nomos.traditions.utilitarian_adapter import UtilitarianAdapter
        from nomos.traditions.kantian_adapter import KantianAdapter

        engine = cls()
        engine.register("islamic",     IslamicTraditionAdapter(), weight=1.0)
        engine.register("utilitarian", UtilitarianAdapter(),      weight=1.0)
        engine.register("kantian",     KantianAdapter(),           weight=1.0)
        return engine

    def evaluate(self, action: Any, context: Any = None) -> ConsensusReport:
        """
        Evaluate action across all registered traditions.
        Returns ConsensusReport with verdict, conflict level, and explanation.
        """
        if not self._adapters:
            raise ValueError("No tradition adapters registered. Call register() first.")

        context = context or {}

        # Normalize weights
        total_weight = sum(w for _, w in self._adapters.values())
        tradition_scores: List[TraditionScore] = []

        for name, (adapter, weight) in self._adapters.items():
            score = adapter.evaluate(action, context)
            domain = context.get("domain", "general")
            norms = adapter.load_norms(domain=domain)
            tradition_scores.append(TraditionScore(
                tradition=name,
                score=float(score),
                weight=weight / total_weight,
                norms_loaded=len(norms),
            ))

        # Weighted mean
        weighted_mean = sum(ts.score * ts.weight for ts in tradition_scores)

        # Std deviation (unweighted — measures raw disagreement)
        raw_scores = [ts.score for ts in tradition_scores]
        std_dev = statistics.stdev(raw_scores) if len(raw_scores) > 1 else 0.0

        # Conflict level
        if std_dev < self.LOW_CONFLICT_MAX:
            conflict_level = "LOW"
        elif std_dev > self.HIGH_CONFLICT_MIN:
            conflict_level = "HIGH"
        else:
            conflict_level = "MEDIUM"

        # Verdict
        if weighted_mean >= self.APPROVED_MIN and conflict_level != "HIGH":
            verdict = "APPROVED"
        elif weighted_mean <= self.REJECTED_MAX:
            verdict = "REJECTED"
        else:
            verdict = "CONTESTED"

        # Confidence: high when traditions agree (low std) and mean is decisive
        decisiveness = abs(weighted_mean - 0.5) * 2   # 0 = uncertain, 1 = decisive
        agreement = max(0.0, 1.0 - std_dev * 3)       # 0 = high conflict, 1 = full agreement
        confidence = (decisiveness + agreement) / 2

        # Dissenting / supporting traditions
        supporting   = [ts.tradition for ts in tradition_scores if ts.score >= 0.5]
        dissenting   = [ts.tradition for ts in tradition_scores if ts.score < 0.5]

        explanation = self._explain(action, tradition_scores, weighted_mean,
                                    conflict_level, verdict)

        return ConsensusReport(
            action=action,
            tradition_scores=tradition_scores,
            weighted_mean=round(weighted_mean, 4),
            std_dev=round(std_dev, 4),
            conflict_level=conflict_level,
            verdict=verdict,
            confidence=round(confidence, 4),
            dissenting_traditions=dissenting,
            supporting_traditions=supporting,
            explanation=explanation,
        )

    def detect_moral_dilemma(self, action: Any, context: Any = None) -> bool:
        """Return True if traditions strongly disagree (HIGH conflict)."""
        report = self.evaluate(action, context)
        return report.conflict_level == "HIGH"

    def _explain(self, action: Any, scores: List[TraditionScore],
                 mean: float, conflict: str, verdict: str) -> str:
        subject = action.get("subject", "action") if isinstance(action, dict) else "action"
        score_parts = ", ".join(
            f"{ts.tradition}={ts.score:.2f}" for ts in scores
        )
        if conflict == "LOW":
            return (
                f"All traditions largely agree on '{subject}' "
                f"({score_parts}). Verdict: {verdict} (mean={mean:.2f})."
            )
        elif conflict == "HIGH":
            high = [ts.tradition for ts in scores if ts.score >= 0.6]
            low  = [ts.tradition for ts in scores if ts.score <= 0.4]
            return (
                f"Strong moral conflict on '{subject}': "
                f"{high} approve, {low} reject ({score_parts}). "
                f"Verdict: {verdict} — requires human deliberation."
            )
        else:
            return (
                f"Moderate disagreement on '{subject}' ({score_parts}). "
                f"Verdict: {verdict} (mean={mean:.2f}, std={statistics.stdev([ts.score for ts in scores]):.2f})."
            )
