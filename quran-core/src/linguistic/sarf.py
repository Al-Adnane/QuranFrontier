"""Arabic Morphology (Sarf) as Group-Theoretic Structure.

The trilateral root system is formalized as a group action:
    word = pattern(root) = wazn ⊗ jidr

where ⊗ is the morphological product (pattern application to root).
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Set
import re

from frontierqu.data.morphology_lexicon import MORPHOLOGY_LEXICON as _LEX, lookup_word as _lex_lookup

ARABIC_LETTERS = set("ءابتثجحخدذرزسشصضطظعغفقكلمنهوي")

PATTERNS = {
    "فَعَلَ": {"form": 1, "meaning": "basic_action"},
    "فَعَّلَ": {"form": 2, "meaning": "intensive/causative"},
    "فَاعَلَ": {"form": 3, "meaning": "reciprocal"},
    "أَفْعَلَ": {"form": 4, "meaning": "causative"},
    "تَفَعَّلَ": {"form": 5, "meaning": "reflexive_intensive"},
    "تَفَاعَلَ": {"form": 6, "meaning": "reciprocal_reflexive"},
    "اِنْفَعَلَ": {"form": 7, "meaning": "passive"},
    "اِفْتَعَلَ": {"form": 8, "meaning": "reflexive"},
    "اِفْعَلَّ": {"form": 9, "meaning": "colors/defects"},
    "اِسْتَفْعَلَ": {"form": 10, "meaning": "seeking"},
}

NOUN_PATTERNS = {
    "فِعَال": "verbal_noun",
    "فَعِيل": "adjective_intensive",
    "فَاعِل": "active_participle",
    "مَفْعُول": "passive_participle",
    "فُعُول": "plural",
    "أَفْعَال": "broken_plural",
    "مَفْعَل": "place/instrument",
    "فِعَالَة": "profession",
}

ROOT_LEXICON: Dict[str, List[str]] = {
    root: [e.word for e in entries]
    for root, entries in _LEX.items()
    if root not in ("الله",)
}

@dataclass
class MorphologicalAnalysis:
    word: str
    root: Optional[str]
    pattern: Optional[str]
    pos: str
    form: Optional[int]
    gender: Optional[str]
    number: Optional[str]
    case: Optional[str]
    state: Optional[str]

    def to_vector(self) -> List[float]:
        features = []
        if self.root:
            features.extend([ord(c) / 1000.0 for c in self.root[:3]])
        else:
            features.extend([0.0, 0.0, 0.0])
        features.append((self.form or 0) / 10.0)
        pos_map = {"noun": [1,0,0], "verb": [0,1,0], "particle": [0,0,1]}
        features.extend(pos_map.get(self.pos, [0,0,0]))
        case_map = {"nominative": [1,0,0], "accusative": [0,1,0], "genitive": [0,0,1]}
        features.extend(case_map.get(self.case or "", [0,0,0]))
        return features


def extract_root(word: str) -> Optional[str]:
    entry = _lex_lookup(word)
    if entry is not None:
        return entry.root
    clean = _strip_affixes(word)
    for root, words in ROOT_LEXICON.items():
        if word in words or clean in words:
            return root
    consonants = [c for c in clean if c in ARABIC_LETTERS and c not in "اويى"]
    if len(consonants) >= 3:
        return "".join(consonants[:3])
    return None


def extract_pattern(word: str, root: str) -> Optional[str]:
    if not root or len(root) < 3:
        return None
    fa, ayn, lam = root[0], root[1], root[2]
    pattern = word
    pattern = pattern.replace(fa, "ف", 1)
    pattern = pattern.replace(ayn, "ع", 1)
    pattern = pattern.replace(lam, "ل", 1)
    return pattern


def root_family(root: str) -> List[str]:
    return ROOT_LEXICON.get(root, [])


def root_pattern_group(pattern: str) -> List[str]:
    results = []
    for root, words in ROOT_LEXICON.items():
        for word in words:
            p = extract_pattern(word, root)
            if p == pattern:
                results.append(root)
                break
    return results


def analyze_word(word: str) -> MorphologicalAnalysis:
    root = extract_root(word)
    pattern = extract_pattern(word, root) if root else None
    pos = _classify_pos(word, pattern)
    form = _detect_verb_form(word, pattern) if pos == "verb" else None
    case = _detect_case(word)
    return MorphologicalAnalysis(
        word=word, root=root, pattern=pattern,
        pos=pos, form=form, gender=None, number=None,
        case=case, state=_detect_state(word)
    )


def _strip_affixes(word: str) -> str:
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', word)
    for prefix in ["ال", "و", "ف", "ب", "ل", "ك"]:
        if stripped.startswith(prefix) and len(stripped) > len(prefix) + 2:
            stripped = stripped[len(prefix):]
            break
    for suffix in ["ون", "ين", "ات", "ة", "ها", "هم", "كم"]:
        if stripped.endswith(suffix) and len(stripped) > len(suffix) + 2:
            stripped = stripped[:-len(suffix)]
            break
    return stripped


def _classify_pos(word: str, pattern: Optional[str]) -> str:
    particles = {"في", "من", "إلى", "على", "عن", "مع", "بين", "حتى",
                "إن", "أن", "لا", "ما", "لم", "لن", "قد", "إذا", "إذ",
                "ثم", "أو", "و", "ف", "ب", "ل", "ك"}
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', word)
    if stripped in particles:
        return "particle"
    if pattern and pattern in PATTERNS:
        return "verb"
    return "noun"


def _detect_verb_form(word: str, pattern: Optional[str]) -> Optional[int]:
    if not pattern:
        return None
    for p, data in PATTERNS.items():
        if pattern == p:
            return data["form"]
    return 1


def _detect_case(word: str) -> Optional[str]:
    if word.endswith('\u064F'):
        return "nominative"
    if word.endswith('\u064E'):
        return "accusative"
    if word.endswith('\u0650'):
        return "genitive"
    return None


def _detect_state(word: str) -> Optional[str]:
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', word)
    if stripped.startswith("ال"):
        return "definite"
    if stripped.endswith("ٍ") or stripped.endswith("ً") or stripped.endswith("ٌ"):
        return "indefinite"
    return None
