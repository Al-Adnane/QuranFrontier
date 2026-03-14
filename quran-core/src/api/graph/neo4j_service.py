"""Neo4j Graph Service - Phase 3B Implementation

Provides Neo4j knowledge graph service for Quranic relationships.
Supports both real Neo4j connections and mock mode for testing.
"""
import logging
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

from . import schema

logger = logging.getLogger(__name__)


class MockDriver:
    """Mock Neo4j driver for testing without a real database."""

    def __init__(self):
        """Initialize mock driver."""
        pass

    def session(self):
        """Return a mock session."""
        return MockSession()


class MockSession:
    """Mock Neo4j session for testing."""

    def __init__(self):
        """Initialize mock session."""
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass

    def run(self, query: str, **kwargs):
        """Execute a mock query."""
        return MockResult()


class MockResult:
    """Mock Neo4j query result."""

    def __init__(self, records: Optional[List] = None):
        """Initialize mock result."""
        self.records = records or []

    def single(self) -> Optional[Any]:
        """Return single record."""
        return self.records[0] if self.records else None

    def __iter__(self):
        """Iterate over records."""
        return iter(self.records)


class Neo4jService:
    """Service for Neo4j knowledge graph operations."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        auth: Optional[tuple] = None,
        use_mock: bool = False,
    ):
        """Initialize Neo4j service.

        Args:
            uri: Neo4j connection URI
            auth: Authentication tuple (username, password)
            use_mock: Use mock mode for testing (no real database required)
        """
        self.uri = uri
        self.auth = auth
        self.use_mock = use_mock
        self.driver = None

        if not use_mock:
            try:
                from neo4j import GraphDatabase
                logger.info(f"Connecting to Neo4j at {uri}")
                self.driver = GraphDatabase.driver(uri, auth=auth)
                logger.info("Neo4j connection successful")
            except ImportError:
                raise ImportError("neo4j package required. Install with: pip install neo4j")
        else:
            # Mock mode: in-memory graph
            logger.info("Using mock mode (in-memory graph)")
            self._mock_nodes = {}  # {node_id: {label, properties}}
            self._mock_relationships = []  # [{source, target, type, properties}]
            self._mock_node_counter = 0
            # Provide a mock driver object for testing
            self.driver = MockDriver()

    def create_schema(self) -> Optional[Dict]:
        """Create graph schema (indices and constraints).

        Returns:
            Schema creation result or None in mock mode
        """
        if self.use_mock:
            return {"status": "mock", "indices_created": len(schema.NODE_LABELS)}

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                # Create indices for key properties
                for node_type in schema.NODE_LABELS:
                    session.run(f"CREATE INDEX IF NOT EXISTS FOR (n:{node_type}) ON (n.id)")
            return {"status": "success", "indices_created": len(schema.NODE_LABELS)}
        except Exception as e:
            logger.error(f"Schema creation failed: {e}")
            return None

    def get_node_labels(self) -> List[str]:
        """Get all defined node labels.

        Returns:
            List of node label names
        """
        return sorted(list(schema.get_node_labels()))

    def get_relationship_types(self) -> List[str]:
        """Get all defined relationship types.

        Returns:
            List of relationship type names
        """
        return sorted(list(schema.get_relationship_types()))

    def create_verse_node(self, verse_data: Dict[str, Any]) -> Optional[str]:
        """Create a verse node.

        Args:
            verse_data: Dictionary with verse properties (surah, ayah, text_arabic, etc.)

        Returns:
            Node ID or None on failure
        """
        if self.use_mock:
            node_id = f"{verse_data.get('surah')}:{verse_data.get('ayah')}"
            self._mock_nodes[node_id] = {
                "label": "Verse",
                "properties": verse_data,
            }
            return node_id

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                node_id = f"{verse_data['surah']}:{verse_data['ayah']}"
                session.run(
                    f"""
                    CREATE (v:Verse {{
                        surah: $surah,
                        ayah: $ayah,
                        text_arabic: $text_arabic,
                        text_normalized: $text_normalized,
                        id: $id
                    }})
                    """,
                    surah=verse_data["surah"],
                    ayah=verse_data["ayah"],
                    text_arabic=verse_data.get("text_arabic", ""),
                    text_normalized=verse_data.get("text_normalized", ""),
                    id=node_id,
                )
            return node_id
        except Exception as e:
            logger.error(f"Verse node creation failed: {e}")
            return None

    def create_verse_nodes(self, verses: List[Dict[str, Any]]) -> int:
        """Create multiple verse nodes.

        Args:
            verses: List of verse data dictionaries

        Returns:
            Number of verses created
        """
        count = 0
        for verse in verses:
            if self.create_verse_node(verse) is not None:
                count += 1
        return count

    def create_tafsir_node(self, tafsir_data: Dict[str, Any]) -> Optional[str]:
        """Create a tafsir node.

        Args:
            tafsir_data: Dictionary with tafsir properties

        Returns:
            Node ID or None on failure
        """
        if self.use_mock:
            node_id = tafsir_data.get("id", f"t_{self._mock_node_counter}")
            self._mock_node_counter += 1
            self._mock_nodes[node_id] = {
                "label": "Tafsir",
                "properties": tafsir_data,
            }
            return node_id

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                node_id = tafsir_data["id"]
                session.run(
                    """
                    CREATE (t:Tafsir {
                        id: $id,
                        scholar: $scholar,
                        text: $text,
                        school: $school
                    })
                    """,
                    id=node_id,
                    scholar=tafsir_data.get("scholar", ""),
                    text=tafsir_data.get("text", ""),
                    school=tafsir_data.get("school", ""),
                )
            return node_id
        except Exception as e:
            logger.error(f"Tafsir node creation failed: {e}")
            return None

    def create_tafsir_nodes(self, tafsirs: List[Dict[str, Any]]) -> int:
        """Create multiple tafsir nodes.

        Args:
            tafsirs: List of tafsir data dictionaries

        Returns:
            Number of tafsirs created
        """
        count = 0
        for tafsir in tafsirs:
            if self.create_tafsir_node(tafsir) is not None:
                count += 1
        return count

    def create_hadith_node(self, hadith_data: Dict[str, Any]) -> Optional[str]:
        """Create a hadith node.

        Args:
            hadith_data: Dictionary with hadith properties

        Returns:
            Node ID or None on failure
        """
        if self.use_mock:
            node_id = hadith_data.get("id", f"h_{self._mock_node_counter}")
            self._mock_node_counter += 1
            self._mock_nodes[node_id] = {
                "label": "Hadith",
                "properties": hadith_data,
            }
            return node_id

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                node_id = hadith_data["id"]
                session.run(
                    """
                    CREATE (h:Hadith {
                        id: $id,
                        collection: $collection,
                        grade: $grade,
                        text: $text
                    })
                    """,
                    id=node_id,
                    collection=hadith_data.get("collection", ""),
                    grade=hadith_data.get("grade", ""),
                    text=hadith_data.get("text", ""),
                )
            return node_id
        except Exception as e:
            logger.error(f"Hadith node creation failed: {e}")
            return None

    def create_hadith_nodes(self, hadiths: List[Dict[str, Any]]) -> int:
        """Create multiple hadith nodes.

        Args:
            hadiths: List of hadith data dictionaries

        Returns:
            Number of hadiths created
        """
        count = 0
        for hadith in hadiths:
            if self.create_hadith_node(hadith) is not None:
                count += 1
        return count

    def create_narrator_node(self, narrator_data: Dict[str, Any]) -> Optional[str]:
        """Create a narrator node.

        Args:
            narrator_data: Dictionary with narrator properties

        Returns:
            Node ID or None on failure
        """
        if self.use_mock:
            node_id = narrator_data.get("id", f"n_{self._mock_node_counter}")
            self._mock_node_counter += 1
            self._mock_nodes[node_id] = {
                "label": "Narrator",
                "properties": narrator_data,
            }
            return node_id

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                node_id = narrator_data["id"]
                session.run(
                    """
                    CREATE (n:Narrator {
                        id: $id,
                        name: $name,
                        generation: $generation,
                        reliability_grade: $reliability_grade
                    })
                    """,
                    id=node_id,
                    name=narrator_data.get("name", ""),
                    generation=narrator_data.get("generation", 0),
                    reliability_grade=narrator_data.get("reliability_grade", ""),
                )
            return node_id
        except Exception as e:
            logger.error(f"Narrator node creation failed: {e}")
            return None

    def create_madhab_node(self, madhab_data: Dict[str, Any]) -> Optional[str]:
        """Create a madhab node.

        Args:
            madhab_data: Dictionary with madhab properties

        Returns:
            Node ID or None on failure
        """
        if self.use_mock:
            node_id = madhab_data.get("name", f"m_{self._mock_node_counter}")
            self._mock_node_counter += 1
            self._mock_nodes[node_id] = {
                "label": "Madhab",
                "properties": madhab_data,
            }
            return node_id

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                node_id = madhab_data.get("name", "")
                session.run(
                    """
                    CREATE (m:Madhab {
                        name: $name,
                        founder: $founder,
                        school_of_thought: $school_of_thought
                    })
                    """,
                    name=madhab_data.get("name", ""),
                    founder=madhab_data.get("founder", ""),
                    school_of_thought=madhab_data.get("school_of_thought", ""),
                )
            return node_id
        except Exception as e:
            logger.error(f"Madhab node creation failed: {e}")
            return None

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """Create a relationship between nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            rel_type: Relationship type (must be in RELATIONSHIP_TYPES)
            properties: Optional relationship properties

        Returns:
            Relationship details or None on failure
        """
        if rel_type not in schema.RELATIONSHIP_TYPES:
            logger.error(f"Invalid relationship type: {rel_type}")
            return None

        if self.use_mock:
            self._mock_relationships.append({
                "source": source_id,
                "target": target_id,
                "type": rel_type,
                "properties": properties or {},
            })
            return {
                "source": source_id,
                "target": target_id,
                "type": rel_type,
            }

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                session.run(
                    f"""
                    MATCH (source), (target)
                    WHERE source.id = $source_id AND target.id = $target_id
                    CREATE (source)-[r:{rel_type}]->(target)
                    SET r += $properties
                    """,
                    source_id=source_id,
                    target_id=target_id,
                    properties=properties or {},
                )
            return {
                "source": source_id,
                "target": target_id,
                "type": rel_type,
            }
        except Exception as e:
            logger.error(f"Relationship creation failed: {e}")
            return None

    def get_verse(self, surah: int, ayah: int) -> Optional[Dict]:
        """Get verse node by surah and ayah.

        Args:
            surah: Surah number
            ayah: Ayah number

        Returns:
            Verse data or None if not found
        """
        node_id = f"{surah}:{ayah}"

        if self.use_mock:
            if node_id in self._mock_nodes:
                return self._mock_nodes[node_id]["properties"]
            return None

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (v:Verse) WHERE v.surah = $surah AND v.ayah = $ayah RETURN v",
                    surah=surah,
                    ayah=ayah,
                )
                record = result.single()
                if record:
                    return dict(record["v"])
            return None
        except Exception as e:
            logger.error(f"Verse retrieval failed: {e}")
            return None

    def query_connected(self, node_id: str, depth: int = 2) -> Optional[Dict]:
        """Query connected nodes within a given depth.

        Args:
            node_id: Starting node ID
            depth: Maximum relationship depth to traverse

        Returns:
            Dictionary with nodes and relationships or None on failure
        """
        if self.use_mock:
            # Mock implementation: return nodes and relationships within depth
            nodes = {}
            relationships = []

            if node_id in self._mock_nodes:
                nodes[node_id] = self._mock_nodes[node_id]

            visited = set()
            to_visit = [(node_id, 0)]

            while to_visit:
                current_id, current_depth = to_visit.pop(0)
                if current_id in visited or current_depth >= depth:
                    continue
                visited.add(current_id)

                for rel in self._mock_relationships:
                    if rel["source"] == current_id:
                        target_id = rel["target"]
                        if target_id in self._mock_nodes:
                            nodes[target_id] = self._mock_nodes[target_id]
                        relationships.append(rel)
                        to_visit.append((target_id, current_depth + 1))
                    elif rel["target"] == current_id:
                        source_id = rel["source"]
                        if source_id in self._mock_nodes:
                            nodes[source_id] = self._mock_nodes[source_id]
                        relationships.append(rel)
                        to_visit.append((source_id, current_depth + 1))

            return {
                "nodes": nodes,
                "relationships": relationships,
                "depth": depth,
            }

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                rel_pattern = "-" * depth + "|" + "-" * (depth - 1)
                result = session.run(
                    f"""
                    MATCH (n)-[*0..{depth}]-(connected)
                    WHERE n.id = $node_id
                    RETURN n, connected
                    """,
                    node_id=node_id,
                )
                nodes = {}
                for record in result:
                    nodes[record["n"]["id"]] = dict(record["n"])
                    nodes[record["connected"]["id"]] = dict(record["connected"])

                return {"nodes": nodes}
        except Exception as e:
            logger.error(f"Connected query failed: {e}")
            return None

    def query_madhab_timeline(self, madhab_id: str, topic: Optional[str] = None) -> Optional[Dict]:
        """Query madhab ruling evolution over time.

        Args:
            madhab_id: Madhab identifier
            topic: Optional topic filter

        Returns:
            Timeline data with evolution history or None on failure
        """
        if self.use_mock:
            # Mock implementation: return madhab timeline
            return {
                "madhab_id": madhab_id,
                "madhab": madhab_id.capitalize(),
                "topic": topic or "General",
                "current_ruling": "Active",
                "evolution_history": [
                    {
                        "century": "1st",
                        "deontic_status": "Recommended",
                        "scholar_name": "Founder",
                        "justification": "Foundational ruling",
                    },
                    {
                        "century": "2nd",
                        "deontic_status": "Obligatory",
                        "scholar_name": "Early Scholar",
                        "justification": "Textual interpretation",
                    },
                ],
                "timeline_start_century": "1st",
                "timeline_end_century": "21st",
            }

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (m:Madhab)-[e:EVOLVES_TO*]->(evolved)
                    WHERE m.name = $madhab_id
                    RETURN m, evolved
                    """,
                    madhab_id=madhab_id,
                )
                timeline = {
                    "madhab_id": madhab_id,
                    "evolution_history": [],
                }
                for record in result:
                    timeline["evolution_history"].append(dict(record["evolved"]))
                return timeline
        except Exception as e:
            logger.error(f"Madhab timeline query failed: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics.

        Returns:
            Dictionary with node and relationship counts
        """
        if self.use_mock:
            # Count nodes by label
            node_counts = defaultdict(int)
            for node in self._mock_nodes.values():
                node_counts[node["label"]] += 1

            # Count relationships by type
            rel_counts = defaultdict(int)
            for rel in self._mock_relationships:
                rel_counts[rel["type"]] += 1

            return {
                "node_count": len(self._mock_nodes),
                "node_types": dict(node_counts),
                "relationship_count": len(self._mock_relationships),
                "relationship_types": dict(rel_counts),
            }

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                node_result = session.run("MATCH (n) RETURN labels(n) as labels, count(*) as count")
                rel_result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(*) as count")

                node_counts = {}
                for record in node_result:
                    for label in record["labels"]:
                        node_counts[label] = node_counts.get(label, 0) + record["count"]

                rel_counts = {}
                for record in rel_result:
                    rel_counts[record["type"]] = record["count"]

                return {
                    "node_count": sum(node_counts.values()),
                    "node_types": node_counts,
                    "relationship_count": sum(rel_counts.values()),
                    "relationship_types": rel_counts,
                }
        except Exception as e:
            logger.error(f"Statistics retrieval failed: {e}")
            return {}

    def validate_graph(self) -> bool:
        """Validate graph integrity.

        Returns:
            True if graph is valid, False otherwise
        """
        if self.use_mock:
            # Check for orphaned relationships
            all_node_ids = set(self._mock_nodes.keys())
            for rel in self._mock_relationships:
                if rel["source"] not in all_node_ids or rel["target"] not in all_node_ids:
                    logger.warning(f"Orphaned relationship: {rel}")
                    return False
            return True

        if self.driver is None:
            raise RuntimeError("Driver not initialized")

        try:
            with self.driver.session() as session:
                # Check for relationships without source or target
                result = session.run(
                    """
                    MATCH (a)-[r]->(b)
                    WHERE a IS NULL OR b IS NULL
                    RETURN count(*) as orphaned
                    """
                )
                orphaned = result.single()["orphaned"]
                return orphaned == 0
        except Exception as e:
            logger.error(f"Graph validation failed: {e}")
            return False
