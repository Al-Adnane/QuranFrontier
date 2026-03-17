"""
Tests for Algorithm 1: Semantic Field Extraction

All tests use in-memory sample data (no actual corpus files required).
"""

import json
import os
import sys
import tempfile
import pytest

# Ensure the algorithms package is importable when running from repo root
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "..", ".."),
)

from quran.algorithms.semantic_field_extractor import (
    SemanticField,
    SemanticFieldExtractor,
)


# --------------------------------------------------------------------------- #
# Fixtures – minimal in-memory data
# --------------------------------------------------------------------------- #

SAMPLE_CORPUS = {
    "verses": [
        {"verse_key": "1:1", "arabic_text": "بِسْمِ اللَّهِ", "translation": "In the name of Allah"},
        {"verse_key": "1:2", "arabic_text": "الْحَمْدُ لِلَّهِ", "translation": "Praise be to Allah"},
        {"verse_key": "1:5", "arabic_text": "إِيَّاكَ نَعْبُدُ", "translation": "You alone we worship"},
        {"verse_key": "2:1", "arabic_text": "الم", "translation": "Alif Lam Meem"},
        {"verse_key": "2:5", "arabic_text": "أُولَٰئِكَ", "translation": "Those are"},
        {"verse_key": "2:20", "arabic_text": "صُمٌّ بُكْمٌ", "translation": "Deaf, dumb"},
        {"verse_key": "3:1", "arabic_text": "الم", "translation": "Alif Lam Meem"},
        {"verse_key": "3:10", "arabic_text": "إِنَّ الَّذِينَ", "translation": "Indeed those"},
    ]
}

SAMPLE_CONCEPTS = {
    "mappings": {
        # concept_alpha appears in 1:1, 1:2, 2:1, 3:1 (4 verses)
        "1:1": [{"concept_id": "concept_alpha", "confidence": 0.9, "tier": 1}],
        "1:2": [
            {"concept_id": "concept_alpha", "confidence": 0.8, "tier": 1},
            {"concept_id": "concept_beta", "confidence": 0.7, "tier": 2},
        ],
        "1:5": [{"concept_id": "concept_beta", "confidence": 0.85, "tier": 1}],
        "2:1": [
            {"concept_id": "concept_alpha", "confidence": 0.75, "tier": 1},
            {"concept_id": "concept_gamma", "confidence": 0.6, "tier": 2},
        ],
        "2:5": [{"concept_id": "concept_gamma", "confidence": 0.65, "tier": 2}],
        "2:20": [{"concept_id": "concept_delta", "confidence": 0.5, "tier": 3}],
        "3:1": [
            {"concept_id": "concept_alpha", "confidence": 0.8, "tier": 1},
            {"concept_id": "concept_delta", "confidence": 0.55, "tier": 2},
        ],
        "3:10": [{"concept_id": "concept_beta", "confidence": 0.7, "tier": 1}],
    }
}


def make_extractor(corpus=None, concepts=None):
    """Create a SemanticFieldExtractor backed by temporary JSON files."""
    corpus = corpus or SAMPLE_CORPUS
    concepts = concepts or SAMPLE_CONCEPTS

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as cf:
        json.dump(corpus, cf)
        corpus_path = cf.name

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as mf:
        json.dump(concepts, mf)
        concepts_path = mf.name

    return SemanticFieldExtractor(corpus_path, concepts_path)


# --------------------------------------------------------------------------- #
# Test 1: build_concept_index returns correct verse lists
# --------------------------------------------------------------------------- #

def test_build_concept_index_returns_correct_verse_lists():
    extractor = make_extractor()
    index = extractor.build_concept_index()

    # concept_alpha should map to 4 verses: 1:1, 1:2, 2:1, 3:1
    assert "concept_alpha" in index
    alpha_verses = set(index["concept_alpha"])
    assert alpha_verses == {"1:1", "1:2", "2:1", "3:1"}

    # concept_beta should map to 3 verses: 1:2, 1:5, 3:10
    assert "concept_beta" in index
    beta_verses = set(index["concept_beta"])
    assert beta_verses == {"1:2", "1:5", "3:10"}

    # concept_gamma should map to 2 verses: 2:1, 2:5
    assert "concept_gamma" in index
    gamma_verses = set(index["concept_gamma"])
    assert gamma_verses == {"2:1", "2:5"}


# --------------------------------------------------------------------------- #
# Test 2: compute_co_occurrence – exact match detection
# --------------------------------------------------------------------------- #

def test_compute_co_occurrence_exact_match():
    extractor = make_extractor()
    index = extractor.build_concept_index()

    # concept_alpha and concept_beta both appear in verse 1:2
    result = extractor.compute_co_occurrence("concept_alpha", "concept_beta", index)

    assert result["exact"] == 1
    # total must include exact contribution (weight 3)
    assert result["total"] >= 3


def test_compute_co_occurrence_no_exact_match():
    extractor = make_extractor()
    index = extractor.build_concept_index()

    # concept_gamma (2:1, 2:5) and concept_delta (2:20, 3:1)
    # They share surah 2 but not the same verse
    result = extractor.compute_co_occurrence("concept_gamma", "concept_delta", index)

    assert result["exact"] == 0


# --------------------------------------------------------------------------- #
# Test 3: compute_co_occurrence – nearby detection (same surah, ≤10 verses apart)
# --------------------------------------------------------------------------- #

def test_compute_co_occurrence_nearby_detection():
    extractor = make_extractor()
    # Build a custom concept index with controlled data
    custom_index = {
        "concept_x": ["2:1", "2:8"],   # surah 2, ayahs 1 and 8
        "concept_y": ["2:5", "5:1"],   # surah 2 ayah 5 (nearby to 2:1 and 2:8), surah 5
    }

    result = extractor.compute_co_occurrence("concept_x", "concept_y", custom_index)

    # 2:1 vs 2:5 -> diff=4 -> nearby
    # 2:8 vs 2:5 -> diff=3 -> nearby
    assert result["nearby"] >= 2
    assert result["exact"] == 0


def test_compute_co_occurrence_not_nearby_when_far():
    extractor = make_extractor()
    custom_index = {
        "concept_x": ["2:1"],
        "concept_y": ["2:20"],  # diff=19 -> same_surah, not nearby
    }

    result = extractor.compute_co_occurrence("concept_x", "concept_y", custom_index)

    assert result["nearby"] == 0
    assert result["same_surah"] >= 1
    assert result["exact"] == 0


# --------------------------------------------------------------------------- #
# Test 4: build_graph creates nodes for each concept with freq >= 2
# --------------------------------------------------------------------------- #

def test_build_graph_creates_nodes_for_each_concept():
    extractor = make_extractor()
    index = extractor.build_concept_index()
    G = extractor.build_graph(index, min_co_occurrence=1)

    # All 4 concepts appear in >= 2 verses
    for cid in ["concept_alpha", "concept_beta", "concept_gamma", "concept_delta"]:
        assert G.has_node(cid), f"Expected node {cid} in graph"


def test_build_graph_excludes_low_frequency_concepts():
    extractor = make_extractor()
    # Add a concept that appears in only 1 verse
    custom_concepts = {
        "mappings": {
            "1:1": [{"concept_id": "rare_concept", "confidence": 0.9, "tier": 1}],
            "2:1": [{"concept_id": "common_concept", "confidence": 0.8, "tier": 1}],
            "2:2": [{"concept_id": "common_concept", "confidence": 0.8, "tier": 1}],
        }
    }
    extractor2 = make_extractor(concepts=custom_concepts)
    index = extractor2.build_concept_index()
    G = extractor2.build_graph(index, min_co_occurrence=1)

    # rare_concept appears only once -> should NOT be a node
    assert not G.has_node("rare_concept")
    # common_concept appears twice -> should be a node
    assert G.has_node("common_concept")


# --------------------------------------------------------------------------- #
# Test 5: extract_fields returns non-empty dict
# --------------------------------------------------------------------------- #

def test_extract_fields_returns_non_empty_dict():
    extractor = make_extractor()
    fields = extractor.extract_fields()

    assert isinstance(fields, dict)
    assert len(fields) > 0


def test_extract_fields_values_are_semantic_field_instances():
    extractor = make_extractor()
    fields = extractor.extract_fields()

    for name, sf in fields.items():
        assert isinstance(sf, SemanticField)
        assert isinstance(sf.name, str)
        assert isinstance(sf.core_concepts, list)
        assert isinstance(sf.all_concepts, list)
        assert isinstance(sf.frequency, int)
        assert isinstance(sf.density, float)
        assert isinstance(sf.verse_refs, list)
        assert sf.frequency >= 0
        assert 0.0 <= sf.density <= 1.0


# --------------------------------------------------------------------------- #
# Test 6: run() returns expected structure
# --------------------------------------------------------------------------- #

def test_run_returns_expected_top_level_keys():
    extractor = make_extractor()
    result = extractor.run()

    assert "fields" in result
    assert "graph_stats" in result
    assert "top_concepts" in result


def test_run_graph_stats_has_required_keys():
    extractor = make_extractor()
    result = extractor.run()

    stats = result["graph_stats"]
    assert "nodes" in stats
    assert "edges" in stats
    assert "components" in stats
    assert "density" in stats

    assert stats["nodes"] >= 0
    assert stats["edges"] >= 0
    assert stats["density"] >= 0.0


def test_run_top_concepts_is_sorted_by_frequency():
    extractor = make_extractor()
    result = extractor.run()

    top = result["top_concepts"]
    assert isinstance(top, list)
    # Each entry is (concept_id, frequency)
    for cid, freq in top:
        assert isinstance(cid, str)
        assert isinstance(freq, int)

    # Should be sorted descending
    if len(top) > 1:
        for i in range(len(top) - 1):
            assert top[i][1] >= top[i + 1][1]


def test_run_top_concepts_includes_most_frequent():
    extractor = make_extractor()
    result = extractor.run()

    top_ids = [cid for cid, _ in result["top_concepts"]]
    # concept_alpha appears in 4 verses, should be among top concepts
    assert "concept_alpha" in top_ids


# --------------------------------------------------------------------------- #
# Test: SemanticField dataclass instantiation
# --------------------------------------------------------------------------- #

def test_semantic_field_dataclass():
    sf = SemanticField(
        name="test_field",
        core_concepts=["a", "b"],
        all_concepts=["a", "b", "c"],
        frequency=10,
        density=0.5,
        verse_refs=["1:1", "2:3"],
    )
    assert sf.name == "test_field"
    assert len(sf.core_concepts) == 2
    assert len(sf.all_concepts) == 3
    assert sf.frequency == 10
    assert sf.density == 0.5
    assert "1:1" in sf.verse_refs
