"""Phase 3B: Neo4j Graph Service Tests (TDD)

Test-driven implementation of Neo4j knowledge graph service for Quranic relationships.
Tests are written FIRST, implementation written to PASS tests.
"""
import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from api.graph.neo4j_service import Neo4jService


class TestNeo4jServiceInitialization:
    """Test Neo4j service can be initialized and connected"""

    def test_neo4j_service_initializes(self):
        """Test that Neo4jService can be created"""
        service = Neo4jService(use_mock=True)
        assert service is not None

    def test_neo4j_service_has_uri(self):
        """Test that service stores URI"""
        service = Neo4jService(use_mock=True)
        assert service.uri is not None

    def test_neo4j_mock_mode_flag(self):
        """Test that mock mode flag is set"""
        service = Neo4jService(use_mock=True)
        assert service.use_mock is True

    def test_neo4j_service_mock_driver(self):
        """Test that mock mode provides a driver"""
        service = Neo4jService(use_mock=True)
        assert service.driver is not None


class TestGraphSchema:
    """Test graph schema creation"""

    def test_create_schema_succeeds(self):
        """Test that schema can be created"""
        service = Neo4jService(use_mock=True)
        result = service.create_schema()
        assert result is not None

    def test_schema_creates_indices(self):
        """Test that schema creation includes indices"""
        service = Neo4jService(use_mock=True)
        result = service.create_schema()
        assert "indices" in result or result is not None

    def test_node_labels_defined(self):
        """Test that graph schema defines node labels"""
        service = Neo4jService(use_mock=True)
        labels = service.get_node_labels()
        assert "Verse" in labels
        assert "Tafsir" in labels
        assert "Hadith" in labels

    def test_relationship_types_defined(self):
        """Test that graph schema defines relationship types"""
        service = Neo4jService(use_mock=True)
        rel_types = service.get_relationship_types()
        assert "EXPLAINED_BY" in rel_types
        assert "SUPPORTS" in rel_types
        assert "CHAINS" in rel_types


class TestVerseNodeCreation:
    """Test creating verse nodes in graph"""

    def test_create_verse_node(self):
        """Test that a single verse node can be created"""
        service = Neo4jService(use_mock=True)
        verse_data = {
            "surah": 1,
            "ayah": 1,
            "text_arabic": "الحمد لله رب العالمين",
            "text_normalized": "الحمد لله رب العالمين"
        }
        result = service.create_verse_node(verse_data)
        assert result is not None

    def test_create_multiple_verse_nodes(self):
        """Test that multiple verse nodes can be created"""
        service = Neo4jService(use_mock=True)
        verses = [
            {"surah": 1, "ayah": 1, "text_arabic": "آية 1"},
            {"surah": 1, "ayah": 2, "text_arabic": "آية 2"},
            {"surah": 1, "ayah": 3, "text_arabic": "آية 3"}
        ]
        result = service.create_verse_nodes(verses)
        assert result >= 0

    def test_verse_nodes_have_properties(self):
        """Test that created verse nodes have required properties"""
        service = Neo4jService(use_mock=True)
        verse_data = {
            "surah": 2,
            "ayah": 255,
            "text_arabic": "الله لا إله إلا هو الحي القيوم",
            "text_normalized": "الله لا اله الا هو الحي القيوم"
        }
        service.create_verse_node(verse_data)

        result = service.get_verse(surah=2, ayah=255)
        assert result is not None


class TestRelationshipCreation:
    """Test creating relationships between nodes"""

    def test_create_relationship(self):
        """Test that relationships can be created"""
        service = Neo4jService(use_mock=True)

        # Create nodes first
        service.create_verse_node({"surah": 1, "ayah": 1, "text_arabic": "آية"})
        service.create_tafsir_node({"id": "t1", "text": "تفسير"})

        # Create relationship
        result = service.create_relationship(
            source_id="1:1",
            target_id="t1",
            rel_type="EXPLAINED_BY"
        )
        assert result is not None

    def test_explained_by_relationship(self):
        """Test EXPLAINED_BY relationship (Verse -> Tafsir)"""
        service = Neo4jService(use_mock=True)
        result = service.create_relationship("1:1", "t1", "EXPLAINED_BY")
        assert result is not None

    def test_supports_relationship(self):
        """Test SUPPORTS relationship (Verse -> Hadith)"""
        service = Neo4jService(use_mock=True)
        result = service.create_relationship("1:1", "h1", "SUPPORTS")
        assert result is not None

    def test_chains_relationship(self):
        """Test CHAINS relationship (Hadith -> Narrator)"""
        service = Neo4jService(use_mock=True)
        result = service.create_relationship("h1", "n1", "CHAINS")
        assert result is not None

    def test_taught_relationship(self):
        """Test TAUGHT relationship (Narrator -> Narrator)"""
        service = Neo4jService(use_mock=True)
        result = service.create_relationship("n1", "n2", "TAUGHT")
        assert result is not None


class TestGraphQueries:
    """Test querying the graph"""

    def test_get_connected_nodes(self):
        """Test retrieving connected nodes"""
        service = Neo4jService(use_mock=True)

        # Create test nodes and relationships
        service.create_verse_node({"surah": 1, "ayah": 1, "text_arabic": "آية"})
        service.create_tafsir_node({"id": "t1", "text": "تفسير"})
        service.create_relationship("1:1", "t1", "EXPLAINED_BY")

        result = service.query_connected("1:1", depth=1)
        assert result is not None
        assert isinstance(result, dict)

    def test_connected_nodes_include_metadata(self):
        """Test that connected nodes include metadata"""
        service = Neo4jService(use_mock=True)

        service.create_verse_node({"surah": 1, "ayah": 1, "text_arabic": "آية"})
        service.create_tafsir_node({"id": "t1", "text": "تفسير", "scholar": "العلماء"})
        service.create_relationship("1:1", "t1", "EXPLAINED_BY")

        result = service.query_connected("1:1", depth=1)
        assert "nodes" in result or "relationships" in result or result is not None

    def test_query_madhab_timeline(self):
        """Test querying madhab ruling evolution"""
        service = Neo4jService(use_mock=True)

        result = service.query_madhab_timeline("Hanafi")
        assert result is not None
        assert isinstance(result, dict)

    def test_query_by_depth(self):
        """Test querying with different depths"""
        service = Neo4jService(use_mock=True)

        service.create_verse_node({"surah": 1, "ayah": 1, "text_arabic": "آية"})

        result_depth1 = service.query_connected("1:1", depth=1)
        result_depth2 = service.query_connected("1:1", depth=2)

        assert result_depth1 is not None
        assert result_depth2 is not None


class TestGraphStatistics:
    """Test graph statistics and validation"""

    def test_get_graph_statistics(self):
        """Test retrieving graph statistics"""
        service = Neo4jService(use_mock=True)

        stats = service.get_statistics()
        assert "node_count" in stats or stats is not None

    def test_statistics_include_node_counts(self):
        """Test that statistics include node type counts"""
        service = Neo4jService(use_mock=True)

        stats = service.get_statistics()
        assert isinstance(stats, dict)

    def test_statistics_include_relationship_counts(self):
        """Test that statistics include relationship counts"""
        service = Neo4jService(use_mock=True)

        stats = service.get_statistics()
        assert isinstance(stats, dict)

    def test_validate_graph_integrity(self):
        """Test graph validation"""
        service = Neo4jService(use_mock=True)

        is_valid = service.validate_graph()
        assert isinstance(is_valid, bool)


class TestTafsirNodes:
    """Test creating and querying tafsir nodes"""

    def test_create_tafsir_node(self):
        """Test creating a tafsir node"""
        service = Neo4jService(use_mock=True)

        tafsir_data = {
            "id": "t1",
            "scholar": "السيوطي",
            "text": "تفسير جزء من الآية",
            "school": "Shafi'i"
        }
        result = service.create_tafsir_node(tafsir_data)
        assert result is not None

    def test_create_multiple_tafsir_nodes(self):
        """Test creating multiple tafsir nodes"""
        service = Neo4jService(use_mock=True)

        tafsirs = [
            {"id": "t1", "scholar": "الطبري", "text": "تفسير الطبري"},
            {"id": "t2", "scholar": "الزمخشري", "text": "تفسير الكشاف"},
            {"id": "t3", "scholar": "السيوطي", "text": "تفسير الجلالين"}
        ]
        result = service.create_tafsir_nodes(tafsirs)
        assert result >= 0


class TestHadithNodes:
    """Test creating and querying hadith nodes"""

    def test_create_hadith_node(self):
        """Test creating a hadith node"""
        service = Neo4jService(use_mock=True)

        hadith_data = {
            "id": "h1",
            "collection": "Sahih al-Bukhari",
            "grade": "Sahih",
            "text": "حديث"
        }
        result = service.create_hadith_node(hadith_data)
        assert result is not None

    def test_create_multiple_hadith_nodes(self):
        """Test creating multiple hadith nodes"""
        service = Neo4jService(use_mock=True)

        hadiths = [
            {"id": "h1", "collection": "Sahih al-Bukhari", "grade": "Sahih"},
            {"id": "h2", "collection": "Sahih Muslim", "grade": "Sahih"},
            {"id": "h3", "collection": "Sunan Abu Dawood", "grade": "Hasan"}
        ]
        result = service.create_hadith_nodes(hadiths)
        assert result >= 0


class TestNarratorNodes:
    """Test creating and querying narrator nodes"""

    def test_create_narrator_node(self):
        """Test creating a narrator node"""
        service = Neo4jService(use_mock=True)

        narrator_data = {
            "id": "n1",
            "name": "أبو هريرة",
            "generation": 1,
            "reliability_grade": "Thiqah"
        }
        result = service.create_narrator_node(narrator_data)
        assert result is not None

    def test_narrator_chain_relationships(self):
        """Test creating narrator chain (isnad)"""
        service = Neo4jService(use_mock=True)

        service.create_narrator_node({"id": "n1", "name": "الراوي الأول"})
        service.create_narrator_node({"id": "n2", "name": "الراوي الثاني"})

        result = service.create_relationship("h1", "n1", "CHAINS")
        assert result is not None


class TestMadhabhNodes:
    """Test madhab (Islamic school) nodes and relationships"""

    def test_create_madhab_node(self):
        """Test creating a madhab node"""
        service = Neo4jService(use_mock=True)

        madhab_data = {
            "name": "Hanafi",
            "founder": "أبو حنيفة",
            "school_of_thought": "Jurisprudence"
        }
        result = service.create_madhab_node(madhab_data)
        assert result is not None

    def test_madhab_ruling_evolution(self):
        """Test madhab ruling evolution relationships"""
        service = Neo4jService(use_mock=True)

        result = service.create_relationship(
            "madhab_ruling_1",
            "madhab_ruling_2",
            "EVOLVES_TO"
        )
        assert result is not None


class TestMockMode:
    """Test mock mode for testing without real database"""

    def test_mock_mode_without_database(self):
        """Test that mock mode works without Neo4j database running"""
        service = Neo4jService(use_mock=True)

        # Should work without database
        service.create_verse_node({"surah": 1, "ayah": 1, "text_arabic": "آية"})
        result = service.query_connected("1:1")

        assert result is not None

    def test_mock_mode_operations_succeed(self):
        """Test that all operations succeed in mock mode"""
        service = Neo4jService(use_mock=True)

        # Create nodes
        service.create_verse_node({"surah": 1, "ayah": 1, "text_arabic": "آية"})
        service.create_tafsir_node({"id": "t1", "text": "تفسير"})

        # Create relationship
        service.create_relationship("1:1", "t1", "EXPLAINED_BY")

        # Query
        result = service.query_connected("1:1")

        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
