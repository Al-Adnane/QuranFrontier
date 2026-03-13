"""Tests for the Quran data layer: metadata, corpus, and cross-references."""

import pytest

from frontierqu.data.quran_metadata import (
    SURAH_METADATA,
    VERSE_COUNTS,
    TOTAL_SURAHS,
    TOTAL_VERSES,
    get_surah_metadata,
    get_verse_count,
)
from frontierqu.data.quran_text import load_quran_corpus
from frontierqu.data.cross_references import CROSS_REFERENCES, THEMATIC_GROUPS


# ---------- Metadata tests ----------

class TestSurahMetadata:
    def test_114_surahs_in_metadata(self):
        assert len(SURAH_METADATA) == 114

    def test_114_surahs_in_verse_counts(self):
        assert len(VERSE_COUNTS) == 114

    def test_verse_counts_sum_to_6236(self):
        assert sum(VERSE_COUNTS.values()) == 6236

    def test_total_constants(self):
        assert TOTAL_SURAHS == 114
        assert TOTAL_VERSES == 6236

    def test_specific_verse_counts(self):
        assert VERSE_COUNTS[1] == 7
        assert VERSE_COUNTS[2] == 286
        assert VERSE_COUNTS[114] == 6

    def test_metadata_verse_counts_match(self):
        """SURAH_METADATA[n]['verses'] must match VERSE_COUNTS[n]."""
        for n in range(1, 115):
            assert SURAH_METADATA[n]["verses"] == VERSE_COUNTS[n], (
                f"Surah {n}: metadata says {SURAH_METADATA[n]['verses']}, "
                f"VERSE_COUNTS says {VERSE_COUNTS[n]}"
            )

    def test_all_surahs_have_required_keys(self):
        required = {"name_ar", "name_en", "verses", "revelation", "type", "themes"}
        for n in range(1, 115):
            assert required.issubset(SURAH_METADATA[n].keys()), (
                f"Surah {n} missing keys: {required - SURAH_METADATA[n].keys()}"
            )

    def test_revelation_types_valid(self):
        valid = {"MECCAN_EARLY", "MECCAN_LATE", "MEDINAN"}
        for n, meta in SURAH_METADATA.items():
            assert meta["revelation"] in valid, (
                f"Surah {n} has invalid revelation type: {meta['revelation']}"
            )

    def test_arabic_names_present(self):
        for n in range(1, 115):
            assert len(SURAH_METADATA[n]["name_ar"]) > 0

    def test_get_surah_metadata_helper(self):
        m = get_surah_metadata(1)
        assert m["name_en"] == "Al-Fatihah"
        assert get_surah_metadata(999) == {}

    def test_get_verse_count_helper(self):
        assert get_verse_count(2) == 286
        assert get_verse_count(999) == 0


# ---------- Corpus tests ----------

class TestQuranCorpus:
    @pytest.fixture(scope="class")
    def corpus(self):
        return load_quran_corpus()

    def test_corpus_has_6236_verses(self, corpus):
        assert len(corpus) == 6236

    def test_every_surah_verse_key_exists(self, corpus):
        for surah, count in VERSE_COUNTS.items():
            for verse in range(1, count + 1):
                assert (surah, verse) in corpus, f"Missing ({surah}, {verse})"

    def test_fatihah_verse1_has_real_arabic(self, corpus):
        v = corpus[(1, 1)]
        assert v["has_real_text"] is True
        assert "\u0628\u0650\u0633\u0652\u0645\u0650" in v["text_ar"]  # bismillah

    def test_ikhlas_has_real_text(self, corpus):
        for verse in range(1, 5):
            assert corpus[(112, verse)]["has_real_text"] is True

    def test_ayat_al_kursi_has_real_text(self, corpus):
        assert corpus[(2, 255)]["has_real_text"] is True

    def test_placeholder_format(self, corpus):
        # A verse without real text should have "surah:verse" placeholder
        v = corpus[(3, 1)]
        assert v["text_ar"] == "3:1"
        assert v["has_real_text"] is False

    def test_verse_data_structure(self, corpus):
        v = corpus[(1, 1)]
        assert v["surah"] == 1
        assert v["verse"] == 1
        assert "text_ar" in v
        assert "has_real_text" in v


# ---------- Cross-reference tests ----------

class TestCrossReferences:
    def test_minimum_cross_references(self):
        assert len(CROSS_REFERENCES) >= 20

    def test_cross_reference_structure(self):
        for ref in CROSS_REFERENCES:
            assert len(ref) == 3
            (s1, v1), (s2, v2), rel = ref
            assert isinstance(s1, int) and isinstance(v1, int)
            assert isinstance(s2, int) and isinstance(v2, int)
            assert isinstance(rel, str) and len(rel) > 0

    def test_minimum_thematic_groups(self):
        assert len(THEMATIC_GROUPS) >= 10

    def test_required_themes_present(self):
        required = {
            "tawhid", "mercy", "justice", "patience", "knowledge",
            "creation", "afterlife", "prayer", "fasting", "charity", "prophets",
        }
        assert required.issubset(THEMATIC_GROUPS.keys())

    def test_thematic_group_entries_are_tuples(self):
        for theme, verses in THEMATIC_GROUPS.items():
            assert len(verses) > 0, f"Theme '{theme}' is empty"
            for entry in verses:
                assert isinstance(entry, tuple) and len(entry) == 2
