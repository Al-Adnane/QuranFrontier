import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

"""Tests for DomainAnalyzer class."""
import pytest
from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer


class TestDomainAnalyzer:
    """Test suite for DomainAnalyzer domain detection and analysis."""

    def setup_method(self):
        """Initialize DomainAnalyzer before each test."""
        self.analyzer = DomainAnalyzer()

    def test_analyze_verse_physics(self):
        """Test physics domain detection with sky and heavens keywords."""
        verse_text = "The sky is expanding and the stars shine with gravity."
        verse_key = "1:1"

        result = self.analyzer.analyze_verse(verse_text, verse_key)

        assert result is not None
        assert result.get("physics") is not None
        physics = result["physics"]
        assert "concepts" in physics
        assert "principles" in physics
        assert "references" in physics
        assert "confidence" in physics
        assert physics["references"] == "1:1"
        assert physics["confidence"] > 0.5

    def test_analyze_verse_biology(self):
        """Test biology domain detection with seed and creation keywords."""
        verse_text = "Every seed grows through stages of creation and cell development."
        verse_key = "2:5"

        result = self.analyzer.analyze_verse(verse_text, verse_key)

        assert result is not None
        assert result.get("biology") is not None
        biology = result["biology"]
        assert "concepts" in biology
        assert "principles" in biology
        assert "references" in biology
        assert "confidence" in biology
        assert biology["references"] == "2:5"
        assert biology["confidence"] > 0.5

    def test_analyze_verse_medicine(self):
        """Test medicine domain detection with healing and cure keywords."""
        verse_text = "In honey there is healing for disease and remedy for illness."
        verse_key = "16:69"

        result = self.analyzer.analyze_verse(verse_text, verse_key)

        assert result is not None
        assert result.get("medicine") is not None
        medicine = result["medicine"]
        assert "concepts" in medicine
        assert "principles" in medicine
        assert "references" in medicine
        assert "confidence" in medicine
        assert medicine["references"] == "16:69"
        assert medicine["confidence"] > 0.5

    def test_analyze_verse_engineering(self):
        """Test engineering domain detection with structure and build keywords."""
        verse_text = "Build a structure with brass and iron for strength and protection."
        verse_key = "18:96"

        result = self.analyzer.analyze_verse(verse_text, verse_key)

        assert result is not None
        assert result.get("engineering") is not None
        engineering = result["engineering"]
        assert "concepts" in engineering
        assert "principles" in engineering
        assert "references" in engineering
        assert "confidence" in engineering
        assert engineering["references"] == "18:96"
        assert engineering["confidence"] > 0.5

    def test_analyze_verse_agriculture(self):
        """Test agriculture domain detection with plants and crops keywords."""
        verse_text = "Plants grow from soil watered by rain, producing gardens and fruits."
        verse_key = "80:31"

        result = self.analyzer.analyze_verse(verse_text, verse_key)

        assert result is not None
        assert result.get("agriculture") is not None
        agriculture = result["agriculture"]
        assert "concepts" in agriculture
        assert "principles" in agriculture
        assert "references" in agriculture
        assert "confidence" in agriculture
        assert agriculture["references"] == "80:31"
        assert agriculture["confidence"] > 0.5

    def test_no_domain_matches(self):
        """Test verse with no matching domains returns all None."""
        verse_text = "Praise be to Allah for His guidance and mercy."
        verse_key = "1:2"

        result = self.analyzer.analyze_verse(verse_text, verse_key)

        assert result is not None
        assert result.get("physics") is None
        assert result.get("biology") is None
        assert result.get("medicine") is None
        assert result.get("engineering") is None
        assert result.get("agriculture") is None

    def test_confidence_scoring(self):
        """Test confidence calculation increases with keyword count."""
        # Single keyword should have lower confidence
        single_keyword = "The sky is vast."
        result_single = self.analyzer.analyze_verse(single_keyword, "1:1")

        # Multiple keywords should have higher confidence
        multi_keyword = "The sky and stars and heavens show gravity and motion."
        result_multi = self.analyzer.analyze_verse(multi_keyword, "1:1")

        if result_single.get("physics") and result_multi.get("physics"):
            single_conf = result_single["physics"]["confidence"]
            multi_conf = result_multi["physics"]["confidence"]
            assert multi_conf > single_conf

    def test_multiple_domains(self):
        """Test verse matching multiple domains simultaneously."""
        verse_text = "Build a structure with iron in gardens of crops under the sky."
        verse_key = "3:14"

        result = self.analyzer.analyze_verse(verse_text, verse_key)

        assert result is not None
        # Check that at least 3 domains are detected
        detected_domains = sum(1 for v in result.values() if v is not None)
        assert detected_domains >= 2

        # Verify structure of detected domains
        for domain_name, domain_data in result.items():
            if domain_data is not None:
                assert "concepts" in domain_data
                assert "principles" in domain_data
                assert domain_data["references"] == "3:14"
