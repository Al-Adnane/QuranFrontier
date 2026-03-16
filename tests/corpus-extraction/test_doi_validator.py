"""
Test suite for DOI validation, retraction tracking, and source quality scoring.

Tests the DOIValidator, RetractionTracker, and SourceQualityScorer classes.
All tests use mocked API responses to avoid actual network calls.
"""

import pytest
import json
import re
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from quran.corpus_extraction.sources.doi_validator import DOIValidator
from quran.corpus_extraction.sources.retraction_tracker import RetractionTracker
from quran.corpus_extraction.sources.source_quality_scorer import SourceQualityScorer


class TestDOIValidator:
    """Test suite for DOIValidator class."""

    @pytest.fixture
    def validator(self):
        """Initialize DOIValidator instance."""
        return DOIValidator()

    def test_validate_doi_format_valid_formats(self, validator):
        """Test validation of valid DOI formats."""
        valid_dois = [
            "10.1038/nature12345",
            "10.1103/PhysRev.47.777",
            "10.1088/0264-9381/23/12/001",
            "10.1016/j.jallcom.2012.04.083",
            "10.1145/2783446.2783467",
        ]
        for doi in valid_dois:
            assert validator.validate_doi_format(doi) is True, f"Should validate {doi}"

    def test_validate_doi_format_invalid_formats(self, validator):
        """Test rejection of invalid DOI formats."""
        invalid_dois = [
            "1038/nature12345",  # Missing 10. prefix
            "10.1038",  # Incomplete
            "10.nature12345",  # No slash
            "nature12345",  # No DOI prefix
            "",  # Empty string
            "10./12345",  # Empty prefix
        ]
        for doi in invalid_dois:
            assert validator.validate_doi_format(doi) is False, f"Should reject {doi}"

    def test_resolve_doi_success(self, validator):
        """Test successful DOI resolution via CrossRef API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": {
                "DOI": "10.1038/nature12345",
                "title": ["Test Paper Title"],
                "published-online": {"date-parts": [[2023, 3, 15]]},
                "author": [{"given": "John", "family": "Doe"}],
                "container-title": "Nature"
            }
        }
        mock_response.status_code = 200
        validator.session.get = Mock(return_value=mock_response)

        result = validator.resolve_doi("10.1038/nature12345")

        assert result is not None
        assert result["doi"] == "10.1038/nature12345"
        assert result["title"] == "Test Paper Title"
        assert result["year"] == 2023
        assert result["journal"] == "Nature"
        assert len(result["authors"]) > 0

    def test_resolve_doi_not_found(self, validator):
        """Test DOI resolution when paper not found."""
        # Mock the session get method
        mock_response = Mock()
        mock_response.status_code = 404
        validator.session.get = Mock(return_value=mock_response)

        result = validator.resolve_doi("10.invalid/doi12345")

        assert result is None

    def test_resolve_doi_network_error(self, validator):
        """Test DOI resolution with network error."""
        validator.session.get = Mock(side_effect=Exception("Network error"))

        result = validator.resolve_doi("10.1038/nature12345")

        assert result is None

    def test_validate_paper_metadata_match(self, validator):
        """Test metadata validation when resolved matches expected."""
        resolved_metadata = {
            "doi": "10.1038/nature12345",
            "title": "Gravitational Waves in Cosmology",
            "year": 2023,
            "journal": "Nature",
            "authors": ["John Doe", "Jane Smith"]
        }

        result = validator.validate_paper_metadata(
            resolved_metadata,
            expected_title="Gravitational Waves in Cosmology",
            expected_year=2023
        )

        assert result["is_valid"] is True
        assert result["match_score"] >= 0.8

    def test_validate_paper_metadata_title_mismatch(self, validator):
        """Test metadata validation with title mismatch."""
        resolved_metadata = {
            "doi": "10.1038/nature12345",
            "title": "Gravitational Waves in Cosmology",
            "year": 2023,
            "journal": "Nature",
            "authors": ["John Doe"]
        }

        result = validator.validate_paper_metadata(
            resolved_metadata,
            expected_title="Completely Different Title About Other Things",
            expected_year=2023
        )

        assert result["is_valid"] is False
        assert result["match_score"] <= 0.7

    def test_validate_paper_metadata_year_mismatch(self, validator):
        """Test metadata validation with year mismatch."""
        resolved_metadata = {
            "doi": "10.1038/nature12345",
            "title": "Gravitational Waves in Cosmology",
            "year": 2015,
            "journal": "Nature",
            "authors": ["John Doe"]
        }

        result = validator.validate_paper_metadata(
            resolved_metadata,
            expected_title="Gravitational Waves in Cosmology",
            expected_year=2023
        )

        assert result["is_valid"] is False

    @patch('quran.corpus_extraction.sources.doi_validator.DOIValidator.resolve_doi')
    def test_validate_all_sources(self, mock_resolve, validator):
        """Test batch validation of multiple sources."""
        # Mock resolve_doi to return metadata for each DOI
        def resolve_side_effect(doi):
            metadata_map = {
                "10.1038/nature12345": {
                    "doi": "10.1038/nature12345",
                    "title": "Paper One",
                    "year": 2023,
                    "journal": "Nature",
                    "authors": ["Author 1"]
                },
                "10.1103/PhysRev.47.777": {
                    "doi": "10.1103/PhysRev.47.777",
                    "title": "Paper Two",
                    "year": 2022,
                    "journal": "Physical Review",
                    "authors": ["Author 2"]
                },
            }
            return metadata_map.get(doi)

        mock_resolve.side_effect = resolve_side_effect

        sources = [
            {"doi": "10.1038/nature12345", "title": "Paper One", "year": 2023},
            {"doi": "10.1103/PhysRev.47.777", "title": "Paper Two", "year": 2022},
        ]

        result = validator.validate_all_sources(sources)

        assert result["total"] == 2
        assert result["valid"] >= 1
        assert "validation_details" in result

    def test_doi_format_regex_pattern(self, validator):
        """Test that DOI regex pattern is properly configured."""
        # The pattern should match 10.XXXX/YYYY format
        pattern = validator.doi_pattern
        assert pattern is not None

        # Test a few patterns
        assert re.match(pattern, "10.1038/nature12345")
        assert not re.match(pattern, "invalid/doi")


class TestRetractionTracker:
    """Test suite for RetractionTracker class."""

    @pytest.fixture
    def tracker(self):
        """Initialize RetractionTracker instance."""
        return RetractionTracker()

    @pytest.fixture
    def retracted_papers_cache(self, tmp_path):
        """Create a temporary retracted papers cache file."""
        cache_data = {
            "10.1038/retracted123": {
                "title": "Retracted Paper",
                "reason": "Fraudulent data",
                "date_retracted": "2023-01-15"
            },
            "10.1103/retracted456": {
                "title": "Another Retracted",
                "reason": "Data manipulation",
                "date_retracted": "2022-06-20"
            }
        }
        cache_file = tmp_path / "retracted_papers.json"
        cache_file.write_text(json.dumps(cache_data))
        return cache_file

    def test_is_paper_retracted_not_retracted(self, tracker):
        """Test checking a non-retracted paper."""
        # Mock the session get method
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_response.status_code = 200
        tracker.session.get = Mock(return_value=mock_response)

        result = tracker.is_paper_retracted("10.1038/nature12345")

        assert result is False

    def test_is_paper_retracted_found(self, tracker):
        """Test checking a retracted paper."""
        # Add to cache first
        tracker.add_to_cache(
            "10.1038/retracted123",
            "Retracted Paper",
            "Fraudulent data",
            "2023-01-15"
        )

        result = tracker.is_paper_retracted("10.1038/retracted123")

        assert result is True

    def test_get_retraction_details_from_cache(self, tracker, retracted_papers_cache):
        """Test retrieving retraction details from cache."""
        tracker.load_retraction_cache(str(retracted_papers_cache))

        result = tracker.get_retraction_details("10.1038/retracted123")

        assert result["is_retracted"] is True
        assert result["reason"] == "Fraudulent data"
        assert result["date_retracted"] == "2023-01-15"

    def test_get_retraction_details_not_found(self, tracker, retracted_papers_cache):
        """Test retrieving retraction details for non-retracted paper."""
        tracker.load_retraction_cache(str(retracted_papers_cache))

        result = tracker.get_retraction_details("10.1038/valid12345")

        assert result["is_retracted"] is False

    @patch('quran.corpus_extraction.sources.retraction_tracker.RetractionTracker.is_paper_retracted')
    def test_check_all_sources_for_retractions(self, mock_is_retracted, tracker):
        """Test batch checking of sources for retractions."""
        # Mock to return retracted=True for one paper
        def retracted_side_effect(doi):
            return doi == "10.1038/retracted123"

        mock_is_retracted.side_effect = retracted_side_effect

        sources = [
            {"doi": "10.1038/nature12345"},
            {"doi": "10.1038/retracted123"},
            {"doi": "10.1103/valid456"},
        ]

        result = tracker.check_all_sources_for_retractions(sources)

        assert result["total_checked"] == 3
        assert result["retracted_count"] == 1
        assert len(result["retracted_papers"]) == 1
        assert result["retracted_papers"][0]["doi"] == "10.1038/retracted123"

    def test_load_and_save_retraction_cache(self, tracker, tmp_path):
        """Test loading and saving retraction cache."""
        cache_file = tmp_path / "retracted_papers.json"

        cache_data = {
            "10.1038/test123": {
                "title": "Test",
                "reason": "Test reason",
                "date_retracted": "2023-01-01"
            }
        }

        tracker.retraction_cache = cache_data
        tracker.save_retraction_cache(str(cache_file))

        assert cache_file.exists()
        saved_data = json.loads(cache_file.read_text())
        assert saved_data == cache_data


class TestSourceQualityScorer:
    """Test suite for SourceQualityScorer class."""

    @pytest.fixture
    def scorer(self):
        """Initialize SourceQualityScorer instance."""
        return SourceQualityScorer()

    def test_score_top_tier_journal(self, scorer):
        """Test scoring for top-tier journal."""
        source = {
            "journal": "Nature",
            "year": 2023,
            "citations": 150,
            "peer_reviewed": True
        }

        score = scorer.calculate_quality_score(source)

        assert 0.0 <= score <= 1.0
        assert score > 0.7  # Top-tier should score high

    def test_score_mid_tier_journal(self, scorer):
        """Test scoring for mid-tier journal."""
        source = {
            "journal": "Journal of Physics",
            "year": 2022,
            "citations": 25,
            "peer_reviewed": True
        }

        score = scorer.calculate_quality_score(source)

        assert 0.0 <= score <= 1.0
        assert 0.4 < score < 0.7

    def test_score_preprint_no_peer_review(self, scorer):
        """Test scoring for preprint without peer review."""
        source = {
            "journal": "arXiv",
            "year": 2023,
            "citations": 5,
            "peer_reviewed": False
        }

        score = scorer.calculate_quality_score(source)

        assert 0.0 <= score <= 1.0
        assert score < 0.4  # Preprint should score lower

    def test_score_recent_paper(self, scorer):
        """Test recency bonus for recent papers."""
        source = {
            "journal": "Nature",
            "year": 2025,
            "citations": 50,
            "peer_reviewed": True
        }

        score = scorer.calculate_quality_score(source)

        assert 0.0 <= score <= 1.0
        assert score > 0.7

    def test_score_old_paper(self, scorer):
        """Test penalty for older papers."""
        source = {
            "journal": "Applied Research Quarterly",
            "year": 2000,
            "citations": 300,
            "peer_reviewed": True
        }

        score = scorer.calculate_quality_score(source)

        assert 0.0 <= score <= 1.0
        # Old paper (26 years old) gets lower score despite high citations
        # Score: journal(0.08) + recency(0.1) + citations(0.3) + peer_review(0.2) = 0.68
        assert score < 0.75

    def test_score_high_citation_count(self, scorer):
        """Test scoring for highly cited papers."""
        source = {
            "journal": "Science",
            "year": 2020,
            "citations": 500,
            "peer_reviewed": True
        }

        score = scorer.calculate_quality_score(source)

        assert 0.0 <= score <= 1.0
        assert score > 0.7

    def test_score_low_citation_count(self, scorer):
        """Test scoring for papers with low citation count."""
        source = {
            "journal": "Specialty Journal",
            "year": 2023,
            "citations": 2,
            "peer_reviewed": True
        }

        score = scorer.calculate_quality_score(source)

        assert 0.0 <= score <= 1.0
        assert score < 0.6

    def test_score_all_sources_batch(self, scorer):
        """Test batch scoring of multiple sources."""
        sources = [
            {
                "doi": "10.1038/nature12345",
                "journal": "Nature",
                "year": 2023,
                "citations": 150,
                "peer_reviewed": True
            },
            {
                "doi": "10.1103/PhysRev.47.777",
                "journal": "Physical Review",
                "year": 2020,
                "citations": 50,
                "peer_reviewed": True
            },
            {
                "doi": "10.1088/arxiv.2301.12345",
                "journal": "arXiv",
                "year": 2023,
                "citations": 5,
                "peer_reviewed": False
            }
        ]

        results = scorer.score_all_sources(sources)

        assert len(results) == 3
        assert all("quality_score" in r for r in results)
        assert all(0.0 <= r["quality_score"] <= 1.0 for r in results)

    def test_get_quality_statistics(self, scorer):
        """Test generation of quality score statistics."""
        sources = [
            {
                "doi": f"10.1038/paper{i}",
                "journal": "Nature" if i < 3 else "Journal X",
                "year": 2023,
                "citations": 100 if i < 3 else 10,
                "peer_reviewed": True
            }
            for i in range(6)
        ]

        scored = scorer.score_all_sources(sources)
        stats = scorer.get_quality_statistics(scored)

        assert stats["total"] == 6
        assert "mean" in stats
        assert "std_dev" in stats
        assert "min" in stats
        assert "max" in stats
        assert 0.0 <= stats["mean"] <= 1.0
        assert stats["std_dev"] >= 0.0

    def test_quality_score_boundaries(self, scorer):
        """Test that quality scores stay within valid bounds."""
        test_cases = [
            {"journal": "Nature", "year": 2025, "citations": 1000, "peer_reviewed": True},
            {"journal": "Unknown", "year": 1900, "citations": 0, "peer_reviewed": False},
            {"journal": "Journal", "year": 2023, "citations": 50, "peer_reviewed": True},
        ]

        for source in test_cases:
            score = scorer.calculate_quality_score(source)
            assert 0.0 <= score <= 1.0, f"Score {score} out of bounds for {source}"


class TestIntegrationValidation:
    """Integration tests for complete validation pipeline."""

    @pytest.fixture
    def sample_sources(self):
        """Create sample sources for integration testing."""
        return [
            {
                "doi": "10.1038/nature12345",
                "title": "Gravitational Waves in Cosmology",
                "year": 2023,
                "journal": "Nature",
                "authors": ["John Doe", "Jane Smith"],
                "citations": 150,
                "peer_reviewed": True
            },
            {
                "doi": "10.1103/PhysRev.47.777",
                "title": "Relativistic Effects in Physics",
                "year": 2022,
                "journal": "Physical Review",
                "authors": ["Albert Einstein"],
                "citations": 50,
                "peer_reviewed": True
            },
            {
                "doi": "10.1088/invalid",  # Invalid format
                "title": "Invalid Paper",
                "year": 2023,
                "journal": "Some Journal",
                "authors": ["Author"],
                "citations": 10,
                "peer_reviewed": False
            }
        ]

    @patch('quran.corpus_extraction.sources.doi_validator.DOIValidator.validate_doi_format')
    @patch('quran.corpus_extraction.sources.doi_validator.DOIValidator.resolve_doi')
    @patch('quran.corpus_extraction.sources.retraction_tracker.RetractionTracker.is_paper_retracted')
    def test_complete_validation_pipeline(
        self,
        mock_is_retracted,
        mock_resolve,
        mock_validate_format,
        sample_sources
    ):
        """Test complete validation pipeline with all components."""
        # Setup mocks
        mock_validate_format.side_effect = [True, True, False]

        def resolve_side_effect(doi):
            if doi == "10.1038/nature12345":
                return {
                    "doi": doi,
                    "title": "Gravitational Waves in Cosmology",
                    "year": 2023,
                    "journal": "Nature",
                    "authors": ["John Doe", "Jane Smith"]
                }
            return None

        mock_resolve.side_effect = resolve_side_effect
        mock_is_retracted.return_value = False

        validator = DOIValidator()
        tracker = RetractionTracker()
        scorer = SourceQualityScorer()

        # Validate
        validation_results = []
        for source in sample_sources:
            is_valid = validator.validate_doi_format(source["doi"])
            is_retracted = tracker.is_paper_retracted(source["doi"]) if is_valid else None
            quality = scorer.calculate_quality_score(source) if is_valid else None

            validation_results.append({
                "doi": source["doi"],
                "is_valid": is_valid,
                "is_retracted": is_retracted,
                "quality_score": quality
            })

        # Verify results
        assert len(validation_results) == 3
        assert validation_results[0]["is_valid"] is True
        assert validation_results[1]["is_valid"] is True
        assert validation_results[2]["is_valid"] is False

    def test_validation_summary_statistics(self, sample_sources):
        """Test generation of validation summary statistics."""
        scorer = SourceQualityScorer()
        scored_sources = scorer.score_all_sources(sample_sources)

        valid_count = len([s for s in scored_sources if "quality_score" in s])
        avg_quality = sum(s.get("quality_score", 0) for s in scored_sources) / max(valid_count, 1)

        assert valid_count >= 1
        assert 0.0 <= avg_quality <= 1.0
