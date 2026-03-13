"""Deontic Logic for Islamic Jurisprudence (Usul al-Fiqh).

Formalizes the five-category deontic system (al-ahkam al-khamsa):
    wajib (obligatory), haram (forbidden), mandub (recommended),
    makruh (discouraged), mubah (permissible)

Reasoning methods:
    - Direct textual derivation (nass)
    - Qiyas (analogical reasoning)
    - Naskh (abrogation / temporal override)
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, Optional, List


class DeonticStatus(Enum):
    WAJIB = auto()    # Obligatory
    HARAM = auto()    # Forbidden
    MANDUB = auto()   # Recommended
    MAKRUH = auto()   # Discouraged
    MUBAH = auto()    # Permissible


# Convenience aliases
Obligatory = DeonticStatus.WAJIB
Forbidden = DeonticStatus.HARAM
Recommended = DeonticStatus.MANDUB
Discouraged = DeonticStatus.MAKRUH
Permissible = DeonticStatus.MUBAH


@dataclass
class FiqhRule:
    subject: str
    status: DeonticStatus
    evidence_verse: Tuple[int, int]
    reasoning_method: str = "nass"  # nass, qiyas, ijma, istihsan
    confidence: float = 1.0
    notes: str = ""


@dataclass
class NaskhResult:
    topic: str
    earlier_verse: Tuple[int, int]
    later_verse: Tuple[int, int]
    active_verse: Tuple[int, int]
    abrogated: bool = True


# Known rulings database (scholarly consensus)
KNOWN_RULINGS = {
    # (surah, verse, subject) -> DeonticStatus
    ((2, 43), "salah"): DeonticStatus.WAJIB,
    ((2, 43), "zakat"): DeonticStatus.WAJIB,
    ((2, 183), "fasting"): DeonticStatus.WAJIB,
    ((2, 275), "riba"): DeonticStatus.HARAM,
    ((5, 90), "khamr"): DeonticStatus.HARAM,
    ((5, 3), "dead_meat"): DeonticStatus.HARAM,
    ((5, 3), "blood"): DeonticStatus.HARAM,
    ((5, 3), "pork"): DeonticStatus.HARAM,
    ((2, 222), "prayer_during_menstruation"): DeonticStatus.HARAM,
    ((4, 103), "salah"): DeonticStatus.WAJIB,
    ((2, 282), "recording_debts"): DeonticStatus.MANDUB,
    ((24, 33), "marriage"): DeonticStatus.MANDUB,
    ((2, 173), "pork_necessity"): DeonticStatus.MUBAH,  # Under necessity
    ((6, 145), "carrion_necessity"): DeonticStatus.MUBAH,
    ((2, 229), "divorce"): DeonticStatus.MAKRUH,
}

# Imperative indicators that suggest obligation
WAJIB_INDICATORS = {"\u0623\u0642\u064a\u0645\u0648\u0627", "\u0622\u062a\u0648\u0627", "\u0643\u062a\u0628", "\u0641\u0631\u0636", "\u0623\u0645\u0631", "\u0648\u062c\u0628"}
# Prohibition indicators
HARAM_INDICATORS = {"\u062d\u0631\u0645", "\u0644\u0627 \u062a\u0642\u0631\u0628\u0648\u0627", "\u0646\u0647\u0649", "\u0644\u0627 \u064a\u062d\u0644"}


def derive_ruling(verse: Tuple[int, int], subject: str) -> FiqhRule:
    """Derive a deontic ruling from verse and subject.

    First checks known rulings database, then uses linguistic heuristics.
    """
    # Check known rulings
    key = (verse, subject)
    if key in KNOWN_RULINGS:
        return FiqhRule(
            subject=subject,
            status=KNOWN_RULINGS[key],
            evidence_verse=verse,
            reasoning_method="nass",
            confidence=1.0
        )

    # Default: mubah (permissible) -- the default in fiqh
    return FiqhRule(
        subject=subject,
        status=DeonticStatus.MUBAH,
        evidence_verse=verse,
        reasoning_method="nass",
        confidence=0.5,
        notes="No specific ruling found; default to mubah"
    )


def apply_naskh(earlier: Tuple[int, int], later: Tuple[int, int],
                topic: str) -> NaskhResult:
    """Apply naskh (abrogation): later verse supersedes earlier."""
    return NaskhResult(
        topic=topic,
        earlier_verse=earlier,
        later_verse=later,
        active_verse=later,
        abrogated=True
    )


def apply_qiyas(asl_verse: Tuple[int, int], asl_ruling: DeonticStatus,
                illa: str, far_case: str) -> FiqhRule:
    """Apply qiyas (analogical reasoning).

    asl = original case with known ruling
    illa = effective cause / ratio legis
    far = new case sharing the same illa
    """
    return FiqhRule(
        subject=far_case,
        status=asl_ruling,
        evidence_verse=asl_verse,
        reasoning_method="qiyas",
        confidence=0.8,
        notes=f"By qiyas from {asl_verse}: shared illa='{illa}'"
    )
