"""Neo4j Query Utilities for Theological Knowledge Graph.

Provides optimized query patterns for complex theological searches including
multi-hop traversals, relationship confidence scoring, and semantic queries.
"""

from typing import List, Dict, Any, Optional
from neo4j import Session
from dataclasses import dataclass


@dataclass
class QueryResult:
    """Represents a query result."""
    success: bool
    data: List[Dict[str, Any]]
    execution_time_ms: float
    row_count: int
    error: Optional[str] = None


class TheologicalGraphQueries:
    """Query utilities for theological knowledge graph."""

    def __init__(self, session: Session):
        """Initialize with Neo4j session.

        Args:
            session: Active Neo4j session
        """
        self.session = session

    def get_verse_with_tafsirs(self, surah: int, ayah: int) -> QueryResult:
        """Get a verse with all its tafsirs.

        Args:
            surah: Surah number
            ayah: Ayah number

        Returns:
            QueryResult with verse and tafsirs
        """
        query = """
            MATCH (v:Verse {surah: $surah, ayah: $ayah})
            OPTIONAL MATCH (v)-[r:EXPLAINED_BY]->(t:Tafsir)
            RETURN v as verse,
                   collect({
                       tafsir: t,
                       scholar: t.scholar_name,
                       school: t.school,
                       confidence: r.confidence
                   }) as tafsirs,
                   count(t) as tafsir_count
        """
        return self._execute_query(query, {"surah": surah, "ayah": ayah})

    def get_verse_supporting_hadiths(
        self, surah: int, ayah: int, min_grade: Optional[str] = "Hasan"
    ) -> QueryResult:
        """Get hadiths supporting a specific verse.

        Args:
            surah: Surah number
            ayah: Ayah number
            min_grade: Minimum hadith grade filter (Sahih, Hasan, Da'if, Maudhu')

        Returns:
            QueryResult with supporting hadiths
        """
        query = """
            MATCH (v:Verse {surah: $surah, ayah: $ayah})
            OPTIONAL MATCH (v)-[r:SUPPORTED_BY]->(h:Hadith)
            WHERE h.grade IN ['Sahih', 'Hasan']
            RETURN v as verse,
                   collect({
                       hadith: h,
                       collection: h.collection,
                       grade: h.grade,
                       confidence: r.confidence
                   }) as supporting_hadiths,
                   count(h) as hadith_count
            ORDER BY r.confidence DESC
        """
        return self._execute_query(query, {"surah": surah, "ayah": ayah})

    def get_madhab_rulings_for_verse(self, surah: int, ayah: int) -> QueryResult:
        """Get madhab-specific rulings for a verse.

        Args:
            surah: Surah number
            ayah: Ayah number

        Returns:
            QueryResult with madhab rulings
        """
        query = """
            MATCH (v:Verse {surah: $surah, ayah: $ayah})
            OPTIONAL MATCH (v)-[r:MADHAB_RULING]->(m:Madhab)
            RETURN v as verse,
                   collect({
                       madhab: m.name,
                       ruling_type: r.ruling_type,
                       confidence: r.confidence,
                       juristic_difference: r.juristic_difference
                   }) as madhab_rulings,
                   count(m) as madhab_count
        """
        return self._execute_query(query, {"surah": surah, "ayah": ayah})

    def get_hadith_narrator_chain(self, hadith_id: str, max_depth: int = 5) -> QueryResult:
        """Get complete narrator chain (isnad) for a hadith.

        Args:
            hadith_id: Hadith identifier
            max_depth: Maximum chain depth to traverse

        Returns:
            QueryResult with narrator chain
        """
        query = """
            MATCH (h:Hadith {id: $hadith_id})
            MATCH chain = (h)-[:NARRATED_BY*1..{max_depth}]->(n:Narrator)
            RETURN h as hadith,
                   [node in nodes(chain)[1..] | {
                       narrator: node.name,
                       generation: node.generation,
                       reliability: node.reliability_grade
                   }] as narrator_chain,
                   length(chain) as chain_length
            ORDER BY chain_length DESC
            LIMIT 1
        """.format(max_depth=max_depth)
        return self._execute_query(query, {"hadith_id": hadith_id})

    def find_related_verses(
        self, surah: int, ayah: int, max_hops: int = 3
    ) -> QueryResult:
        """Find verses related through various relationships.

        Args:
            surah: Surah number
            ayah: Ayah number
            max_hops: Maximum relationship hops

        Returns:
            QueryResult with related verses
        """
        query = """
            MATCH (v1:Verse {surah: $surah, ayah: $ayah})
            MATCH (v1)-[r:RELATED_TO*1..{max_hops}]->(v2:Verse)
            WHERE v2 <> v1
            RETURN v1 as source_verse,
                   collect(DISTINCT {
                       verse: v2,
                       surah: v2.surah,
                       ayah: v2.ayah,
                       relationship_count: count(r)
                   }) as related_verses,
                   count(DISTINCT v2) as related_count
        """.format(max_hops=max_hops)
        return self._execute_query(query, {"surah": surah, "ayah": ayah})

    def get_abrogation_relationships(self, surah: int, ayah: int) -> QueryResult:
        """Get abrogation relationships for a verse.

        Args:
            surah: Surah number
            ayah: Ayah number

        Returns:
            QueryResult with abrogation data
        """
        query = """
            MATCH (v:Verse {surah: $surah, ayah: $ayah})
            OPTIONAL MATCH (v)-[r1:ABROGATES]->(v_abrogates:Verse)
            OPTIONAL MATCH (v)<-[r2:ABROGATED_BY]-(v_abrogated_by:Verse)
            RETURN v as verse,
                   collect({
                       abrogates: v_abrogates,
                       abrogation_type: r1.abrogation_type,
                       scholarly_consensus: r1.scholarly_consensus
                   }) as abrogates,
                   collect({
                       abrogated_by: v_abrogated_by,
                       abrogation_type: r2.abrogation_type,
                       scholarly_consensus: r2.scholarly_consensus
                   }) as abrogated_by
        """
        return self._execute_query(query, {"surah": surah, "ayah": ayah})

    def search_by_linguistic_root(self, root: str) -> QueryResult:
        """Search verses by Arabic linguistic root.

        Args:
            root: Arabic root letters (e.g., "د ع و")

        Returns:
            QueryResult with verses containing root
        """
        query = """
            MATCH (lc:LinguisticConcept {root: $root})
            MATCH (v:Verse)-[:LINGUISTIC_ROOT]->(lc)
            RETURN lc as linguistic_concept,
                   collect({
                       verse: v,
                       surah: v.surah,
                       ayah: v.ayah
                   }) as verses,
                   count(v) as verse_count
            ORDER BY verse_count DESC
        """
        return self._execute_query(query, {"root": root})

    def find_complex_relationship(
        self, surah: int, ayah: int, madhab_name: str = "Hanafi"
    ) -> QueryResult:
        """Complex query: Find hadiths supporting verses with Madhab interpretation.

        This demonstrates a sophisticated multi-relationship traversal:
        Verse -> Hadith (supporting) -> Narrator (chain) AND Verse -> Madhab (ruling)

        Args:
            surah: Surah number
            ayah: Ayah number
            madhab_name: Islamic school name

        Returns:
            QueryResult with complex relationship data
        """
        query = """
            MATCH (v:Verse {surah: $surah, ayah: $ayah})
            OPTIONAL MATCH (v)-[:SUPPORTED_BY]->(h:Hadith)
            WHERE h.grade IN ['Sahih', 'Hasan']
            OPTIONAL MATCH (h)-[:NARRATED_BY]->(n:Narrator)
            OPTIONAL MATCH (v)-[:MADHAB_RULING {ruling_type: 'obligatory'}]->(m:Madhab {name: $madhab_name})
            RETURN v as verse,
                   collect(DISTINCT {
                       hadith: h,
                       collection: h.collection,
                       narrators: collect(DISTINCT n.name),
                       madhab_interpretation: m.name
                   }) as evidence
            LIMIT 10
        """
        return self._execute_query(
            query, {"surah": surah, "ayah": ayah, "madhab_name": madhab_name}
        )

    def get_graph_statistics(self) -> QueryResult:
        """Get comprehensive graph statistics.

        Returns:
            QueryResult with graph metrics
        """
        query = """
            MATCH (n)
            WITH labels(n)[0] as node_type, count(n) as node_count
            WITH collect({type: node_type, count: node_count}) as nodes,
                 sum(node_count) as total_nodes
            MATCH ()-[r]->()
            WITH nodes, total_nodes,
                 type(r) as rel_type,
                 count(r) as rel_count
            WITH nodes, total_nodes,
                 collect({type: rel_type, count: rel_count}) as relationships,
                 sum(rel_count) as total_rels
            RETURN {
                nodes: nodes,
                total_nodes: total_nodes,
                relationships: relationships,
                total_relationships: total_rels,
                average_degree: CASE WHEN total_nodes > 0 THEN total_rels * 1.0 / total_nodes ELSE 0 END
            } as statistics
        """
        return self._execute_query(query)

    def search_by_theme(self, theme: str, category: Optional[str] = None) -> QueryResult:
        """Search for verses and related content by theme.

        Args:
            theme: Theme name (e.g., "tawhid", "law")
            category: Optional category filter

        Returns:
            QueryResult with themed verses
        """
        query = """
            MATCH (v:Verse {theme: $theme})
            OPTIONAL MATCH (v)-[:EXPLAINED_BY]->(t:Tafsir)
            OPTIONAL MATCH (v)-[:SUPPORTED_BY]->(h:Hadith)
            RETURN v as verse,
                   count(DISTINCT t) as tafsir_count,
                   count(DISTINCT h) as hadith_count
            ORDER BY v.surah, v.ayah
        """
        return self._execute_query(query, {"theme": theme})

    def find_juristic_differences(self, surah: int, ayah: int) -> QueryResult:
        """Find madhabs with different rulings (juristic disagreement).

        Args:
            surah: Surah number
            ayah: Ayah number

        Returns:
            QueryResult with different madhab positions
        """
        query = """
            MATCH (v:Verse {surah: $surah, ayah: $ayah})
            MATCH (v)-[r:MADHAB_RULING {juristic_difference: true}]->(m:Madhab)
            RETURN v as verse,
                   collect({
                       madhab: m.name,
                       ruling_type: r.ruling_type,
                       confidence: r.confidence
                   }) as different_rulings,
                   count(DISTINCT m) as madhab_variation_count
        """
        return self._execute_query(query, {"surah": surah, "ayah": ayah})

    def _execute_query(self, query: str, params: Dict[str, Any] = None) -> QueryResult:
        """Execute a Cypher query and return structured result.

        Args:
            query: Cypher query string
            params: Query parameters

        Returns:
            QueryResult object
        """
        try:
            result = self.session.run(query, params or {})
            records = result.data()
            summary = result.consume()

            return QueryResult(
                success=True,
                data=records,
                execution_time_ms=summary.result_available_after + summary.result_consumed_after,
                row_count=len(records),
            )
        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                execution_time_ms=0.0,
                row_count=0,
                error=str(e),
            )


# Sample query executor for testing
def run_sample_queries(session: Session) -> None:
    """Run sample queries against the graph.

    Args:
        session: Neo4j session
    """
    queries = TheologicalGraphQueries(session)

    print("\n" + "=" * 80)
    print("SAMPLE THEOLOGICAL QUERIES")
    print("=" * 80)

    # Query 1: Verse with Tafsirs
    print("\n1. Verse 2:183 (Fasting) with Tafsirs:")
    result = queries.get_verse_with_tafsirs(2, 183)
    if result.success:
        print(f"   Found {result.row_count} results in {result.execution_time_ms:.2f}ms")
        if result.data:
            print(f"   Tafsirs available: {result.data[0].get('tafsir_count', 0)}")
    else:
        print(f"   Error: {result.error}")

    # Query 2: Supporting Hadiths
    print("\n2. Supporting Hadiths for Verse 2:183:")
    result = queries.get_verse_supporting_hadiths(2, 183)
    if result.success:
        print(f"   Found {result.row_count} results in {result.execution_time_ms:.2f}ms")
        if result.data:
            print(f"   Supporting hadiths: {result.data[0].get('hadith_count', 0)}")
    else:
        print(f"   Error: {result.error}")

    # Query 3: Madhab Rulings
    print("\n3. Madhab Rulings for Verse 2:183:")
    result = queries.get_madhab_rulings_for_verse(2, 183)
    if result.success:
        print(f"   Found {result.row_count} results in {result.execution_time_ms:.2f}ms")
        if result.data:
            print(f"   Schools with rulings: {result.data[0].get('madhab_count', 0)}")
    else:
        print(f"   Error: {result.error}")

    # Query 4: Graph Statistics
    print("\n4. Graph Statistics:")
    result = queries.get_graph_statistics()
    if result.success:
        print(f"   Completed in {result.execution_time_ms:.2f}ms")
        if result.data:
            stats = result.data[0].get("statistics", {})
            print(f"   Total Nodes: {stats.get('total_nodes', 0)}")
            print(f"   Total Relationships: {stats.get('total_relationships', 0)}")
            print(f"   Average Degree: {stats.get('average_degree', 0):.2f}")
    else:
        print(f"   Error: {result.error}")

    print("\n" + "=" * 80)
