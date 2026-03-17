#!/usr/bin/env python3
"""
BLOCKER 0: Tests for corpus text wiring.
Verifies that complete_corpus.json contains real Quranic text, not synthetic placeholders.
"""

import json
import re
import pytest
from pathlib import Path

# Path to the corpus file (resolved relative to this test file)
TESTS_DIR = Path(__file__).parent
CORPUS_PATH = TESTS_DIR.parent / "output" / "complete_corpus.json"

EXPECTED_VERSE_COUNT = 6236


@pytest.fixture(scope="session")
def corpus_data():
    """Load complete_corpus.json once per session."""
    assert CORPUS_PATH.exists(), f"Corpus file not found: {CORPUS_PATH}"
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("verses", [])
    return data


def test_verse_count(corpus_data):
    """Corpus must contain exactly 6,236 verses."""
    assert len(corpus_data) == EXPECTED_VERSE_COUNT, (
        f"Expected {EXPECTED_VERSE_COUNT} verses, got {len(corpus_data)}"
    )


def test_no_synthetic_verse_text(corpus_data):
    """No verse should have 'Verse N text' as arabic_text."""
    synthetic_pattern = re.compile(r"^Verse \d+ text$")
    offenders = [
        v.get("verse_key", f"{v.get('surah')}:{v.get('ayah')}")
        for v in corpus_data
        if synthetic_pattern.match(str(v.get("arabic_text", "")))
    ]
    assert offenders == [], (
        f"Found {len(offenders)} verses with synthetic arabic_text. "
        f"First offenders: {offenders[:5]}"
    )


def test_no_synthetic_translation(corpus_data):
    """No verse should have 'Translation of verse N' as translation."""
    synthetic_pattern = re.compile(r"^Translation of verse \d+$")
    offenders = [
        v.get("verse_key", f"{v.get('surah')}:{v.get('ayah')}")
        for v in corpus_data
        if synthetic_pattern.match(str(v.get("translation", "")))
    ]
    assert offenders == [], (
        f"Found {len(offenders)} verses with synthetic translation. "
        f"First offenders: {offenders[:5]}"
    )


def test_all_verses_have_arabic_text(corpus_data):
    """All 6,236 verses must have non-empty arabic_text."""
    missing = [
        v.get("verse_key", f"{v.get('surah')}:{v.get('ayah')}")
        for v in corpus_data
        if not v.get("arabic_text", "").strip()
    ]
    assert missing == [], (
        f"Found {len(missing)} verses with empty arabic_text. "
        f"First missing: {missing[:5]}"
    )


def test_all_verses_have_translation(corpus_data):
    """All 6,236 verses must have non-empty translation."""
    missing = [
        v.get("verse_key", f"{v.get('surah')}:{v.get('ayah')}")
        for v in corpus_data
        if not v.get("translation", "").strip()
    ]
    assert missing == [], (
        f"Found {len(missing)} verses with empty translation. "
        f"First missing: {missing[:5]}"
    )


def test_sample_verse_1_1(corpus_data):
    """Surah 1 Ayah 1 (Al-Fatiha opening) should contain bismillah Arabic."""
    verse_1_1 = next(
        (v for v in corpus_data if v.get("surah") == 1 and v.get("ayah") == 1),
        None,
    )
    assert verse_1_1 is not None, "Verse 1:1 not found in corpus"

    arabic_text = verse_1_1.get("arabic_text", "")
    # Bismillah contains Arabic characters — verify real Unicode Arabic is present
    has_arabic = any("\u0600" <= c <= "\u06FF" for c in arabic_text)
    assert has_arabic, (
        f"Verse 1:1 arabic_text does not contain Arabic Unicode characters: "
        f"'{arabic_text}'"
    )
    # Should contain بِسْمِ (bismi) pattern
    assert "بس" in arabic_text or "بِسْ" in arabic_text or "بِسۡ" in arabic_text or "بِسْمِ" in arabic_text, (
        f"Verse 1:1 arabic_text does not appear to be bismillah: '{arabic_text}'"
    )


def test_sha256_field_present(corpus_data):
    """Each verse entry should have integrity_hash field."""
    missing = [
        v.get("verse_key", f"{v.get('surah')}:{v.get('ayah')}")
        for v in corpus_data
        if not v.get("integrity_hash", "").strip()
    ]
    assert missing == [], (
        f"Found {len(missing)} verses missing integrity_hash. "
        f"First missing: {missing[:5]}"
    )
