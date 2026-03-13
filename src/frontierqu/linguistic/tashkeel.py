"""Arabic Diacritics (Tashkeel) Analyzer.

Analyzes the diacritical marks (harakat) in Quranic Arabic text.
Tashkeel includes: fatha, damma, kasra, tanwin variants, sukun, shadda,
and superscript alef. These marks encode vowelization and pronunciation
that are essential for correct Quranic recitation.

Unicode range for Arabic diacritical marks:
    U+064B  FATHATAN    (tanwin fath)
    U+064C  DAMMATAN    (tanwin damm)
    U+064D  KASRATAN    (tanwin kasr)
    U+064E  FATHA
    U+064F  DAMMA
    U+0650  KASRA
    U+0651  SHADDA      (gemination)
    U+0652  SUKUN       (vowelless)
    U+0653  MADDAH      (above)
    U+0654  HAMZA_ABOVE
    U+0655  HAMZA_BELOW
    U+0656  SUBSCRIPT_ALEF
    U+0657  INVERTED_DAMMA
    U+0658  MARK_NOON_GHUNNA
    U+0659  ZWARAKAY
    U+065A  VOWEL_SIGN_V_ABOVE
    U+065B  VOWEL_SIGN_INVERTED_V_ABOVE
    U+065C  VOWEL_SIGN_DOT_BELOW
    U+065D  REVERSED_DAMMA
    U+065E  FATHA_WITH_TWO_DOTS
    U+065F  WAVY_HAMZA_BELOW
    U+0670  SUPERSCRIPT_ALEF (dagger alef)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import re


# ============================================================================
# Diacritic Definitions
# ============================================================================

class Diacritic:
    """Arabic diacritical mark constants."""
    # Core harakat
    FATHATAN        = '\u064B'
    DAMMATAN        = '\u064C'
    KASRATAN        = '\u064D'
    FATHA           = '\u064E'
    DAMMA           = '\u064F'
    KASRA           = '\u0650'
    SHADDA          = '\u0651'
    SUKUN           = '\u0652'
    MADDAH          = '\u0653'
    HAMZA_ABOVE     = '\u0654'
    HAMZA_BELOW     = '\u0655'
    SUBSCRIPT_ALEF  = '\u0656'
    INVERTED_DAMMA  = '\u0657'
    NOON_GHUNNA     = '\u0658'
    SUPERSCRIPT_ALEF = '\u0670'

    # Grouped sets
    SHORT_VOWELS = {FATHA, DAMMA, KASRA}
    TANWIN       = {FATHATAN, DAMMATAN, KASRATAN}
    ALL_MARKS    = set(chr(c) for c in range(0x064B, 0x0660)) | {'\u0670'}


# Regex matching any single Arabic diacritical mark
_TASHKEEL_RE = re.compile(r'[\u064B-\u065F\u0670]')

# Category labels for each diacritic codepoint
DIACRITIC_NAMES: Dict[str, str] = {
    '\u064B': 'fathatan',
    '\u064C': 'dammatan',
    '\u064D': 'kasratan',
    '\u064E': 'fatha',
    '\u064F': 'damma',
    '\u0650': 'kasra',
    '\u0651': 'shadda',
    '\u0652': 'sukun',
    '\u0653': 'maddah',
    '\u0654': 'hamza_above',
    '\u0655': 'hamza_below',
    '\u0656': 'subscript_alef',
    '\u0657': 'inverted_damma',
    '\u0658': 'noon_ghunna',
    '\u0659': 'zwarakay',
    '\u065A': 'vowel_sign_v_above',
    '\u065B': 'vowel_sign_inv_v_above',
    '\u065C': 'vowel_sign_dot_below',
    '\u065D': 'reversed_damma',
    '\u065E': 'fatha_two_dots',
    '\u065F': 'wavy_hamza_below',
    '\u0670': 'superscript_alef',
}

# Category groupings
DIACRITIC_CATEGORIES: Dict[str, str] = {
    'fathatan': 'tanwin', 'dammatan': 'tanwin', 'kasratan': 'tanwin',
    'fatha': 'short_vowel', 'damma': 'short_vowel', 'kasra': 'short_vowel',
    'shadda': 'gemination', 'sukun': 'quiescence',
    'maddah': 'elongation', 'superscript_alef': 'elongation',
    'hamza_above': 'hamza', 'hamza_below': 'hamza',
    'subscript_alef': 'other', 'inverted_damma': 'other',
    'noon_ghunna': 'nasalization',
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class DiacriticPosition:
    """A single diacritical mark occurrence."""
    char: str
    name: str
    category: str
    position: int          # character offset in original text
    base_char: str         # the consonant/letter it attaches to


@dataclass
class TashkeelAnalysis:
    """Complete analysis of diacritical marks in a text."""
    text: str
    total_chars: int
    total_diacritics: int
    positions: List[DiacriticPosition]
    frequencies: Dict[str, int]              # name -> count
    category_frequencies: Dict[str, int]     # category -> count
    density: float                           # diacritics / total characters

    @property
    def has_full_tashkeel(self) -> bool:
        """True if density suggests fully vowelized text (>0.3 is typical)."""
        return self.density >= 0.3

    @property
    def short_vowel_count(self) -> int:
        return sum(self.frequencies.get(n, 0) for n in ('fatha', 'damma', 'kasra'))

    @property
    def tanwin_count(self) -> int:
        return sum(self.frequencies.get(n, 0) for n in ('fathatan', 'dammatan', 'kasratan'))


# ============================================================================
# Analyzer
# ============================================================================

class TashkeelAnalyzer:
    """Analyzer for Arabic diacritical marks (tashkeel/harakat).

    Provides extraction, stripping, density computation, and positional
    analysis of diacritics in Quranic and general Arabic text.
    """

    # Compiled regex for diacritic detection
    _diacritic_re = _TASHKEEL_RE

    # Full vocabulary of recognized diacritics
    VOCABULARY = Diacritic.ALL_MARKS

    def analyze_verse(self, text: str) -> TashkeelAnalysis:
        """Extract all diacritical marks with positions, types, and frequencies.

        Args:
            text: Arabic text (typically a Quranic verse).

        Returns:
            TashkeelAnalysis with full positional and frequency data.
        """
        positions: List[DiacriticPosition] = []
        frequencies: Dict[str, int] = {}
        category_frequencies: Dict[str, int] = {}

        total_chars = len(text)
        base_char = ''

        for i, ch in enumerate(text):
            if ch in Diacritic.ALL_MARKS:
                name = DIACRITIC_NAMES.get(ch, 'unknown')
                category = DIACRITIC_CATEGORIES.get(name, 'other')

                positions.append(DiacriticPosition(
                    char=ch,
                    name=name,
                    category=category,
                    position=i,
                    base_char=base_char,
                ))

                frequencies[name] = frequencies.get(name, 0) + 1
                category_frequencies[category] = category_frequencies.get(category, 0) + 1
            else:
                base_char = ch

        total_diacritics = len(positions)
        density = total_diacritics / total_chars if total_chars > 0 else 0.0

        return TashkeelAnalysis(
            text=text,
            total_chars=total_chars,
            total_diacritics=total_diacritics,
            positions=positions,
            frequencies=frequencies,
            category_frequencies=category_frequencies,
            density=density,
        )

    def strip_tashkeel(self, text: str) -> str:
        """Remove all diacritical marks from text.

        Strips Unicode range U+064B-U+065F and U+0670 (superscript alef).

        Args:
            text: Arabic text with diacritics.

        Returns:
            Text with all tashkeel removed.
        """
        return self._diacritic_re.sub('', text)

    def tashkeel_density(self, text: str) -> float:
        """Compute ratio of diacritical marks to total characters.

        A fully vowelized Quranic text typically has density 0.30-0.45.
        Unvowelized modern Arabic is near 0.0.

        Args:
            text: Arabic text.

        Returns:
            Float ratio in [0.0, 1.0].
        """
        if not text:
            return 0.0
        diacritic_count = len(self._diacritic_re.findall(text))
        return diacritic_count / len(text)

    def compare_tashkeel(self, text_a: str, text_b: str) -> Dict[str, any]:
        """Compare diacritical patterns between two text variants.

        Useful for comparing qiraat (variant readings) that differ in
        vowelization but share the same consonantal skeleton (rasm).

        Args:
            text_a: First text variant.
            text_b: Second text variant.

        Returns:
            Dict with shared count, unique to each, and Jaccard similarity.
        """
        analysis_a = self.analyze_verse(text_a)
        analysis_b = self.analyze_verse(text_b)

        names_a = set(analysis_a.frequencies.keys())
        names_b = set(analysis_b.frequencies.keys())

        shared = names_a & names_b
        only_a = names_a - names_b
        only_b = names_b - names_a

        union = names_a | names_b
        jaccard = len(shared) / len(union) if union else 1.0

        return {
            'shared_types': shared,
            'only_in_a': only_a,
            'only_in_b': only_b,
            'jaccard_similarity': jaccard,
            'density_a': analysis_a.density,
            'density_b': analysis_b.density,
        }

    def extract_vowel_pattern(self, word: str) -> str:
        """Extract the vowel pattern of a word as a compact string.

        Encodes: f=fatha, d=damma, k=kasra, F=fathatan, D=dammatan,
        K=kasratan, s=sukun, S=shadda, .=consonant (no mark).

        Args:
            word: Single Arabic word.

        Returns:
            Pattern string like "f.dk" for a 4-consonant word.
        """
        _map = {
            Diacritic.FATHA: 'f', Diacritic.DAMMA: 'd', Diacritic.KASRA: 'k',
            Diacritic.FATHATAN: 'F', Diacritic.DAMMATAN: 'D', Diacritic.KASRATAN: 'K',
            Diacritic.SUKUN: 's', Diacritic.SHADDA: 'S',
        }
        pattern = []
        pending_consonant = False
        for ch in word:
            if ch in Diacritic.ALL_MARKS:
                code = _map.get(ch, '?')
                pattern.append(code)
                pending_consonant = False
            elif not ch.isspace():
                if pending_consonant:
                    pattern.append('.')
                pending_consonant = True

        if pending_consonant:
            pattern.append('.')

        return ''.join(pattern)
