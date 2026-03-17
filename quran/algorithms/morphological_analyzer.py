"""Arabic Morphological Analyzer - Algorithm 3 for QuranFrontier.

Implements Arabic morphology: Root × Pattern = Word
- Roots are tri-consonantal (e.g., k-t-b = write)
- Patterns encode grammatical function (FaCaLa = perfective active verb)

Optional neural backend via sarf_group.py (PyTorch model).
Falls back to rule-based analysis when PyTorch is unavailable.
"""

import re
import unicodedata
import sys
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

# --- Optional neural backend ---
_NEURAL_AVAILABLE = False
_sarf_model = None

try:
    import torch
    # Add the quran-core models directory to path
    _models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'quran-core', 'models')
    _models_dir = os.path.abspath(_models_dir)
    if _models_dir not in sys.path:
        sys.path.insert(0, _models_dir)
    from sarf_group import SarfGroupNetwork, create_sarf_model
    _NEURAL_AVAILABLE = True
except (ImportError, Exception):
    pass


# ---------------------------------------------------------------------------
# Enumerations and dataclasses
# ---------------------------------------------------------------------------

class MorphologicalType(Enum):
    VERB_PERFECTIVE_ACTIVE = "fa'ala"
    VERB_PERFECTIVE_PASSIVE = "fu'ila"
    VERB_IMPERFECTIVE = "yaf'alu"
    AGENT_NOUN = "fa'il"
    PATIENT_NOUN = "maf'ul"
    PLACE_NOUN = "maf'al"
    ABSTRACT_NOUN = "fi'la"
    INTENSIVE = "fa''al"
    CAUSATIVE = "af'ala"
    UNKNOWN = "unknown"


@dataclass
class ArabicRoot:
    consonants: str          # e.g. "كتب"
    primary_meaning: str
    frequency_in_quran: int


@dataclass
class WordAnalysis:
    original: str
    normalized: str          # diacritics removed
    root: Optional[str]
    pattern: Optional[str]
    morph_type: MorphologicalType
    affixes: Dict[str, str]  # prefix/suffix extracted
    meaning: str
    word_family: List[str]
    confidence: float


# ---------------------------------------------------------------------------
# Diacritic ranges (Unicode U+064B – U+0652 plus tatweel U+0640)
# ---------------------------------------------------------------------------
_DIACRITIC_RANGE = re.compile(r'[\u064b-\u0652\u0670\u0640]')

# Hamza normalisation map (optional light normalisation)
_HAMZA_MAP = str.maketrans({
    '\u0622': '\u0627',  # آ → ا
    '\u0623': '\u0627',  # أ → ا
    '\u0625': '\u0627',  # إ → ا
    '\u0671': '\u0627',  # ٱ → ا
})


# ---------------------------------------------------------------------------
# Main analyser class
# ---------------------------------------------------------------------------

class ArabicMorphologicalAnalyzer:
    """Rule-based Arabic morphological analyser with optional neural backend.

    Usage::

        analyzer = ArabicMorphologicalAnalyzer()
        result = analyzer.analyze('كِتَاب')
        print(result.root, result.morph_type)
    """

    # Built-in root database – most common Quranic roots
    COMMON_ROOTS: Dict[str, Tuple[str, List[str]]] = {
        'كتب': ('write/book',   ['كَتَبَ', 'كِتَاب', 'كَاتِب', 'مَكْتُوب', 'مَكْتَب']),
        'علم': ('know/knowledge', ['عَلِمَ', 'عِلْم', 'عَالِم', 'مَعْلُوم', 'عُلَمَاء']),
        'رحم': ('mercy/womb',   ['رَحِمَ', 'رَحْمَة', 'رَحْمَن', 'رَحِيم', 'أَرْحَام']),
        'عبد': ('worship/slave', ['عَبَدَ', 'عَبْد', 'عِبَادَة', 'عَابِد', 'مَعْبُود']),
        'قرأ': ('read/recite',  ['قَرَأَ', 'قُرْآن', 'قَارِئ', 'مَقْرُوء']),
        'هدي': ('guide',        ['هَدَى', 'هُدَى', 'هِدَايَة', 'هَادٍ', 'مَهْدِيّ']),
        'سلم': ('peace/submit', ['سَلَّمَ', 'سَلَام', 'إِسْلَام', 'مُسْلِم', 'سَلِيم']),
        'حكم': ('judge/wisdom', ['حَكَمَ', 'حُكْم', 'حَكِيم', 'مُحْكَم', 'حِكْمَة']),
        'صلح': ('righteousness', ['صَلَحَ', 'صَلَاح', 'صَالِح', 'إِصْلَاح']),
        'خلق': ('create',       ['خَلَقَ', 'خَلْق', 'خَالِق', 'مَخْلُوق', 'خُلُق']),
        'ملك': ('own/king',     ['مَلَكَ', 'مَلِك', 'مَلَكُوت', 'مَلَائِكَة', 'مَالِك']),
        'نزل': ('descend/send', ['نَزَلَ', 'نَزَّلَ', 'أَنزَلَ', 'تَنزِيل', 'مَنزِل']),
        'امن': ('believe/trust', ['آمَنَ', 'إِيمَان', 'مُؤْمِن', 'أَمِين', 'أَمَانَة']),
        'كفر': ('disbelieve',   ['كَفَرَ', 'كُفْر', 'كَافِر', 'كَفَّارَة']),
        'صلو': ('pray',         ['صَلَّى', 'صَلَاة', 'مُصَلٍّ']),
        'زكو': ('purify/alms',  ['زَكَّى', 'زَكَاة', 'زَكِيّ']),
        'قول': ('say/speech',   ['قَالَ', 'قَوْل', 'قَائِل', 'مَقُول']),
        'فعل': ('do/act',       ['فَعَلَ', 'فِعْل', 'فَاعِل', 'مَفْعُول']),
        'جعل': ('make/place',   ['جَعَلَ', 'جَعْل']),
        'كون': ('be/exist',     ['كَانَ', 'كَوْن', 'مَكَان']),
        'ايي': ('come/bring',   ['جَاءَ', 'إِيَاب']),
        'رسل': ('send/messenger', ['أَرْسَلَ', 'رَسُول', 'رِسَالَة', 'مُرْسَل']),
        'نبي': ('prophet/news', ['نَبَّأَ', 'نَبِيّ', 'إِنْبَاء']),
        'كذب': ('lie/deny',     ['كَذَبَ', 'كَذِب', 'كَاذِب', 'مُكَذِّب']),
        'ظلم': ('wrong/dark',   ['ظَلَمَ', 'ظُلْم', 'ظَالِم', 'مَظْلُوم']),
        'رحل': ('travel',       ['رَحَلَ', 'رِحْلَة']),
        'حمد': ('praise',       ['حَمَدَ', 'حَمْد', 'حَامِد', 'مَحْمُود', 'مُحَمَّد']),
        'بسم': ('name/bless',   ['بَسْمَلَة', 'اسْم', 'سُمِّيَ']),
        'رحب': ('welcome/wide', ['رَحُبَ', 'رَحْب', 'مَرْحَبًا']),
        'قدر': ('power/measure', ['قَدَرَ', 'قُدْرَة', 'قَادِر', 'مُقَدَّر', 'قَدِير']),
        'سمع': ('hear',         ['سَمِعَ', 'سَمْع', 'سَامِع', 'مَسْمُوع']),
        'بصر': ('see/insight',  ['بَصَرَ', 'بَصَر', 'بَصِير', 'مُبْصِر']),
        'حيي': ('life/live',    ['حَيَّ', 'حَيَاة', 'حَيّ', 'مُحْيِي']),
        'موت': ('death/die',    ['مَاتَ', 'مَوْت', 'مَيِّت', 'مَمَات']),
    }

    # Prefixes: (Arabic prefix string, grammatical label)
    PREFIXES: List[Tuple[str, str]] = [
        ('الـ', 'definite_article'),
        ('ال',  'definite_article'),
        ('وَ',  'conj_and'),
        ('و',   'conj_and'),
        ('فَ',  'conj_then'),
        ('ف',   'conj_then'),
        ('بِ',  'prep_by'),
        ('ب',   'prep_by'),
        ('لِ',  'prep_for'),
        ('ل',   'prep_for'),
        ('كَ',  'prep_like'),
        ('ك',   'prep_like'),
        ('سَ',  'future_marker'),
        ('س',   'future_marker'),
    ]

    # Suffixes: (Arabic suffix string, grammatical label)
    SUFFIXES: List[Tuple[str, str]] = [
        ('هَا', 'fem_poss'),
        ('ها',  'fem_poss'),
        ('هُم', 'masc_pl_poss'),
        ('هم',  'masc_pl_poss'),
        ('هُ',  'masc_poss'),
        ('ه',   'masc_poss'),
        ('كُم', 'pl_address'),
        ('كم',  'pl_address'),
        ('نَا', 'pl_we'),
        ('نا',  'pl_we'),
        ('وْن', 'masc_pl_nom'),
        ('ون',  'masc_pl_nom'),
        ('يْن', 'dual_oblique'),
        ('ين',  'dual_oblique'),
        ('ات',  'fem_pl'),
        ('ة',   'fem_sg'),
    ]

    def __init__(self, use_neural: bool = False):
        """Create the analyser.

        Args:
            use_neural: If True and PyTorch is available, load the neural
                        SarfGroupNetwork backend.  Silently falls back to
                        rule-based analysis when unavailable.
        """
        self.root_db: Dict[str, str] = self._build_root_db()
        self._neural: Optional[object] = None
        if use_neural and _NEURAL_AVAILABLE:
            try:
                self._neural = create_sarf_model()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_root_db(self) -> Dict[str, str]:
        """Build a reverse-lookup dict: normalised word form → root."""
        db: Dict[str, str] = {}
        for root, (_, forms) in self.COMMON_ROOTS.items():
            for form in forms:
                key = self.remove_diacritics(form)
                db[key] = root
            # Also register the bare root itself
            db[root] = root
        return db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def remove_diacritics(self, text: str) -> str:
        """Remove Arabic diacritics (harakat) from *text*.

        Strips Unicode characters U+064B through U+0652 (fathatan through
        sukun), plus tatweel (U+0640) and superscript alef (U+0670).
        """
        return _DIACRITIC_RANGE.sub('', text)

    def normalize(self, text: str) -> str:
        """Remove diacritics and normalise hamza variants to bare alef."""
        return self.remove_diacritics(text).translate(_HAMZA_MAP)

    def extract_affixes(self, word: str) -> Tuple[str, Dict[str, str]]:
        """Strip leading prefixes and trailing suffixes from *word*.

        Returns a tuple ``(stem, affixes)`` where *affixes* is a dict with
        optional keys ``'prefix'`` and ``'suffix'`` mapped to their
        grammatical labels.

        The method works on the raw (possibly vocalised) word and also
        accepts diacritic-stripped input.
        """
        affixes: Dict[str, str] = {}
        stem = word

        # Try prefixes (longest match first).
        # Only strip a prefix when the remaining stem has at least 3 consonants,
        # preserving the minimal tri-consonantal Arabic root.
        for prefix, label in sorted(self.PREFIXES, key=lambda x: -len(x[0])):
            if stem.startswith(prefix):
                candidate = stem[len(prefix):]
                if len(self.remove_diacritics(candidate)) >= 3:
                    stem = candidate
                    affixes['prefix'] = label
                    break

        # Try suffixes (longest match first)
        for suffix, label in sorted(self.SUFFIXES, key=lambda x: -len(x[0])):
            if stem.endswith(suffix) and len(stem) > len(suffix) + 1:
                stem = stem[: -len(suffix)]
                affixes['suffix'] = label
                break

        return stem, affixes

    def identify_root(self, stem: str) -> Tuple[Optional[str], float]:
        """Attempt to identify the tri-consonantal root of *stem*.

        Strategy:
        1. Direct lookup in the root DB (exact match after normalisation).
        2. Try stripping any remaining suffix/prefix layers.
        3. Partial consonant skeleton matching against all known root forms.

        Returns ``(root_consonants, confidence)`` where confidence is in
        ``[0, 1]``.  Returns ``(None, 0.0)`` when no root is found.
        """
        norm = self.normalize(stem)

        # Direct lookup
        if norm in self.root_db:
            return self.root_db[norm], 1.0

        # Try stripping one more layer of affixes
        stem2, _ = self.extract_affixes(norm)
        norm2 = self.normalize(stem2)
        if norm2 in self.root_db:
            return self.root_db[norm2], 0.85

        # Partial / substring matching – look for any root whose forms share
        # a consonant skeleton with the normalised stem.
        best_root: Optional[str] = None
        best_score = 0.0

        for root, (_, forms) in self.COMMON_ROOTS.items():
            for form in forms:
                form_norm = self.normalize(form)
                # Score = fraction of root consonants present in stem, in order
                score = self._consonant_overlap(norm, root)
                if score > best_score:
                    best_score = score
                    best_root = root

        if best_score >= 0.67:
            return best_root, best_score * 0.7  # discount for fuzzy match

        return None, 0.0

    def _consonant_overlap(self, text: str, root: str) -> float:
        """Return the fraction of *root* consonants found in *text* in order."""
        pos = 0
        found = 0
        for ch in root:
            idx = text.find(ch, pos)
            if idx != -1:
                found += 1
                pos = idx + 1
        return found / max(len(root), 1)

    def classify_pattern(self, word: str, root: str) -> MorphologicalType:
        """Classify the morphological pattern of *word* given its *root*.

        Uses structural heuristics (no neural model required):

        * Starts with مَ/مُ/مِ  → noun class (place / patient)
        * Starts with يَ/تَ/نَ/أَ → imperfect verb
        * Middle doubled consonant → intensive (fa''ala)
        * Starts with اِسْتَ / اسْتَ → Form-X (causative / seeking)
        * Starts with أَفْ / اف  → causative (Form-IV / af'ala)
        * Ends with ة            → feminine / abstract noun
        * Pattern فَاعِل (active participle structure) → AGENT_NOUN
        * Otherwise perfective active verb
        """
        norm = self.normalize(word)
        raw = word

        # Strip only unambiguous, clearly-grammatical prefixes before classifying.
        # Single-letter prefixes that coincide with common root initials (ك، ب، ل)
        # are NOT stripped here to avoid misidentifying root-initial letters as
        # clitics.  Only vocalised single-letter prefixes are safe to strip.
        _CLASSIFY_PREFIXES = [
            ('الـ', 'definite_article'),
            ('ال',  'definite_article'),
            ('وَ',  'conj_and'),    # vocalised – unambiguous
            ('فَ',  'conj_then'),   # vocalised – unambiguous
            ('بِ',  'prep_by'),     # vocalised – unambiguous
            ('لِ',  'prep_for'),    # vocalised – unambiguous
            # NOTE: 'كَ' intentionally excluded – too easily confused with root-ك
            ('سَ',  'future_marker'),
        ]
        for prefix, _ in sorted(_CLASSIFY_PREFIXES, key=lambda x: -len(x[0])):
            p_norm = self.normalize(prefix)
            # Only strip if what remains is >= 3 chars (preserves full root)
            if norm.startswith(p_norm) and len(norm) - len(p_norm) >= 3:
                norm = norm[len(p_norm):]
                break

        # --- Imperfective verb markers ---
        if norm and norm[0] in 'يتنأاى':
            # Stronger: leading imperfective marker
            if len(norm) >= 3 and norm[0] in 'يتنأ':
                return MorphologicalType.VERB_IMPERFECTIVE

        # --- Noun prefix م ---
        if norm.startswith('م') or norm.startswith('مَ') or norm.startswith('مُ') or norm.startswith('مِ'):
            bare = self.remove_diacritics(raw)
            if bare.startswith('م'):
                # Patient noun vs place noun heuristic: ends with ة → abstract
                if norm.endswith('ة') or norm.endswith('ه'):
                    return MorphologicalType.ABSTRACT_NOUN
                # مَفْعُول pattern (passive participle)
                if 'و' in norm[2:]:
                    return MorphologicalType.PATIENT_NOUN
                return MorphologicalType.PLACE_NOUN

        # --- Causative Form-X: استفعل ---
        if norm.startswith('است') or norm.startswith('اسْت'):
            return MorphologicalType.CAUSATIVE

        # --- Causative Form-IV: أفعل ---
        if norm.startswith('أ') and len(norm) >= 4:
            return MorphologicalType.CAUSATIVE

        # --- Intensive: fa''ala (doubled middle radical) ---
        if root and len(root) >= 2:
            # Check if the second root letter is doubled in the word
            second_radical = root[1] if len(root) > 1 else ''
            if second_radical and second_radical * 2 in norm:
                return MorphologicalType.INTENSIVE

        # --- Active participle فَاعِل: alef after first radical ---
        if root and len(root) >= 2:
            first_radical = root[0]
            # Look for pattern: C + ا + C (alef after first radical)
            if first_radical in norm:
                idx = norm.index(first_radical)
                rest = norm[idx + 1:]
                if rest.startswith('ا') or rest.startswith('ى'):
                    return MorphologicalType.AGENT_NOUN

        # --- Feminine / abstract noun ---
        if norm.endswith('ة') or (len(raw) > 0 and raw[-1] == 'ة'):
            return MorphologicalType.ABSTRACT_NOUN

        # --- Passive perfective: fu'ila indicated by no strong cue ---
        # (rare to detect without full diacritics; default to active)

        # Default: perfective active verb
        return MorphologicalType.VERB_PERFECTIVE_ACTIVE

    def get_word_family(self, root: str) -> List[str]:
        """Return all known forms for *root*."""
        if root in self.COMMON_ROOTS:
            return self.COMMON_ROOTS[root][1]
        return []

    def analyze(self, word: str) -> WordAnalysis:
        """Full morphological analysis pipeline for a single *word*."""
        normalized = self.remove_diacritics(word)
        stem, affixes = self.extract_affixes(word)
        root, confidence = self.identify_root(stem)

        if root is None:
            # Fall back to trying the full word
            root, confidence = self.identify_root(word)

        morph_type = self.classify_pattern(word, root or '')
        pattern = morph_type.value
        word_family = self.get_word_family(root) if root else []

        # Derive meaning from root DB
        meaning = ''
        if root and root in self.COMMON_ROOTS:
            meaning = self.COMMON_ROOTS[root][0]

        return WordAnalysis(
            original=word,
            normalized=normalized,
            root=root,
            pattern=pattern,
            morph_type=morph_type,
            affixes=affixes,
            meaning=meaning,
            word_family=word_family,
            confidence=confidence,
        )

    def analyze_verse(self, verse_text: str) -> List[WordAnalysis]:
        """Analyse each whitespace-separated token in *verse_text*."""
        tokens = verse_text.split()
        return [self.analyze(token) for token in tokens if token.strip()]

    # ------------------------------------------------------------------
    # Optional neural backend
    # ------------------------------------------------------------------

    def analyze_neural(self, word: str) -> Optional[object]:
        """Attempt neural analysis via SarfGroupNetwork.

        Returns the neural MorphologicalAnalysis object when the model is
        available, or None otherwise.
        """
        if self._neural is None:
            return None
        try:
            arabic_letters = "ءابتثجحخدذرزسشصضطظعغفقكلمنهوي"
            letter_to_idx = {c: i + 1 for i, c in enumerate(arabic_letters)}
            norm = self.remove_diacritics(word)
            token_ids = [letter_to_idx.get(c, 0) for c in norm[:10]]
            return self._neural.analyze(word, token_ids)
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Demo / __main__
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    analyzer = ArabicMorphologicalAnalyzer()

    demo_words = [
        ('كِتَاب',    'kitab – book'),
        ('عَالِم',    'alim – scholar/knower'),
        ('مَكْتُوب',  'maktub – written (passive participle)'),
        ('يَكْتُبُ', 'yaktub – he writes (imperfect)'),
        ('مَكْتَب',   'maktab – office/place of writing'),
        ('كَاتِب',   'katib – writer (active participle)'),
        ('بِسْمِ',   'bismi – in the name of (with prep prefix)'),
        ('الرَّحْمَٰنِ', 'al-rahman – the Most Merciful'),
        ('وَالرَّحِيمِ', 'wa-l-rahim – and the Most Compassionate'),
        ('خَلَقَ',    'khalaqa – he created'),
    ]

    print("=" * 70)
    print("Arabic Morphological Analyzer – Demo")
    print("=" * 70)

    for word, gloss in demo_words:
        result = analyzer.analyze(word)
        print(f"\nWord   : {word}  ({gloss})")
        print(f"  Norm : {result.normalized}")
        print(f"  Root : {result.root or '—'}")
        print(f"  Type : {result.morph_type.name}")
        print(f"  Affxs: {result.affixes or '—'}")
        print(f"  Meanng: {result.meaning or '—'}")
        print(f"  Conf : {result.confidence:.2f}")

    print("\n" + "=" * 70)
    verse = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    print(f"Verse analysis: {verse}")
    analyses = analyzer.analyze_verse(verse)
    for wa in analyses:
        print(f"  {wa.original:20s} root={wa.root or '—':6s}  type={wa.morph_type.name}")
    print("=" * 70)
