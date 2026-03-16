"""
Neo4j Knowledge Graph Ingestion for Quranic Corpus.
Ingests 6,236 verses into Neo4j for semantic querying and relationship analysis.
"""

import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time
from neo4j import GraphDatabase, Session
from neo4j.exceptions import Neo4jError


class Neo4jIngester:
    """Ingest Quranic corpus into Neo4j knowledge graph"""

    def __init__(self, neo4j_uri: str = "neo4j://localhost:7687",
                 username: str = "neo4j", password: str = "password"):
        """
        Initialize Neo4j connection.

        Args:
            neo4j_uri: Neo4j database URI
            username: Database username
            password: Database password
        """
        self.neo4j_uri = neo4j_uri
        self.username = username
        self.password = password
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(username, password)
        )

    def __del__(self):
        """Cleanup: close driver connection"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.close()
            except Exception:
                pass

    def create_schema(self) -> bool:
        """
        Create indexes and constraints on knowledge graph.

        Returns:
            True if schema creation successful
        """
        schema_queries = [
            # Constraints on verse unique identifier
            "CREATE CONSTRAINT verse_key_unique IF NOT EXISTS ON (v:Verse) ASSERT v.verse_key IS UNIQUE",

            # Indexes for fast lookups
            "CREATE INDEX verse_surah IF NOT EXISTS ON (v:Verse) FOR (v.surah)",
            "CREATE INDEX verse_ayah IF NOT EXISTS ON (v:Verse) FOR (v.ayah)",
            "CREATE INDEX verse_confidence IF NOT EXISTS ON (v:Verse) FOR (v.confidence_score)",

            # Domain concept indexes
            "CREATE INDEX physics_concept IF NOT EXISTS ON (p:PhysicsConcept) FOR (p.name)",
            "CREATE INDEX biology_concept IF NOT EXISTS ON (b:BiologyConcept) FOR (b.name)",
            "CREATE INDEX medicine_concept IF NOT EXISTS ON (m:MedicineConcept) FOR (m.name)",
            "CREATE INDEX engineering_concept IF NOT EXISTS ON (e:EngineeringConcept) FOR (e.name)",
            "CREATE INDEX agriculture_concept IF NOT EXISTS ON (a:AgricultureConcept) FOR (a.name)",

            # Tafsir indexes
            "CREATE INDEX tafsir_source IF NOT EXISTS ON (t:Tafsir) FOR (t.source)",
            "CREATE INDEX tafsir_verse IF NOT EXISTS ON (t:Tafsir) FOR (t.verse_key)",

            # Scientific principle indexes
            "CREATE INDEX principle_name IF NOT EXISTS ON (s:ScientificPrinciple) FOR (s.name)",
        ]

        try:
            with self.driver.session() as session:
                for query in schema_queries:
                    session.run(query)
            return True
        except Neo4jError as e:
            print(f"Error creating schema: {e}")
            return False

    def ingest_corpus(self, corpus: List[Dict]) -> Dict:
        """
        Ingest all verses into Neo4j.

        Args:
            corpus: List of verse dictionaries from complete_corpus.json

        Returns:
            {
                'verses_ingested': int,
                'relationships_created': int,
                'errors': List[str],
                'duration_seconds': float
            }
        """
        start_time = time.time()
        verses_ingested = 0
        relationships_created = 0
        errors = []

        try:
            with self.driver.session() as session:
                for verse in corpus:
                    try:
                        # Ingest verse node
                        if self._ingest_verse_node(verse, session):
                            verses_ingested += 1

                        # Create domain concept nodes
                        domain_nodes = self._create_domain_nodes(verse, session)
                        relationships_created += len(domain_nodes)

                        # Create tafsir nodes
                        tafsir_nodes = self._create_tafsir_nodes(verse, session)
                        relationships_created += len(tafsir_nodes)

                        # Create relationships
                        self._create_verse_relationships(verse, session)
                        self._create_domain_relationships(verse, session)
                        self._create_tafsir_relationships(verse, session)

                    except Exception as e:
                        error_msg = f"Error ingesting verse {verse.get('verse_key', 'unknown')}: {str(e)}"
                        errors.append(error_msg)

        except Neo4jError as e:
            errors.append(f"Database error: {str(e)}")

        duration_seconds = time.time() - start_time

        return {
            'verses_ingested': verses_ingested,
            'relationships_created': relationships_created,
            'errors': errors,
            'duration_seconds': duration_seconds
        }

    def _ingest_verse_node(self, verse: Dict, session: Session) -> bool:
        """
        Create VERSE node for single verse.

        Args:
            verse: Verse dictionary from corpus
            session: Neo4j session

        Returns:
            True if successful
        """
        try:
            query = """
            CREATE (:Verse {
                surah: $surah,
                ayah: $ayah,
                verse_key: $verse_key,
                arabic_text: $arabic_text,
                translation: $translation,
                transliteration: $transliteration,
                physics_concepts: $physics_concepts,
                biology_concepts: $biology_concepts,
                medicine_concepts: $medicine_concepts,
                engineering_concepts: $engineering_concepts,
                agriculture_concepts: $agriculture_concepts,
                confidence_score: $confidence_score,
                created_at: $created_at
            })
            """

            params = {
                'surah': verse.get('surah'),
                'ayah': verse.get('ayah'),
                'verse_key': verse.get('verse_key'),
                'arabic_text': verse.get('arabic_text'),
                'translation': verse.get('translation'),
                'transliteration': verse.get('transliteration'),
                'physics_concepts': str(verse.get('physics_content', {}).get('concepts', [])),
                'biology_concepts': str(verse.get('biology_content', {}).get('concepts', [])),
                'medicine_concepts': str(verse.get('medicine_content', {}).get('concepts', [])),
                'engineering_concepts': str(verse.get('engineering_content', {}).get('concepts', [])),
                'agriculture_concepts': str(verse.get('agriculture_content', {}).get('concepts', [])),
                'confidence_score': verse.get('confidence_score', 0.0),
                'created_at': datetime.utcnow().isoformat()
            }

            session.run(query, params)
            return True
        except Exception as e:
            return False

    def _create_domain_nodes(self, verse: Dict, session: Session) -> List[str]:
        """
        Create nodes for each scientific domain content.

        Args:
            verse: Verse dictionary
            session: Neo4j session

        Returns:
            List of created node IDs
        """
        node_ids = []

        domains = {
            'physics_content': 'PhysicsConcept',
            'biology_content': 'BiologyConcept',
            'medicine_content': 'MedicineConcept',
            'engineering_content': 'EngineeringConcept',
            'agriculture_content': 'AgricultureConcept'
        }

        try:
            for domain_key, node_type in domains.items():
                domain_data = verse.get(domain_key, {})
                concepts = domain_data.get('concepts', [])
                confidence = domain_data.get('confidence', 0.0)

                for concept in concepts:
                    query = f"""
                    CREATE (:{node_type} {{
                        name: $name,
                        verse_key: $verse_key,
                        confidence: $confidence,
                        domain: $domain,
                        created_at: $created_at
                    }})
                    """

                    params = {
                        'name': concept,
                        'verse_key': verse.get('verse_key'),
                        'confidence': confidence,
                        'domain': domain_key.replace('_content', ''),
                        'created_at': datetime.utcnow().isoformat()
                    }

                    session.run(query, params)
                    node_ids.append(f"{node_type}:{concept}")

        except Exception:
            pass

        return node_ids

    def _create_tafsir_nodes(self, verse: Dict, session: Session) -> List[str]:
        """
        Create nodes for tafsir interpretations.

        Args:
            verse: Verse dictionary
            session: Neo4j session

        Returns:
            List of created tafsir node IDs
        """
        node_ids = []
        tafsirs = verse.get('tafsirs', [])

        try:
            for tafsir in tafsirs:
                query = """
                CREATE (:Tafsir {
                    source: $source,
                    name: $name,
                    verse_key: $verse_key,
                    text: $text,
                    category: $category,
                    created_at: $created_at
                })
                """

                params = {
                    'source': tafsir.get('source', 'Unknown'),
                    'name': tafsir.get('name', 'Unknown'),
                    'verse_key': verse.get('verse_key'),
                    'text': tafsir.get('text', ''),
                    'category': tafsir.get('category', 'classical'),
                    'created_at': datetime.utcnow().isoformat()
                }

                session.run(query, params)
                node_ids.append(f"Tafsir:{tafsir.get('source', 'Unknown')}")

        except Exception:
            pass

        return node_ids

    def _create_verse_relationships(self, verse: Dict, session: Session):
        """
        Create relationships between verses.

        Args:
            verse: Verse dictionary
            session: Neo4j session
        """
        try:
            verse_key = verse.get('verse_key')
            surah = verse.get('surah')
            ayah = verse.get('ayah')

            # Create SAME_SURAH relationship with adjacent verses
            if ayah > 1:
                prev_verse_key = f"{surah}:{ayah - 1}"
                query = """
                MATCH (v1:Verse {verse_key: $verse_key}),
                      (v2:Verse {verse_key: $prev_verse_key})
                CREATE (v2)-[:NEXT_VERSE]->(v1)
                """
                session.run(query, {
                    'verse_key': verse_key,
                    'prev_verse_key': prev_verse_key
                })

            # Create SAME_SURAH for all verses in same surah
            query = """
            MATCH (v1:Verse {verse_key: $verse_key}),
                  (v2:Verse {surah: $surah})
            WHERE v1 <> v2
            MERGE (v1)-[:SAME_SURAH]->(v2)
            """
            session.run(query, {
                'verse_key': verse_key,
                'surah': surah
            })

        except Exception:
            pass

    def _create_domain_relationships(self, verse: Dict, session: Session):
        """
        Create relationships between scientific domains and verses.

        Args:
            verse: Verse dictionary
            session: Neo4j session
        """
        try:
            verse_key = verse.get('verse_key')

            domains = {
                'physics_content': 'PhysicsConcept',
                'biology_content': 'BiologyConcept',
                'medicine_content': 'MedicineConcept',
                'engineering_content': 'EngineeringConcept',
                'agriculture_content': 'AgricultureConcept'
            }

            for domain_key, node_type in domains.items():
                domain_data = verse.get(domain_key, {})
                concepts = domain_data.get('concepts', [])

                for concept in concepts:
                    query = f"""
                    MATCH (v:Verse {{verse_key: $verse_key}}),
                          (c:{node_type} {{name: $name, verse_key: $verse_key}})
                    MERGE (c)-[:APPEARS_IN]->(v)
                    MERGE (v)-[:CONTAINS_CONCEPT]->(c)
                    """

                    session.run(query, {
                        'verse_key': verse_key,
                        'name': concept
                    })

        except Exception:
            pass

    def _create_tafsir_relationships(self, verse: Dict, session: Session):
        """
        Create relationships between tafsirs and verses.

        Args:
            verse: Verse dictionary
            session: Neo4j session
        """
        try:
            verse_key = verse.get('verse_key')
            tafsirs = verse.get('tafsirs', [])

            for tafsir in tafsirs:
                source = tafsir.get('source', 'Unknown')

                # Create INTERPRETS relationship
                query = """
                MATCH (v:Verse {verse_key: $verse_key}),
                      (t:Tafsir {source: $source, verse_key: $verse_key})
                MERGE (t)-[:INTERPRETS]->(v)
                """

                session.run(query, {
                    'verse_key': verse_key,
                    'source': source
                })

        except Exception:
            pass

    def validate_ingestion(self) -> Dict:
        """
        Validate ingestion completeness.

        Returns:
            {
                'total_verses': int,
                'total_verse_nodes': int,
                'total_concept_nodes': int,
                'total_tafsir_nodes': int,
                'total_relationships': int,
                'coverage_percentage': float,
                'issues': List[str]
            }
        """
        issues = []

        try:
            with self.driver.session() as session:
                # Count verse nodes
                verse_count_result = session.run(
                    "MATCH (v:Verse) RETURN count(v) as count"
                ).single()
                verse_nodes = verse_count_result['count'] if verse_count_result else 0

                # Count concept nodes
                concept_count_result = session.run(
                    "MATCH (c:PhysicsConcept) OR (c:BiologyConcept) OR (c:MedicineConcept) OR (c:EngineeringConcept) OR (c:AgricultureConcept) RETURN count(c) as count"
                ).single()
                concept_nodes = concept_count_result['count'] if concept_count_result else 0

                # Count tafsir nodes
                tafsir_count_result = session.run(
                    "MATCH (t:Tafsir) RETURN count(t) as count"
                ).single()
                tafsir_nodes = tafsir_count_result['count'] if tafsir_count_result else 0

                # Count relationships
                rel_count_result = session.run(
                    "MATCH ()-[r]->() RETURN count(r) as count"
                ).single()
                relationship_count = rel_count_result['count'] if rel_count_result else 0

                # Expected counts (6,236 verses)
                total_verses = 6236
                coverage = (verse_nodes / total_verses * 100) if total_verses > 0 else 0

                # Validate thresholds
                if verse_nodes < total_verses * 0.95:
                    issues.append(f"Verse coverage below 95%: {coverage:.1f}%")

                if concept_nodes < total_verses:
                    issues.append("Domain concept coverage is low")

                return {
                    'total_verses': total_verses,
                    'total_verse_nodes': verse_nodes,
                    'total_concept_nodes': concept_nodes,
                    'total_tafsir_nodes': tafsir_nodes,
                    'total_relationships': relationship_count,
                    'coverage_percentage': coverage,
                    'issues': issues
                }

        except Neo4jError as e:
            return {
                'total_verses': 6236,
                'total_verse_nodes': 0,
                'total_concept_nodes': 0,
                'total_tafsir_nodes': 0,
                'total_relationships': 0,
                'coverage_percentage': 0.0,
                'issues': [f"Database error: {str(e)}"]
            }

    def get_ingestion_stats(self) -> Dict:
        """
        Get statistics about ingested knowledge graph.

        Returns:
            Dictionary with ingestion statistics
        """
        try:
            with self.driver.session() as session:
                # Get verse node count
                verse_result = session.run(
                    "MATCH (v:Verse) RETURN count(v) as count"
                ).single()
                verse_nodes = verse_result['count'] if verse_result else 0

                # Get concept node count
                concept_result = session.run(
                    "MATCH (c:PhysicsConcept) OR (c:BiologyConcept) OR (c:MedicineConcept) OR (c:EngineeringConcept) OR (c:AgricultureConcept) RETURN count(c) as count"
                ).single()
                concept_nodes = concept_result['count'] if concept_result else 0

                # Get tafsir node count
                tafsir_result = session.run(
                    "MATCH (t:Tafsir) RETURN count(t) as count"
                ).single()
                tafsir_nodes = tafsir_result['count'] if tafsir_result else 0

                # Get relationship count
                rel_result = session.run(
                    "MATCH ()-[r]->() RETURN count(r) as count"
                ).single()
                relationship_count = rel_result['count'] if rel_result else 0

                # Calculate averages
                avg_concepts = (concept_nodes / verse_nodes) if verse_nodes > 0 else 0
                avg_tafsirs = (tafsir_nodes / verse_nodes) if verse_nodes > 0 else 0

                return {
                    'verse_nodes': verse_nodes,
                    'concept_nodes': concept_nodes,
                    'tafsir_nodes': tafsir_nodes,
                    'relationship_count': relationship_count,
                    'avg_concepts_per_verse': round(avg_concepts, 2),
                    'avg_tafsirs_per_verse': round(avg_tafsirs, 2)
                }

        except Neo4jError as e:
            return {
                'verse_nodes': 0,
                'concept_nodes': 0,
                'tafsir_nodes': 0,
                'relationship_count': 0,
                'avg_concepts_per_verse': 0.0,
                'avg_tafsirs_per_verse': 0.0,
                'error': str(e)
            }
