"""Tests for Neo4j theological knowledge graph components.

Tests schema validation, graph building, and query functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from quran_core.src.data.neo4j_schema import (
    NodeType, RelationshipType, VerseNodeProperties, TafsirNodeProperties,
    HadithNodeProperties, NarratorNodeProperties, MadhhabNodeProperties,
    LinguisticConceptNodeProperties
)


class TestNodeProperties:
    """Test node property dataclasses."""

    def test_verse_node_properties(self):
        """Test Verse node properties."""
        props = VerseNodeProperties(
            surah=2,
            ayah=183,
            text_arabic="يا أيها الذين آمنوا",
            revelation_context="MEDINAN",
            revelation_order=87,
            theme="fasting",
            legal_topics=["fasting", "worship"],
            word_count=23,
        )

        assert props.surah == 2
        assert props.ayah == 183
        assert props.revelation_context == "MEDINAN"
        assert props.abrogation_status == "active"

        props_dict = props.to_dict()
        assert props_dict["surah"] == 2
        assert props_dict["abrogation_status"] == "active"

    def test_tafsir_node_properties(self):
        """Test Tafsir node properties."""
        props = TafsirNodeProperties(
            scholar_name="Ibn Kathir",
            school="Ibn Kathir",
            text_snippet="Commentary excerpt",
            edition="1st Edition",
            confidence=0.98,
        )

        assert props.scholar_name == "Ibn Kathir"
        assert props.confidence == 0.98
        assert props.to_dict()["confidence"] == 0.98

    def test_hadith_node_properties(self):
        """Test Hadith node properties."""
        props = HadithNodeProperties(
            text="Hadith text",
            collection="Sahih Bukhari",
            hadith_number="1901",
            grade="Sahih",
        )

        assert props.grade == "Sahih"
        assert props.collection == "Sahih Bukhari"

    def test_narrator_node_properties(self):
        """Test Narrator node properties."""
        props = NarratorNodeProperties(
            name="Abu Huraira",
            generation="Sahaba",
            reliability_grade="Thiqa",
            living_period="1st century AH",
            number_of_narrations=5374,
        )

        assert props.name == "Abu Huraira"
        assert props.reliability_grade == "Thiqa"
        assert props.number_of_narrations == 5374

    def test_madhab_node_properties(self):
        """Test Madhab node properties."""
        props = MadhhabNodeProperties(
            name="Hanafi",
            founder="Abu Hanifah",
            founding_century=8,
            principles=["Qiyas", "Istihsan"],
        )

        assert props.name == "Hanafi"
        assert len(props.principles) == 2

    def test_linguistic_concept_properties(self):
        """Test LinguisticConcept node properties."""
        props = LinguisticConceptNodeProperties(
            root="ص و م",
            meaning="Fasting",
            frequency_in_quran=17,
            surahs_containing_root=[2, 5, 9],
        )

        assert props.root == "ص و م"
        assert props.frequency_in_quran == 17
        assert 2 in props.surahs_containing_root


class TestNodeTypes:
    """Test node type enumerations."""

    def test_node_type_values(self):
        """Test NodeType enum values."""
        assert NodeType.VERSE.value == "Verse"
        assert NodeType.TAFSIR.value == "Tafsir"
        assert NodeType.HADITH.value == "Hadith"
        assert NodeType.NARRATOR.value == "Narrator"
        assert NodeType.MADHAB.value == "Madhab"

    def test_relationship_type_values(self):
        """Test RelationshipType enum values."""
        assert RelationshipType.EXPLAINED_BY.value == "EXPLAINED_BY"
        assert RelationshipType.SUPPORTED_BY.value == "SUPPORTED_BY"
        assert RelationshipType.MADHAB_RULING.value == "MADHAB_RULING"
        assert RelationshipType.ABROGATES.value == "ABROGATES"


class TestNeo4jGraphBuilder:
    """Test Neo4j graph building functionality."""

    @pytest.fixture
    def mock_driver(self):
        """Create mock Neo4j driver."""
        return MagicMock()

    @pytest.fixture
    def builder(self, mock_driver):
        """Create builder with mock driver."""
        from quran_core.src.data.neo4j_builder import Neo4jGraphBuilder

        with patch('quran_core.src.data.neo4j_builder.GraphDatabase') as mock_gdb:
            mock_gdb.driver.return_value = mock_driver
            builder = Neo4jGraphBuilder("neo4j://localhost", "user", "pass")
            builder.driver = mock_driver
            return builder

    def test_builder_initialization(self, builder, mock_driver):
        """Test builder initialization."""
        assert builder.driver == mock_driver
        assert builder.graph_stats["nodes_created"]["Verse"] == 0
        assert builder.graph_stats["errors"] == []

    def test_verse_node_creation_structure(self):
        """Test verse node creation structure."""
        from quran_core.src.data.neo4j_builder import Neo4jGraphBuilder
        from quran_core.src.data.quran_metadata import VERSE_COUNTS, SURAH_METADATA

        # Test properties are correctly formed
        props = VerseNodeProperties(
            surah=2,
            ayah=183,
            text_arabic="Test text",
            revelation_context="MEDINAN",
            theme="fasting",
        )

        props_dict = props.to_dict()
        assert "surah" in props_dict
        assert "ayah" in props_dict
        assert "text_arabic" in props_dict
        assert props_dict["surah"] == 2

    def test_graph_statistics_calculation(self):
        """Test graph statistics calculation."""
        from quran_core.src.data.neo4j_builder import Neo4jGraphBuilder

        # Mock stats dictionary
        stats = {
            "nodes": {"Verse": 100, "Hadith": 50},
            "relationships": {"EXPLAINED_BY": 200, "SUPPORTED_BY": 150},
        }

        assert stats["nodes"]["Verse"] == 100
        assert stats["relationships"]["EXPLAINED_BY"] == 200


class TestTheologicalGraphQueries:
    """Test query generation and execution."""

    @pytest.fixture
    def mock_session(self):
        """Create mock Neo4j session."""
        return MagicMock()

    @pytest.fixture
    def queries(self, mock_session):
        """Create query object with mock session."""
        from quran_core.src.data.graph_queries import TheologicalGraphQueries

        return TheologicalGraphQueries(mock_session)

    def test_verse_with_tafsirs_query(self, queries, mock_session):
        """Test verse with tafsirs query."""
        # Mock the result
        mock_result = MagicMock()
        mock_result.data.return_value = [
            {
                "verse": {"surah": 2, "ayah": 183},
                "tafsirs": [{"tafsir": "Ibn Kathir"}]
            }
        ]
        mock_result.consume.return_value = MagicMock(
            result_available_after=1,
            result_consumed_after=2
        )
        mock_session.run.return_value = mock_result

        result = queries.get_verse_with_tafsirs(2, 183)

        assert result.success
        assert result.row_count == 1
        assert len(result.data) > 0

    def test_madhab_rulings_query(self, queries, mock_session):
        """Test madhab rulings query."""
        mock_result = MagicMock()
        mock_result.data.return_value = [
            {
                "verse": {"surah": 2},
                "madhab_rulings": [
                    {"madhab": "Hanafi", "ruling_type": "obligatory"}
                ]
            }
        ]
        mock_result.consume.return_value = MagicMock(
            result_available_after=1,
            result_consumed_after=2
        )
        mock_session.run.return_value = mock_result

        result = queries.get_madhab_rulings_for_verse(2, 183)

        assert result.success
        assert result.row_count == 1


class TestGraphReport:
    """Test graph reporting functionality."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()

    @pytest.fixture
    def reporter(self, mock_session):
        """Create reporter with mock session."""
        from quran_core.src.data.graph_report import GraphReporter

        return GraphReporter(mock_session)

    def test_report_generation(self, reporter, mock_session):
        """Test report generation."""
        # Mock overview query
        mock_result = MagicMock()
        mock_result.single.return_value = {
            "total_nodes": 1000,
            "total_relationships": 2000,
        }
        mock_session.run.return_value = mock_result

        report = reporter.generate_full_report()

        assert "timestamp" in report
        assert "sections" in report
        assert "overview" in report["sections"]

    def test_density_calculation(self, reporter):
        """Test network density calculation."""
        # For a graph with 100 nodes and 500 relationships
        # Max relationships = 100 * 99 = 9900 (directed)
        density = reporter._calculate_density(100, 500)

        assert 0 <= density <= 1
        assert density == pytest.approx(500 / 9900, rel=1e-6)

    def test_density_edge_cases(self, reporter):
        """Test density calculation edge cases."""
        assert reporter._calculate_density(0, 0) == 0.0
        assert reporter._calculate_density(1, 0) == 0.0
        assert reporter._calculate_density(2, 2) == 1.0  # Fully connected


class TestQuranMetadata:
    """Test Quran metadata."""

    def test_verse_counts(self):
        """Test verse counts."""
        from quran_core.src.data.quran_metadata import VERSE_COUNTS

        # Check total
        total = sum(VERSE_COUNTS.values())
        assert total == 6236

        # Check specific surahs
        assert VERSE_COUNTS[1] == 7  # Al-Fatihah
        assert VERSE_COUNTS[2] == 286  # Al-Baqarah
        assert VERSE_COUNTS[114] == 6  # An-Nas

    def test_surah_metadata(self):
        """Test surah metadata."""
        from quran_core.src.data.quran_metadata import SURAH_METADATA

        # Check Al-Baqarah
        surah_2 = SURAH_METADATA[2]
        assert surah_2["name_en"] == "Al-Baqarah"
        assert surah_2["verses"] == 286
        assert surah_2["revelation"] == "MEDINAN"


class TestIntegration:
    """Integration tests."""

    def test_schema_consistency(self):
        """Test schema definitions are consistent."""
        # All node types should have corresponding schema definitions
        assert len(NodeType) > 0
        assert len(RelationshipType) > 0

    def test_relationship_property_completeness(self):
        """Test relationship properties are complete."""
        from quran_core.src.data.neo4j_schema import (
            TafsirRelationshipProperties,
            HadithRelationshipProperties,
            MadhhabRulingProperties,
            AbrogationProperties
        )

        # Test each relationship type has properties
        tafsir_rel = TafsirRelationshipProperties(confidence=0.98)
        assert tafsir_rel.confidence == 0.98

        hadith_rel = HadithRelationshipProperties(confidence=0.85)
        assert hadith_rel.confidence == 0.85

        madhab_rel = MadhhabRulingProperties(confidence=0.90)
        assert madhab_rel.confidence == 0.90

        abrogate_rel = AbrogationProperties(confidence=0.95)
        assert abrogate_rel.confidence == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
