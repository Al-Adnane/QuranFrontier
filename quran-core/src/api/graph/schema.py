"""Neo4j Graph Schema Definitions

Defines node types, relationship types, and properties for the knowledge graph.
"""
from typing import Dict, Set

# Node Labels
NODE_LABELS = {
    "Verse",
    "Tafsir",
    "Hadith",
    "Narrator",
    "Madhab",
    "DeonticStatus",
}

# Relationship Types
RELATIONSHIP_TYPES = {
    "EXPLAINED_BY",      # Verse → Tafsir
    "SUPPORTS",           # Verse → Hadith
    "CHAINS",             # Hadith → Narrator (sequential in isnad)
    "TAUGHT",             # Narrator → Narrator (teacher→student)
    "RULED_BY",           # Verse → Madhab ruling
    "EVOLVES_TO",         # Madhab ruling evolution (century to century)
    "ABROGATES",          # Verse → Verse (abrogation)
    "RELATED_TO",         # Verse → Verse (thematic/narrative)
}

# Node Properties by Type
NODE_PROPERTIES = {
    "Verse": {
        "surah": "int",
        "ayah": "int",
        "text_arabic": "str",
        "text_normalized": "str",
        "embedding_id": "str",
    },
    "Tafsir": {
        "id": "str",
        "scholar": "str",
        "school": "str",
        "text": "str",
        "confidence": "float",
    },
    "Hadith": {
        "id": "str",
        "collection": "str",
        "narrator_chain": "str",
        "grade": "str",
    },
    "Narrator": {
        "id": "str",
        "name": "str",
        "birth_year": "int",
        "death_year": "int",
        "reliability_grade": "str",
    },
    "Madhab": {
        "name": "str",
        "founder": "str",
        "school_of_thought": "str",
    },
    "DeonticStatus": {
        "value": "str",
        "definition": "str",
    },
}


def get_node_labels() -> Set[str]:
    """Return all defined node labels."""
    return NODE_LABELS.copy()


def get_relationship_types() -> Set[str]:
    """Return all defined relationship types."""
    return RELATIONSHIP_TYPES.copy()


def validate_node_properties(node_type: str, properties: Dict) -> bool:
    """Validate that node properties match the schema."""
    if node_type not in NODE_PROPERTIES:
        return False
    return True
