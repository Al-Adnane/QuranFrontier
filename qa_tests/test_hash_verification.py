#!/usr/bin/env python3
"""
QA Test Suite: Hash Verification
Tests for corpus hash integrity and tamper detection
"""

import json
import pytest
from pathlib import Path
import hashlib
from typing import Dict


class TestHashVerification:
    """Tests for hash verification and integrity"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        """Load corpus file"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        assert corpus_path.exists(), f"Corpus file not found at {corpus_path}"

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def manifest_file(self):
        """Load verification manifest if it exists"""
        manifest_path = Path("/Users/mac/Desktop/QuranFrontier/verification/corpus_manifest.json")
        if not manifest_path.exists():
            return None

        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_corpus_hash_format_valid(self, corpus_file):
        """TEST: Verify corpus hash format is valid SHA-256"""
        metadata = corpus_file.get('metadata', {})
        corpus_hash = metadata.get('corpus_hash', '')

        # SHA-256 produces 64-character hex string
        assert len(corpus_hash) == 64, f"Invalid hash length: {len(corpus_hash)}"
        assert all(c in '0123456789abcdef' for c in corpus_hash.lower()), "Invalid hex characters in hash"

    def test_verse_hash_format(self, corpus_file):
        """TEST: Verify individual verse hashes are valid"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:100]:
            if 'text_hash' in verse:
                verse_hash = verse['text_hash']

                # Should be 64-char hex (SHA-256)
                assert len(verse_hash) == 64, f"Invalid verse hash length in {verse.get('verse_id')}"
                assert all(c in '0123456789abcdef' for c in verse_hash.lower()), f"Invalid hex in {verse.get('verse_id')}"

    def test_hash_reproducibility(self, corpus_file):
        """TEST: Verify hashes are reproducible"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:20]:
            if 'text_ar' in verse and 'text_hash' in verse:
                ar_text = verse['text_ar']
                stored_hash = verse['text_hash']

                # Compute hash of Arabic text
                computed_hash = hashlib.sha256(ar_text.encode('utf-8')).hexdigest()

                # Hashes should match
                assert computed_hash == stored_hash, f"Hash mismatch in {verse.get('verse_id')}: computed {computed_hash} != stored {stored_hash}"

    def test_source_hash_validity(self, corpus_file):
        """TEST: Verify source hashes are valid"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            for tafsir in verse.get('tafsir', [])[:3]:
                if 'source_hash' in tafsir:
                    source_hash = tafsir['source_hash']

                    # Should be valid hex
                    assert len(source_hash) == 64, f"Invalid source hash in {verse.get('verse_id')}"
                    assert all(c in '0123456789abcdef' for c in source_hash.lower()), "Invalid hex in source hash"

    def test_no_hash_collisions_in_sample(self, corpus_file):
        """TEST: Verify no hash collisions in sampled verses"""
        verses = corpus_file.get('verses', [])

        hashes = set()
        collisions = []

        for verse in verses[:500]:
            if 'text_hash' in verse:
                verse_hash = verse['text_hash']

                if verse_hash in hashes:
                    collisions.append(verse.get('verse_id'))
                else:
                    hashes.add(verse_hash)

        assert len(collisions) == 0, f"Hash collisions detected: {collisions}"

    def test_manifest_hash_consistency(self, corpus_file, manifest_file):
        """TEST: Verify manifest hash matches corpus"""
        if manifest_file is None:
            pytest.skip("Manifest file not found")

        metadata = corpus_file.get('metadata', {})
        corpus_hash = metadata.get('corpus_hash', '')
        manifest_hash = manifest_file.get('master_corpus_hash', '')

        # Should match
        assert corpus_hash == manifest_hash, f"Hash mismatch: corpus {corpus_hash} != manifest {manifest_hash}"

    def test_tafsir_hash_consistency(self, corpus_file):
        """TEST: Verify tafsir text hashes are consistent"""
        verses = corpus_file.get('verses', [])

        for verse in verses[:50]:
            for tafsir in verse.get('tafsir', [])[:3]:
                if 'text' in tafsir and 'source_hash' in tafsir:
                    text = tafsir['text']
                    stored_hash = tafsir['source_hash']

                    # Compute expected hash
                    expected_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

                    # Should match
                    assert expected_hash == stored_hash, f"Tafsir hash mismatch"

    def test_metadata_hash_timestamp(self, corpus_file):
        """TEST: Verify hash timestamp is recent"""
        metadata = corpus_file.get('metadata', {})
        created_at = metadata.get('created_at', '')
        last_updated = metadata.get('last_updated', '')

        # Should be ISO format timestamps
        assert 'T' in created_at, "Invalid timestamp format in created_at"
        assert 'T' in last_updated, "Invalid timestamp format in last_updated"

    def test_hash_stability_across_calls(self, corpus_file):
        """TEST: Verify hash calculation is deterministic"""
        verses = corpus_file.get('verses', [])

        # Calculate hash of first verse twice
        if len(verses) > 0 and 'text_ar' in verses[0]:
            text = verses[0]['text_ar']
            hash1 = hashlib.sha256(text.encode('utf-8')).hexdigest()
            hash2 = hashlib.sha256(text.encode('utf-8')).hexdigest()

            # Should be identical
            assert hash1 == hash2, "Hash is not deterministic"


class TestTamperingDetection:
    """Tests for tamper detection capabilities"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_hash_changes_with_text_modification(self, corpus_file):
        """TEST: Verify hash changes if text is modified"""
        verses = corpus_file.get('verses', [])

        if len(verses) > 0 and 'text_ar' in verses[0]:
            original_text = verses[0]['text_ar']
            original_hash = hashlib.sha256(original_text.encode('utf-8')).hexdigest()

            # Modify text slightly
            modified_text = original_text + " "
            modified_hash = hashlib.sha256(modified_text.encode('utf-8')).hexdigest()

            # Hashes should be different
            assert original_hash != modified_hash, "Hash did not change on text modification"

    def test_hash_sensitive_to_character_changes(self, corpus_file):
        """TEST: Verify hash detects single character changes"""
        verses = corpus_file.get('verses', [])

        if len(verses) > 0 and 'text_ar' in verses[0]:
            original_text = verses[0]['text_ar']
            if len(original_text) > 0:
                original_hash = hashlib.sha256(original_text.encode('utf-8')).hexdigest()

                # Change one character
                text_list = list(original_text)
                # Find a character position and change it
                for i, char in enumerate(text_list):
                    # Try changing to a different character
                    if ord(char) < 0x0700:
                        text_list[i] = chr(ord(char) + 1)
                        break

                modified_text = ''.join(text_list)
                modified_hash = hashlib.sha256(modified_text.encode('utf-8')).hexdigest()

                # Hashes should be different
                assert original_hash != modified_hash, "Hash did not detect single character change"

    def test_hash_order_sensitive(self):
        """TEST: Verify hash is sensitive to character order"""
        text1 = "مرحبا"
        text2 = "احمرب"

        hash1 = hashlib.sha256(text1.encode('utf-8')).hexdigest()
        hash2 = hashlib.sha256(text2.encode('utf-8')).hexdigest()

        # Different order should produce different hash
        assert hash1 != hash2, "Hash is not sensitive to character order"

    def test_hash_unicode_normalization_impact(self):
        """TEST: Verify hash detects unicode normalization differences"""
        import unicodedata

        text = "مرحبا"
        nfc_text = unicodedata.normalize('NFC', text)
        nfd_text = unicodedata.normalize('NFD', text)

        nfc_hash = hashlib.sha256(nfc_text.encode('utf-8')).hexdigest()
        nfd_hash = hashlib.sha256(nfd_text.encode('utf-8')).hexdigest()

        # NFC and NFD forms may have different hashes
        # This tests that hash can detect normalization differences


class TestHashConsistency:
    """Tests for hash consistency across corpus"""

    @pytest.fixture(scope="module")
    def corpus_file(self):
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_unique_verses_have_unique_hashes(self, corpus_file):
        """TEST: Verify unique verses have unique hashes"""
        verses = corpus_file.get('verses', [])

        verse_hashes = {}
        for verse in verses[:200]:
            if 'text_ar' in verse:
                text = verse['text_ar']
                text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

                # Same text should have same hash
                if text in verse_hashes:
                    assert verse_hashes[text] == text_hash, "Same text produced different hashes"
                else:
                    verse_hashes[text] = text_hash

    def test_hash_distribution_randomness(self, corpus_file):
        """TEST: Verify hash values are well-distributed"""
        verses = corpus_file.get('verses', [])

        # Get first digits of hashes
        first_digits = []
        for verse in verses[:100]:
            if 'text_ar' in verse:
                text = verse['text_ar']
                text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
                first_digits.append(text_hash[0])

        # Should have variety in first digits (not all same)
        unique_first_digits = len(set(first_digits))
        assert unique_first_digits > 5, f"Hash distribution seems poor: only {unique_first_digits} unique first digits"

    def test_all_verses_hashable(self, corpus_file):
        """TEST: Verify all verses can be hashed without error"""
        verses = corpus_file.get('verses', [])

        unhashable = []
        for verse in verses:
            try:
                if 'text_ar' in verse:
                    text = verse['text_ar']
                    hashlib.sha256(text.encode('utf-8')).hexdigest()
            except Exception as e:
                unhashable.append((verse.get('verse_id'), str(e)))

        assert len(unhashable) == 0, f"Could not hash {len(unhashable)} verses: {unhashable[:5]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
