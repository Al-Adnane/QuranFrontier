"""Neo4j Knowledge Graph Schema for Islamic Theological Relationships.

Defines comprehensive node types, relationship types, and properties for mapping
theological relationships including verses, tafsirs, hadiths, narrators, madhabs,
and linguistic concepts.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class NodeType(str, Enum):
    """Enumeration of node types in the knowledge graph."""
    VERSE = "Verse"
    TAFSIR = "Tafsir"
    HADITH = "Hadith"
    NARRATOR = "Narrator"
    MADHAB = "Madhab"
    LINGUISTIC_CONCEPT = "LinguisticConcept"
    THEME = "Theme"
    LEGAL_TOPIC = "LegalTopic"


class RelationshipType(str, Enum):
    """Enumeration of relationship types in the knowledge graph."""
    EXPLAINED_BY = "EXPLAINED_BY"
    SUPPORTED_BY = "SUPPORTED_BY"
    NARRATED_BY = "NARRATED_BY"
    MADHAB_RULING = "MADHAB_RULING"
    ABROGATES = "ABROGATES"
    ABROGATED_BY = "ABROGATED_BY"
    LINGUISTIC_ROOT = "LINGUISTIC_ROOT"
    RELATED_TO = "RELATED_TO"
    CROSS_REFERENCE = "CROSS_REFERENCE"
    CITED_IN = "CITED_IN"
    GRADED_BY = "GRADED_BY"
    PART_OF = "PART_OF"


@dataclass
class VerseNodeProperties:
    """Properties for Verse nodes."""
    surah: int
    ayah: int
    text_arabic: str
    revelation_context: str  # MECCAN_EARLY, MECCAN_LATE, MEDINAN
    revelation_order: Optional[int] = None
    theme: str = ""
    legal_topics: List[str] = field(default_factory=list)
    abrogation_status: str = "active"  # active, abrogating, abrogated
    word_count: int = 0
    root_letters: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surah": self.surah,
            "ayah": self.ayah,
            "text_arabic": self.text_arabic,
            "revelation_context": self.revelation_context,
            "revelation_order": self.revelation_order,
            "theme": self.theme,
            "legal_topics": self.legal_topics,
            "abrogation_status": self.abrogation_status,
            "word_count": self.word_count,
            "root_letters": self.root_letters,
        }


@dataclass
class TafsirNodeProperties:
    """Properties for Tafsir (exegesis) nodes."""
    scholar_name: str
    school: str  # e.g., Tabari, Qurtubi, Ibn Kathir, Saadi, Alusi
    text_snippet: str
    edition: str
    confidence: float = 1.0  # 0.0 to 1.0
    scholar_period: str = ""
    methodology: str = ""
    length: int = 0  # character count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scholar_name": self.scholar_name,
            "school": self.school,
            "text_snippet": self.text_snippet,
            "edition": self.edition,
            "confidence": self.confidence,
            "scholar_period": self.scholar_period,
            "methodology": self.methodology,
            "length": self.length,
        }


@dataclass
class HadithNodeProperties:
    """Properties for Hadith nodes."""
    text: str
    collection: str  # Sahih Bukhari, Sahih Muslim, Sunan Abu Dawud, etc.
    hadith_number: str
    grade: str  # Sahih, Hasan, Da'if, Maudhu'
    grade_confidence: float = 0.85
    theme: str = ""
    related_topics: List[str] = field(default_factory=list)
    narration_language: str = "Arabic"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "collection": self.collection,
            "hadith_number": self.hadith_number,
            "grade": self.grade,
            "grade_confidence": self.grade_confidence,
            "theme": self.theme,
            "related_topics": self.related_topics,
            "narration_language": self.narration_language,
        }


@dataclass
class NarratorNodeProperties:
    """Properties for Narrator (sahaba, tabi'un, etc.) nodes."""
    name: str
    generation: str  # Sahaba, Tabi'un, Taba Tabi'un, etc.
    reliability_grade: str  # Thiqa, Saduq, Da'if, etc.
    living_period: str
    biography: str = ""
    number_of_narrations: int = 0
    known_for: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "generation": self.generation,
            "reliability_grade": self.reliability_grade,
            "living_period": self.living_period,
            "biography": self.biography,
            "number_of_narrations": self.number_of_narrations,
            "known_for": self.known_for,
        }


@dataclass
class MadhhabNodeProperties:
    """Properties for Islamic School (Madhab) nodes."""
    name: str
    founder: str
    founding_century: int
    principles: List[str] = field(default_factory=list)
    regional_distribution: List[str] = field(default_factory=list)
    primary_sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "founder": self.founder,
            "founding_century": self.founding_century,
            "principles": self.principles,
            "regional_distribution": self.regional_distribution,
            "primary_sources": self.primary_sources,
        }


@dataclass
class LinguisticConceptNodeProperties:
    """Properties for Linguistic/Etymology concept nodes."""
    root: str  # Arabic root letters (e.g., د ع و)
    meaning: str
    frequency_in_quran: int
    surahs_containing_root: List[int] = field(default_factory=list)
    morphological_forms: List[str] = field(default_factory=list)
    semantic_field: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "meaning": self.meaning,
            "frequency_in_quran": self.frequency_in_quran,
            "surahs_containing_root": self.surahs_containing_root,
            "morphological_forms": self.morphological_forms,
            "semantic_field": self.semantic_field,
        }


@dataclass
class ThemeNodeProperties:
    """Properties for Thematic concept nodes."""
    name: str
    category: str  # theological, legal, eschatological, ethical
    verses_count: int = 0
    surahs_containing: List[int] = field(default_factory=list)
    related_madhab_positions: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "verses_count": self.verses_count,
            "surahs_containing": self.surahs_containing,
            "related_madhab_positions": self.related_madhab_positions,
        }


@dataclass
class RelationshipProperties:
    """Base properties for relationships."""
    confidence: float = 1.0  # 0.0 to 1.0
    source_reference: str = ""
    date_added: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence,
            "source_reference": self.source_reference,
            "date_added": self.date_added,
            "notes": self.notes,
        }


@dataclass
class TafsirRelationshipProperties(RelationshipProperties):
    """Properties for EXPLAINED_BY relationships."""
    tafsir_length: int = 0
    methodology: str = ""


@dataclass
class HadithRelationshipProperties(RelationshipProperties):
    """Properties for SUPPORTED_BY relationships."""
    grade_level: float = 0.85  # Based on hadith grade
    supporting_strength: str = "supportive"  # supportive, contradictory, neutral


@dataclass
class MadhhabRulingProperties(RelationshipProperties):
    """Properties for MADHAB_RULING relationships."""
    ruling_type: str = ""  # obligatory, recommended, permissible, disliked, forbidden
    juristic_difference: bool = False
    legal_maxim: str = ""


@dataclass
class AbrogationProperties(RelationshipProperties):
    """Properties for ABROGATES/ABROGATED_BY relationships."""
    abrogation_type: str = "partial"  # partial, complete, textual, ruling
    scholarly_consensus: float = 0.95  # Level of agreement on abrogation
    disputing_scholars: List[str] = field(default_factory=list)


# Cypher schema definition templates
CYPHER_SCHEMA = """
// Create constraints and indexes
CREATE CONSTRAINT unique_verse_id IF NOT EXISTS
  FOR (v:Verse) REQUIRE v.id IS UNIQUE;

CREATE CONSTRAINT unique_tafsir_id IF NOT EXISTS
  FOR (t:Tafsir) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT unique_hadith_id IF NOT EXISTS
  FOR (h:Hadith) REQUIRE h.id IS UNIQUE;

CREATE CONSTRAINT unique_narrator_id IF NOT EXISTS
  FOR (n:Narrator) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT unique_madhab_id IF NOT EXISTS
  FOR (m:Madhab) REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT unique_linguistic_id IF NOT EXISTS
  FOR (lc:LinguisticConcept) REQUIRE lc.id IS UNIQUE;

// Create indexes for common queries
CREATE INDEX verse_surah_ayah IF NOT EXISTS
  FOR (v:Verse) ON (v.surah, v.ayah);

CREATE INDEX hadith_collection IF NOT EXISTS
  FOR (h:Hadith) ON (h.collection);

CREATE INDEX hadith_grade IF NOT EXISTS
  FOR (h:Hadith) ON (h.grade);

CREATE INDEX narrator_grade IF NOT EXISTS
  FOR (n:Narrator) ON (n.reliability_grade);

CREATE INDEX theme_category IF NOT EXISTS
  FOR (t:Theme) ON (t.category);

// Create full-text search indexes
CALL db.index.fulltext.createNodeIndex(
  'verse_text_search',
  ['Verse'],
  ['text_arabic'],
  {provider: 'lucene'}
);

CALL db.index.fulltext.createNodeIndex(
  'tafsir_text_search',
  ['Tafsir'],
  ['text_snippet'],
  {provider: 'lucene'}
);

CALL db.index.fulltext.createNodeIndex(
  'hadith_text_search',
  ['Hadith'],
  ['text'],
  {provider: 'lucene'}
);
"""

# Common query templates
QUERY_TEMPLATES = {
    "verse_with_tafsirs": """
        MATCH (v:Verse {surah: $surah, ayah: $ayah})
        OPTIONAL MATCH (v)-[r:EXPLAINED_BY]->(t:Tafsir)
        RETURN v, collect({tafsir: t, relationship: r}) as tafsirs
    """,

    "verse_with_supporting_hadiths": """
        MATCH (v:Verse {surah: $surah, ayah: $ayah})
        OPTIONAL MATCH (v)-[r:SUPPORTED_BY]->(h:Hadith)
        WHERE h.grade IN ['Sahih', 'Hasan']
        RETURN v, collect({hadith: h, relationship: r}) as supporting_hadiths
    """,

    "madhab_rulings_for_verse": """
        MATCH (v:Verse {surah: $surah, ayah: $ayah})
        OPTIONAL MATCH (v)-[r:MADHAB_RULING]->(m:Madhab)
        RETURN v, collect({madhab: m, ruling: r}) as madhab_rulings
    """,

    "hadith_narrator_chain": """
        MATCH (h:Hadith {id: $hadith_id})
        MATCH (h)-[:NARRATED_BY]->(n1:Narrator)
        OPTIONAL MATCH (n1)-[:NARRATED_BY]->(n2:Narrator)
        OPTIONAL MATCH (n2)-[:NARRATED_BY]->(n3:Narrator)
        RETURN h, collect(DISTINCT n1) as narrators
    """,

    "related_verses_by_theme": """
        MATCH (v1:Verse {surah: $surah, ayah: $ayah})
        MATCH (v1)-[:RELATED_TO*1..3]->(v2:Verse)
        RETURN v1, collect(DISTINCT v2) as related_verses
    """,

    "abrogation_relationships": """
        MATCH (v1:Verse {surah: $surah, ayah: $ayah})
        OPTIONAL MATCH (v1)-[r:ABROGATES]->(v2:Verse)
        OPTIONAL MATCH (v1)<-[r2:ABROGATED_BY]-(v3:Verse)
        RETURN v1,
               collect({abrogates: v2, relationship: r}) as abrogating,
               collect({abrogated_by: v3, relationship: r2}) as abrogated_by
    """,

    "linguistic_analysis": """
        MATCH (v:Verse)
        MATCH (v)-[:LINGUISTIC_ROOT]->(lc:LinguisticConcept)
        WHERE lc.root = $root
        RETURN v, lc, collect(DISTINCT v) as verses_with_root
    """,

    "fasting_hadith_hanafi": """
        MATCH (v:Verse)-[:RELATED_TO]->(v2:Verse)
        WHERE v.surah = 2 AND v.ayah = 183
        MATCH (v)-[:SUPPORTED_BY]->(h:Hadith)
        MATCH (v)-[:MADHAB_RULING {ruling_type: 'obligatory'}]->(m:Madhab {name: 'Hanafi'})
        RETURN v, collect(DISTINCT h) as supporting_hadiths, m as madhab_ruling
    """,

    "graph_statistics": """
        MATCH (n)
        WITH labels(n) as node_type, count(n) as count
        RETURN node_type, count
        UNION ALL
        MATCH ()-[r]->()
        RETURN [type(r)] as relationship_type, count(r) as count
    """,
}
