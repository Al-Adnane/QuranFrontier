import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from quran.corpus_extraction.infrastructure.knowledge_graph_api import KnowledgeGraphAPI

def test_kg_initialization():
    kg = KnowledgeGraphAPI(backend="neo4j", uri="bolt://localhost:7687")
    assert kg.is_connected()
    assert kg.schema_version == "1.0"

def test_verse_node_creation():
    kg = KnowledgeGraphAPI()
    verse_id = kg.create_verse_node(surah=2, ayah=164, text_ar="إن في خلق السماوات والأرض", text_en="In the creation of the heavens and the earth")
    assert verse_id == "2:164"
    assert kg.get_node("2:164") is not None

def test_concept_node_creation():
    kg = KnowledgeGraphAPI()
    concept_id = kg.create_concept_node(name="cosmology", domain="physics", tier=1, definition="Study of the origin and structure of the universe")
    assert concept_id == "cosmology"
    assert kg.get_node("cosmology")["tier"] == 1
