"""
BLOCKER 2: Tests for real scientific concept wiring.
These tests verify that verse_to_concepts_real.json contains real
scientific concepts (not synthetic placeholders).
"""
import json
import re
import pytest
from pathlib import Path

WORKTREE = Path(__file__).parent.parent.parent.parent
OUTPUT_PATH = WORKTREE / "quran" / "corpus_extraction" / "ontology" / "verse_to_concepts_real.json"


def load_real_mappings():
    """Load the real verse-concept mappings output file."""
    if not OUTPUT_PATH.exists():
        pytest.skip(f"verse_to_concepts_real.json not yet generated at {OUTPUT_PATH}")
    with open(OUTPUT_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_all_entries(data):
    """Extract list of verse mapping entries from the output structure."""
    mappings = data.get("mappings", {})
    if isinstance(mappings, dict):
        # {verse_key: [list of concept dicts]}
        entries = []
        for verse_key, concepts in mappings.items():
            if isinstance(concepts, list):
                for concept in concepts:
                    entries.append({"verse_key": verse_key, **concept})
        return entries
    elif isinstance(mappings, list):
        return mappings
    return []


def test_no_synthetic_concept_ids():
    """No concept_id should match 'concept_N_domain' or 'concept_N' pattern."""
    data = load_real_mappings()
    entries = get_all_entries(data)
    assert len(entries) > 0, "No entries found in verse_to_concepts_real.json"

    synthetic_pattern = re.compile(r"^concept_\d+(_\w+)?$")
    bad_ids = [
        e.get("concept_id", "")
        for e in entries
        if synthetic_pattern.match(e.get("concept_id", ""))
    ]
    assert len(bad_ids) == 0, (
        f"Found {len(bad_ids)} synthetic concept IDs: {bad_ids[:5]}"
    )


def test_concepts_have_real_names():
    """Concept names should be real scientific terms, not 'Concept N' placeholders."""
    data = load_real_mappings()
    entries = get_all_entries(data)
    assert len(entries) > 0, "No entries found"

    placeholder_pattern = re.compile(r"^[Cc]oncept\s+\d+$")
    bad_names = [
        e.get("concept_name", e.get("concept", ""))
        for e in entries
        if placeholder_pattern.match(e.get("concept_name", e.get("concept", "")))
    ]
    assert len(bad_names) == 0, (
        f"Found {len(bad_names)} placeholder concept names: {bad_names[:5]}"
    )


def test_verse_concept_coverage():
    """At least 500 verses should have at least 1 real concept mapping."""
    data = load_real_mappings()
    mappings = data.get("mappings", {})

    if isinstance(mappings, dict):
        verses_with_concepts = sum(
            1 for concepts in mappings.values()
            if isinstance(concepts, list) and len(concepts) > 0
        )
    elif isinstance(mappings, list):
        verse_keys = set(e.get("verse_key", e.get("verse_id", "")) for e in mappings)
        verses_with_concepts = len(verse_keys)
    else:
        verses_with_concepts = 0

    assert verses_with_concepts >= 500, (
        f"Only {verses_with_concepts} verses have concept mappings, need >= 500"
    )


def test_concept_has_verse_references():
    """Each concept entry should reference actual verse keys (e.g. '2:164')."""
    data = load_real_mappings()
    mappings = data.get("mappings", {})

    verse_key_pattern = re.compile(r"^\d+:\d+(-\d+)?$")

    if isinstance(mappings, dict):
        verse_keys = list(mappings.keys())
    elif isinstance(mappings, list):
        verse_keys = [e.get("verse_key", e.get("verse_id", "")) for e in mappings]
    else:
        verse_keys = []

    assert len(verse_keys) > 0, "No verse keys found in mappings"

    valid_keys = [k for k in verse_keys if verse_key_pattern.match(str(k))]
    validity_ratio = len(valid_keys) / len(verse_keys) if verse_keys else 0

    assert validity_ratio >= 0.9, (
        f"Only {len(valid_keys)}/{len(verse_keys)} verse keys match 'N:N' format "
        f"({validity_ratio:.1%}). Sample invalid: "
        f"{[k for k in verse_keys if not verse_key_pattern.match(str(k))][:5]}"
    )


def test_domain_distribution():
    """Multiple domains should be represented in concept mappings."""
    data = load_real_mappings()
    entries = get_all_entries(data)
    assert len(entries) > 0, "No entries found"

    domains = set(
        e.get("domain", "").lower()
        for e in entries
        if e.get("domain", "").strip()
    )
    # Filter out empty
    domains = {d for d in domains if d}

    assert len(domains) >= 3, (
        f"Only {len(domains)} domain(s) found: {domains}. Expected >= 3."
    )


def test_no_duplicate_verse_entries():
    """No verse_key should appear twice in the concept mappings (at the top level)."""
    data = load_real_mappings()
    mappings = data.get("mappings", {})

    if isinstance(mappings, dict):
        # Dict keys are inherently unique
        assert len(mappings) == len(set(mappings.keys())), "Dict has duplicate keys"
    elif isinstance(mappings, list):
        verse_keys = [e.get("verse_key", e.get("verse_id", "")) for e in mappings]
        duplicates = [k for k in set(verse_keys) if verse_keys.count(k) > 1]
        assert len(duplicates) == 0, (
            f"Found {len(duplicates)} duplicate verse keys: {duplicates[:5]}"
        )
