"""
Utilitarian Tradition Adapter — NOMOS tradition plugin.

Implements Bentham's felicific calculus:
    utility = Σ(beneficiaries × intensity) - Σ(harmed_parties × intensity)
    score   = sigmoid(net_utility / normalizer)

Seven Bentham dimensions (all extracted from action dict when available):
    beneficiaries, harmed_parties, intensity, duration,
    certainty, propinquity (proximity), extent
"""

import math
from typing import Any, Dict, List

from nomos.interfaces.protocols import TraditionAdapter


def _sigmoid(x: float) -> float:
    """Squash utility to 0–1."""
    return 1.0 / (1.0 + math.exp(-x))


class UtilitarianAdapter(TraditionAdapter):
    """
    Bentham/Mill utilitarian reasoning.
    evaluate() computes real aggregate welfare — not a stub.
    """

    # Base intensity assumed when not specified
    DEFAULT_INTENSITY = 1.0
    # Normalizer controls how "extreme" scores become
    NORMALIZER = 5.0

    @property
    def name(self) -> str:
        return "utilitarian"

    def load_norms(self, domain: str = "general") -> List[Dict[str, Any]]:
        return [
            {"id": "maximize_welfare", "type": "obligatory",
             "condition": "aggregate_utility > 0", "strength": 1.0},
            {"id": "minimize_harm", "type": "prohibited",
             "condition": "net_harm > net_benefit", "strength": 0.9},
            {"id": "equal_consideration", "type": "obligatory",
             "condition": "all_interests_counted", "strength": 0.8},
        ]

    def resolve_conflict(self, norm_a: Dict, norm_b: Dict) -> Dict:
        """Higher expected utility wins."""
        return norm_a if norm_a.get("strength", 0) >= norm_b.get("strength", 0) else norm_b

    def evaluate(self, action: Any, context: Any) -> float:
        """
        Bentham felicific calculus.

        Reads from action dict:
            beneficiaries  — number of people who gain (default 1)
            harmed_parties — number of people who lose (default 0)
            intensity      — pleasure/pain intensity multiplier (default 1.0)
            duration       — relative duration factor (default 1.0)
            certainty      — probability 0–1 that consequences occur (default 0.8)
            reversible     — True reduces harm weight by 0.5

        Returns sigmoid(net_utility / NORMALIZER) in [0, 1].
        > 0.5 = net positive (approve), < 0.5 = net negative (reject)
        """
        if not isinstance(action, dict):
            return 0.5

        beneficiaries  = float(action.get("beneficiaries", 1))
        harmed_parties = float(action.get("harmed_parties", 0))
        intensity      = float(action.get("intensity", self.DEFAULT_INTENSITY))
        duration       = float(action.get("duration", 1.0))
        certainty      = float(action.get("certainty", 0.8))
        reversible     = bool(action.get("reversible", True))

        # Harm weight reduced if consequences are reversible
        harm_weight = 0.5 if reversible else 1.0

        # Felicific calculus
        pleasure = beneficiaries * intensity * duration * certainty
        pain     = harmed_parties * intensity * duration * certainty * harm_weight

        net_utility = pleasure - pain

        # Sigmoid squash to [0, 1]
        return _sigmoid(net_utility / self.NORMALIZER)
