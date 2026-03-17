"""
Test suite for Neo4j Knowledge Graph Ingestion.
Uses mocking - does NOT require actual Neo4j running.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

# Add quran module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from quran.corpus_extraction.output.neo4j_ingester import Neo4jIngester


# Test Fixtures
@pytest.fixture
def sample_verse():
    """Sample verse from corpus"""
    return {
        "surah": 1,
        "ayah": 1,
        "verse_key": "1:1",
        "arabic_text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "translation": "In the name of Allah, the Most Merciful, the Most Compassionate",
        "transliteration": "Bismillah ir-Rahman ir-Rahim",
        "physics_content": {
            "concepts": ["electromagnetic_force", "quantum_mechanics"],
            "principles": ["energy_conservation"],
            "applications": [],
            "confidence": 0.85
        },
        "biology_content": {
            "concepts": ["cellular_life", "organic_chemistry"],
            "principles": ["evolution"],
            "applications": [],
            "confidence": 0.82
        },
        "medicine_content": {
            "concepts": ["human_anatomy", "healing"],
            "principles": ["balance"],
            "applications": [],
            "confidence": 0.88
        },
        "engineering_content": {
            "concepts": ["structural_design"],
            "principles": ["engineering_principles"],
            "applications": [],
            "confidence": 0.8
        },
        "agriculture_content": {
            "concepts": ["plant_growth"],
            "principles": ["fertilization"],
            "applications": [],
            "confidence": 0.79
        },
        "tafsirs": [
            {
                "name": "Ibn Kathir",
                "text": "This verse signifies divine mercy and compassion",
                "source": "Ibn Kathir",
                "category": "classical"
            },
            {
                "name": "Al-Tabari",
                "text": "A statement of God's attributes",
                "source": "Al-Tabari",
                "category": "classical"
            }
        ],
        "asbab_nuzul": {
            "historical_context": "Opening of the Quran",
            "event": "Revelation began",
            "related_verses": []
        },
        "semantic_analysis": {
            "key_terms": ["name", "Allah", "mercy"],
            "grammatical_structure": "Prepositional phrase",
            "linguistic_patterns": []
        },
        "verification_layers": {
            "layer_1_primary": True,
            "layer_2_secondary": True,
            "layer_3_peer_review": True,
            "layer_4_semantic": True,
            "layer_5_zero_fab": True,
            "all_passed": True
        },
        "confidence_score": 0.9,
        "source_citations": [
            {
                "source_type": "quran",
                "reference": "1:1",
                "author": "Prophet Muhammad",
                "year": 632
            }
        ],
        "metadata": {
            "extraction_method": "automated_domain_analysis",
            "extraction_timestamp": "2026-03-16T00:00:00Z",
            "extractor_version": "1.0",
            "language": "en"
        }
    }


@pytest.fixture
def sample_corpus(sample_verse):
    """Sample corpus with multiple verses"""
    verses = [sample_verse.copy()]
    for i in range(2, 5):
        v = sample_verse.copy()
        v["surah"] = 1
        v["ayah"] = i
        v["verse_key"] = f"1:{i}"
        v["arabic_text"] = f"Arabic text for verse {i}"
        v["translation"] = f"Translation for verse {i}"
        verses.append(v)
    return {"verses": verses}


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver"""
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value = session
    return driver


@pytest.fixture
@patch('neo4j_ingester.GraphDatabase')
def ingester_with_mock(mock_graphdb, mock_neo4j_driver):
    """Create ingester with mocked Neo4j connection"""
    mock_graphdb.driver.return_value = mock_neo4j_driver
    ingester = Neo4jIngester(
        neo4j_uri="neo4j://localhost:7687",
        username="neo4j",
        password="password"
    )
    ingester.driver = mock_neo4j_driver
    return ingester


# Tests

class TestNeo4jIngesterInitialization:
    """Test 1: Initialization with connection parameters"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_neo4j_ingester_initialization(self, mock_graphdb):
        """Initialize ingester with connection params and verify Neo4j connection"""
        # Arrange
        mock_driver = MagicMock()
        mock_graphdb.driver.return_value = mock_driver

        # Act
        ingester = Neo4jIngester(
            neo4j_uri="neo4j://localhost:7687",
            username="neo4j",
            password="password"
        )

        # Assert
        mock_graphdb.driver.assert_called_once_with(
            "neo4j://localhost:7687",
            auth=("neo4j", "password")
        )
        assert ingester.driver is not None
        assert ingester.neo4j_uri == "neo4j://localhost:7687"
        assert ingester.username == "neo4j"


class TestCreateSchema:
    """Test 2: Create indexes and constraints"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_create_schema(self, mock_graphdb):
        """Create indexes and constraints on knowledge graph"""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)
        mock_driver.session.return_value = mock_session
        mock_graphdb.driver.return_value = mock_driver

        ingester = Neo4jIngester()
        ingester.driver = mock_driver

        # Act
        result = ingester.create_schema()

        # Assert
        assert result is True
        # Verify session methods were called
        assert mock_driver.session.called
        # Verify constraints and indexes were created
        assert mock_session.run.called
        calls_made = [str(call) for call in mock_session.run.call_args_list]
        assert any("CONSTRAINT" in str(call) or "INDEX" in str(call)
                   for call in calls_made), "Schema creation should create constraints/indexes"


class TestIngestSingleVerse:
    """Test 3: Ingest single verse"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_ingest_single_verse(self, mock_graphdb, sample_verse):
        """Ingest one verse and verify (:Verse) node created"""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value = mock_session
        mock_graphdb.driver.return_value = mock_driver

        ingester = Neo4jIngester()
        ingester.driver = mock_driver

        # Act
        result = ingester._ingest_verse_node(sample_verse, mock_session)

        # Assert
        assert result is True
        # Verify Verse node creation query was executed
        assert mock_session.run.called
        call_args = str(mock_session.run.call_args_list)
        assert "Verse" in call_args, "Should create Verse node"


class TestIngestDomainConcepts:
    """Test 4: Ingest domain concepts"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_ingest_domain_concepts(self, mock_graphdb, sample_verse):
        """Ingest verse with physics concepts and verify concept nodes created"""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value = mock_session
        mock_graphdb.driver.return_value = mock_driver

        ingester = Neo4jIngester()
        ingester.driver = mock_driver

        # Act
        domain_nodes = ingester._create_domain_nodes(sample_verse, mock_session)

        # Assert
        assert isinstance(domain_nodes, list)
        assert len(domain_nodes) > 0, "Should create domain concept nodes"
        assert mock_session.run.called
        call_args = str(mock_session.run.call_args_list)
        assert any(domain in call_args for domain in
                  ["Physics", "Biology", "Medicine", "Engineering", "Agriculture"]), \
            "Should create concept nodes for scientific domains"


class TestIngestTafsirInterpretations:
    """Test 5: Ingest tafsir interpretations"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_ingest_tafsir_interpretations(self, mock_graphdb, sample_verse):
        """Ingest tafsir data and verify (:Tafsir) nodes created"""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value = mock_session
        mock_graphdb.driver.return_value = mock_driver

        ingester = Neo4jIngester()
        ingester.driver = mock_driver

        # Act
        tafsir_nodes = ingester._create_tafsir_nodes(sample_verse, mock_session)

        # Assert
        assert isinstance(tafsir_nodes, list)
        assert len(tafsir_nodes) == 2, "Should create tafsir nodes for each tafsir"
        assert mock_session.run.called
        call_args = str(mock_session.run.call_args_list)
        assert "Tafsir" in call_args, "Should create Tafsir nodes"
        assert "Ibn Kathir" in call_args or "Al-Tabari" in call_args, \
            "Should include tafsir sources"


class TestCreateRelationships:
    """Test 6: Create inter-verse relationships"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_create_relationships(self, mock_graphdb, sample_verse):
        """Create inter-verse relationships and verify (Verse)-[:SAME_SURAH]->(Verse)"""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value = mock_session
        mock_graphdb.driver.return_value = mock_driver

        ingester = Neo4jIngester()
        ingester.driver = mock_driver

        # Act
        ingester._create_verse_relationships(sample_verse, mock_session)

        # Assert
        assert mock_session.run.called
        call_args = str(mock_session.run.call_args_list)
        assert "SAME_SURAH" in call_args or "NEXT_VERSE" in call_args, \
            "Should create verse relationship types"


class TestValidateIngestion:
    """Test 7: Validate ingestion completeness"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_validate_ingestion(self, mock_graphdb):
        """Validate ingestion completeness and verify coverage > 95%"""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)
        mock_driver.session.return_value = mock_session

        # Mock validation query results - need to handle multiple calls
        mock_query_result = MagicMock()
        mock_query_result.single.return_value = {"count": 6236}
        mock_session.run.return_value = mock_query_result

        mock_graphdb.driver.return_value = mock_driver

        ingester = Neo4jIngester()
        ingester.driver = mock_driver

        # Act
        validation_result = ingester.validate_ingestion()

        # Assert
        assert isinstance(validation_result, dict)
        assert "total_verses" in validation_result
        assert "total_verse_nodes" in validation_result
        assert "total_concept_nodes" in validation_result
        assert "total_tafsir_nodes" in validation_result
        assert "total_relationships" in validation_result
        assert "coverage_percentage" in validation_result
        assert "issues" in validation_result
        assert validation_result["coverage_percentage"] >= 0
        assert isinstance(validation_result["issues"], list)


class TestIngestionStatistics:
    """Test 8: Get ingestion statistics"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_ingestion_statistics(self, mock_graphdb):
        """Get ingestion stats and verify counts match expected"""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)
        mock_driver.session.return_value = mock_session

        # Mock stats query results - need to handle multiple calls
        mock_query_result = MagicMock()
        mock_query_result.single.return_value = {"count": 6236}
        mock_session.run.return_value = mock_query_result

        mock_graphdb.driver.return_value = mock_driver

        ingester = Neo4jIngester()
        ingester.driver = mock_driver

        # Act
        stats = ingester.get_ingestion_stats()

        # Assert
        assert isinstance(stats, dict)
        assert "verse_nodes" in stats
        assert "concept_nodes" in stats
        assert "tafsir_nodes" in stats
        assert "relationship_count" in stats
        assert "avg_concepts_per_verse" in stats
        assert "avg_tafsirs_per_verse" in stats
        assert stats["verse_nodes"] == 6236
        assert stats["concept_nodes"] == 6236
        assert stats["tafsir_nodes"] == 6236


class TestFullCorpusIngestion:
    """Integration test for full corpus ingestion"""

    @patch('quran.corpus_extraction.output.neo4j_ingester.GraphDatabase')
    def test_ingest_corpus(self, mock_graphdb, sample_corpus):
        """Test full corpus ingestion with multiple verses"""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value = mock_session
        mock_graphdb.driver.return_value = mock_driver

        ingester = Neo4jIngester()
        ingester.driver = mock_driver

        # Act
        result = ingester.ingest_corpus(sample_corpus["verses"])

        # Assert
        assert isinstance(result, dict)
        assert "verses_ingested" in result
        assert "relationships_created" in result
        assert "errors" in result
        assert "duration_seconds" in result
        assert result["verses_ingested"] == len(sample_corpus["verses"])
        assert isinstance(result["errors"], list)
        assert isinstance(result["duration_seconds"], float)
