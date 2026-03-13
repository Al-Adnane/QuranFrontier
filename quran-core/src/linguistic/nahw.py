"""Arabic Syntax (Nahw) as Constraint Satisfaction.

I'rab (case marking) is a constraint system where:
    role(word) -> case_requirement(word)

A sentence is grammatically valid iff all constraints are satisfied.
This is equivalent to a constraint satisfaction problem (CSP).
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional


class GrammaticalRole(Enum):
    MUBTADA = auto()     # Subject (topic)
    KHABAR = auto()      # Predicate
    FAIL = auto()        # Agent (doer)
    MAFUL = auto()       # Object (patient)
    MUDAF = auto()       # Construct state (first)
    MUDAF_ILAYH = auto() # Construct state (second)
    MAJRUR = auto()      # Prepositional object
    HAL = auto()         # Circumstantial
    TAMYIZ = auto()      # Specification
    NIDA = auto()        # Vocative


class CaseRequirement(Enum):
    MARFU = auto()   # Nominative (raf')
    MANSUB = auto()  # Accusative (nasb)
    MAJRUR = auto()  # Genitive (jarr)
    MAJZUM = auto()  # Jussive (jazm)


# The core mapping: grammatical role -> required case
CASE_ASSIGNMENTS: Dict[GrammaticalRole, CaseRequirement] = {
    GrammaticalRole.MUBTADA: CaseRequirement.MARFU,
    GrammaticalRole.KHABAR: CaseRequirement.MARFU,
    GrammaticalRole.FAIL: CaseRequirement.MARFU,
    GrammaticalRole.MAFUL: CaseRequirement.MANSUB,
    GrammaticalRole.HAL: CaseRequirement.MANSUB,
    GrammaticalRole.TAMYIZ: CaseRequirement.MANSUB,
    GrammaticalRole.NIDA: CaseRequirement.MANSUB,
    GrammaticalRole.MUDAF: CaseRequirement.MARFU,
    GrammaticalRole.MUDAF_ILAYH: CaseRequirement.MAJRUR,
    GrammaticalRole.MAJRUR: CaseRequirement.MAJRUR,
}

# Particles that govern specific cases
NASB_PARTICLES = {"إن", "أن", "كأن", "لكن", "ليت", "لعل"}
JARR_PARTICLES = {"في", "من", "إلى", "على", "عن", "ب", "ل", "ك", "حتى", "مع"}


@dataclass
class IrabConstraint:
    word: str
    role: GrammaticalRole
    required_case: CaseRequirement
    actual_case: Optional[CaseRequirement] = None

    @property
    def satisfied(self) -> bool:
        if self.actual_case is None:
            return True  # Unknown case = assume valid
        return self.actual_case == self.required_case


@dataclass
class SyntacticNode:
    word: str
    role: GrammaticalRole
    children: List['SyntacticNode'] = field(default_factory=list)


class SyntacticTree:
    """Dependency tree for Arabic verse syntax."""

    def __init__(self, root_word: str, root_role: GrammaticalRole):
        self.root = SyntacticNode(word=root_word, role=root_role)
        self.nodes: Dict[str, SyntacticNode] = {root_word: self.root}

    def add_child(self, word: str, role: GrammaticalRole, parent: str):
        node = SyntacticNode(word=word, role=role)
        self.nodes[word] = node
        if parent in self.nodes:
            self.nodes[parent].children.append(node)

    def depth(self) -> int:
        def _depth(node: SyntacticNode) -> int:
            if not node.children:
                return 0
            return 1 + max(_depth(c) for c in node.children)
        return _depth(self.root)


def parse_verse(tokens: List[str]) -> List[IrabConstraint]:
    """Parse a verse's tokens into i'rab constraints.

    Uses positional and particle-based heuristics to assign roles.
    """
    import re
    constraints = []

    for i, token in enumerate(tokens):
        stripped = re.sub(r'[\u064B-\u065F\u0670]', '', token)

        # Check if preceded by jarr particle
        if i > 0:
            prev = re.sub(r'[\u064B-\u065F\u0670]', '', tokens[i - 1])
            if prev in JARR_PARTICLES or stripped.startswith(("لل", "بال")):
                role = GrammaticalRole.MAJRUR
                constraints.append(IrabConstraint(
                    word=token, role=role,
                    required_case=CASE_ASSIGNMENTS[role]
                ))
                continue

        # Check for jarr prefix (attached preposition)
        if len(stripped) > 2 and stripped[0] in "بلك" and stripped[1:].startswith("ال"):
            role = GrammaticalRole.MAJRUR
            constraints.append(IrabConstraint(
                word=token, role=role,
                required_case=CASE_ASSIGNMENTS[role]
            ))
            continue

        # First nominal token = mubtada
        if i == 0:
            role = GrammaticalRole.MUBTADA
        elif i == 1 and len(constraints) > 0 and constraints[-1].role == GrammaticalRole.MUBTADA:
            role = GrammaticalRole.KHABAR
        else:
            role = GrammaticalRole.KHABAR  # Default

        constraints.append(IrabConstraint(
            word=token, role=role,
            required_case=CASE_ASSIGNMENTS[role]
        ))

    return constraints


def check_constraints(constraints: List[IrabConstraint]) -> bool:
    """Check if all i'rab constraints are satisfied."""
    return all(c.satisfied for c in constraints)
