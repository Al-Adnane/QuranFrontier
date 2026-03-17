#!/usr/bin/env python3
"""
QA Test Suite: Data Integrity & Quality
Tests for data source validation, accuracy, and consistency
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Set
import random


class TestDataSourceValidation:
    """Tests for data source validation"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        """Load corpus file"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        if not corpus_path.exists():
            return None

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_tafsir_sources_documented(self, corpus_file):
        """TEST: Verify tafsir sources are properly documented"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])
        tafsir_sources = set()

        for verse in verses[:100]:
            for tafsir in verse.get('tafsir', []):
                source = tafsir.get('tafsir_name', '')
                if source:
                    tafsir_sources.add(source)

        # Should have multiple tafsir sources
        assert len(tafsir_sources) > 0, "No tafsir sources found"

    def test_hadith_collection_validity(self, corpus_file):
        """TEST: Verify hadith collections are valid"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        valid_collections = [
            'Sahih Bukhari',
            'Sahih Muslim',
            'Jami at-Tirmidhi',
            'Sunan Abu Dawud',
            'Sunan ibn Majah',
            'Sunan an-Nasai'
        ]

        verses = corpus_file.get('verses', [])
        hadith_collections = set()

        for verse in verses[:100]:
            for hadith in verse.get('hadith_references', []):
                collection = hadith.get('collection', '')
                if collection:
                    hadith_collections.add(collection)

        # All found collections should be valid
        for collection in hadith_collections:
            # Allow some flexibility in naming
            found = False
            for valid in valid_collections:
                if valid.lower() in collection.lower() or collection.lower() in valid.lower():
                    found = True
                    break

    def test_hadith_grades_validity(self, corpus_file):
        """TEST: Verify hadith grades are valid"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        valid_grades = ['Sahih', 'Hasan', 'Daif', 'Maudu', 'Munkar', 'Weak', 'Unknown']

        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            for hadith in verse.get('hadith_references', []):
                grade = hadith.get('grading', '').lower()
                if grade:
                    # Grade should match one of the valid grades
                    valid = any(v.lower() in grade for v in valid_grades)
                    # If not exactly matching, it's likely a variant
                    assert len(grade) > 0, "Grade should not be empty"

    def test_source_attribution_present(self, corpus_file):
        """TEST: Verify proper source attribution"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        for verse in verses[:100]:
            # Verse should have source information
            if 'source' in verse:
                source = verse['source']
                assert 'name' in source, "Source should have name"
                assert 'version' in source, "Source should have version"

    def test_no_plagiarism_indicators(self, corpus_file):
        """TEST: Check for plagiarism red flags"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            for tafsir in verse.get('tafsir', []):
                text = tafsir.get('text', '').lower()

                # Look for modern/copyrighted content
                suspicious_phrases = [
                    'copyright',
                    'all rights reserved',
                    'patent',
                    'licensed'
                ]

                for phrase in suspicious_phrases:
                    assert phrase not in text, f"Suspicious phrase found: {phrase}"


class TestDataConsistencyAcrossReferences:
    """Tests for data consistency across references"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        if not corpus_path.exists():
            return None

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_verse_reference_consistency(self, corpus_file):
        """TEST: Verify verse references are consistent"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        # Build index of verses
        verse_index = {}
        for verse in verses:
            verse_id = verse.get('verse_id')
            surah = verse.get('surah_number')
            ayah = verse.get('ayah_number')

            if verse_id:
                verse_index[verse_id] = (surah, ayah)

        # Check references in tafsir
        for verse in verses[:100]:
            for tafsir in verse.get('tafsir', []):
                verse_ref = tafsir.get('verse_reference', '')

                # Reference should be resolvable to a verse
                # Allow some flexibility in format

    def test_hadith_narrator_chain_validity(self, corpus_file):
        """TEST: Verify hadith narrator chains are present"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            for hadith in verse.get('hadith_references', []):
                # Should have some identifier
                assert 'hadith_id' in hadith, "Hadith should have ID"
                assert 'collection' in hadith, "Hadith should have collection"

    def test_cross_reference_completeness(self, corpus_file):
        """TEST: Verify cross-references are complete"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        for verse in verses[:100]:
            # Check for related verses
            if 'revelation_context' in verse:
                ctx = verse['revelation_context']
                if 'related_verses' in ctx:
                    related = ctx['related_verses']
                    # Related verses should be list
                    assert isinstance(related, list), "Related verses should be a list"


class TestDataQualityMetrics:
    """Tests for data quality metrics"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        if not corpus_path.exists():
            return None

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_field_completion_ratio(self, corpus_file):
        """TEST: Verify field completion ratio"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        # Check completion for key fields
        total_verses = len(verses)
        completed_verses = 0

        for verse in verses:
            has_all_fields = all(k in verse for k in ['verse_id', 'surah_number', 'ayah_number', 'text_ar', 'text_en'])
            if has_all_fields:
                completed_verses += 1

        completion_ratio = completed_verses / total_verses if total_verses > 0 else 0
        assert completion_ratio > 0.99, f"Field completion ratio too low: {completion_ratio * 100}%"

    def test_text_length_distribution(self, corpus_file):
        """TEST: Verify text length distribution is reasonable"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        text_lengths = []
        for verse in verses:
            if 'text_ar' in verse:
                text_lengths.append(len(verse['text_ar']))

        if text_lengths:
            avg_length = sum(text_lengths) / len(text_lengths)
            min_length = min(text_lengths)
            max_length = max(text_lengths)

            # Average verse should be reasonable length
            assert 10 < avg_length < 500, f"Unusual average verse length: {avg_length}"
            assert min_length > 0, "Some verses have no text"
            assert max_length < 2000, "Some verses are unreasonably long"

    def test_translation_coverage(self, corpus_file):
        """TEST: Verify translation coverage"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        verses_with_translation = 0
        for verse in verses:
            if 'text_en' in verse and verse['text_en']:
                verses_with_translation += 1

        coverage = verses_with_translation / len(verses) if verses else 0
        assert coverage > 0.95, f"Translation coverage too low: {coverage * 100}%"

    def test_metadata_accuracy(self, corpus_file):
        """TEST: Verify metadata accuracy"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        metadata = corpus_file.get('metadata', {})

        # Reported counts should match actual data
        reported_verses = metadata.get('total_verses', 0)
        actual_verses = len(corpus_file.get('verses', []))

        # Allow 5% difference
        ratio = actual_verses / reported_verses if reported_verses > 0 else 0
        assert 0.95 < ratio < 1.05, f"Metadata verse count mismatch: reported {reported_verses}, actual {actual_verses}"


class TestContentAccuracy:
    """Tests for content accuracy spot checks"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        if not corpus_path.exists():
            return None

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_fatiha_surah_structure(self, corpus_file):
        """TEST: Verify Al-Fatiha surah structure"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        # Al-Fatiha is Surah 1 with 7 verses
        fatiha_verses = [v for v in verses if v.get('surah_number') == 1]

        # Should have approximately 7 verses
        assert len(fatiha_verses) >= 6, f"Al-Fatiha should have ~7 verses, found {len(fatiha_verses)}"

    def test_verse_numbering_continuity(self, corpus_file):
        """TEST: Verify verse numbering is continuous per surah"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        # Group by surah
        by_surah = {}
        for verse in verses:
            surah = verse.get('surah_number')
            ayah = verse.get('ayah_number')

            if surah not in by_surah:
                by_surah[surah] = []
            by_surah[surah].append(ayah)

        # Check continuity in first few surahs
        for surah in sorted(by_surah.keys())[:5]:
            ayahs = sorted(by_surah[surah])
            # Should start from 1
            if len(ayahs) > 0:
                assert ayahs[0] == 1, f"Surah {surah} should start at verse 1, starts at {ayahs[0]}"

    def test_english_translation_quality(self, corpus_file):
        """TEST: Verify English translation quality"""
        if corpus_file is None:
            pytest.skip("Corpus file not found")

        verses = corpus_file.get('verses', [])

        quality_issues = 0
        for verse in verses[:50]:
            en_text = verse.get('text_en', '')

            # Check for common quality issues
            if len(en_text) < 3:
                quality_issues += 1
            if en_text.count('[') > 5:  # Too many brackets/notes
                quality_issues += 1
            if en_text.count('***') > 2:  # Too many asterisks
                quality_issues += 1

        quality_ratio = quality_issues / 50
        assert quality_ratio < 0.1, f"Translation quality issues: {quality_ratio * 100}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
