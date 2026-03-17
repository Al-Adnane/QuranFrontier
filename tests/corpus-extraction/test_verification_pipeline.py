import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, patch, MagicMock
from quran.corpus_extraction.infrastructure.verification_pipeline import VerificationPipeline


@pytest.fixture
def mock_api_layer():
    """Create a mock API layer."""
    mock = Mock()
    return mock


@pytest.fixture
def mock_cache_layer():
    """Create a mock cache layer."""
    mock = Mock()
    return mock


@pytest.fixture
def verification_pipeline(mock_api_layer, mock_cache_layer):
    """Create a VerificationPipeline instance with mocked dependencies."""
    return VerificationPipeline(api_layer=mock_api_layer, cache_layer=mock_cache_layer)


@pytest.fixture
def valid_extraction():
    """Create a valid extraction dict with all required fields."""
    return {
        'surah': 1,
        'ayah': 1,
        'text': 'In the name of Allah',
        'tafsir': {
            'name': 'standard',
            'content': 'Tafsir content'
        },
        'source_citations': [
            {'title': 'Tafsir Al-Tabari', 'url': 'https://example.com'}
        ],
        'domain_concepts': ['mercy', 'knowledge'],
        'claims': [
            {'claim': 'Allah is merciful', 'verifiable': True}
        ]
    }


class TestVerificationPipelineAllLayersPass:
    """Test when all 5 layers pass verification."""

    def test_all_layers_pass(self, verification_pipeline, valid_extraction):
        """All 5 layers should pass and return confidence=1.0."""
        with patch.object(verification_pipeline, '_layer_1_quran_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_2_ansari_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_3_peer_review', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_4_semantic_consistency', return_value=(True, 'Valid')), \
             patch.object(verification_pipeline, '_layer_5_zero_fabrication', return_value=(True, 'No fabrication detected')):

            passed, result = verification_pipeline.verify_extraction(1, 1, valid_extraction)

            assert passed is True
            assert result['overall_passed'] is True
            assert result['layer_1_quran_api']['passed'] is True
            assert result['layer_2_ansari_api']['passed'] is True
            assert result['layer_3_peer_review']['passed'] is True
            assert result['layer_4_semantic_consistency']['passed'] is True
            assert result['layer_5_zero_fabrication']['passed'] is True
            assert result['confidence_score'] == 1.0


class TestVerificationPipelineSingleLayerFails:
    """Test when a single layer fails."""

    def test_single_layer_fails(self, verification_pipeline, valid_extraction):
        """Overall should fail if even one layer fails."""
        with patch.object(verification_pipeline, '_layer_1_quran_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_2_ansari_api', return_value=(False, 'Not found')), \
             patch.object(verification_pipeline, '_layer_3_peer_review', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_4_semantic_consistency', return_value=(True, 'Valid')), \
             patch.object(verification_pipeline, '_layer_5_zero_fabrication', return_value=(True, 'No fabrication detected')):

            passed, result = verification_pipeline.verify_extraction(1, 1, valid_extraction)

            assert passed is False
            assert result['overall_passed'] is False
            assert result['layer_2_ansari_api']['passed'] is False
            assert result['layer_2_ansari_api']['message'] == 'Not found'


class TestVerificationPipelineMultipleLayersFail:
    """Test when multiple layers fail."""

    def test_multiple_layers_fail(self, verification_pipeline, valid_extraction):
        """Should capture all failures and calculate confidence correctly."""
        with patch.object(verification_pipeline, '_layer_1_quran_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_2_ansari_api', return_value=(False, 'Not found')), \
             patch.object(verification_pipeline, '_layer_3_peer_review', return_value=(False, 'Missing citations')), \
             patch.object(verification_pipeline, '_layer_4_semantic_consistency', return_value=(True, 'Valid')), \
             patch.object(verification_pipeline, '_layer_5_zero_fabrication', return_value=(True, 'No fabrication detected')):

            passed, result = verification_pipeline.verify_extraction(1, 1, valid_extraction)

            assert passed is False
            assert result['overall_passed'] is False
            assert result['layer_2_ansari_api']['passed'] is False
            assert result['layer_3_peer_review']['passed'] is False
            assert result['confidence_score'] == 0.6  # 3/5 layers passed


class TestVerificationPipelineMissingSourceCitations:
    """Test layer 3 fails when source citations are missing."""

    def test_missing_source_citations(self, verification_pipeline, valid_extraction):
        """Layer 3 should fail if source_citations is empty."""
        extraction_no_citations = valid_extraction.copy()
        extraction_no_citations['source_citations'] = []

        with patch.object(verification_pipeline, '_layer_1_quran_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_2_ansari_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_3_peer_review', return_value=(False, 'Missing peer-reviewed source citations')), \
             patch.object(verification_pipeline, '_layer_4_semantic_consistency', return_value=(True, 'Valid')), \
             patch.object(verification_pipeline, '_layer_5_zero_fabrication', return_value=(True, 'No fabrication detected')):

            passed, result = verification_pipeline.verify_extraction(1, 1, extraction_no_citations)

            assert result['layer_3_peer_review']['passed'] is False
            assert 'citation' in result['layer_3_peer_review']['message'].lower()


class TestVerificationPipelineUnverifiableClaims:
    """Test layer 5 detects fabricated or unverifiable claims."""

    def test_unverifiable_claims(self, verification_pipeline, valid_extraction):
        """Layer 5 should detect and fail on unverifiable claims."""
        extraction_fabricated = valid_extraction.copy()
        extraction_fabricated['claims'] = [
            {'claim': 'Fabricated scientific claim', 'verifiable': False}
        ]

        with patch.object(verification_pipeline, '_layer_1_quran_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_2_ansari_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_3_peer_review', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_4_semantic_consistency', return_value=(True, 'Valid')), \
             patch.object(verification_pipeline, '_layer_5_zero_fabrication', return_value=(False, 'Unverifiable claims detected: fabrication risk')):

            passed, result = verification_pipeline.verify_extraction(1, 1, extraction_fabricated)

            assert result['layer_5_zero_fabrication']['passed'] is False
            assert 'fabricat' in result['layer_5_zero_fabrication']['message'].lower()


class TestVerificationPipelineConfidenceScoreCalculation:
    """Test confidence score is calculated correctly."""

    def test_confidence_score_calculation(self, verification_pipeline, valid_extraction):
        """Confidence should equal (passed_layers / 5)."""
        # 3 layers pass, 2 fail = 0.6 confidence
        with patch.object(verification_pipeline, '_layer_1_quran_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_2_ansari_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_3_peer_review', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_4_semantic_consistency', return_value=(False, 'Invalid concepts')), \
             patch.object(verification_pipeline, '_layer_5_zero_fabrication', return_value=(False, 'Fabrication detected')):

            passed, result = verification_pipeline.verify_extraction(1, 1, valid_extraction)

            assert result['confidence_score'] == 0.6


class TestVerificationPipelineResultStructure:
    """Test the result dictionary has the correct structure."""

    def test_result_structure(self, verification_pipeline, valid_extraction):
        """Result dict should have all required fields and structure."""
        with patch.object(verification_pipeline, '_layer_1_quran_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_2_ansari_api', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_3_peer_review', return_value=(True, 'Verified')), \
             patch.object(verification_pipeline, '_layer_4_semantic_consistency', return_value=(True, 'Valid')), \
             patch.object(verification_pipeline, '_layer_5_zero_fabrication', return_value=(True, 'No fabrication detected')):

            passed, result = verification_pipeline.verify_extraction(1, 1, valid_extraction)

            # Check overall structure
            assert 'overall_passed' in result
            assert 'layer_1_quran_api' in result
            assert 'layer_2_ansari_api' in result
            assert 'layer_3_peer_review' in result
            assert 'layer_4_semantic_consistency' in result
            assert 'layer_5_zero_fabrication' in result
            assert 'confidence_score' in result

            # Check each layer has correct structure
            for layer_key in ['layer_1_quran_api', 'layer_2_ansari_api', 'layer_3_peer_review',
                             'layer_4_semantic_consistency', 'layer_5_zero_fabrication']:
                assert 'passed' in result[layer_key]
                assert 'message' in result[layer_key]
                assert isinstance(result[layer_key]['passed'], bool)
                assert isinstance(result[layer_key]['message'], str)

            # Check confidence_score is a float
            assert isinstance(result['confidence_score'], float)
            assert 0.0 <= result['confidence_score'] <= 1.0
