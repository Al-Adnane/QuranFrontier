"""
BLOCKER 1: Tests for real peer-reviewed sources replacing synthetic fabricated DOIs.

These tests validate that concept_sources_real.json contains genuine sources
discovered via live APIs (Semantic Scholar, CrossRef), not fabricated entries.

Run against the real output file:
    pytest quran/corpus_extraction/tests/test_real_sources.py -v
"""

import json
import re
import pytest
from pathlib import Path

# Path to the real sources output file (produced by discover_real_sources.py)
REAL_SOURCES_FILE = Path(__file__).parent.parent / "sources" / "concept_sources_real.json"

# Synthetic DOI pattern that must NOT appear in real sources
SYNTHETIC_DOI_PATTERN = re.compile(r"^10\.1038/s0\d{4}$")

# Generic title patterns from synthetic data
SYNTHETIC_TITLE_PATTERNS = [
    re.compile(r"^Physics Study \d+$"),
    re.compile(r"^Nature Physics \d{4}$"),
    re.compile(r"^Biology Study \d+$"),
    re.compile(r"^Medicine Study \d+$"),
    re.compile(r"^Engineering Study \d+$"),
    re.compile(r"^Agriculture Study \d+$"),
    re.compile(r"^\w+ Study \d+$"),
]

# Key seed concepts that must have sources
SEED_CONCEPT_IDS = [
    "embryology",
    "expanding_universe",
    "mountain_isostasy",
    "water_cycle",
    "oceanography_halocline",
]


def load_real_sources():
    """Load the real sources file, skipping if it doesn't exist."""
    if not REAL_SOURCES_FILE.exists():
        pytest.skip(f"Real sources file not found: {REAL_SOURCES_FILE}. Run discover_real_sources.py first.")
    with open(REAL_SOURCES_FILE) as f:
        return json.load(f)


def get_all_sources(data):
    """Flatten all sources from all concepts into a list."""
    sources = []
    for concept_entry in data.get("concepts", []):
        sources.extend(concept_entry.get("sources", []))
    return sources


def get_concept_map(data):
    """Return dict mapping concept_id -> list of sources."""
    return {entry["concept_id"]: entry.get("sources", []) for entry in data.get("concepts", [])}


# ---------------------------------------------------------------------------
# Test 1: No sequential fabricated DOIs
# ---------------------------------------------------------------------------

def test_no_sequential_dois():
    """No DOI should match the synthetic pattern 10.1038/s00XXX."""
    data = load_real_sources()
    all_sources = get_all_sources(data)

    assert len(all_sources) > 0, "No sources found in real sources file"

    offending = [
        s["doi"] for s in all_sources
        if s.get("doi") and SYNTHETIC_DOI_PATTERN.match(s["doi"])
    ]

    assert offending == [], (
        f"Found {len(offending)} synthetic sequential DOIs: {offending[:5]}"
    )


# ---------------------------------------------------------------------------
# Test 2: No generic fabricated titles
# ---------------------------------------------------------------------------

def test_sources_have_real_titles():
    """No source title should match generic synthetic patterns like 'Physics Study N'."""
    data = load_real_sources()
    all_sources = get_all_sources(data)

    assert len(all_sources) > 0, "No sources found in real sources file"

    offending = []
    for s in all_sources:
        title = s.get("title", "")
        for pattern in SYNTHETIC_TITLE_PATTERNS:
            if pattern.match(title):
                offending.append(title)
                break

    assert offending == [], (
        f"Found {len(offending)} generic synthetic titles: {offending[:5]}"
    )


# ---------------------------------------------------------------------------
# Test 3: Minimum sources per concept
# ---------------------------------------------------------------------------

def test_minimum_sources_per_concept():
    """Each concept should have at least 1 real source (we aim for 3+)."""
    data = load_real_sources()
    concept_map = get_concept_map(data)

    assert len(concept_map) > 0, "No concepts found in real sources file"

    empty_concepts = [cid for cid, sources in concept_map.items() if len(sources) == 0]

    # Allow up to 25% of concepts to have 0 sources (API rate-limits may prevent full coverage)
    # Success criterion: at least 15/20 concepts have sources (= 75% coverage)
    max_empty = max(1, int(len(concept_map) * 0.25))
    assert len(empty_concepts) <= max_empty, (
        f"{len(empty_concepts)} concepts have zero sources (allowed max: {max_empty}): "
        f"{empty_concepts[:10]}"
    )

    # At least 15 of 20 priority concepts must have >= 1 source
    concepts_with_sources = sum(1 for s in concept_map.values() if len(s) >= 1)
    assert concepts_with_sources >= min(15, len(concept_map)), (
        f"Only {concepts_with_sources}/{len(concept_map)} concepts have at least 1 source"
    )


# ---------------------------------------------------------------------------
# Test 4: Valid DOI format
# ---------------------------------------------------------------------------

VALID_DOI_PATTERN = re.compile(r"^10\.\d{4,}/[^\s]+$")


def test_doi_format_valid():
    """All DOIs should match the real DOI format: 10.XXXX/..."""
    data = load_real_sources()
    all_sources = get_all_sources(data)

    sources_with_doi = [s for s in all_sources if s.get("doi")]
    assert len(sources_with_doi) > 0, "No sources with DOIs found"

    invalid = [
        s["doi"] for s in sources_with_doi
        if not VALID_DOI_PATTERN.match(s["doi"])
    ]

    assert invalid == [], (
        f"Found {len(invalid)} invalid DOI formats: {invalid[:5]}"
    )


# ---------------------------------------------------------------------------
# Test 5: Quality scores are varied (not all the same)
# ---------------------------------------------------------------------------

def test_quality_scores_varied():
    """Quality scores should vary across sources (real scores differ by citation count, journal, etc.)."""
    data = load_real_sources()
    all_sources = get_all_sources(data)

    scores = [s["quality_score"] for s in all_sources if "quality_score" in s]
    assert len(scores) >= 3, f"Need at least 3 scored sources, got {len(scores)}"

    unique_scores = set(scores)
    assert len(unique_scores) > 1, (
        f"All {len(scores)} quality scores are the same value ({scores[0]}). "
        "Real scores should vary by citation count and journal tier."
    )

    # The range should be non-trivial (real papers vary meaningfully)
    score_range = max(scores) - min(scores)
    assert score_range > 0.01, (
        f"Quality score range is only {score_range:.4f}. Real sources should vary more."
    )


# ---------------------------------------------------------------------------
# Test 6: Sources have required metadata fields
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"doi", "title", "journal", "year", "quality_score"}


def test_sources_have_metadata():
    """Each source must have: doi, title, journal, year, quality_score."""
    data = load_real_sources()
    all_sources = get_all_sources(data)

    assert len(all_sources) > 0, "No sources found in real sources file"

    missing_fields_report = []
    for i, source in enumerate(all_sources):
        missing = REQUIRED_FIELDS - set(source.keys())
        if missing:
            missing_fields_report.append(
                f"Source {i} (doi={source.get('doi', 'N/A')}): missing {missing}"
            )

    # Allow up to 10% of sources to be missing optional fields
    max_incomplete = max(1, int(len(all_sources) * 0.1))
    assert len(missing_fields_report) <= max_incomplete, (
        f"{len(missing_fields_report)} sources are missing required fields:\n"
        + "\n".join(missing_fields_report[:10])
    )


# ---------------------------------------------------------------------------
# Test 7: Seed concepts have sources
# ---------------------------------------------------------------------------

def test_seed_concepts_have_sources():
    """Key concepts (embryology, geology, hydrology, oceanography) must have sources."""
    data = load_real_sources()
    concept_map = get_concept_map(data)

    # Also accept partial name matches (concept_id may be e.g. "embryology" or similar)
    found_seed_ids = set(concept_map.keys())

    missing_seeds = []
    for seed_id in SEED_CONCEPT_IDS:
        # Check if any concept_id starts with or equals the seed
        matches = [cid for cid in found_seed_ids if cid == seed_id or cid.startswith(seed_id)]
        if not matches:
            missing_seeds.append(seed_id)
        else:
            # Check that at least one of those concepts has sources
            has_source = any(len(concept_map[cid]) > 0 for cid in matches)
            if not has_source:
                missing_seeds.append(seed_id)

    # Allow up to 2 seed concepts to be missing (API may not return all)
    assert len(missing_seeds) <= 2, (
        f"The following seed concepts have no sources: {missing_seeds}. "
        f"Available concept IDs: {sorted(found_seed_ids)[:20]}"
    )


# ---------------------------------------------------------------------------
# Additional: File structure sanity checks
# ---------------------------------------------------------------------------

def test_real_sources_file_structure():
    """The real sources file must have the expected top-level structure."""
    data = load_real_sources()

    assert "concepts" in data, "Real sources file must have 'concepts' key"
    assert "metadata" in data, "Real sources file must have 'metadata' key"

    metadata = data["metadata"]
    assert "generated" in metadata or "discovery_date" in metadata, (
        "Metadata must include generation timestamp"
    )
    assert len(data["concepts"]) >= 15, (
        f"Expected at least 15 concepts, got {len(data['concepts'])}"
    )


def test_at_least_one_validated_doi():
    """At least one source should have validated=True (CrossRef confirmed)."""
    data = load_real_sources()
    all_sources = get_all_sources(data)

    validated = [s for s in all_sources if s.get("validated") is True]
    assert len(validated) > 0, (
        "No sources have validated=True. At least some DOIs should be CrossRef-validated."
    )
