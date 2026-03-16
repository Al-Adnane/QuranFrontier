import pytest
from unittest.mock import Mock, patch, MagicMock
from quran.corpus_extraction.infrastructure.api_integration import ApiIntegrationLayer


def test_get_verse_from_quran():
    api = ApiIntegrationLayer()
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'verse': {
                'text_madani': 'بسم الله',
                'translations': [{'text': 'In the name of God'}]
            }
        }
        verse = api.get_verse_from_quran(1, 1)
        assert verse['surah'] == 1
        assert verse['ayah'] == 1
        assert verse['text_ar'] == 'بسم الله'


def test_get_tafsir_from_ansari():
    api = ApiIntegrationLayer()
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'interpretation': 'Classical interpretation'
        }
        result = api.get_tafsir_from_ansari(23, 12, 'Ibn Kathir')
        assert result['source'] == 'Ibn Kathir'
        assert 'interpretation' in result['text']


def test_get_asbab_nuzul():
    api = ApiIntegrationLayer()
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'occasion': 'During early Medina period'
        }
        result = api.get_asbab_nuzul(2, 286)
        assert 'occasion' in result


def test_rate_limiting():
    api = ApiIntegrationLayer(rate_limit_per_hour=3)
    assert api.get_remaining_quota() == 3


def test_error_handling():
    api = ApiIntegrationLayer()
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception('Connection error')
        result = api.get_verse_from_quran(1, 1)
        assert 'error' in result
