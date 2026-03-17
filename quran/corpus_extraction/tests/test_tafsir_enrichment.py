"""
Tests for P1: Multi-scholar classical tafsir enrichment.

Verifies that complete_corpus.json has been enriched with real 6-scholar
tafsir metadata replacing the single synthetic Ibn Kathir entries.
"""

import json
import re
import pytest
from pathlib import Path


CORPUS_PATH = Path(__file__).parent.parent / "output" / "complete_corpus.json"


@pytest.fixture(scope="module")
def corpus():
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def verses(corpus):
    return corpus.get("verses", [])


def test_corpus_has_multiple_scholars(verses):
    """At least 3 scholars should appear across the corpus tafsirs."""
    all_scholars = set()
    for verse in verses:
        tafsirs = verse.get("tafsirs", {})
        if isinstance(tafsirs, dict):
            all_scholars.update(tafsirs.keys())
        elif isinstance(tafsirs, list):
            for entry in tafsirs:
                if isinstance(entry, dict) and "name" in entry:
                    all_scholars.add(entry["name"].lower().replace(" ", "_").replace("-", "_"))

    assert len(all_scholars) >= 3, (
        f"Expected at least 3 scholars, found {len(all_scholars)}: {all_scholars}"
    )


def test_no_synthetic_tafsir_text(verses):
    """No tafsir text should match 'Tafsir Ibn Kathir for verse N' pattern."""
    synthetic_pattern = re.compile(r"Tafsir Ibn Kathir for verse \d+", re.IGNORECASE)

    violations = []
    for verse in verses:
        tafsirs = verse.get("tafsirs", {})
        if isinstance(tafsirs, dict):
            for scholar, data in tafsirs.items():
                text = data.get("text", "") if isinstance(data, dict) else str(data)
                if synthetic_pattern.search(text):
                    violations.append(verse.get("verse_key", "?"))
        elif isinstance(tafsirs, list):
            for entry in tafsirs:
                text = entry.get("text", "") if isinstance(entry, dict) else str(entry)
                if synthetic_pattern.search(text):
                    violations.append(verse.get("verse_key", "?"))

    assert len(violations) == 0, (
        f"Found {len(violations)} synthetic tafsir entries in verses: {violations[:10]}"
    )


def test_tafsir_agreement_field_populated(verses):
    """tafsir_agreement should be a float between 0 and 1 for each verse."""
    missing = []
    out_of_range = []

    for verse in verses:
        tafsirs = verse.get("tafsirs", {})
        if not isinstance(tafsirs, dict):
            continue

        agreement = tafsirs.get("tafsir_agreement")
        if agreement is None:
            # Check top-level field
            agreement = verse.get("tafsir_agreement")

        if agreement is None:
            missing.append(verse.get("verse_key", "?"))
        elif not (0.0 <= float(agreement) <= 1.0):
            out_of_range.append((verse.get("verse_key", "?"), agreement))

    # Allow missing only if tafsir_agreement is stored at verse level rather than inside tafsirs
    # Check verse-level as alternative
    verse_level_missing = []
    for verse in verses:
        if verse.get("tafsir_agreement") is None:
            tafsirs = verse.get("tafsirs", {})
            if isinstance(tafsirs, dict) and tafsirs.get("tafsir_agreement") is None:
                verse_level_missing.append(verse.get("verse_key", "?"))

    total_verses = len(verses)
    missing_count = len(verse_level_missing)

    assert missing_count == 0, (
        f"tafsir_agreement missing from {missing_count}/{total_verses} verses. "
        f"First 10 missing: {verse_level_missing[:10]}"
    )
    assert len(out_of_range) == 0, (
        f"tafsir_agreement out of [0,1] range in {len(out_of_range)} verses: {out_of_range[:5]}"
    )


def test_scholars_present(verses):
    """ibn_kathir, al_tabari, al_qurtubi should all appear somewhere in corpus."""
    required_scholars = {"ibn_kathir", "al_tabari", "al_qurtubi"}
    found_scholars = set()

    for verse in verses:
        tafsirs = verse.get("tafsirs", {})
        if isinstance(tafsirs, dict):
            for key in tafsirs.keys():
                # Normalize key for comparison
                normalized = key.lower().replace(" ", "_").replace("-", "_").replace("'", "")
                for req in required_scholars:
                    if req in normalized or normalized in req:
                        found_scholars.add(req)

    assert required_scholars.issubset(found_scholars), (
        f"Missing required scholars: {required_scholars - found_scholars}. "
        f"Found: {found_scholars}"
    )
