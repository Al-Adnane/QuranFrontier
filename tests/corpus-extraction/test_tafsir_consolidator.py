"""
Tests for Tafsir Consolidator - Semantic Agreement Matrix

Tests consolidation of 8 classical Quranic tafsirs into unified semantic analysis.
All tests follow TDD principles and must not fabricate differences.
"""

import pytest
from quran.corpus_extraction.framework.tafsir_consolidator import TafsirConsolidator


class TestTafsirConsolidator:
    """Test suite for TafsirConsolidator class"""

    @pytest.fixture
    def consolidator(self):
        """Fixture providing a TafsirConsolidator instance"""
        return TafsirConsolidator()

    @pytest.fixture
    def sample_tafsirs_basic(self):
        """Fixture with 8 basic tafsir texts"""
        return {
            'Al-Tabari': 'This verse refers to divine mercy and justice in all circumstances',
            'Ibn Kathir': 'This verse refers to divine mercy and justice according to Islamic principles',
            'Al-Zamakhshari': 'The verse indicates rational understanding of divine attributes and justice',
            'Al-Qurtubi': 'This verse discusses divine mercy and justice with legal implications',
            'Al-Baydawi': 'The verse refers to divine mercy and justice in interpretation',
            'Ibn Juzayy': 'This verse indicates divine mercy and justice as key principles',
            'Al-Shawkani': 'The verse discusses divine mercy and justice literally',
            'Al-Alousi': 'This verse refers to divine mercy and justice in all contexts'
        }

    @pytest.fixture
    def sample_tafsirs_with_differences(self):
        """Fixture with 8 tafsirs where Mu'tazili stands out"""
        return {
            'Al-Tabari': 'The divine will is absolute and humans follow His decree completely',
            'Ibn Kathir': 'The divine will is absolute and creates all human actions',
            'Al-Zamakhshari': 'Humans possess free will and are responsible for their choices',
            'Al-Qurtubi': 'The divine will works with human choice and responsibility',
            'Al-Baydawi': 'Divine will and human choice work together in harmony',
            'Ibn Juzayy': 'The divine decree encompasses all with human responsibility',
            'Al-Shawkani': 'Divine will is absolute in literal interpretation',
            'Al-Alousi': 'The divine will and human choice operate together in practice'
        }

    @pytest.fixture
    def sample_tafsirs_high_similarity(self):
        """Fixture with two groups of high similarity"""
        return {
            'Al-Tabari': 'The believers are those who establish prayer and give charity',
            'Ibn Kathir': 'The believers establish prayer and give charity as religious duties',
            'Al-Zamakhshari': 'The believers perform rituals and give financial support',
            'Al-Qurtubi': 'The believers are those who pray regularly and donate to charity',
            'Al-Baydawi': 'The believers establish prayer and give charity by divine command',
            'Ibn Juzayy': 'The believers perform prayer and give charity as obligations',
            'Al-Shawkani': 'The believers literally establish prayer and give charity',
            'Al-Alousi': 'The believers establish prayer and give charity in all circumstances'
        }

    @pytest.fixture
    def sample_tafsirs_partial_coverage(self):
        """Fixture with some empty tafsirs"""
        return {
            'Al-Tabari': 'The verse refers to knowledge and wisdom from Allah',
            'Ibn Kathir': 'The verse discusses knowledge and wisdom in Islamic context',
            'Al-Zamakhshari': '',  # Empty
            'Al-Qurtubi': 'The verse indicates knowledge and wisdom as gifts',
            'Al-Baydawi': '',  # Empty
            'Ibn Juzayy': 'Knowledge and wisdom are mentioned in the verse',
            'Al-Shawkani': 'The verse literally means knowledge and wisdom',
            'Al-Alousi': 'Knowledge and wisdom are divine blessings in this verse'
        }

    def test_consolidate_tafsirs_basic(self, consolidator, sample_tafsirs_basic):
        """Test basic consolidation returns all required fields"""
        result = consolidator.consolidate_tafsirs(surah=2, ayah=5, tafsir_texts=sample_tafsirs_basic)

        # Verify all required fields present
        assert 'consensus_themes' in result
        assert 'consensus_confidence' in result
        assert 'madhab_differences' in result
        assert 'semantic_agreement_matrix' in result
        assert 'key_concepts' in result
        assert 'verse_key' in result
        assert 'tafsir_coverage' in result

        # Verify data types
        assert isinstance(result['consensus_themes'], list)
        assert isinstance(result['consensus_confidence'], float)
        assert isinstance(result['madhab_differences'], dict)
        assert isinstance(result['semantic_agreement_matrix'], dict)
        assert isinstance(result['key_concepts'], list)
        assert isinstance(result['verse_key'], str)
        assert isinstance(result['tafsir_coverage'], float)

        # Verify verse key format
        assert result['verse_key'] == '2:5'

    def test_consensus_themes_extraction(self, consolidator, sample_tafsirs_basic):
        """Test extraction of common themes across tafsirs"""
        result = consolidator.consolidate_tafsirs(surah=1, ayah=1, tafsir_texts=sample_tafsirs_basic)

        # Common themes should be identified
        assert len(result['consensus_themes']) > 0

        # Check for expected common words/concepts
        themes_text = ' '.join(result['consensus_themes']).lower()
        assert 'mercy' in themes_text or 'divine' in themes_text or 'justice' in themes_text

    def test_madhab_differences(self, consolidator, sample_tafsirs_with_differences):
        """Test identification of madhab-specific interpretations"""
        result = consolidator.consolidate_tafsirs(surah=2, ayah=256, tafsir_texts=sample_tafsirs_with_differences)

        # Madhab differences should be identified
        assert len(result['madhab_differences']) > 0

        # Mu'tazili should have unique interpretations
        assert len(result['madhab_differences']) >= 1

        # Verify madhab keys are present
        madhab_keys = list(result['madhab_differences'].keys())
        assert len(madhab_keys) > 0

    def test_semantic_agreement_calculation(self, consolidator, sample_tafsirs_high_similarity):
        """Test semantic agreement matrix calculation"""
        result = consolidator.consolidate_tafsirs(surah=2, ayah=3, tafsir_texts=sample_tafsirs_high_similarity)

        agreement_matrix = result['semantic_agreement_matrix']

        # Verify matrix structure
        assert isinstance(agreement_matrix, dict)
        assert len(agreement_matrix) == 8

        # Each tafsir should have agreements with others
        for tafsir_name, agreements in agreement_matrix.items():
            assert isinstance(agreements, dict)
            # Should have agreements with other tafsirs (max 7 others)
            assert len(agreements) <= 7

        # Agreement scores should be between 0 and 1
        for tafsir_name, agreements in agreement_matrix.items():
            for other_name, score in agreements.items():
                assert 0 <= score <= 1

    def test_consensus_confidence_score(self, consolidator, sample_tafsirs_basic):
        """Test consensus confidence is calculated as average pairwise agreement"""
        result = consolidator.consolidate_tafsirs(surah=3, ayah=7, tafsir_texts=sample_tafsirs_basic)

        confidence = result['consensus_confidence']

        # Confidence should be between 0 and 1
        assert 0 <= confidence <= 1

        # For similar texts, confidence should be relatively high
        assert confidence > 0.3

    def test_empty_tafsir_handling(self, consolidator, sample_tafsirs_partial_coverage):
        """Test graceful handling of empty/missing tafsirs"""
        result = consolidator.consolidate_tafsirs(surah=4, ayah=1, tafsir_texts=sample_tafsirs_partial_coverage)

        # Should return all fields
        assert 'consensus_themes' in result
        assert 'tafsir_coverage' in result

        # Coverage should be less than 1.0 (not all 8 provided)
        assert result['tafsir_coverage'] < 1.0
        assert result['tafsir_coverage'] > 0.5  # But still significant coverage

    def test_complete_coverage(self, consolidator, sample_tafsirs_basic):
        """Test coverage calculation with all 8 tafsirs present"""
        result = consolidator.consolidate_tafsirs(surah=5, ayah=2, tafsir_texts=sample_tafsirs_basic)

        # All 8 tafsirs provided, so coverage should be 1.0
        assert result['tafsir_coverage'] == 1.0

    def test_no_fabrication(self, consolidator):
        """Test that output contains only extracted content, no synthesis"""
        # Use simple, distinct texts
        simple_tafsirs = {
            'Al-Tabari': 'Apple',
            'Ibn Kathir': 'Apple',
            'Al-Zamakhshari': 'Orange',
            'Al-Qurtubi': 'Apple',
            'Al-Baydawi': 'Apple',
            'Ibn Juzayy': 'Apple',
            'Al-Shawkani': 'Apple',
            'Al-Alousi': 'Apple'
        }

        result = consolidator.consolidate_tafsirs(surah=6, ayah=1, tafsir_texts=simple_tafsirs)

        # All output should be derived from input
        themes = ' '.join(result['consensus_themes']).lower()
        concepts = ' '.join(result['key_concepts']).lower()

        # Should contain extracted words from input
        assert 'apple' in themes or 'apple' in concepts

        # Should NOT fabricate synthetic content
        assert 'synthesis' not in themes.lower()
        assert 'combination' not in themes.lower()
        assert 'blend' not in themes.lower()
