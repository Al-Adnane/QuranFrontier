"""
Kantian Deontological Adapter — NOMOS tradition plugin.

Implements Kant's three formulations of the Categorical Imperative:
    F1 — Universal Law: "Act only on maxims you could will to be universal law."
    F2 — Humanity:      "Treat humanity never merely as means, always as ends."
    F3 — Kingdom of Ends: "Act as a legislating member of a kingdom of ends."

evaluate() tests all three formulas against known maxim patterns.
A pass on all three → 1.0. Each failure reduces the score.
"""

from typing import Any, Dict, List, Set

from nomos.interfaces.protocols import TraditionAdapter


# ── Known maxim classifications ────────────────────────────────────────────
# Actions whose maxim leads to CONTRADICTION IN CONCEPTION (cannot be universalized)
# "If everyone did X, X would become impossible / self-defeating"
_CONCEPTION_CONTRADICTIONS: Set[str] = {
    "lying",           # Universal lying destroys trust → lying impossible
    "false_promise",   # Universal false promises destroy the institution of promises
    "fraud",           # Universal fraud collapses commerce
    "theft",           # Universal theft destroys property rights
    "deception",       # Universal deception collapses communication
    "manipulation",    # Universal manipulation collapses voluntary agency
}

# Actions whose maxim leads to CONTRADICTION IN WILL (irrational to universalize)
# "I could conceive it as law but could not rationally will it"
_WILL_CONTRADICTIONS: Set[str] = {
    "neglect_others",  # We cannot will a world where no one helps anyone (we need help)
    "ingratitude",     # We cannot will universal ingratitude (we need gratitude)
    "laziness",        # We cannot will universal laziness (society collapses)
    "selfishness",     # We cannot will universal selfishness (we need benevolence)
}

# Actions that treat persons as MERE MEANS (violate humanity formula)
# Kant: lying bypasses the listener's rational agency — using them as a mere means
_MERE_MEANS: Set[str] = {
    "manipulation",
    "coercion",
    "slavery",
    "exploitation",
    "deception",       # Bypasses rational agency
    "fraud",
    "torture",
    "lying",           # Kant: lying violates rational autonomy of the listener
}

# Actions that are UNIVERSALIZABLE and pass all three formulas
_UNIVERSALIZABLE: Set[str] = {
    "trade",           # Universal fair trade is coherent and rational to will
    "promise_keeping", # Universal promise keeping supports communication
    "honesty",         # Universal honesty is coherent
    "helping_others",  # Universal benevolence is rationally willable
    "justice",         # Universal justice is coherent and willable
    "prayer",          # Personal worship does not self-destruct universally
    "salah",
    "fasting",
    "zakat",
    "charity",
}

# Maxim-level scoring
_FORMULA_WEIGHT = {
    "F1_universalizability": 0.40,
    "F2_humanity":           0.40,
    "F3_kingdom_of_ends":    0.20,
}


class KantianAdapter(TraditionAdapter):
    """
    Tests actions against Kant's Categorical Imperative.
    Returns scores close to 1.0 for morally permissible actions,
    close to 0.0 for actions that fail universalizability or respect for persons.
    """

    @property
    def name(self) -> str:
        return "kantian"

    def load_norms(self, domain: str = "general") -> List[Dict[str, Any]]:
        return [
            {"id": "categorical_imperative", "type": "obligatory",
             "condition": "universalizable(action)", "strength": 1.0,
             "duty_type": "perfect"},
            {"id": "humanity_formula", "type": "prohibited",
             "condition": "treats_persons_as_mere_means(action)", "strength": 1.0,
             "duty_type": "perfect"},
            {"id": "kingdom_of_ends", "type": "obligatory",
             "condition": "consistent_with_rational_community(action)", "strength": 0.8,
             "duty_type": "imperfect"},
        ]

    def resolve_conflict(self, norm_a: Dict, norm_b: Dict) -> Dict:
        """Perfect duties override imperfect duties."""
        if norm_a.get("duty_type") == "perfect":
            return norm_a
        if norm_b.get("duty_type") == "perfect":
            return norm_b
        # Both same type: higher strength wins
        return norm_a if norm_a.get("strength", 0) >= norm_b.get("strength", 0) else norm_b

    def evaluate(self, action: Any, context: Any) -> float:
        """
        Score 0.0–1.0 by testing all three CI formulations.

        Reads from action dict:
            subject     — action type (e.g. "lying", "trade")
            maxim       — explicit maxim string (optional, used for override)
            description — natural language description (fallback parsing)

        Formula weights: F1=40%, F2=40%, F3=20%.
        All pass → 1.0. All fail → 0.0.
        """
        if not isinstance(action, dict):
            return 0.5

        subject = action.get("subject", "").lower().replace(" ", "_")
        maxim   = action.get("maxim", "").lower()
        desc    = action.get("description", "").lower()

        # Resolve subject from description if not explicit
        if not subject:
            for candidate in list(_CONCEPTION_CONTRADICTIONS | _MERE_MEANS | _UNIVERSALIZABLE):
                if candidate in desc:
                    subject = candidate
                    break

        # ── Formula 1: Universalizability ─────────────────────────────────
        if subject in _UNIVERSALIZABLE:
            f1_score = 1.0
        elif subject in _CONCEPTION_CONTRADICTIONS:
            f1_score = 0.0
        elif subject in _WILL_CONTRADICTIONS:
            f1_score = 0.2  # Conceivable but irrational to will
        else:
            # Unknown subject: check maxim for self-defeating language
            if "whenever convenient" in maxim or "for my benefit" in maxim or "for personal gain" in maxim:
                f1_score = 0.1
            elif "save" in maxim or "help" in maxim or "protect" in maxim:
                # Life-saving special case: a single exception doesn't destroy the maxim
                f1_score = 0.6
            else:
                f1_score = 0.7  # Charitable default for unknown maxims

        # ── Formula 2: Humanity (no mere means) ───────────────────────────
        if subject in _MERE_MEANS:
            f2_score = 0.0
        elif subject in _UNIVERSALIZABLE:
            f2_score = 1.0
        else:
            f2_score = 0.8  # Charitable default

        # ── Formula 3: Kingdom of Ends (rational community consistency) ───
        # F3 ≈ F1 but more lenient: can we act as if legislating for all?
        f3_score = max(f1_score, 0.5) if f1_score > 0 else 0.2

        # ── Weighted total ─────────────────────────────────────────────────
        score = (
            _FORMULA_WEIGHT["F1_universalizability"] * f1_score +
            _FORMULA_WEIGHT["F2_humanity"]           * f2_score +
            _FORMULA_WEIGHT["F3_kingdom_of_ends"]    * f3_score
        )

        return round(score, 4)
