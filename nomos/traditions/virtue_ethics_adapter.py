"""
Virtue Ethics Adapter — NOMOS tradition plugin.

Implements MacIntyre/Anscombe/Aristotle virtue ethics:

    Eudaimonia:  human flourishing as the telos of action
    Phronesis:   practical wisdom to navigate particular situations
    Golden Mean: each virtue is the mean between excess and deficiency
    Virtues:     courage, justice, prudence, temperance, honesty,
                 compassion, generosity, integrity, wisdom, humility
    Vices:       cowardice, injustice, imprudence, intemperance, dishonesty,
                 cruelty, greed, deception, arrogance, laziness

evaluate() maps action subject + description keywords to a virtue/vice profile
and computes a flourishing score in [0.0, 1.0].

Score guide:
  Pure virtue expression      → near 1.0
  Pure vice expression        → near 0.0
  Mixed / phronesis-required  → 0.4–0.7 (contested mean)
"""

from typing import Any, Dict, List, Set

from nomos.interfaces.protocols import TraditionAdapter


# ── Virtue-positive actions ────────────────────────────────────────────────
# Subject → base score reflecting virtue expression

_VIRTUE_SCORES: Dict[str, float] = {
    # Commerce / social
    "trade":           0.85,   # honest exchange → justice + temperance
    "helping_others":  0.90,   # beneficence → compassion + generosity
    "charity":         0.95,   # generosity + justice
    "giving_charity":  0.95,
    "zakat":           0.95,   # generosity + justice
    "promise_keeping": 0.90,   # integrity + honesty
    "honesty":         0.90,   # honesty as intrinsic virtue
    "justice":         0.95,   # cardinal virtue (Aristotle)

    # Contemplative / spiritual
    "prayer":          0.90,   # piety + humility + contemplation
    "salah":           0.90,
    "fasting":         0.85,   # temperance + self-mastery

    # Courage
    "courage":         0.90,
    "sacrifice":       0.88,   # courage + generosity
}

# ── Vice-positive actions ──────────────────────────────────────────────────

_VICE_SCORES: Dict[str, float] = {
    "riba":            0.12,   # greed + injustice (excessive interest)
    "interest":        0.15,
    "lying":           0.10,   # dishonesty + injustice (for gain; see context override)
    "fraud":           0.05,   # dishonesty + injustice + deception
    "theft":           0.05,   # injustice + cowardice (taking without earning)
    "deception":       0.08,
    "manipulation":    0.08,
    "exploitation":    0.08,   # injustice + cruelty
    "coercion":        0.07,
    "torture":         0.03,
    "laziness":        0.25,   # vice of deficiency (lack of industriousness)
    "ingratitude":     0.20,
    "arrogance":       0.15,
    "greed":           0.10,
    "cruelty":         0.05,
}

# ── Context keywords that shift score toward compassion-based exception ────
# e.g. "lying to save a life" invokes phronesis / competing virtues

_COMPASSION_CONTEXT: Set[str] = {
    "save", "protect", "rescue", "life", "necessity", "emergency",
    "harm", "innocent", "family", "shelter", "starving",
}

# Score for a lie-to-save style conflict
# Honesty vs compassion — the contested golden mean under phronesis
_LIE_TO_SAVE_SCORE = 0.55


class VirtueEthicsAdapter(TraditionAdapter):
    """
    Aristotelian virtue ethics tradition.
    evaluate() asks: does this action express virtue, and does it conduce to
    eudaimonia (flourishing)?  Returns 0.0–1.0.
    """

    @property
    def name(self) -> str:
        return "virtue_ethics"

    def load_norms(self, domain: str = "general") -> List[Dict[str, Any]]:
        """
        Return the core virtue norms.  These are not domain-partitioned —
        Aristotle holds that virtues are universal excellences of character.
        """
        return [
            {
                "id": "courage",
                "type": "obligatory",
                "virtue": "courage",
                "description": "Act bravely between cowardice and rashness.",
                "strength": 0.8,
            },
            {
                "id": "justice",
                "type": "obligatory",
                "virtue": "justice",
                "description": "Give each person their due; the master virtue.",
                "strength": 1.0,
            },
            {
                "id": "phronesis",
                "type": "obligatory",
                "virtue": "phronesis",
                "description": "Apply practical wisdom to navigate particulars.",
                "strength": 0.9,
            },
            {
                "id": "vice_prohibition",
                "type": "prohibited",
                "virtue": "temperance",
                "description": "Avoid excess and deficiency; seek the golden mean.",
                "strength": 0.9,
            },
            {
                "id": "eudaimonia",
                "type": "obligatory",
                "virtue": "eudaimonia",
                "description": "Act always toward human flourishing as the final end.",
                "strength": 1.0,
            },
        ]

    def resolve_conflict(self, norm_a: Dict, norm_b: Dict) -> Dict:
        """
        Higher strength wins; virtues (obligatory) beat vices (prohibited)
        when strength is equal.
        """
        strength_a = norm_a.get("strength", 0.5)
        strength_b = norm_b.get("strength", 0.5)

        if strength_a == strength_b:
            # Obligatory norms represent virtues; they take precedence
            if norm_a.get("type") == "obligatory" and norm_b.get("type") != "obligatory":
                return norm_a
            if norm_b.get("type") == "obligatory" and norm_a.get("type") != "obligatory":
                return norm_b

        return norm_a if strength_a >= strength_b else norm_b

    def evaluate(self, action: Any, context: Any = None) -> float:
        """
        Score 0.0–1.0 by asking: does this action express virtue and conduce to
        eudaimonia?

        Reads from action dict:
            subject      — action type (e.g. "lying", "trade", "salah")
            description  — natural language description (context override)
            maxim        — explicit intent string (used for compassion context)

        Scoring:
            Pure virtue subjects         → _VIRTUE_SCORES value
            Pure vice subjects           → _VICE_SCORES value
            Vice + compassion context    → _LIE_TO_SAVE_SCORE (0.55)
            Unknown subject              → 0.65 (charitable default — mubah-style)
        """
        if not isinstance(action, dict):
            return 0.5

        subject = action.get("subject", "").lower().strip().replace(" ", "_")
        desc    = action.get("description", "").lower()
        maxim   = action.get("maxim", "").lower()
        full_text = desc + " " + maxim

        # Resolve subject from description if not given
        if not subject:
            for candidate in list(_VIRTUE_SCORES) + list(_VICE_SCORES):
                if candidate in full_text:
                    subject = candidate
                    break

        # Check for compassion / necessity context
        has_compassion_context = any(kw in full_text for kw in _COMPASSION_CONTEXT)

        # ── Primary classification ─────────────────────────────────────────
        if subject in _VIRTUE_SCORES:
            return round(_VIRTUE_SCORES[subject], 4)

        if subject in _VICE_SCORES:
            if has_compassion_context:
                # Phronesis: practical wisdom recognizes competing virtues.
                # Honesty vs compassion — neither fully wins, both are virtues.
                # Aristotle: the practically wise person acts for the best
                # available outcome; saving a life is a genuine good.
                # Score: contested mean ~0.55 (not approved, not condemned).
                return round(_LIE_TO_SAVE_SCORE, 4)
            return round(_VICE_SCORES[subject], 4)

        # ── Fallback: scan description for virtue/vice keywords ───────────
        virtue_keywords = {
            "honest", "charity", "justice", "courage", "generosity",
            "fair", "trade", "prayer", "helping", "compassion", "wisdom",
        }
        vice_keywords = {
            "lying", "fraud", "theft", "exploitation", "riba",
            "manipulation", "deception", "cheat", "steal", "greed",
        }

        virtue_hits = sum(1 for kw in virtue_keywords if kw in full_text)
        vice_hits   = sum(1 for kw in vice_keywords   if kw in full_text)

        if virtue_hits > 0 and vice_hits == 0:
            return round(0.75 + min(0.20, virtue_hits * 0.05), 4)
        if vice_hits > 0 and virtue_hits == 0:
            return round(max(0.10, 0.30 - vice_hits * 0.05), 4)
        if virtue_hits > 0 and vice_hits > 0:
            # Mixed — return contested zone
            return round(0.50 + (virtue_hits - vice_hits) * 0.05, 4)

        # Truly unknown: Aristotle assumes most human actions are eudaimonia-compatible
        return 0.65
