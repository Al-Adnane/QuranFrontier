"""Naskh (Abrogation) as Temporal Logic.

Models Quranic abrogation using temporal logic operators:
    diamond(A) = A was once valid (diamond / possibility in past)
    box(B) = B is always valid from now (box / necessity from now)
    A > B = B abrogates A (temporal override)

Scholarly database of recognized naskh relationships included.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict


class NaskhType(Enum):
    EXPLICIT = auto()   # Naskh sarih -- clear textual abrogation
    IMPLIED = auto()    # Naskh dimni -- implied by contradiction
    PARTIAL = auto()    # Naskh juz'i -- partial abrogation


@dataclass
class NaskhRelation:
    topic: str
    abrogated_verse: Tuple[int, int]     # mansukh (abrogated)
    abrogating_verse: Tuple[int, int]    # nasikh (abrogating)
    naskh_type: NaskhType
    scholarly_consensus: float = 1.0      # 0-1, how agreed upon
    notes: str = ""


@dataclass
class TemporalFormula:
    """Temporal logic formula for naskh."""
    operator: str          # "diamond" or "box"
    verse: Tuple[int, int]
    topic: str
    was_valid: bool = False
    is_active: bool = False

    @classmethod
    def once_valid(cls, verse: Tuple[int, int], topic: str) -> 'TemporalFormula':
        """diamond(A) -- A was once valid."""
        return cls(operator="diamond", verse=verse, topic=topic, was_valid=True, is_active=False)

    @classmethod
    def always_valid(cls, verse: Tuple[int, int], topic: str) -> 'TemporalFormula':
        """box(B) -- B is always valid from now."""
        return cls(operator="box", verse=verse, topic=topic, was_valid=True, is_active=True)


class NaskhDatabase:
    """Database of known naskh (abrogation) relationships."""

    def __init__(self):
        self.relations: List[NaskhRelation] = self._load_relations()

    def _load_relations(self) -> List[NaskhRelation]:
        """Load scholarly database of naskh relationships."""
        return [
            # Iddah (waiting period): 2:234 abrogates 2:240
            NaskhRelation(
                topic="iddah",
                abrogated_verse=(2, 240),
                abrogating_verse=(2, 234),
                naskh_type=NaskhType.EXPLICIT,
                scholarly_consensus=0.95,
                notes="Waiting period changed from one year to four months and ten days"
            ),
            # Qiblah direction: 2:144 abrogates 2:115
            NaskhRelation(
                topic="qiblah",
                abrogated_verse=(2, 115),
                abrogating_verse=(2, 144),
                naskh_type=NaskhType.EXPLICIT,
                scholarly_consensus=0.90,
                notes="Direction of prayer changed from Jerusalem to Mecca"
            ),
            # Night prayer: initially obligatory (73:1-4), then relaxed (73:20)
            NaskhRelation(
                topic="night_prayer",
                abrogated_verse=(73, 2),
                abrogating_verse=(73, 20),
                naskh_type=NaskhType.PARTIAL,
                scholarly_consensus=0.85,
                notes="Night prayer obligation relaxed"
            ),
            # Bequest: 2:180 (bequest to parents) partially abrogated by inheritance verses 4:11
            NaskhRelation(
                topic="bequest",
                abrogated_verse=(2, 180),
                abrogating_verse=(4, 11),
                naskh_type=NaskhType.IMPLIED,
                scholarly_consensus=0.80,
                notes="Fixed inheritance shares replace discretionary bequest"
            ),
            # Alcohol prohibition: gradual (2:219 -> 4:43 -> 5:90)
            NaskhRelation(
                topic="alcohol_stage1",
                abrogated_verse=(2, 219),
                abrogating_verse=(4, 43),
                naskh_type=NaskhType.PARTIAL,
                scholarly_consensus=0.90,
                notes="First restriction: don't pray while intoxicated"
            ),
            NaskhRelation(
                topic="alcohol_stage2",
                abrogated_verse=(4, 43),
                abrogating_verse=(5, 90),
                naskh_type=NaskhType.EXPLICIT,
                scholarly_consensus=0.95,
                notes="Complete prohibition of alcohol"
            ),
            # Fighting permission: 2:190 (defensive only) context, 9:5 (broader context)
            NaskhRelation(
                topic="fighting_permission",
                abrogated_verse=(2, 190),
                abrogating_verse=(9, 5),
                naskh_type=NaskhType.IMPLIED,
                scholarly_consensus=0.60,
                notes="Debated among scholars; many reject this naskh"
            ),
        ]

    def query(self, topic: Optional[str] = None,
              verse: Optional[Tuple[int, int]] = None) -> List[NaskhRelation]:
        """Query naskh database by topic or verse."""
        results = self.relations
        if topic:
            results = [r for r in results if r.topic == topic]
        if verse:
            results = [r for r in results
                      if r.abrogated_verse == verse or r.abrogating_verse == verse]
        return results


def query_naskh(topic: str) -> List[NaskhRelation]:
    """Convenience function to query naskh database."""
    db = NaskhDatabase()
    return db.query(topic=topic)


def get_active_ruling(topic: str) -> Optional[Tuple[int, int]]:
    """Get the currently active (non-abrogated) verse for a topic."""
    db = NaskhDatabase()
    results = db.query(topic=topic)
    if not results:
        return None
    # Return the abrogating verse (the one that supersedes)
    return results[-1].abrogating_verse
