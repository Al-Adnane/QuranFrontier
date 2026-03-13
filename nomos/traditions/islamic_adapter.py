"""
Islamic Tradition Adapter — NOMOS tradition plugin.

Wired to quran_core.src.logic.deontic for real norm loading and evaluation.

Deontic mapping (ahkam al-khamsa → universal):
    wajib / fard     → "obligatory"   score: 1.0
    mandub / mustah. → "recommended"  score: 0.8
    mubah / halal    → "permitted"    score: 0.65
    makruh           → "discouraged"  score: 0.35
    haram            → "prohibited"   score: 0.05
"""

import sys
import os
from typing import Any, Dict, List, Optional, Tuple

from nomos.interfaces.protocols import TraditionAdapter

# Wire to quran_core (sibling directory)
_QURAN_CORE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "quran-core"
)
if _QURAN_CORE not in sys.path:
    sys.path.insert(0, _QURAN_CORE)

try:
    from src.logic.deontic import (
        DeonticStatus, KNOWN_RULINGS, derive_ruling
    )
    _DEONTIC_AVAILABLE = True
except ImportError:
    _DEONTIC_AVAILABLE = False

# Score mapping: deontic status → 0–1 compliance score
_STATUS_SCORE: Dict = {
    "WAJIB":  1.0,
    "MANDUB": 0.8,
    "MUBAH":  0.65,
    "MAKRUH": 0.35,
    "HARAM":  0.05,
} if _DEONTIC_AVAILABLE else {}

_STATUS_TYPE: Dict = {
    "WAJIB":  "obligatory",
    "MANDUB": "recommended",
    "MUBAH":  "permitted",
    "MAKRUH": "discouraged",
    "HARAM":  "prohibited",
} if _DEONTIC_AVAILABLE else {}

MAQASID = [
    "preservation_of_religion",
    "preservation_of_life",
    "preservation_of_intellect",
    "preservation_of_lineage",
    "preservation_of_property",
]

# Map action subjects to KNOWN_RULINGS keys
_SUBJECT_KEYS: Dict[str, List[Tuple]] = {
    "riba":        [((2, 275), "riba")],
    "interest":    [((2, 275), "riba")],
    "salah":       [((2, 43), "salah"), ((4, 103), "salah")],
    "prayer":      [((2, 43), "salah")],
    "zakat":       [((2, 43), "zakat")],
    "fasting":     [((2, 183), "fasting")],
    "khamr":       [((5, 90), "khamr")],
    "alcohol":     [((5, 90), "khamr")],
    "pork":        [((5, 3), "pork")],
    "dead_meat":   [((5, 3), "dead_meat")],
    "blood":       [((5, 3), "blood")],
    "trade":       [((2, 282), "recording_debts")],
    "divorce":     [((2, 229), "divorce")],
    "marriage":    [((24, 33), "marriage")],
    "lying":       [],  # No verse: defaults to mubah
}

_DOMAIN_SUBJECTS: Dict[str, set] = {
    "finance":  {"riba", "zakat", "recording_debts"},
    "worship":  {"salah", "zakat", "fasting"},
    "food":     {"khamr", "dead_meat", "blood", "pork"},
    "family":   {"marriage", "divorce"},
}


class IslamicTraditionAdapter(TraditionAdapter):
    """
    Plugs quran_core deontic logic into NOMOS as one tradition among many.
    """

    DEONTIC_MAP = {
        "wajib": "obligatory", "fard": "obligatory",
        "mandub": "recommended", "mustahabb": "recommended",
        "mubah": "permitted", "halal": "permitted",
        "makruh": "discouraged",
        "haram": "prohibited", "forbidden": "prohibited",
    }

    @property
    def name(self) -> str:
        return "islamic"

    def load_norms(self, domain: str = "general") -> List[Dict[str, Any]]:
        """Load norms from quran_core KNOWN_RULINGS database."""
        if not _DEONTIC_AVAILABLE:
            return self._fallback_norms()

        norms = []
        for (verse, subject), status in KNOWN_RULINGS.items():
            status_name = status.name
            if domain != "general" and subject not in _DOMAIN_SUBJECTS.get(domain, {subject}):
                continue
            norms.append({
                "id": f"quran_{verse[0]}_{verse[1]}_{subject}",
                "type": _STATUS_TYPE.get(status_name, "permitted"),
                "subject": subject,
                "condition": f"action.subject == '{subject}'",
                "strength": _STATUS_SCORE.get(status_name, 0.65),
                "verse": verse,
                "source": "quran_core",
                "status": status_name,
            })

        if not norms:
            # domain filter too narrow, return all
            return self.load_norms("general")

        return norms

    def _fallback_norms(self) -> List[Dict[str, Any]]:
        return [
            {"id": "riba_prohibition", "type": "prohibited",
             "condition": "action.subject == 'riba'", "strength": 1.0, "source": "fallback"},
            {"id": "salah_obligation", "type": "obligatory",
             "condition": "action.subject == 'salah'", "strength": 1.0, "source": "fallback"},
            {"id": "default_permissible", "type": "permitted",
             "condition": "true", "strength": 0.65, "source": "fallback"},
        ]

    def resolve_conflict(self, norm_a: Dict, norm_b: Dict) -> Dict:
        """
        Naskh: later verse supersedes earlier.
        Falls back to strength comparison when no verse reference.
        """
        verse_a: Optional[Tuple] = norm_a.get("verse")
        verse_b: Optional[Tuple] = norm_b.get("verse")

        if verse_a and verse_b:
            # Higher surah*1000+ayah = later in revelation order
            idx_a = verse_a[0] * 1000 + verse_a[1]
            idx_b = verse_b[0] * 1000 + verse_b[1]
            return norm_b if idx_b >= idx_a else norm_a

        # No verse: stronger norm wins
        return norm_b if norm_b.get("strength", 0.5) >= norm_a.get("strength", 0.5) else norm_a

    def evaluate(self, action: Any, context: Any) -> float:
        """
        Score 0.0–1.0 using quran_core deontic ruling lookup.
        Uses derive_ruling() for known subjects; defaults to mubah (0.65).
        """
        subject = ""
        if isinstance(action, dict):
            subject = action.get("subject", "").lower().replace(" ", "_")

        # Necessity (darura) check — necessity makes prohibited things permissible
        description = (action.get("description", "") if isinstance(action, dict) else "").lower()
        necessity = any(w in description for w in ("save", "necessity", "emergency", "life", "starving"))

        if _DEONTIC_AVAILABLE:
            ruling_keys = _SUBJECT_KEYS.get(subject, [])
            if ruling_keys:
                best_rule = None
                for verse, subj in ruling_keys:
                    rule = derive_ruling(verse, subj)
                    if best_rule is None or rule.confidence > best_rule.confidence:
                        best_rule = rule
                if best_rule:
                    score = _STATUS_SCORE.get(best_rule.status.name, 0.65)
                    # Necessity elevates haram to mubah
                    if necessity and score < 0.5:
                        return 0.65
                    return score
        else:
            # Fallback lookup
            HARAM = {"riba", "interest", "khamr", "alcohol", "pork", "dead_meat", "blood"}
            WAJIB = {"salah", "prayer", "zakat", "fasting"}
            if subject in HARAM:
                return 0.65 if necessity else 0.05
            if subject in WAJIB:
                return 1.0

        # Unknown subject → mubah (the fiqh default)
        return 0.65

    def maqasid_weights(self) -> Dict[str, float]:
        return {m: 0.2 for m in MAQASID}
