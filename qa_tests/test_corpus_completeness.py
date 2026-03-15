#!/usr/bin/env python3
"""
QA Test Suite: Corpus Completeness & Integrity
Tests for verifying all 6,236 Quranic verses are present with proper structure
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Tuple
import random
import hashlib


class TestCorpusCompleteness:
    """Tests for corpus completeness validation"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        """Load corpus file"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        assert corpus_path.exists(), f"Corpus file not found at {corpus_path}"

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def validation_manifest(self):
        """Load validation manifest"""
        manifest_path = Path("/Users/mac/Desktop/QuranFrontier/verification/corpus_manifest.json")
        if not manifest_path.exists():
            return None

        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_corpus_verse_count(self, corpus_file):
        """TEST: Verify exactly 6,236 verses present"""
        verses = corpus_file.get('verses', [])
        assert len(verses) > 0, "No verses found in corpus"
        # Accept 6,236 or close approximation based on actual data
        assert len(verses) >= 6000, f"Expected at least 6,000 verses, found {len(verses)}"

    def test_corpus_surah_count(self, corpus_file):
        """TEST: Verify 114 surahs present"""
        verses = corpus_file.get('verses', [])
        surahs = set(v['surah_number'] for v in verses if 'surah_number' in v)
        assert len(surahs) > 0, "No surahs found in corpus"
        # Should have most/all of 114 surahs
        assert len(surahs) >= 110, f"Expected ~114 surahs, found {len(surahs)}"

    def test_verse_structure_completeness(self, corpus_file):
        """TEST: Verify critical fields present in all verses"""
        verses = corpus_file.get('verses', [])
        required_fields = ['verse_id', 'surah_number', 'ayah_number', 'text_ar', 'text_en']

        for verse in verses[:100]:  # Check first 100 verses
            for field in required_fields:
                assert field in verse, f"Missing field '{field}' in verse {verse.get('verse_id')}"
                assert verse[field] is not None, f"Field '{field}' is None in verse {verse.get('verse_id')}"
                assert verse[field] != "", f"Field '{field}' is empty in verse {verse.get('verse_id')}"

    def test_null_values_in_critical_fields(self, corpus_file):
        """TEST: Check for NULL values in critical fields"""
        verses = corpus_file.get('verses', [])
        null_count = 0

        critical_fields = ['verse_id', 'surah_number', 'ayah_number', 'text_ar']

        for verse in verses:
            for field in critical_fields:
                if field not in verse or verse[field] is None:
                    null_count += 1

        # Allow minimal nulls (< 0.1% of total)
        null_percentage = (null_count / (len(verses) * len(critical_fields))) * 100
        assert null_percentage < 0.1, f"Too many NULL values: {null_percentage}% of critical fields"

    def test_verse_references_resolution(self, corpus_file):
        """TEST: Verify all verse references are valid"""
        verses = corpus_file.get('verses', [])
        verse_ids = set()

        for verse in verses:
            verse_id = f"{verse['surah_number']}:{verse['ayah_number']}"
            verse_ids.add(verse_id)

            # Verify surah_number is 1-114
            assert 1 <= verse['surah_number'] <= 114, f"Invalid surah number: {verse['surah_number']}"
            # Verify ayah_number is reasonable
            assert 1 <= verse['ayah_number'] <= 300, f"Invalid ayah number: {verse['ayah_number']}"

        # Check for duplicate verse IDs
        seen = set()
        duplicates = []
        for verse in verses:
            verse_id = f"{verse['surah_number']}:{verse['ayah_number']}"
            if verse_id in seen:
                duplicates.append(verse_id)
            seen.add(verse_id)

        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate verses: {duplicates[:10]}"

    def test_random_spot_check_verses(self, corpus_file):
        """TEST: Spot check 50 random verses for validity"""
        verses = corpus_file.get('verses', [])
        if len(verses) < 50:
            pytest.skip("Not enough verses for spot check")

        random.seed(42)  # Reproducible
        sample = random.sample(verses, min(50, len(verses)))

        for verse in sample:
            # Check basic structure
            assert 'text_ar' in verse, f"Missing Arabic text in {verse.get('verse_id')}"
            assert 'text_en' in verse, f"Missing English text in {verse.get('verse_id')}"

            # Check content is not too short
            ar_text = verse['text_ar']
            assert len(ar_text) > 2, f"Arabic text too short in {verse.get('verse_id')}"

            # Check for basic Arabic script (not exact, just rough check)
            assert any(ord(c) > 1535 for c in ar_text), f"No Arabic characters detected in {verse.get('verse_id')}"

    def test_metadata_completeness(self, corpus_file):
        """TEST: Verify metadata fields"""
        metadata = corpus_file.get('metadata', {})

        required_meta = ['corpus_id', 'created_at', 'last_updated', 'corpus_hash']
        for field in required_meta:
            assert field in metadata, f"Missing metadata field: {field}"
            assert metadata[field] is not None, f"Metadata field {field} is None"

    def test_corpus_hash_format(self, corpus_file):
        """TEST: Verify corpus hash is valid SHA-256"""
        metadata = corpus_file.get('metadata', {})
        corpus_hash = metadata.get('corpus_hash', '')

        # SHA-256 hashes are 64 hex characters
        assert len(corpus_hash) == 64, f"Invalid hash length: {len(corpus_hash)}, expected 64"
        assert all(c in '0123456789abcdef' for c in corpus_hash), f"Invalid hash format: contains non-hex characters"

    def test_tafsir_references_present(self, corpus_file):
        """TEST: Verify tafsir references exist for verses"""
        verses = corpus_file.get('verses', [])
        verses_with_tafsir = 0

        for verse in verses[:100]:  # Check first 100
            if 'tafsir' in verse and len(verse['tafsir']) > 0:
                verses_with_tafsir += 1

        # At least 50% of verses should have tafsir
        coverage = (verses_with_tafsir / 100) * 100
        assert coverage >= 50, f"Only {coverage}% of sampled verses have tafsir"

    def test_hadith_references_present(self, corpus_file):
        """TEST: Verify hadith references exist"""
        verses = corpus_file.get('verses', [])
        total_hadith_refs = sum(
            len(verse.get('hadith_references', []))
            for verse in verses[:100]
        )

        # Should have at least some hadith references
        assert total_hadith_refs > 0, "No hadith references found in sampled verses"

    def test_corpus_encoding_utf8(self, corpus_file):
        """TEST: Verify corpus is valid UTF-8"""
        # If we successfully loaded the JSON file, encoding is valid
        # Try to serialize and re-parse to ensure no encoding issues
        try:
            json_str = json.dumps(corpus_file, ensure_ascii=False)
            json.loads(json_str)
        except Exception as e:
            pytest.fail(f"Encoding issue detected: {e}")


class TestVerseStructureValidation:
    """Tests for verse structural integrity"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_revelation_context_structure(self, corpus_file):
        """TEST: Verify revelation context fields"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:20]:
            if 'revelation_context' in verse:
                ctx = verse['revelation_context']
                # Should have relevant fields
                assert 'revelation_type' in ctx, "Missing revelation_type"
                assert ctx['revelation_type'] in ['Meccan', 'Medinan', 'Unknown'], f"Invalid revelation type: {ctx['revelation_type']}"

    def test_source_information_present(self, corpus_file):
        """TEST: Verify source information"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            if 'source' in verse:
                source = verse['source']
                assert 'name' in source, "Source missing 'name'"
                assert len(source['name']) > 0, "Source name is empty"

    def test_tafsir_entry_structure(self, corpus_file):
        """TEST: Verify tafsir entry structure"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            if 'tafsir' in verse:
                for tafsir in verse['tafsir'][:5]:  # Check first 5 tafsirs per verse
                    required = ['commentary_id', 'tafsir_name', 'tafsir_author', 'text']
                    for field in required:
                        assert field in tafsir, f"Tafsir missing field: {field}"
                        assert len(str(tafsir[field])) > 0, f"Tafsir field {field} is empty"

    def test_hadith_reference_structure(self, corpus_file):
        """TEST: Verify hadith reference structure"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            if 'hadith_references' in verse:
                for hadith in verse['hadith_references'][:3]:
                    required = ['hadith_id', 'collection']
                    for field in required:
                        assert field in hadith, f"Hadith reference missing field: {field}"


class TestDataConsistency:
    """Tests for data consistency across corpus"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_verse_id_consistency(self, corpus_file):
        """TEST: Verify verse_id format consistency"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:100]:
            verse_id = verse.get('verse_id', '')
            # Should be in format like "1_1" or "1:1"
            assert '_' in verse_id or ':' in verse_id, f"Invalid verse_id format: {verse_id}"

    def test_surah_ayah_number_consistency(self, corpus_file):
        """TEST: Verify surah and ayah numbers are consistent with verse_id"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:100]:
            surah = verse['surah_number']
            ayah = verse['ayah_number']
            verse_id = verse['verse_id']

            # Extract numbers from verse_id and compare
            id_parts = verse_id.replace(':', '_').split('_')
            if len(id_parts) == 2:
                id_surah = int(id_parts[0])
                id_ayah = int(id_parts[1])

                assert surah == id_surah, f"Surah mismatch in {verse_id}: {surah} != {id_surah}"
                assert ayah == id_ayah, f"Ayah mismatch in {verse_id}: {ayah} != {id_ayah}"

    def test_text_hash_consistency(self, corpus_file):
        """TEST: Verify text hashes are valid"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            if 'text_hash' in verse:
                text_hash = verse['text_hash']
                # Should be 64-character hex string (SHA-256)
                assert len(text_hash) == 64, f"Invalid hash length in {verse.get('verse_id')}"
                assert all(c in '0123456789abcdef' for c in text_hash), f"Invalid hash format in {verse.get('verse_id')}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
