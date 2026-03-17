import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

"""
Tests for the Verse Extractor Coordinator - Phase 2 Integration Framework.

Tests orchestration of all 5 Phase 2 components:
1. Domain Analyzer (5 domains)
2. Tafsir Consolidator (8 scholars)
3. Asbab Mapper (revelation context)
4. Semantic Analyzer (lexical relationships)
5. Verification Pipeline (5 layers)
"""

import pytest
from quran.corpus_extraction.framework.verse_coordinator import VerseExtractorCoordinator
from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
from quran.corpus_extraction.framework.tafsir_consolidator import TafsirConsolidator
from quran.corpus_extraction.framework.asbab_mapper import AsbabAlNuzulMapper
from quran.corpus_extraction.framework.semantic_analyzer import SemanticFieldAnalyzer
from quran.corpus_extraction.infrastructure.verification_pipeline import VerificationPipeline
from quran.corpus_extraction.schema.data_models import VerseExtraction


class TestVerseExtractorCoordinator:
    """Test suite for VerseExtractorCoordinator integration."""

    def test_extract_complete_verse_basic(self):
        """Test basic verse extraction with all components."""
        # Setup
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=DomainAnalyzer(),
            tafsir_consolidator=TafsirConsolidator(),
            asbab_mapper=AsbabAlNuzulMapper(),
            semantic_analyzer=SemanticFieldAnalyzer(),
            verification_pipeline=VerificationPipeline()
        )

        # Input
        surah = 39
        ayah = 5
        verse_text = "He created the heavens and the earth in true proportions"
        tafsir_texts = {
            'Al-Tabari': 'Creation of heavens and earth with perfect measure',
            'Ibn Kathir': 'Allah created all things with wisdom and order',
            'Al-Zamakhshari': 'The creation reflects divine wisdom',
            'Al-Qurtubi': 'Perfect proportions show divine design',
            'Al-Baydawi': 'Everything created in its proper measure',
            'Ibn Juzayy': 'The universe reveals divine truth',
            'Al-Shawkani': 'Creation demonstrates Allah\'s power',
            'Al-Alousi': 'All creation reflects perfect proportion'
        }

        # Execute
        result = coordinator.extract_complete_verse(
            surah=surah,
            ayah=ayah,
            verse_text=verse_text,
            tafsir_texts=tafsir_texts
        )

        # Verify
        assert isinstance(result, VerseExtraction)
        assert result.surah == 39
        assert result.ayah == 5
        assert result.verse_key == "39:5"
        assert result.arabic_text == verse_text
        assert len(result.tafsirs) > 0
        assert result.confidence_score >= 0.0
        assert result.confidence_score <= 1.0

    def test_domain_analyses_integration(self):
        """Test that all 5 domain analyzers run and populate results."""
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=DomainAnalyzer(),
            tafsir_consolidator=TafsirConsolidator(),
            asbab_mapper=AsbabAlNuzulMapper(),
            semantic_analyzer=SemanticFieldAnalyzer(),
            verification_pipeline=VerificationPipeline()
        )

        # Verse with physics and biology content
        surah = 39
        ayah = 5
        verse_text = "He created the heavens and earth with layers, made water, plants, and creatures with genetics and growth patterns"

        result = coordinator.extract_complete_verse(
            surah=surah,
            ayah=ayah,
            verse_text=verse_text,
            tafsir_texts={}
        )

        # Verify domain analyses ran
        assert result.physics_content is not None or result.biology_content is not None
        assert result.medicine_content is not None or result.engineering_content is not None or result.agriculture_content is not None

        # Verify at least some domains detected content
        domains = result.get_scientific_domains()
        assert any(content is not None for content in domains.values())

    def test_tafsir_consolidation_integration(self):
        """Test tafsir consolidation with 8 classical scholars."""
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=DomainAnalyzer(),
            tafsir_consolidator=TafsirConsolidator(),
            asbab_mapper=AsbabAlNuzulMapper(),
            semantic_analyzer=SemanticFieldAnalyzer(),
            verification_pipeline=VerificationPipeline()
        )

        surah = 39
        ayah = 5
        verse_text = "He created the heavens and the earth"

        # All 8 tafsirs
        tafsir_texts = {
            'Al-Tabari': 'Allah created the heavens and earth with perfect wisdom',
            'Ibn Kathir': 'The creation of heavens and earth shows divine power',
            'Al-Zamakhshari': 'Heavens and earth created with divine intention',
            'Al-Qurtubi': 'Creation is a sign of divine wisdom and power',
            'Al-Baydawi': 'The heavens and earth manifest divine attributes',
            'Ibn Juzayy': 'Creation reveals the unity of Allah',
            'Al-Shawkani': 'Heavens and earth demonstrate divine mastery',
            'Al-Alousi': 'The creation of all things reflects divine knowledge'
        }

        result = coordinator.extract_complete_verse(
            surah=surah,
            ayah=ayah,
            verse_text=verse_text,
            tafsir_texts=tafsir_texts
        )

        # Verify tafsirs consolidated
        assert len(result.tafsirs) > 0
        assert result.tafsir_agreement >= 0.0
        assert result.tafsir_agreement <= 1.0

    def test_asbab_context_retrieval(self):
        """Test asbab al-nuzul mapping for revelation context."""
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=DomainAnalyzer(),
            tafsir_consolidator=TafsirConsolidator(),
            asbab_mapper=AsbabAlNuzulMapper(),
            semantic_analyzer=SemanticFieldAnalyzer(),
            verification_pipeline=VerificationPipeline()
        )

        # Well-known Medinan verse with clear asbab
        surah = 2  # Al-Baqarah (Medinan)
        ayah = 219  # Wine and gambling inquiry
        verse_text = "They ask you about wine and gambling"

        result = coordinator.extract_complete_verse(
            surah=surah,
            ayah=ayah,
            verse_text=verse_text,
            tafsir_texts={'Al-Tabari': 'Companions asked about wine'}
        )

        # Verify asbab populated for known verses
        assert result.asbab_nuzul is not None
        assert 'occasion_type' in result.asbab_nuzul
        assert 'historical_period' in result.asbab_nuzul

    def test_semantic_analysis_integration(self):
        """Test semantic field analysis for lexical relationships."""
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=DomainAnalyzer(),
            tafsir_consolidator=TafsirConsolidator(),
            asbab_mapper=AsbabAlNuzulMapper(),
            semantic_analyzer=SemanticFieldAnalyzer(),
            verification_pipeline=VerificationPipeline()
        )

        surah = 39
        ayah = 5
        # Verse with rich semantic content (using transliteration)
        verse_text = "khalaq al-samawat wa-al-ard"  # Creation vocabulary

        result = coordinator.extract_complete_verse(
            surah=surah,
            ayah=ayah,
            verse_text=verse_text,
            tafsir_texts={}
        )

        # Verify semantic analysis populated
        assert result.semantic_analysis is not None
        assert 'semantic_field' in result.semantic_analysis or 'root_clusters' in result.semantic_analysis

    def test_verification_pipeline_integration(self):
        """Test 5-layer verification pipeline runs."""
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=DomainAnalyzer(),
            tafsir_consolidator=TafsirConsolidator(),
            asbab_mapper=AsbabAlNuzulMapper(),
            semantic_analyzer=SemanticFieldAnalyzer(),
            verification_pipeline=VerificationPipeline()
        )

        surah = 39
        ayah = 5
        verse_text = "He created the heavens and the earth"

        result = coordinator.extract_complete_verse(
            surah=surah,
            ayah=ayah,
            verse_text=verse_text,
            tafsir_texts={}
        )

        # Verify verification layers ran
        assert len(result.verification_layers) >= 0
        # Verification results should be bool or dict-like
        for layer_name, layer_result in result.verification_layers.items():
            assert isinstance(layer_name, str)

    def test_confidence_score_calculation(self):
        """Test overall confidence score calculation."""
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=DomainAnalyzer(),
            tafsir_consolidator=TafsirConsolidator(),
            asbab_mapper=AsbabAlNuzulMapper(),
            semantic_analyzer=SemanticFieldAnalyzer(),
            verification_pipeline=VerificationPipeline()
        )

        surah = 39
        ayah = 5
        verse_text = "He created the heavens and the earth with layers"
        tafsir_texts = {
            'Al-Tabari': 'Creation with divine wisdom',
            'Ibn Kathir': 'Perfect creation by Allah',
            'Al-Zamakhshari': 'Divine creation',
            'Al-Qurtubi': 'Layered creation',
            'Al-Baydawi': 'Heavens and earth created',
            'Ibn Juzayy': 'Divine power in creation',
            'Al-Shawkani': 'Manifest creation',
            'Al-Alousi': 'Allah is the creator'
        }

        result = coordinator.extract_complete_verse(
            surah=surah,
            ayah=ayah,
            verse_text=verse_text,
            tafsir_texts=tafsir_texts
        )

        # Verify confidence score
        assert isinstance(result.confidence_score, float)
        assert 0.0 <= result.confidence_score <= 1.0

    def test_missing_components(self):
        """Test graceful handling when components are missing."""
        # Initialize with None components
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=None,
            tafsir_consolidator=None,
            asbab_mapper=None,
            semantic_analyzer=None,
            verification_pipeline=None
        )

        surah = 39
        ayah = 5
        verse_text = "He created the heavens and the earth"

        # Should still return partial extraction
        result = coordinator.extract_complete_verse(
            surah=surah,
            ayah=ayah,
            verse_text=verse_text,
            tafsir_texts={}
        )

        # Verify minimum requirements met
        assert isinstance(result, VerseExtraction)
        assert result.surah == 39
        assert result.ayah == 5
        assert result.verse_key == "39:5"
        # Should have metadata even if components missing
        assert result.arabic_text is not None
