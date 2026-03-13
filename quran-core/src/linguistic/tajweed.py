"""Tajweed as Context-Sensitive Formal Grammar.

Tajweed rules formalized as production rules:
    (left_context, phoneme, right_context) -> transformed_phoneme

This is a context-sensitive grammar (Type-1 in Chomsky hierarchy)
because the transformation depends on surrounding phonological context.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple
import re


class TajweedCategory(Enum):
    IDGHAM = auto()     # Merging (assimilation)
    IKHFA = auto()      # Hiding (partial assimilation)
    IQLAB = auto()      # Conversion (noon -> meem before ba)
    IZHAR = auto()      # Clear pronunciation
    GHUNNAH = auto()    # Nasalization
    MADD = auto()       # Elongation
    QALQALAH = auto()   # Echo/bounce on sukun letters
    TAFKHIM = auto()    # Heavy/emphatic pronunciation
    TARQIQ = auto()     # Light pronunciation
    WAQF = auto()       # Stopping rules


@dataclass
class TajweedRule:
    category: TajweedCategory
    name: str
    left_context: str         # What precedes
    phoneme: str              # The phoneme being transformed
    right_context: str        # What follows
    transformed: str          # Result after rule application
    description: str = ""


@dataclass
class TajweedResult:
    original: str
    applied_rules: List[TajweedRule]
    annotations: List[Tuple[int, int, TajweedCategory]]  # (start, end, category)


# Letters for specific rules
YARMALUN = set("\u064a\u0631\u0645\u0644\u0648\u0646")  # Letters of idgham
IKHFA_LETTERS = set("\u062a\u062b\u062c\u062f\u0630\u0632\u0633\u0634\u0635\u0636\u0637\u0638\u0641\u0642\u0643")  # 15 ikhfa letters
THROAT_LETTERS = set("\u0621\u0647\u0639\u062d\u063a\u062e")  # Izhar letters
QALQALAH_LETTERS = set("\u0642\u0637\u0628\u062c\u062f")  # Qalqalah letters
TAFKHIM_LETTERS = set("\u0635\u0636\u0637\u0638\u062e\u063a\u0642")  # Emphatic/heavy letters


class TajweedGrammar:
    """Complete tajweed rule system as formal grammar."""

    def __init__(self):
        self.rules = self._build_rules()

    def _build_rules(self) -> List[TajweedRule]:
        rules = []

        # Idgham rules: noon sakinah/tanwin + yarmalun letters
        for letter in YARMALUN:
            ghunnah = letter in set("\u064a\u0646\u0645\u0648")
            rules.append(TajweedRule(
                category=TajweedCategory.IDGHAM,
                name=f"Idgham {'with' if ghunnah else 'without'} Ghunnah into {letter}",
                left_context="\u0646\u0652",
                phoneme="\u0646",
                right_context=letter,
                transformed=f"{letter}\u0651",
                description=f"Noon sakinah merges into {letter}"
            ))

        # Ikhfa rules: noon sakinah + ikhfa letters
        for letter in IKHFA_LETTERS:
            rules.append(TajweedRule(
                category=TajweedCategory.IKHFA,
                name=f"Ikhfa before {letter}",
                left_context="\u0646\u0652",
                phoneme="\u0646",
                right_context=letter,
                transformed=f"~{letter}",
                description=f"Noon sakinah hidden before {letter}"
            ))

        # Iqlab: noon sakinah + ba -> meem
        rules.append(TajweedRule(
            category=TajweedCategory.IQLAB,
            name="Iqlab",
            left_context="\u0646\u0652",
            phoneme="\u0646",
            right_context="\u0628",
            transformed="\u0645\u0652\u0628",
            description="Noon sakinah converts to meem before ba"
        ))

        # Izhar: noon sakinah + throat letters
        for letter in THROAT_LETTERS:
            rules.append(TajweedRule(
                category=TajweedCategory.IZHAR,
                name=f"Izhar before {letter}",
                left_context="\u0646\u0652",
                phoneme="\u0646",
                right_context=letter,
                transformed="\u0646\u0652",
                description=f"Noon sakinah pronounced clearly before {letter}"
            ))

        # Ghunnah: noon/meem with shaddah
        rules.append(TajweedRule(
            category=TajweedCategory.GHUNNAH,
            name="Ghunnah on Noon Mushaddadah",
            left_context="",
            phoneme="\u0646\u0651",
            right_context="",
            transformed="\u0646\u0651~",
            description="Nasalization on doubled noon (2 counts)"
        ))
        rules.append(TajweedRule(
            category=TajweedCategory.GHUNNAH,
            name="Ghunnah on Meem Mushaddadah",
            left_context="",
            phoneme="\u0645\u0651",
            right_context="",
            transformed="\u0645\u0651~",
            description="Nasalization on doubled meem (2 counts)"
        ))

        # Madd rules
        rules.append(TajweedRule(
            category=TajweedCategory.MADD,
            name="Madd Tabee'i (Natural)",
            left_context="",
            phoneme="\u0627",
            right_context="",
            transformed="\u0627~",
            description="Natural elongation (2 counts) after fathah"
        ))
        rules.append(TajweedRule(
            category=TajweedCategory.MADD,
            name="Madd Muttasil (Connected)",
            left_context="\u0627",
            phoneme="\u0621",
            right_context="",
            transformed="\u0627~~\u0621",
            description="Obligatory connected elongation (4-5 counts)"
        ))
        rules.append(TajweedRule(
            category=TajweedCategory.MADD,
            name="Madd Munfasil (Separated)",
            left_context="",
            phoneme="\u0627",
            right_context="\u0621",
            transformed="\u0627~\u0621",
            description="Permissible separated elongation (2-5 counts)"
        ))

        # Qalqalah
        for letter in QALQALAH_LETTERS:
            rules.append(TajweedRule(
                category=TajweedCategory.QALQALAH,
                name=f"Qalqalah on {letter}",
                left_context="",
                phoneme=f"{letter}\u0652",
                right_context="",
                transformed=f"{letter}\u00b0",
                description=f"Echo/bounce on {letter} with sukun"
            ))

        return rules


def detect_tajweed_rules(text: str) -> List[TajweedRule]:
    """Detect applicable tajweed rules in Arabic text."""
    grammar = TajweedGrammar()
    detected = []

    # Look for noon sakinah patterns
    if "\u0646\u0652" in text or "\u0646\u0651" in text or "\u0645\u0651" in text:
        for rule in grammar.rules:
            if rule.left_context in text or rule.phoneme in text:
                detected.append(rule)
                break  # One detection per pattern

    # Look for madd patterns (alif after voweled letter)
    if "\u0627" in text:
        madd_rules = [r for r in grammar.rules if r.category == TajweedCategory.MADD]
        if madd_rules:
            detected.append(madd_rules[0])

    return detected


def apply_tajweed(text: str) -> TajweedResult:
    """Apply tajweed analysis to Arabic text."""
    rules = detect_tajweed_rules(text)
    annotations = []

    # Find positions of rule applications
    for i, rule in enumerate(rules):
        # Simple position detection
        if rule.phoneme in text:
            pos = text.find(rule.phoneme)
            if pos >= 0:
                annotations.append((pos, pos + len(rule.phoneme), rule.category))

    return TajweedResult(
        original=text,
        applied_rules=rules,
        annotations=annotations
    )
