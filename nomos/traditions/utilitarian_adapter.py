"""
Utilitarian Tradition Adapter — NOMOS tradition plugin.

Implements consequentialist/utilitarian ethical reasoning
as a universal TraditionAdapter.
"""

from typing import Any, Dict, List
from nomos.interfaces.protocols import TraditionAdapter


class UtilitarianAdapter(TraditionAdapter):
    """
    Bentham/Mill utilitarian reasoning.
    Maximizes aggregate welfare across all affected parties.
    """

    @property
    def name(self) -> str:
        return "utilitarian"

    def load_norms(self, domain: str = "general") -> List[Dict[str, Any]]:
        return [
            {"id": "maximize_welfare", "type": "obligatory",
             "condition": "aggregate_utility > 0", "strength": 1.0},
            {"id": "minimize_harm", "type": "prohibited",
             "condition": "net_harm > net_benefit", "strength": 0.9},
        ]

    def resolve_conflict(self, norm_a: Dict, norm_b: Dict) -> Dict:
        """Choose the norm with higher expected utility."""
        if norm_a.get("strength", 0) >= norm_b.get("strength", 0):
            return norm_a
        return norm_b

    def evaluate(self, action: Any, context: Any) -> float:
        """
        Score 0.0–1.0 based on estimated aggregate utility.
        TODO: Implement with actual welfare function.
        """
        return 0.5
