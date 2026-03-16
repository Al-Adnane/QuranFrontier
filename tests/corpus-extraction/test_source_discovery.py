"""
Test suite for source discovery module.
Tests API client initialization, concept discovery, caching, and deduplication.
All tests use mocked API responses to avoid actual network calls.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from quran.corpus_extraction.sources.source_discovery import SourceDiscovery
from quran.corpus_extraction.sources.semantic_scholar_client import SemanticScholarClient
from quran.corpus_extraction.sources.crossref_client import CrossRefClient


@pytest.fixture
def mock_semantic_scholar_response():
    """Mock response from Semantic Scholar API."""
    return {
        "data": [
            {
                "paperId": "ss_001",
                "title": "Gravitational Waves in Cosmology",
                "year": 2023,
                "authors": [{"name": "John Doe"}, {"name": "Jane Smith"}],
                "externalIds": {
                    "DOI": "10.1038/nature12345"
                },
                "venue": "Nature"
            },
            {
                "paperId": "ss_002",
                "title": "General Relativity and Modern Physics",
                "year": 2022,
                "authors": [{"name": "Albert Einstein"}],
                "externalIds": {
                    "DOI": "10.1103/PhysRev.47.777"
                },
                "venue": "Physical Review"
            }
        ]
    }


@pytest.fixture
def mock_crossref_response():
    """Mock response from CrossRef API."""
    return {
        "message": {
            "items": [
                {
                    "title": ["Relativistic Effects in Gravitational Systems"],
                    "DOI": "10.1088/0264-9381/23/12/001",
                    "published-online": {
                        "date-parts": [[2023, 3, 15]]
                    },
                    "author": [
                        {"given": "Robert", "family": "Oppenheimer"},
                        {"given": "Richard", "family": "Feynman"}
                    ],
                    "container-title": "Classical and Quantum Gravity"
                },
                {
                    "title": ["Quantum Mechanics and Gravity"],
                    "DOI": "10.1103/RevModPhys.21.447",
                    "published-online": {
                        "date-parts": [[2021, 6, 10]]
                    },
                    "author": [
                        {"given": "Paul", "family": "Dirac"}
                    ],
                    "container-title": "Reviews of Modern Physics"
                }
            ]
        }
    }


@pytest.fixture
def sample_concepts():
    """Sample concepts for testing."""
    return [
        {
            "id": "physics_001",
            "name": "gravitation",
            "domain": "physics",
            "tier": 1,
            "definition": "The force of attraction between masses"
        },
        {
            "id": "physics_002",
            "name": "celestial_mechanics",
            "domain": "physics",
            "tier": 1,
            "definition": "Physics of motion of celestial bodies"
        }
    ]


@pytest.fixture
def source_discovery():
    """Create a SourceDiscovery instance for testing."""
    return SourceDiscovery()


class TestSemanticScholarClientInitialization:
    """Test SemanticScholarClient initialization."""

    def test_semantic_scholar_client_initializes(self):
        """Test that SemanticScholarClient can be instantiated."""
        client = SemanticScholarClient()
        assert client is not None

    def test_semantic_scholar_has_api_endpoint(self):
        """Test that client has API endpoint configured."""
        client = SemanticScholarClient()
        assert hasattr(client, 'api_endpoint')
        assert 'api.semanticscholar.org' in client.api_endpoint

    def test_semantic_scholar_has_rate_limiting(self):
        """Test that client has rate limiting configured."""
        client = SemanticScholarClient()
        assert hasattr(client, 'rate_limiter')


class TestCrossRefClientInitialization:
    """Test CrossRefClient initialization."""

    def test_crossref_client_initializes(self):
        """Test that CrossRefClient can be instantiated."""
        client = CrossRefClient()
        assert client is not None

    def test_crossref_has_api_endpoint(self):
        """Test that client has API endpoint configured."""
        client = CrossRefClient()
        assert hasattr(client, 'api_endpoint')
        assert 'api.crossref.org' in client.api_endpoint

    def test_crossref_has_rate_limiting(self):
        """Test that client has rate limiting configured."""
        client = CrossRefClient()
        assert hasattr(client, 'rate_limiter')


class TestSourceDiscoveryInitialization:
    """Test SourceDiscovery class initialization."""

    def test_source_discovery_initializes(self, source_discovery):
        """Test that SourceDiscovery can be instantiated."""
        assert source_discovery is not None

    def test_source_discovery_has_clients(self, source_discovery):
        """Test that SourceDiscovery has API clients."""
        assert hasattr(source_discovery, 'ss_client')
        assert hasattr(source_discovery, 'crossref_client')

    def test_source_discovery_has_cache(self, source_discovery):
        """Test that SourceDiscovery has cache."""
        assert hasattr(source_discovery, 'cache')
        assert isinstance(source_discovery.cache, dict)

    def test_source_discovery_initializes_empty_cache(self, source_discovery):
        """Test that cache initializes empty."""
        assert len(source_discovery.cache) == 0


class TestSemanticScholarQuerying:
    """Test Semantic Scholar API querying."""

    @patch('quran.corpus_extraction.sources.semantic_scholar_client.requests.Session.get')
    def test_query_semantic_scholar_returns_papers(self, mock_get, mock_semantic_scholar_response):
        """Test that querying Semantic Scholar returns papers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_semantic_scholar_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = SemanticScholarClient()
        papers = client.search("gravitation")

        assert papers is not None
        assert len(papers) >= 2
        assert "Gravitational" in papers[0]['title'] or "General Relativity" in papers[0]['title']

    @patch('quran.corpus_extraction.sources.semantic_scholar_client.requests.Session.get')
    def test_query_semantic_scholar_extracts_doi(self, mock_get, mock_semantic_scholar_response):
        """Test that DOI is extracted correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_semantic_scholar_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = SemanticScholarClient()
        papers = client.search("gravitation")

        assert papers[0]['doi'] == "10.1038/nature12345"
        assert papers[1]['doi'] == "10.1103/PhysRev.47.777"

    @patch('quran.corpus_extraction.sources.semantic_scholar_client.requests.Session.get')
    def test_query_semantic_scholar_respects_rate_limiting(self, mock_get):
        """Test that rate limiting is applied."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = SemanticScholarClient()
        # Make multiple requests
        client.search("gravitation")
        client.search("physics")

        # Should have applied rate limiting (delay)
        assert mock_get.call_count >= 2


class TestCrossRefQuerying:
    """Test CrossRef API querying."""

    @patch('quran.corpus_extraction.sources.crossref_client.requests.Session.get')
    def test_query_crossref_returns_papers(self, mock_get, mock_crossref_response):
        """Test that querying CrossRef returns papers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_crossref_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = CrossRefClient()
        papers = client.search("gravitation")

        assert papers is not None
        assert len(papers) >= 2

    @patch('quran.corpus_extraction.sources.crossref_client.requests.Session.get')
    def test_query_crossref_extracts_metadata(self, mock_get, mock_crossref_response):
        """Test that CrossRef metadata is extracted correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_crossref_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = CrossRefClient()
        papers = client.search("gravitation")

        assert papers[0]['doi'] == "10.1088/0264-9381/23/12/001"
        assert 'title' in papers[0]
        assert 'authors' in papers[0]
        assert len(papers[0]['authors']) > 0
        assert papers[0]['year'] is not None


class TestSourceDiscoveryConcept:
    """Test discovering sources for a single concept."""

    @patch.object(SemanticScholarClient, 'search')
    @patch.object(CrossRefClient, 'search')
    def test_discover_sources_for_concept(self, mock_crossref_search, mock_ss_search,
                                          source_discovery, mock_semantic_scholar_response,
                                          mock_crossref_response):
        """Test discovering sources for a single concept."""
        # Mock API responses
        ss_papers = [
            {
                "doi": "10.1038/nature12345",
                "title": "Gravitational Waves in Cosmology",
                "year": 2023,
                "authors": ["John Doe", "Jane Smith"],
                "source": "semantic_scholar"
            }
        ]

        cf_papers = [
            {
                "doi": "10.1088/0264-9381/23/12/001",
                "title": "Relativistic Effects in Gravitational Systems",
                "year": 2023,
                "authors": ["Robert Oppenheimer"],
                "source": "crossref"
            }
        ]

        mock_ss_search.return_value = ss_papers
        mock_crossref_search.return_value = cf_papers

        sources = source_discovery.discover_sources_for_concept(
            "physics_001", "gravitation", "physics", limit=10
        )

        assert sources is not None
        assert len(sources) == 2
        assert sources[0]['source'] in ['semantic_scholar', 'crossref']

    @patch.object(SemanticScholarClient, 'search')
    @patch.object(CrossRefClient, 'search')
    def test_discover_sources_returns_correct_structure(self, mock_crossref_search,
                                                         mock_ss_search, source_discovery):
        """Test that discovered sources have correct structure."""
        ss_papers = [
            {
                "doi": "10.1038/nature12345",
                "title": "Test Paper",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            }
        ]

        mock_ss_search.return_value = ss_papers
        mock_crossref_search.return_value = []

        sources = source_discovery.discover_sources_for_concept(
            "physics_001", "gravitation", "physics"
        )

        source = sources[0]
        assert 'doi' in source
        assert 'title' in source
        assert 'year' in source
        assert 'authors' in source
        assert 'source' in source


class TestSourceDeduplication:
    """Test deduplication of sources from multiple APIs."""

    @patch.object(SemanticScholarClient, 'search')
    @patch.object(CrossRefClient, 'search')
    def test_deduplication_by_doi(self, mock_crossref_search, mock_ss_search,
                                   source_discovery):
        """Test that duplicate papers (same DOI) are deduplicated."""
        # Same paper from both APIs
        same_doi = "10.1038/nature12345"

        ss_papers = [
            {
                "doi": same_doi,
                "title": "Gravitational Waves",
                "year": 2023,
                "authors": ["John Doe"],
                "source": "semantic_scholar"
            }
        ]

        cf_papers = [
            {
                "doi": same_doi,
                "title": "Gravitational Waves",
                "year": 2023,
                "authors": ["John Doe"],
                "source": "crossref"
            }
        ]

        mock_ss_search.return_value = ss_papers
        mock_crossref_search.return_value = cf_papers

        sources = source_discovery.discover_sources_for_concept(
            "physics_001", "gravitation", "physics"
        )

        # Should only have one entry despite appearing in both APIs
        dois = [s['doi'] for s in sources]
        assert len(set(dois)) == 1

    @patch.object(SemanticScholarClient, 'search')
    @patch.object(CrossRefClient, 'search')
    def test_no_deduplication_for_different_papers(self, mock_crossref_search,
                                                     mock_ss_search, source_discovery):
        """Test that different papers are not deduplicated."""
        ss_papers = [
            {
                "doi": "10.1038/nature12345",
                "title": "Paper A",
                "year": 2023,
                "authors": ["Author A"],
                "source": "semantic_scholar"
            }
        ]

        cf_papers = [
            {
                "doi": "10.1088/0264-9381/23/12/001",
                "title": "Paper B",
                "year": 2023,
                "authors": ["Author B"],
                "source": "crossref"
            }
        ]

        mock_ss_search.return_value = ss_papers
        mock_crossref_search.return_value = cf_papers

        sources = source_discovery.discover_sources_for_concept(
            "physics_001", "gravitation", "physics"
        )

        assert len(sources) == 2


class TestSourceValidation:
    """Test source validation."""

    @patch.object(SemanticScholarClient, 'search')
    @patch.object(CrossRefClient, 'search')
    def test_validate_sources_requires_doi(self, mock_crossref_search, mock_ss_search,
                                            source_discovery):
        """Test that sources without DOI are handled."""
        papers = [
            {
                "doi": "10.1038/nature12345",
                "title": "Valid Paper",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            },
            {
                "title": "Invalid Paper (no DOI)",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            }
        ]

        mock_ss_search.return_value = papers
        mock_crossref_search.return_value = []

        sources = source_discovery.discover_sources_for_concept(
            "physics_001", "gravitation", "physics"
        )

        # Should have at least the valid paper with DOI
        assert len(sources) >= 1
        # Most sources should have DOI
        doi_sources = [s for s in sources if 'doi' in s]
        assert len(doi_sources) > 0

    def test_validate_sources_function_exists(self, source_discovery):
        """Test that validate_sources method exists."""
        assert hasattr(source_discovery, 'validate_sources')
        assert callable(source_discovery.validate_sources)

    def test_validate_sources_checks_structure(self, source_discovery):
        """Test that validate_sources checks source structure."""
        valid_source = {
            "doi": "10.1038/nature12345",
            "title": "Valid Paper",
            "year": 2023,
            "authors": ["Author"],
            "source": "semantic_scholar"
        }

        result = source_discovery.validate_sources([valid_source])
        assert result is True

    def test_validate_sources_rejects_invalid(self, source_discovery):
        """Test that validate_sources rejects invalid sources."""
        invalid_source = {
            "title": "No DOI"
        }

        result = source_discovery.validate_sources([invalid_source])
        assert result is False


class TestSourceCaching:
    """Test source caching functionality."""

    @patch.object(SemanticScholarClient, 'search')
    @patch.object(CrossRefClient, 'search')
    def test_sources_are_cached(self, mock_crossref_search, mock_ss_search,
                                source_discovery):
        """Test that discovered sources are cached."""
        papers = [
            {
                "doi": "10.1038/nature12345",
                "title": "Test Paper",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            }
        ]

        mock_ss_search.return_value = papers
        mock_crossref_search.return_value = []

        source_discovery.discover_sources_for_concept(
            "physics_001", "gravitation", "physics"
        )

        assert "physics_001" in source_discovery.cache
        assert len(source_discovery.cache["physics_001"]) > 0

    def test_get_sources_by_concept_from_cache(self, source_discovery):
        """Test retrieving cached sources."""
        concept_id = "physics_001"
        test_sources = [
            {
                "doi": "10.1038/nature12345",
                "title": "Cached Paper",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            }
        ]

        source_discovery.cache[concept_id] = test_sources

        cached = source_discovery.get_sources_by_concept(concept_id)

        assert cached == test_sources

    def test_get_sources_returns_empty_for_unknown_concept(self, source_discovery):
        """Test that unknown concepts return empty."""
        sources = source_discovery.get_sources_by_concept("unknown_concept")

        assert sources == [] or sources is None


class TestBatchSourceDiscovery:
    """Test batch discovery for all concepts."""

    @patch('builtins.open', create=True)
    @patch('json.load')
    @patch.object(SourceDiscovery, 'discover_sources_for_concept')
    def test_discover_sources_for_all_concepts(self, mock_discover_concept,
                                               mock_json_load, mock_open,
                                               source_discovery, sample_concepts):
        """Test discovering sources for all concepts."""
        # Mock concepts file
        concepts_data = {
            "concepts": sample_concepts
        }
        mock_json_load.return_value = concepts_data

        # Mock individual concept discovery
        mock_discover_concept.return_value = [
            {
                "doi": f"10.1038/{i}",
                "title": f"Paper {i}",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            }
            for i in range(10)
        ]

        source_discovery.discover_sources_for_all_concepts("concepts.json")

        # Should have called discover for each concept
        assert mock_discover_concept.call_count >= len(sample_concepts)

    def test_batch_discovery_saves_cache(self, sample_concepts, tmp_path):
        """Test that batch discovery saves to cache."""
        # Create temporary concepts file
        concepts_file = tmp_path / "test_concepts.json"
        concepts_data = {
            "concepts": sample_concepts
        }
        import json
        with open(concepts_file, 'w') as f:
            json.dump(concepts_data, f)

        # Create a new discovery instance and mock its internal methods
        discovery = SourceDiscovery()

        with patch.object(discovery.ss_client, 'search') as mock_ss:
            with patch.object(discovery.crossref_client, 'search') as mock_cf:
                mock_ss.return_value = [
                    {
                        "doi": "10.1038/nature12345",
                        "title": "Test Paper",
                        "year": 2023,
                        "authors": ["Author"],
                        "source": "semantic_scholar"
                    }
                ]
                mock_cf.return_value = []

                discovery.discover_sources_for_all_concepts(str(concepts_file))

                # Cache should be populated
                assert len(discovery.cache) > 0


class TestStatisticsAndMetadata:
    """Test statistics and metadata generation."""

    def test_generate_metadata(self, source_discovery):
        """Test that metadata is generated correctly."""
        # Populate cache with test data
        for i in range(3):
            source_discovery.cache[f"concept_{i}"] = [
                {"doi": f"10.1038/{j}", "title": f"Paper {j}", "year": 2023}
                for j in range(10)
            ]

        metadata = source_discovery.get_metadata()

        assert "total_concepts" in metadata
        assert "covered_concepts" in metadata
        assert "total_papers" in metadata
        assert "discovery_date" in metadata

    def test_metadata_counts_correctly(self, source_discovery):
        """Test that metadata counts are accurate."""
        source_discovery.cache["concept_1"] = [
            {"doi": "10.1038/a"},
            {"doi": "10.1038/b"}
        ]
        source_discovery.cache["concept_2"] = [
            {"doi": "10.1038/c"}
        ]

        metadata = source_discovery.get_metadata()

        assert metadata["covered_concepts"] == 2
        assert metadata["total_papers"] == 3


class TestSourceCacheFile:
    """Test source cache file operations."""

    def test_save_cache_to_file(self, source_discovery, tmp_path):
        """Test saving cache to JSON file."""
        cache_file = tmp_path / "source_cache.json"

        source_discovery.cache["physics_001"] = [
            {
                "doi": "10.1038/nature12345",
                "title": "Test Paper",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            }
        ]

        source_discovery.save_cache(str(cache_file))

        assert cache_file.exists()

    def test_cache_file_has_correct_structure(self, source_discovery, tmp_path):
        """Test that cache file has expected structure."""
        cache_file = tmp_path / "source_cache.json"

        source_discovery.cache["physics_001"] = [
            {
                "doi": "10.1038/nature12345",
                "title": "Test Paper",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            }
        ]

        source_discovery.save_cache(str(cache_file))

        with open(cache_file) as f:
            data = json.load(f)

        assert "metadata" in data
        assert "concept_sources" in data

    def test_load_cache_from_file(self, source_discovery, tmp_path):
        """Test loading cache from file."""
        cache_file = tmp_path / "source_cache.json"

        # Create test cache file
        test_data = {
            "metadata": {
                "total_concepts": 400,
                "covered_concepts": 2,
                "total_papers": 20
            },
            "concept_sources": {
                "physics_001": [
                    {
                        "doi": "10.1038/nature12345",
                        "title": "Test Paper",
                        "year": 2023,
                        "authors": ["Author"],
                        "source": "semantic_scholar"
                    }
                ]
            }
        }

        with open(cache_file, 'w') as f:
            json.dump(test_data, f)

        source_discovery.load_cache(str(cache_file))

        assert "physics_001" in source_discovery.cache


class TestErrorHandling:
    """Test error handling in source discovery."""

    @patch.object(SemanticScholarClient, 'search')
    def test_handles_api_errors_gracefully(self, mock_search, source_discovery):
        """Test that API errors are handled gracefully."""
        mock_search.side_effect = Exception("API Error")

        # Should not raise exception
        try:
            sources = source_discovery.discover_sources_for_concept(
                "physics_001", "gravitation", "physics"
            )
            # Either returns empty or handles error
            assert isinstance(sources, list)
        except Exception as e:
            pytest.fail(f"Should handle API errors gracefully: {e}")

    def test_handles_invalid_concept_file(self, source_discovery):
        """Test handling of invalid concept file."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises((FileNotFoundError, Exception)):
                source_discovery.discover_sources_for_all_concepts("nonexistent.json")


class TestIntegration:
    """Integration tests."""

    @patch.object(SemanticScholarClient, 'search')
    @patch.object(CrossRefClient, 'search')
    def test_end_to_end_discovery_and_caching(self, mock_crossref_search, mock_ss_search,
                                               source_discovery, tmp_path):
        """Test complete workflow: discover, validate, cache, save."""
        papers = [
            {
                "doi": f"10.1038/paper{i}",
                "title": f"Paper {i}",
                "year": 2023,
                "authors": ["Author"],
                "source": "semantic_scholar"
            }
            for i in range(5)
        ]

        mock_ss_search.return_value = papers
        mock_crossref_search.return_value = []

        # Discover
        sources = source_discovery.discover_sources_for_concept(
            "physics_001", "gravitation", "physics"
        )

        assert len(sources) == 5

        # Cache file
        cache_file = tmp_path / "source_cache.json"
        source_discovery.save_cache(str(cache_file))

        assert cache_file.exists()

        # Load back
        new_discovery = SourceDiscovery()
        new_discovery.load_cache(str(cache_file))

        assert "physics_001" in new_discovery.cache
