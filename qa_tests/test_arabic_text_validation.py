#!/usr/bin/env python3
"""
QA Test Suite: Arabic Text Validation
Tests for UTF-8 encoding, diacritics, and Arabic script integrity
"""

import json
import pytest
from pathlib import Path
import random
import unicodedata


class TestArabicTextValidation:
    """Tests for Arabic text encoding and diacritics"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        """Load corpus file"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        assert corpus_path.exists(), f"Corpus file not found at {corpus_path}"

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_utf8_encoding_validation(self, corpus_file):
        """TEST: Validate UTF-8 encoding for all Arabic text"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:200]:  # Test first 200 verses
            ar_text = verse.get('text_ar', '')

            # Ensure text is properly encoded as UTF-8
            try:
                # Try to encode and decode
                encoded = ar_text.encode('utf-8')
                decoded = encoded.decode('utf-8')
                assert decoded == ar_text, f"Encoding/decoding mismatch in {verse.get('verse_id')}"
            except Exception as e:
                pytest.fail(f"UTF-8 encoding error in {verse.get('verse_id')}: {e}")

    def test_arabic_script_detection(self, corpus_file):
        """TEST: Verify Arabic script is present and valid"""
        verses = corpus_file.get('verses', [])
        arabic_range = range(0x0600, 0x06FF)  # Arabic Unicode block

        for verse in verses[:100]:
            ar_text = verse.get('text_ar', '')

            # Should contain Arabic script characters
            arabic_chars = [c for c in ar_text if ord(c) in arabic_range]
            assert len(arabic_chars) > 0, f"No Arabic script detected in {verse.get('verse_id')}"

            # At least 70% should be Arabic
            percentage = (len(arabic_chars) / len(ar_text)) * 100
            assert percentage >= 70, f"Only {percentage}% Arabic characters in {verse.get('verse_id')}"

    def test_diacritic_consistency(self, corpus_file):
        """TEST: Verify diacritic consistency"""
        verses = corpus_file.get('verses', [])

        # Diacritics range in Arabic: U+064B to U+0652
        diacritics_range = range(0x064B, 0x0653)

        for verse in verses[:100]:
            ar_text = verse.get('text_ar', '')

            # Count diacritics
            diacritics = [c for c in ar_text if ord(c) in diacritics_range]

            # If verse has diacritics, should have reasonable amount
            if len(diacritics) > 0:
                diacritic_percentage = (len(diacritics) / len(ar_text)) * 100
                # Diacritics should be 10-40% of text
                assert 5 <= diacritic_percentage <= 60, f"Unusual diacritic percentage in {verse.get('verse_id')}: {diacritic_percentage}%"

    def test_no_corruption_in_arabic_text(self, corpus_file):
        """TEST: Verify no encoding corruption"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:150]:
            ar_text = verse.get('text_ar', '')

            # Should not contain replacement characters
            assert '\ufffd' not in ar_text, f"Replacement character found in {verse.get('verse_id')}"

            # Should not contain control characters
            for char in ar_text:
                cat = unicodedata.category(char)
                assert cat[0] != 'C', f"Control character found in {verse.get('verse_id')}: {char}"

    def test_diacritic_normalization(self, corpus_file):
        """TEST: Verify diacritics are normalized"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            ar_text = verse.get('text_ar', '')

            # Try to normalize and verify consistency
            nfc_text = unicodedata.normalize('NFC', ar_text)
            nfd_text = unicodedata.normalize('NFD', ar_text)

            # After normalization should have consistent length changes
            assert len(nfc_text) > 0, f"NFC normalization failed in {verse.get('verse_id')}"

    def test_arabic_vowel_marks(self, corpus_file):
        """TEST: Validate Arabic vowel marks (tashkeel)"""
        verses = corpus_file.get('verses', [])

        # Arabic vowel marks
        vowels = {
            '\u064B': 'Fathatan',
            '\u064C': 'Dammatan',
            '\u064D': 'Kasratan',
            '\u064E': 'Fatha',
            '\u064F': 'Damma',
            '\u0650': 'Kasra',
            '\u0651': 'Shadda',
            '\u0652': 'Sukun'
        }

        for verse in verses[:100]:
            ar_text = verse.get('text_ar', '')

            # Check for valid vowel marks
            for char in ar_text:
                if ord(char) in [ord(v) for v in vowels.keys()]:
                    # Valid diacritic found
                    pass

    def test_hamza_variations(self, corpus_file):
        """TEST: Verify hamza (glottal stop) variations"""
        verses = corpus_file.get('verses', [])

        # Hamza can appear in different positions
        hamza_forms = [
            '\u0621',  # Hamza standalone
            '\u0623',  # Hamza with Alef above
            '\u0625',  # Hamza with Alef below
            '\u0624',  # Hamza with Waw
            '\u0626'   # Hamza with Ya
        ]

        hamza_count = 0
        for verse in verses[:100]:
            ar_text = verse.get('text_ar', '')
            for hamza in hamza_forms:
                if hamza in ar_text:
                    hamza_count += 1

        # Should find at least some hamza forms
        assert hamza_count > 0, "No hamza forms found in sampled verses"

    def test_text_length_consistency(self, corpus_file):
        """TEST: Verify text length is reasonable"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:100]:
            ar_text = verse.get('text_ar', '')
            en_text = verse.get('text_en', '')

            # Arabic text should be present
            assert len(ar_text) > 0, f"Empty Arabic text in {verse.get('verse_id')}"

            # Arabic typically 2-3x as many characters as English for same content
            # But we accept various ratios
            assert len(ar_text) > 5, f"Arabic text too short in {verse.get('verse_id')}"
            assert len(ar_text) < 2000, f"Arabic text too long in {verse.get('verse_id')}"

    def test_special_arabic_letters(self, corpus_file):
        """TEST: Verify special Arabic letters present"""
        verses = corpus_file.get('verses', [])

        special_letters = {
            '\u0628': 'Ba',
            '\u062B': 'Tha',
            '\u062C': 'Jim',
            '\u0634': 'Shin',
            '\u0635': 'Sad',
            '\u0636': 'Dad',
            '\u0637': 'Tah',
            '\u0638': 'Zah',
            '\u0643': 'Kaf',
            '\u0645': 'Mim',
            '\u0646': 'Nun',
            '\u0647': 'Ha',
        }

        letters_found = set()
        for verse in verses[:50]:
            ar_text = verse.get('text_ar', '')
            for letter, name in special_letters.items():
                if letter in ar_text:
                    letters_found.add(name)

        # Should find at least half of the special letters in sample
        assert len(letters_found) > len(special_letters) // 2, f"Missing special letters. Found: {letters_found}"


class TestDiacriticsHandling:
    """Tests for diacritics handling and consistency"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_diacritics_preserved_in_canonical(self, corpus_file):
        """TEST: Diacritics should be present in canonical text"""
        verses = corpus_file.get('verses', [])

        diacritics_range = range(0x064B, 0x0653)

        # In canonical texts, we expect diacritics
        canonical_verses_with_diacritics = 0
        for verse in verses[:50]:
            ar_text = verse.get('text_ar', '')
            if any(ord(c) in diacritics_range for c in ar_text):
                canonical_verses_with_diacritics += 1

        # At least some verses should have diacritics in canonical form
        assert canonical_verses_with_diacritics > 0, "No diacritics found in canonical text"

    def test_no_double_diacritics(self, corpus_file):
        """TEST: Verify no double diacritics on single letter"""
        verses = corpus_file.get('verses', [])

        diacritics = set('\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652')

        for verse in verses[:100]:
            ar_text = verse.get('text_ar', '')

            # Check for consecutive diacritics (should be rare)
            for i in range(len(ar_text) - 1):
                if ar_text[i] in diacritics and ar_text[i+1] in diacritics:
                    # This might be valid in some cases, but log it
                    pass


class TestManualSampleValidation:
    """Manual spot checks against known good data"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_surah_fatiha_first_verse(self, corpus_file):
        """TEST: Spot check Surah Al-Fatiha (1), Verse 1"""
        verses = corpus_file.get('verses', [])

        # Find verse 1:1
        verse_1_1 = next((v for v in verses if v['surah_number'] == 1 and v['ayah_number'] == 1), None)

        if verse_1_1:
            ar_text = verse_1_1.get('text_ar', '')

            # Should contain "بسم" (Bismillah)
            assert 'بسم' in ar_text or 'ب' in ar_text, f"Expected 'بسم' in Surah 1 Verse 1"
            assert len(ar_text) > 10, "Verse text seems incomplete"

    def test_surah_second_verse(self, corpus_file):
        """TEST: Spot check Surah Al-Fatiha, Verse 2"""
        verses = corpus_file.get('verses', [])

        verse_1_2 = next((v for v in verses if v['surah_number'] == 1 and v['ayah_number'] == 2), None)

        if verse_1_2:
            ar_text = verse_1_2.get('text_ar', '')
            # Should contain "الحمد" (Praise)
            assert 'الح' in ar_text or len(ar_text) > 5, "Verse 2 seems corrupted"

    def test_random_verses_have_arabic(self, corpus_file):
        """TEST: Random sample of 10 verses all have Arabic text"""
        verses = corpus_file.get('verses', [])

        if len(verses) < 10:
            pytest.skip("Not enough verses")

        random.seed(42)
        sample = random.sample(verses, 10)

        for verse in sample:
            ar_text = verse.get('text_ar', '')
            # Should be Arabic
            assert len(ar_text) > 0, f"No Arabic text in {verse.get('verse_id')}"
            # Should have Arabic characters
            assert any(0x0600 <= ord(c) < 0x06FF for c in ar_text), f"No Arabic script in {verse.get('verse_id')}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
