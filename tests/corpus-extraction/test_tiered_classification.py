import pytest
from quran.corpus_extraction.ontology.tiered_classification import TieredClassifier

def test_tier1_empirical_science():
    classifier = TieredClassifier()
    claim = {
        "verse": "2:164",
        "scientific_claim": "Heavens expand",
        "supporting_sources": [{"doi": "10.1038/nature", "type": "peer-reviewed", "year": 2020}]
    }
    tier = classifier.classify(claim)
    assert tier == 1
    assert classifier.get_confidence_ceiling(tier) == 0.95

def test_tier2_frontier_science():
    classifier = TieredClassifier()
    claim = {
        "verse": "23:14",
        "scientific_claim": "Embryo develops through stages",
        "supporting_sources": [{"arxiv": "2203.14526", "type": "preprint", "year": 2022}]
    }
    tier = classifier.classify(claim)
    assert tier == 2
    assert classifier.get_confidence_ceiling(tier) == 0.60

def test_tier3_metaphorical():
    classifier = TieredClassifier()
    claim = {
        "verse": "37:5",
        "scientific_claim": "Sky as protective canopy",
        "supporting_sources": [],
        "is_metaphorical": True
    }
    tier = classifier.classify(claim)
    assert tier == 3
    assert classifier.get_confidence_ceiling(tier) == 0.30
