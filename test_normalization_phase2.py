#!/usr/bin/env python3
"""
Phase 2 Normalization - Test-Driven Development
Tests for Unicode NFC normalization, SHA-256 hashing, and file generation
"""

import json
import pytest
import hashlib
import unicodedata
from pathlib import Path
from typing import Dict, List


class TestNormalizationPhase2:
    """Tests for Phase 2 normalization process"""

    @pytest.fixture(scope="module")
    def merged_corpus(self):
        """Load the Phase 1 merged corpus"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        assert corpus_path.exists(), f"Corpus file not found at {corpus_path}"

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def normalized_quran(self):
        """Load normalized_quran.json output"""
        output_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/normalized_quran.json")
        assert output_path.exists(), f"normalized_quran.json not found at {output_path}"

        with open(output_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def normalized_report(self):
        """Load normalization_report.json"""
        report_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/normalization_report.json")
        assert report_path.exists(), f"normalization_report.json not found at {report_path}"

        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_all_verses_normalized_to_unicode_nfc(self, normalized_quran):
        """TEST: Verify all 6,236 verses are in NFC form"""
        verses = normalized_quran.get('verses', [])
        assert len(verses) == 6236, f"Expected 6,236 verses, found {len(verses)}"

        for verse in verses:
            text_ar = verse.get('text_ar', '')

            # Verify text is in NFC form
            nfc_text = unicodedata.normalize('NFC', text_ar)
            assert text_ar == nfc_text, \
                f"Verse {verse.get('verse_id')} is not in NFC form"

            # Verify no diacritics removed from main text
            assert len(text_ar) > 0, f"Verse {verse.get('verse_id')} has empty Arabic text"

    def test_all_verses_have_sha256_hash(self, normalized_quran):
        """TEST: Verify each verse has a SHA-256 hash"""
        verses = normalized_quran.get('verses', [])
        assert len(verses) == 6236, f"Expected 6,236 verses, found {len(verses)}"

        for verse in verses:
            verse_id = verse.get('verse_id')

            # Check hash exists
            assert 'hash' in verse, f"Verse {verse_id} missing 'hash' field"

            verse_hash = verse['hash']
            # SHA-256 produces 64 hex characters
            assert len(verse_hash) == 64, \
                f"Verse {verse_id} hash has invalid length: {len(verse_hash)}"
            assert all(c in '0123456789abcdef' for c in verse_hash), \
                f"Verse {verse_id} hash contains invalid hex characters"

    def test_hash_validation_succeeds(self, normalized_quran):
        """TEST: Verify hashes can be re-computed and match"""
        verses = normalized_quran.get('verses', [])

        for verse in verses[:100]:  # Check first 100 verses
            verse_id = verse.get('verse_id')
            stored_hash = verse.get('hash')

            # Reconstruct the hashable data
            hashable_data = json.dumps({
                'verse_id': verse.get('verse_id'),
                'surah_number': verse.get('surah_number'),
                'ayah_number': verse.get('ayah_number'),
                'text_ar': verse.get('text_ar'),
                'text_en': verse.get('text_en')
            }, ensure_ascii=False, sort_keys=True)

            # Compute hash
            computed_hash = hashlib.sha256(hashable_data.encode('utf-8')).hexdigest()

            # Verify match
            assert computed_hash == stored_hash, \
                f"Verse {verse_id} hash mismatch: stored={stored_hash}, computed={computed_hash}"

    def test_arabic_text_preserved(self, merged_corpus, normalized_quran):
        """TEST: Verify no Arabic text is lost during normalization"""
        original_verses = {v['verse_id']: v for v in merged_corpus.get('verses', [])}
        normalized_verses = {v['verse_id']: v for v in normalized_quran.get('verses', [])}

        # Check all verse IDs match
        assert len(original_verses) == len(normalized_verses), \
            f"Verse count mismatch: original={len(original_verses)}, normalized={len(normalized_verses)}"

        for verse_id in list(original_verses.keys())[:100]:  # Check first 100
            orig = original_verses[verse_id]
            norm = normalized_verses[verse_id]

            orig_text = orig.get('text_ar', '').strip()
            norm_text = norm.get('text_ar', '').strip()

            # Both should be non-empty
            assert len(orig_text) > 0, f"Original verse {verse_id} has empty text"
            assert len(norm_text) > 0, f"Normalized verse {verse_id} has empty text"

            # Length should be similar (within 10% - NFC normalization doesn't change length much)
            length_diff = abs(len(orig_text) - len(norm_text))
            max_diff = max(10, len(orig_text) // 10)
            assert length_diff <= max_diff, \
                f"Verse {verse_id} text length changed too much: {len(orig_text)} -> {len(norm_text)}"

    def test_normalized_files_created(self):
        """TEST: Verify output files exist"""
        required_files = [
            Path("/Users/mac/Desktop/QuranFrontier/corpus/normalized_quran.json"),
            Path("/Users/mac/Desktop/QuranFrontier/corpus/normalized_tafsir.json"),
            Path("/Users/mac/Desktop/QuranFrontier/corpus/normalized_hadith.json"),
            Path("/Users/mac/Desktop/QuranFrontier/corpus/normalization_report.json"),
        ]

        for file_path in required_files:
            assert file_path.exists(), f"Required file not found: {file_path}"
            assert file_path.stat().st_size > 0, f"File is empty: {file_path}"

    def test_normalization_metadata_complete(self, normalized_report):
        """TEST: Verify normalization_report.json has all required fields"""
        required_fields = [
            'normalization_id',
            'timestamp',
            'total_verses_processed',
            'total_verses_normalized',
            'unicode_normalization_form',
            'hash_algorithm',
            'output_files',
            'validation_stats'
        ]

        for field in required_fields:
            assert field in normalized_report, \
                f"Missing required field in report: {field}"
            assert normalized_report[field] is not None, \
                f"Report field {field} is None"

    def test_normalization_output_verse_count(self, normalized_report):
        """TEST: Verify report shows correct verse count"""
        total_processed = normalized_report.get('total_verses_processed', 0)
        total_normalized = normalized_report.get('total_verses_normalized', 0)

        assert total_processed == 6236, \
            f"Expected 6,236 verses processed, got {total_processed}"
        assert total_normalized == 6236, \
            f"Expected 6,236 verses normalized, got {total_normalized}"

    def test_nfc_form_specified_in_report(self, normalized_report):
        """TEST: Verify report specifies NFC normalization form"""
        norm_form = normalized_report.get('unicode_normalization_form', '')
        assert 'NFC' in norm_form, \
            f"Expected NFC normalization form, got: {norm_form}"

    def test_sha256_hash_algorithm_in_report(self, normalized_report):
        """TEST: Verify report specifies SHA-256 hash algorithm"""
        hash_algo = normalized_report.get('hash_algorithm', '')
        assert 'SHA-256' in hash_algo or 'sha256' in hash_algo.lower(), \
            f"Expected SHA-256 hash algorithm, got: {hash_algo}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
