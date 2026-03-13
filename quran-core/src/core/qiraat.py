"""Qira'at (Variant Readings) as Fiber Bundle.

The 10 canonical readings form a fiber bundle:
    Base space B = Uthmani rasm (consonantal skeleton)
    Fiber F_v at verse v = {valid readings of v}
    Total space E = union of F_v (all readings of all verses)
    Projection pi: E -> B maps each reading to its base verse

Holonomy around a thematic loop measures total pronunciation variation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


@dataclass
class Qari:
    """A canonical reader (qari)."""
    name: str
    arabic_name: str
    transmitter: str          # Primary rawi
    death_year_ah: int        # Hijri year
    region: str


@dataclass
class Reading:
    """A specific reading variant at a verse."""
    verse: Tuple[int, int]
    qari: str
    arabic: str
    transliteration: str
    semantic_impact: str      # How this reading changes meaning
    phonological_diff: float  # 0-1, how different from base


# The 10 canonical readers
CANONICAL_QURRA = [
    Qari("Nafi'", "\u0646\u0627\u0641\u0639", "Warsh/Qalun", 169, "Medina"),
    Qari("Ibn Kathir", "\u0627\u0628\u0646 \u0643\u062b\u064a\u0631", "Al-Bazzi/Qunbul", 120, "Mecca"),
    Qari("Abu Amr", "\u0623\u0628\u0648 \u0639\u0645\u0631\u0648", "Al-Duri/Al-Susi", 154, "Basra"),
    Qari("Ibn Amir", "\u0627\u0628\u0646 \u0639\u0627\u0645\u0631", "Hisham/Ibn Dhakwan", 118, "Damascus"),
    Qari("Asim", "\u0639\u0627\u0635\u0645", "Hafs/Shu'bah", 127, "Kufa"),
    Qari("Hamzah", "\u062d\u0645\u0632\u0629", "Khalaf/Khallad", 156, "Kufa"),
    Qari("Al-Kisa'i", "\u0627\u0644\u0643\u0633\u0627\u0626\u064a", "Al-Layth/Al-Duri", 189, "Kufa"),
    Qari("Abu Ja'far", "\u0623\u0628\u0648 \u062c\u0639\u0641\u0631", "Isa/Sulayman", 130, "Medina"),
    Qari("Ya'qub", "\u064a\u0639\u0642\u0648\u0628", "Ruways/Rawh", 205, "Basra"),
    Qari("Khalaf", "\u062e\u0644\u0641", "Ishaq/Idris", 229, "Baghdad"),
]

# Known variant readings where meaning or form differs
VARIANT_READINGS: Dict[Tuple[int, int], List[Reading]] = {
    (1, 4): [
        Reading((1, 4), "Asim (Hafs)",
                "\u0645\u064e\u0627\u0644\u0650\u0643\u0650 \u064a\u064e\u0648\u0652\u0645\u0650 \u0627\u0644\u062f\u0651\u0650\u064a\u0646\u0650",
                "maaliki yawm id-deen", "Owner/Possessor of the Day", 0.3),
        Reading((1, 4), "Nafi' (Warsh)",
                "\u0645\u064e\u0644\u0650\u0643\u0650 \u064a\u064e\u0648\u0652\u0645\u0650 \u0627\u0644\u062f\u0651\u0650\u064a\u0646\u0650",
                "maliki yawm id-deen", "King/Sovereign of the Day", 0.3),
    ],
    (2, 184): [
        Reading((2, 184), "Hafs",
                "\u0648\u064e\u0639\u064e\u0644\u064e\u0649 \u0627\u0644\u0651\u064e\u0630\u0650\u064a\u0646\u064e \u064a\u064f\u0637\u0650\u064a\u0642\u064f\u0648\u0646\u064e\u0647\u064f",
                "yutiiqoonahu", "Those who can bear it (with difficulty)", 0.2),
        Reading((2, 184), "Ibn Kathir",
                "\u0648\u064e\u0639\u064e\u0644\u064e\u0649 \u0627\u0644\u0651\u064e\u0630\u0650\u064a\u0646\u064e \u064a\u064e\u0637\u0651\u064e\u0648\u0651\u064e\u0642\u064f\u0648\u0646\u064e\u0647\u064f",
                "yattawwaqoonahu", "Those who struggle to bear it", 0.4),
    ],
    (3, 146): [
        Reading((3, 146), "Hafs",
                "\u0642\u064e\u0627\u062a\u064e\u0644\u064e \u0645\u064e\u0639\u064e\u0647\u064f \u0631\u0650\u0628\u0651\u0650\u064a\u0651\u064f\u0648\u0646\u064e \u0643\u064e\u062b\u0650\u064a\u0631\u064c",
                "qaatala", "fought alongside him", 0.2),
        Reading((3, 146), "Nafi'",
                "\u0642\u064f\u062a\u0650\u0644\u064e \u0645\u064e\u0639\u064e\u0647\u064f \u0631\u0650\u0628\u0651\u0650\u064a\u0651\u064f\u0648\u0646\u064e \u0643\u064e\u062b\u0650\u064a\u0631\u064c",
                "qutila", "were killed alongside him", 0.5),
    ],
    (18, 86): [
        Reading((18, 86), "Hafs",
                "\u0648\u064e\u062c\u064e\u062f\u064e\u0647\u064e\u0627 \u062a\u064e\u063a\u0652\u0631\u064f\u0628\u064f \u0641\u0650\u064a \u0639\u064e\u064a\u0652\u0646\u064d \u062d\u064e\u0645\u0650\u0626\u064e\u0629\u064d",
                "hami'ah", "muddy spring", 0.3),
        Reading((18, 86), "Abu Amr",
                "\u0648\u064e\u062c\u064e\u062f\u064e\u0647\u064e\u0627 \u062a\u064e\u063a\u0652\u0631\u064f\u0628\u064f \u0641\u0650\u064a \u0639\u064e\u064a\u0652\u0646\u064d \u062d\u064e\u0627\u0645\u0650\u064a\u064e\u0629\u064d",
                "haamiyah", "hot spring", 0.4),
    ],
    (2, 285): [
        Reading((2, 285), "Hafs",
                "\u0648\u064e\u0643\u064f\u062a\u064f\u0628\u0650\u0647\u0650",
                "wa kutubihi", "and His books (plural)", 0.2),
        Reading((2, 285), "Hamzah",
                "\u0648\u064e\u0643\u0650\u062a\u064e\u0627\u0628\u0650\u0647\u0650",
                "wa kitaabihi", "and His book (singular)", 0.3),
    ],
}


class QiraatFiberBundle:
    """Fiber bundle of Quranic readings over the text base space."""

    def __init__(self):
        self.qurra = CANONICAL_QURRA
        self.variants = VARIANT_READINGS

    def fiber_at(self, verse: Tuple[int, int]) -> List[Reading]:
        """Get all variant readings at a verse (the fiber)."""
        if verse in self.variants:
            return self.variants[verse]
        # Default: single reading (Hafs)
        return [Reading(verse, "Hafs", f"Standard reading at {verse[0]}:{verse[1]}",
                        "standard", "No variant", 0.0)]

    def holonomy(self, theme: str) -> float:
        """Compute holonomy (total variation) around a thematic loop.

        Sum of phonological differences across all variant readings
        in verses belonging to the theme.
        """
        from frontierqu.data.cross_references import THEMATIC_GROUPS

        if theme not in THEMATIC_GROUPS:
            return 0.0

        verses = THEMATIC_GROUPS[theme]
        total_variation = 0.0

        for verse in verses:
            fiber = self.fiber_at(verse)
            if len(fiber) > 1:
                # Sum pairwise differences
                for i in range(len(fiber)):
                    for j in range(i + 1, len(fiber)):
                        total_variation += abs(
                            fiber[i].phonological_diff - fiber[j].phonological_diff
                        )
                        total_variation += 0.1  # Base variation for multiple readings

        return total_variation

    def section(self, qari_name: str) -> Dict[Tuple[int, int], Reading]:
        """Get a section (choice of reading) for a specific qari."""
        result = {}
        for verse, readings in self.variants.items():
            for r in readings:
                if qari_name.lower() in r.qari.lower():
                    result[verse] = r
                    break
        return result


def get_readings_for_verse(verse: Tuple[int, int]) -> List[Reading]:
    """Convenience function to get readings for a verse."""
    bundle = QiraatFiberBundle()
    return bundle.fiber_at(verse)
