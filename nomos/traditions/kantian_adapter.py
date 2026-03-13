"""
Kantian Deontological Adapter — NOMOS tradition plugin.

Implements Kant's categorical imperative as a universal TraditionAdapter.
"""

from typing import Any, Dict, List
from nomos.interfaces.protocols import TraditionAdapter


class KantianAdapter(TraditionAdapter):
    """
    Kantian deontological ethics.
    Evaluates actions by universalizability and respect for persons.
    """

    @property
    def name(self) -> str:
        return "kantian"

    def load_norms(self, domain: str = "general") -> List[Dict[str, Any]]:
        return [
            {"id": "categorical_imperative", "type": "obligatory",
             "condition": "universalizable(action)", "strength": 1.0},
            {"id": "humanity_formula", "type": "prohibited",
             "condition": "treats_persons_as_mere_means(action)", "strength": 1.0},
            {"id": "perfect_duty", "type": "obligatory",
             "condition": "is_perfect_duty(action)", "strength": 1.0},
        ]

    def resolve_conflict(self, norm_a: Dict, norm_b: Dict) -> Dict:
        """Perfect duties override imperfect duties."""
        if norm_a.get("duty_type") == "perfect":
            return norm_a
        return norm_b

    def evaluate(self, action: Any, context: Any) -> float:
        """
        Score 0.0–1.0 based on universalizability and respect for persons.
        TODO: Implement categorical imperative test.
        """
        return 0.5
