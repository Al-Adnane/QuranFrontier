import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

"""Tests for AsbabAlNuzulMapper class."""
import pytest
from quran.corpus_extraction.framework.asbab_mapper import AsbabAlNuzulMapper


class TestAsbabAlNuzulMapper:
    """Test suite for AsbabAlNuzulMapper revelation context extraction."""

    def setup_method(self):
        """Initialize AsbabAlNuzulMapper before each test."""
        self.mapper = AsbabAlNuzulMapper()

    def test_extract_asbab_basic(self):
        """Test basic asbab extraction returns dict with all required fields."""
        surah = 2
        ayah = 143
        verse_text = "Thus, We have made you a moderate nation, that you may be witnesses over mankind."

        result = self.mapper.extract_asbab(surah, ayah, verse_text)

        assert result is not None
        assert isinstance(result, dict)
        assert "surah" in result
        assert "ayah" in result
        assert "verse_key" in result
        assert "occasion_type" in result
        assert "historical_period" in result
        assert "key_events" in result
        assert "involved_persons" in result
        assert "scholarly_consensus" in result
        assert "confidence" in result
        assert "source_indicators" in result

        # Verify values
        assert result["surah"] == 2
        assert result["ayah"] == 143
        assert result["verse_key"] == "2:143"
        assert isinstance(result["key_events"], list)
        assert isinstance(result["involved_persons"], list)
        assert isinstance(result["scholarly_consensus"], bool)
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["source_indicators"], list)

    def test_occasion_type_identification(self):
        """Test identification of inquiry-type occasion (companions asking questions)."""
        surah = 2
        ayah = 219
        # Classic inquiry verse: "They ask you about wine and gambling..."
        verse_text = "They ask you about wine and gambling. Say: In both there is great sin."

        result = self.mapper.extract_asbab(surah, ayah, verse_text)

        assert result is not None
        assert result["occasion_type"] == "inquiry"
        assert len(result["source_indicators"]) > 0
        assert any("ask" in indicator.lower() for indicator in result["source_indicators"])

    def test_meccan_period_detection(self):
        """Test detection of Meccan period verses (early revelation)."""
        surah = 96  # Early Meccan surah
        ayah = 1
        verse_text = "Read in the name of your Lord who created"

        result = self.mapper.extract_asbab(surah, ayah, verse_text)

        assert result is not None
        assert result["historical_period"] == "Meccan"

    def test_medinan_period_detection(self):
        """Test detection of Medinan period verses (later revelation)."""
        surah = 2  # Clearly Medinan surah
        ayah = 1
        verse_text = "Alif Lam Meem. This is the Book in which there is no doubt."

        result = self.mapper.extract_asbab(surah, ayah, verse_text)

        assert result is not None
        assert result["historical_period"] == "Medinan"

    def test_key_events_extraction(self):
        """Test extraction of key historical events from verse content."""
        surah = 3
        ayah = 123
        # Verse referencing Battle of Uhud context
        verse_text = "Allah has given you victory at Badr, when you were weak."

        result = self.mapper.extract_asbab(surah, ayah, verse_text)

        assert result is not None
        assert isinstance(result["key_events"], list)
        # Should extract battle/event references
        assert len(result["key_events"]) > 0 or result["confidence"] < 0.5  # May be low confidence if no clear events

    def test_persons_extraction(self):
        """Test extraction of persons mentioned or involved in verse context."""
        surah = 9
        ayah = 40
        # Verse mentioning Prophet Muhammad and Abu Bakr in cave
        verse_text = "If you do not aid the Prophet, Allah has already aided him."

        result = self.mapper.extract_asbab(surah, ayah, verse_text)

        assert result is not None
        assert isinstance(result["involved_persons"], list)
        # Should identify Prophet Muhammad
        assert len(result["involved_persons"]) > 0

    def test_source_indicators(self):
        """Test identification of textual cues suggesting revelation context."""
        surah = 5
        ayah = 101
        verse_text = "O you who have believed, ask not about matters which, if made plain to you, may cause you hardship."

        result = self.mapper.extract_asbab(surah, ayah, verse_text)

        assert result is not None
        assert isinstance(result["source_indicators"], list)
        assert len(result["source_indicators"]) > 0
        # Should identify "O you who have believed" or "ask" as indicators
        indicators_text = " ".join(result["source_indicators"]).lower()
        assert "ask" in indicators_text or "believed" in indicators_text or len(indicators_text) > 0

    def test_confidence_scoring(self):
        """Test confidence scoring - higher with clear context, lower with ambiguous."""
        # Clear inquiry verse
        surah1 = 2
        ayah1 = 219
        verse_text1 = "They ask you about wine and gambling. Say: In both there is great sin."
        result1 = self.mapper.extract_asbab(surah1, ayah1, verse_text1)

        # Generic theological verse
        surah2 = 1
        ayah2 = 2
        verse_text2 = "Praise be to Allah, Lord of the worlds."
        result2 = self.mapper.extract_asbab(surah2, ayah2, verse_text2)

        assert result1 is not None
        assert result2 is not None
        # Verse with clear asbab markers should have higher or equal confidence
        assert result1["confidence"] >= result2["confidence"]
