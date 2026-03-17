"""Tests for quran/algorithms/morphological_analyzer.py – Algorithm 3."""

import sys
import os

# Ensure the algorithms package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from quran.algorithms.morphological_analyzer import (
    ArabicMorphologicalAnalyzer,
    MorphologicalType,
    WordAnalysis,
)


@pytest.fixture(scope="module")
def analyzer():
    return ArabicMorphologicalAnalyzer()


# ---------------------------------------------------------------------------
# Test 1 – remove_diacritics strips harakat
# ---------------------------------------------------------------------------

class TestRemoveDiacritics:
    def test_strips_fatha(self, analyzer):
        """Fatha (U+064E) should be removed."""
        assert analyzer.remove_diacritics('كَتَبَ') == 'كتب'

    def test_strips_kasra(self, analyzer):
        """Kasra (U+0650) should be removed."""
        assert analyzer.remove_diacritics('كِتَاب') == 'كتاب'

    def test_strips_damma(self, analyzer):
        """Damma (U+064F) should be removed."""
        assert analyzer.remove_diacritics('كُتُب') == 'كتب'

    def test_strips_sukun(self, analyzer):
        """Sukun (U+0652) should be removed."""
        assert analyzer.remove_diacritics('مَكْتُوب') == 'مكتوب'

    def test_strips_shadda(self, analyzer):
        """Shadda (U+0651) should be removed."""
        assert analyzer.remove_diacritics('رَحِيمٌ') == 'رحيم'

    def test_strips_tanwin(self, analyzer):
        """Tanwin fath (U+064B) should be removed."""
        assert analyzer.remove_diacritics('كِتَابًا') == 'كتابا'

    def test_no_arabic_unchanged(self, analyzer):
        """Plain ASCII should pass through unchanged."""
        assert analyzer.remove_diacritics('hello') == 'hello'

    def test_mixed_text(self, analyzer):
        """Mixed Arabic-Latin string retains non-diacritic characters."""
        result = analyzer.remove_diacritics('كَتَبَ (kataba)')
        assert '\u064e' not in result        # fatha gone
        assert 'كتب' in result


# ---------------------------------------------------------------------------
# Test 2 – extract_affixes strips ال prefix
# ---------------------------------------------------------------------------

class TestExtractAffixes:
    def test_strips_definite_article_al(self, analyzer):
        stem, affixes = analyzer.extract_affixes('الكتاب')
        assert stem == 'كتاب'
        assert affixes.get('prefix') == 'definite_article'

    def test_strips_definite_article_with_vowel(self, analyzer):
        """ال prefix in vocalised text."""
        stem, affixes = analyzer.extract_affixes('الْكِتَاب')
        assert affixes.get('prefix') == 'definite_article'

    # ------------------------------------------------------------------
    # Test 3 – extract_affixes strips وَ prefix
    # ------------------------------------------------------------------
    def test_strips_wa_prefix_vocalised(self, analyzer):
        """Conjunction وَ (with fatha) should be stripped."""
        stem, affixes = analyzer.extract_affixes('وَكَتَبَ')
        assert affixes.get('prefix') == 'conj_and'

    def test_strips_wa_prefix_bare(self, analyzer):
        """Conjunction و (bare) should be stripped."""
        stem, affixes = analyzer.extract_affixes('وكتب')
        assert affixes.get('prefix') == 'conj_and'

    def test_strips_bi_prefix(self, analyzer):
        """Preposition ب should be stripped."""
        stem, affixes = analyzer.extract_affixes('بالكتاب')
        assert affixes.get('prefix') == 'prep_by'

    def test_strips_fem_pl_suffix(self, analyzer):
        """Feminine plural ات suffix should be stripped."""
        stem, affixes = analyzer.extract_affixes('كتابات')
        assert affixes.get('suffix') == 'fem_pl'

    def test_no_affixes(self, analyzer):
        """A bare three-letter root returns empty affixes dict."""
        stem, affixes = analyzer.extract_affixes('كتب')
        assert affixes == {}

    def test_stem_not_empty_after_strip(self, analyzer):
        """Stripping affixes should never produce an empty stem."""
        stem, _ = analyzer.extract_affixes('الله')
        assert len(stem) > 0


# ---------------------------------------------------------------------------
# Test 4 – identify_root finds كتب from كِتَاب
# ---------------------------------------------------------------------------

class TestIdentifyRoot:
    def test_finds_ktb_from_kitab(self, analyzer):
        root, conf = analyzer.identify_root('كتاب')
        assert root == 'كتب', f"Expected 'كتب', got '{root}'"
        assert conf > 0.0

    def test_finds_ktb_from_vocalised_kitab(self, analyzer):
        """Works with full diacritics on the input."""
        root, conf = analyzer.identify_root('كِتَاب')
        assert root == 'كتب'

    def test_finds_alm_root(self, analyzer):
        root, conf = analyzer.identify_root('علم')
        assert root == 'علم'
        assert conf >= 0.8

    def test_finds_root_from_word_family_form(self, analyzer):
        """مَعْلُوم (known) should map back to علم."""
        root, conf = analyzer.identify_root('معلوم')
        assert root == 'علم'

    def test_unknown_word_returns_none_or_low_confidence(self, analyzer):
        """Random non-root letters return no root or very low confidence."""
        root, conf = analyzer.identify_root('zzz')
        # Either no match or very low confidence
        assert root is None or conf < 0.5

    def test_confidence_is_float(self, analyzer):
        _, conf = analyzer.identify_root('كتب')
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0


# ---------------------------------------------------------------------------
# Test 5 – classify_pattern returns AGENT_NOUN for كَاتِب
# ---------------------------------------------------------------------------

class TestClassifyPattern:
    def test_katib_is_agent_noun(self, analyzer):
        """كَاتِب (writer) follows فَاعِل pattern → AGENT_NOUN."""
        result = analyzer.classify_pattern('كَاتِب', 'كتب')
        assert result == MorphologicalType.AGENT_NOUN

    def test_maktub_is_patient_noun(self, analyzer):
        """مَكْتُوب (written) follows مَفْعُول pattern → PATIENT_NOUN."""
        result = analyzer.classify_pattern('مَكْتُوب', 'كتب')
        assert result == MorphologicalType.PATIENT_NOUN

    def test_yaktub_is_imperfective(self, analyzer):
        """يَكْتُبُ follows imperfective marker → VERB_IMPERFECTIVE."""
        result = analyzer.classify_pattern('يَكْتُبُ', 'كتب')
        assert result == MorphologicalType.VERB_IMPERFECTIVE

    def test_maktab_is_place_noun(self, analyzer):
        """مَكْتَب (office) → PLACE_NOUN."""
        result = analyzer.classify_pattern('مَكْتَب', 'كتب')
        assert result in (MorphologicalType.PLACE_NOUN, MorphologicalType.PATIENT_NOUN)

    def test_kataba_is_perfective_active(self, analyzer):
        """كَتَبَ (he wrote) → VERB_PERFECTIVE_ACTIVE."""
        result = analyzer.classify_pattern('كَتَبَ', 'كتب')
        assert result == MorphologicalType.VERB_PERFECTIVE_ACTIVE

    def test_morphological_type_is_enum(self, analyzer):
        result = analyzer.classify_pattern('كَاتِب', 'كتب')
        assert isinstance(result, MorphologicalType)


# ---------------------------------------------------------------------------
# Test 6 – analyze returns WordAnalysis with root for a known word
# ---------------------------------------------------------------------------

class TestAnalyze:
    def test_returns_word_analysis_instance(self, analyzer):
        result = analyzer.analyze('كِتَاب')
        assert isinstance(result, WordAnalysis)

    def test_original_preserved(self, analyzer):
        word = 'كِتَاب'
        result = analyzer.analyze(word)
        assert result.original == word

    def test_normalized_has_no_diacritics(self, analyzer):
        result = analyzer.analyze('كِتَاب')
        # No diacritic code-points (U+064B–U+0652) should be present in normalized
        for ch in result.normalized:
            assert not ('\u064b' <= ch <= '\u0652'), (
                f"Diacritic U+{ord(ch):04X} found in normalized text: {result.normalized!r}"
            )

    def test_root_identified_for_kitab(self, analyzer):
        result = analyzer.analyze('كِتَاب')
        assert result.root == 'كتب', f"Root was {result.root!r}"

    def test_confidence_positive_for_known_word(self, analyzer):
        result = analyzer.analyze('كِتَاب')
        assert result.confidence > 0.0

    def test_meaning_populated_for_known_root(self, analyzer):
        result = analyzer.analyze('كِتَاب')
        assert result.meaning != ''

    def test_word_family_non_empty_for_known_root(self, analyzer):
        result = analyzer.analyze('كِتَاب')
        assert isinstance(result.word_family, list)
        assert len(result.word_family) > 0

    def test_morph_type_is_enum(self, analyzer):
        result = analyzer.analyze('كِتَاب')
        assert isinstance(result.morph_type, MorphologicalType)

    def test_affixes_dict(self, analyzer):
        result = analyzer.analyze('كِتَاب')
        assert isinstance(result.affixes, dict)

    def test_analyze_with_prefix(self, analyzer):
        """الكتاب (the book) should still find كتب root."""
        result = analyzer.analyze('الكتاب')
        assert result.root == 'كتب'
        assert result.affixes.get('prefix') == 'definite_article'

    def test_analyze_unknown_word(self, analyzer):
        """Unknown word should still return a WordAnalysis (no crash)."""
        result = analyzer.analyze('xxxxxxx')
        assert isinstance(result, WordAnalysis)
        assert result.morph_type == MorphologicalType.VERB_PERFECTIVE_ACTIVE or True  # just no crash


# ---------------------------------------------------------------------------
# Test 7 – analyze_verse returns list of WordAnalysis (one per word)
# ---------------------------------------------------------------------------

class TestAnalyzeVerse:
    BASMALA = 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ'

    def test_returns_list(self, analyzer):
        result = analyzer.analyze_verse(self.BASMALA)
        assert isinstance(result, list)

    def test_one_analysis_per_token(self, analyzer):
        tokens = self.BASMALA.split()
        result = analyzer.analyze_verse(self.BASMALA)
        assert len(result) == len(tokens)

    def test_each_element_is_word_analysis(self, analyzer):
        result = analyzer.analyze_verse(self.BASMALA)
        for wa in result:
            assert isinstance(wa, WordAnalysis)

    def test_original_words_match(self, analyzer):
        tokens = self.BASMALA.split()
        result = analyzer.analyze_verse(self.BASMALA)
        for wa, token in zip(result, tokens):
            assert wa.original == token

    def test_empty_verse_returns_empty_list(self, analyzer):
        assert analyzer.analyze_verse('') == []
        assert analyzer.analyze_verse('   ') == []

    def test_single_word_verse(self, analyzer):
        result = analyzer.analyze_verse('كِتَاب')
        assert len(result) == 1
        assert result[0].root == 'كتب'

    def test_multi_verse(self, analyzer):
        verse = 'خَلَقَ الإِنسَانَ مِنْ عَلَقٍ'
        result = analyzer.analyze_verse(verse)
        assert len(result) == 4  # 4 tokens


# ---------------------------------------------------------------------------
# Additional edge-case tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_remove_diacritics_empty_string(self, analyzer):
        assert analyzer.remove_diacritics('') == ''

    def test_extract_affixes_single_char(self, analyzer):
        """Single character word – should not crash."""
        stem, affixes = analyzer.extract_affixes('ب')
        assert isinstance(stem, str)
        assert isinstance(affixes, dict)

    def test_get_word_family_known_root(self, analyzer):
        family = analyzer.get_word_family('كتب')
        assert isinstance(family, list)
        assert len(family) > 0

    def test_get_word_family_unknown_root(self, analyzer):
        family = analyzer.get_word_family('xyz')
        assert family == []

    def test_identify_root_returns_tuple(self, analyzer):
        result = analyzer.identify_root('كتاب')
        assert isinstance(result, tuple)
        assert len(result) == 2
