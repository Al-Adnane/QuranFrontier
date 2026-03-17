"""
P2: Tests for 4 new scientific domains in the corpus extraction framework.

Tests cover:
- VerseExtraction data model fields for mathematics, hydrology, oceanography, geology
- DomainAnalyzer detection for each new domain using key Quranic verses
"""

import sys
import os

# Ensure the project root is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest


# ===== DATA MODEL TESTS =====

def test_data_model_has_mathematics_field():
    """VerseExtraction must include mathematics_content field."""
    from quran.corpus_extraction.schema.data_models import VerseExtraction
    v = VerseExtraction.__dataclass_fields__
    assert 'mathematics_content' in v


def test_data_model_has_hydrology_field():
    """VerseExtraction must include hydrology_content field."""
    from quran.corpus_extraction.schema.data_models import VerseExtraction
    v = VerseExtraction.__dataclass_fields__
    assert 'hydrology_content' in v


def test_data_model_has_oceanography_field():
    """VerseExtraction must include oceanography_content field."""
    from quran.corpus_extraction.schema.data_models import VerseExtraction
    v = VerseExtraction.__dataclass_fields__
    assert 'oceanography_content' in v


def test_data_model_has_geology_field():
    """VerseExtraction must include geology_content field."""
    from quran.corpus_extraction.schema.data_models import VerseExtraction
    v = VerseExtraction.__dataclass_fields__
    assert 'geology_content' in v


def test_get_scientific_domains_includes_new_domains():
    """get_scientific_domains() must include all 4 new domains."""
    from quran.corpus_extraction.schema.data_models import VerseExtraction
    ve = VerseExtraction(surah=4, ayah=11, verse_key="4:11",
                         arabic_text="test", translation="test")
    domains = ve.get_scientific_domains()
    assert 'mathematics' in domains
    assert 'hydrology' in domains
    assert 'oceanography' in domains
    assert 'geology' in domains


# ===== DOMAIN ANALYZER DETECTION TESTS =====

def test_domain_analyzer_detects_mathematics():
    """Q4:11 inheritance verse should be detected as mathematics (fractions/inheritance)."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    # Q4:11 deals with prescribed inheritance shares (fractions)
    verse_text = "Allah instructs you concerning the inheritance shares and fractions for your children: the male shall have the equal of the portion of two females"
    result = analyzer._analyze_mathematics(verse_text, "4:11")
    assert result is not None, "Mathematics content should be detected in Q4:11 inheritance verse"
    assert result["confidence"] > 0


def test_domain_analyzer_detects_mathematics_calendar():
    """Q18:25 with 300/309 years should be detected as calendar mathematics."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    verse_text = "And they remained in their cave for three hundred years and exceeded by nine in the lunar calendar calculation"
    result = analyzer._analyze_mathematics(verse_text, "18:25")
    assert result is not None, "Mathematics content should be detected in Q18:25 calendar verse"


def test_domain_analyzer_detects_hydrology():
    """Q23:18 water cycle verse should be detected as hydrology."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    # Q23:18: "We sent down water from the sky and stored it in the earth"
    verse_text = "And We sent down water from the sky in a measured amount and settled it in the earth, and indeed We are able to take it away"
    result = analyzer._analyze_hydrology(verse_text, "23:18")
    assert result is not None, "Hydrology content should be detected in Q23:18 water cycle verse"
    assert result["confidence"] > 0


def test_domain_analyzer_detects_hydrology_springs():
    """Q39:21 groundwater/springs verse should be detected as hydrology."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    verse_text = "Do you not see that Allah sends down rain from the sky and leads it through springs in the earth, then brings forth crops of various colors"
    result = analyzer._analyze_hydrology(verse_text, "39:21")
    assert result is not None, "Hydrology content should be detected in Q39:21 springs verse"


def test_domain_analyzer_detects_oceanography():
    """Q55:19 two seas verse should be detected as oceanography."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    # Q55:19-20: "He released the two seas meeting [side by side]; Between them is a barrier [so] neither of them transgresses"
    verse_text = "He released the two seas meeting side by side, between them is a barrier so neither of them transgresses"
    result = analyzer._analyze_oceanography(verse_text, "55:19")
    assert result is not None, "Oceanography content should be detected in Q55:19 two seas verse"
    assert result["confidence"] > 0


def test_domain_analyzer_detects_oceanography_darkness():
    """Q24:40 darkness layers in deep ocean should be detected as oceanography."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    verse_text = "Or like darkness in a deep sea which is covered by waves upon waves above which are clouds, layers of darkness one upon another"
    result = analyzer._analyze_oceanography(verse_text, "24:40")
    assert result is not None, "Oceanography content should be detected in Q24:40 aphotic zone verse"


def test_domain_analyzer_detects_geology():
    """Q16:15 mountains verse should be detected as geology."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    # Q16:15: "And He has cast into the earth firmly set mountains"
    verse_text = "And He has cast into the earth firmly set mountains, lest it shift with you, and rivers and roads that you might be guided"
    result = analyzer._analyze_geology(verse_text, "16:15")
    assert result is not None, "Geology content should be detected in Q16:15 mountains verse"
    assert result["confidence"] > 0


def test_domain_analyzer_detects_geology_pegs():
    """Q31:10 mountain pegs/isostasy verse should be detected as geology."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    verse_text = "He created the heavens without pillars that you see and has cast into the earth firmly set mountains as pegs lest it shift with you"
    result = analyzer._analyze_geology(verse_text, "31:10")
    assert result is not None, "Geology content should be detected in Q31:10 mountain pegs verse"


def test_geology_confidence_ceiling():
    """Geology (Tier 2) should have a lower confidence ceiling than Tier 1 domains."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    # Use a rich geology verse to hit the ceiling
    verse_text = "He cast into the earth firmly set mountains as pegs and rock layers to stabilize and anchor the earth with mineral strata"
    result = analyzer._analyze_geology(verse_text, "31:10")
    assert result is not None
    assert result["confidence"] <= 0.75, f"Geology confidence ceiling should be 0.75, got {result['confidence']}"


def test_mathematics_confidence_ceiling():
    """Mathematics (Tier 1) should have confidence ceiling of 0.85."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    verse_text = "fractions inheritance calculation ratio calendar lunar solar year prescribed shares"
    result = analyzer._analyze_mathematics(verse_text, "4:11")
    assert result is not None
    assert result["confidence"] <= 0.85, f"Mathematics confidence ceiling should be 0.85, got {result['confidence']}"


def test_analyze_verse_returns_all_nine_domains():
    """analyze_verse() should return keys for all 9 domains including the 4 new ones."""
    from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
    analyzer = DomainAnalyzer()
    result = analyzer.analyze_verse("test verse text", "1:1")
    assert 'mathematics' in result
    assert 'hydrology' in result
    assert 'oceanography' in result
    assert 'geology' in result
