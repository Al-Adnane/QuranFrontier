"""Neo4j Persistence - Syncs hypergraph to Neo4j graph database.

Provides transactional persistence with support for
node/edge sync and query result hydration.

Changed: MockNeoDriver replaced with InMemoryGraphDriver — a real dict-based
graph store that actually stores/queries nodes and edges. Neo4j remains primary;
this fallback is functional (not a stub).
"""

from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from copy import deepcopy
from frontier_neuro_symbolic.hypergraph_kb.hypergraph import Node, Hyperedge, HypergraphKB


class InMemoryGraphStore:
    """In-memory graph database using dicts — functional Neo4j fallback.

    Stores nodes as {node_id: {label, properties}} and edges as
    {edge_id: {type, source_id, target_id, properties}}.  Supports
    MERGE/MATCH/DELETE semantics matching the Cypher queries used by
    NeoPersistence.
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}  # id -> {label, properties}
        self.edges: Dict[str, Dict[str, Any]] = {}  # auto-key -> {type, src, tgt, props}
        self._edge_counter = 0

    def merge_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a node (MERGE semantics)."""
        if node_id in self.nodes:
            self.nodes[node_id]["properties"].update(properties)
        else:
            self.nodes[node_id] = {"label": label, "properties": dict(properties), "id": node_id}
        return self.nodes[node_id]

    def merge_edge(self, source_id: str, target_id: str, rel_type: str,
                   properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update an edge (MERGE semantics)."""
        # Check for existing edge with same src/tgt/type
        for eid, e in self.edges.items():
            if e["source_id"] == source_id and e["target_id"] == target_id and e["type"] == rel_type:
                e["properties"].update(properties)
                return e
        self._edge_counter += 1
        eid = f"e{self._edge_counter}"
        edge = {"type": rel_type, "source_id": source_id,
                "target_id": target_id, "properties": dict(properties)}
        self.edges[eid] = edge
        return edge

    def match_nodes(self, label: Optional[str] = None) -> List[Dict[str, Any]]:
        """MATCH (n) or MATCH (n:Label)."""
        results = []
        for nid, data in self.nodes.items():
            if label is None or data.get("label") == label:
                results.append({**data, "id": nid})
        return results

    def match_edges(self, rel_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """MATCH ()-[r]->() or MATCH ()-[r:TYPE]->()."""
        results = []
        for eid, data in self.edges.items():
            if rel_type is None or data.get("type") == rel_type:
                results.append({**data, "edge_id": eid})
        return results

    def delete_node(self, node_id: str) -> None:
        """DETACH DELETE — remove node and all its edges."""
        self.nodes.pop(node_id, None)
        to_remove = [eid for eid, e in self.edges.items()
                     if e["source_id"] == node_id or e["target_id"] == node_id]
        for eid in to_remove:
            del self.edges[eid]

    def delete_all(self) -> None:
        """MATCH (n) DETACH DELETE n."""
        self.nodes.clear()
        self.edges.clear()
        self._edge_counter = 0

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def snapshot(self) -> Dict[str, Any]:
        """Serializable snapshot for backup."""
        return {"nodes": deepcopy(self.nodes), "edges": deepcopy(self.edges)}

    def restore_snapshot(self, data: Dict[str, Any]) -> None:
        """Restore from snapshot."""
        self.nodes = deepcopy(data.get("nodes", {}))
        self.edges = deepcopy(data.get("edges", {}))


class InMemoryGraphDriver:
    """Drop-in replacement for neo4j.GraphDatabase.driver().

    Wraps InMemoryGraphStore with session/transaction API matching
    the Neo4j driver interface used by NeoPersistence.
    """

    def __init__(self):
        self.store = InMemoryGraphStore()

    def close(self):
        pass

    def session(self, **kwargs):
        return InMemorySession(self.store)


class InMemorySession:
    """Session wrapping InMemoryGraphStore."""

    def __init__(self, store: InMemoryGraphStore):
        self._store = store

    def begin_transaction(self):
        return InMemoryTransaction(self._store)

    def close(self):
        pass


class InMemoryTransaction:
    """Transaction with Cypher-like run() that dispatches to InMemoryGraphStore.

    Parses the simplified Cypher patterns actually used by NeoPersistence
    (MERGE node, MERGE edge, MATCH, DELETE, count) and executes them
    against the in-memory store.
    """

    def __init__(self, store: InMemoryGraphStore):
        self._store = store
        self._snapshot = store.snapshot()  # for rollback
        self._committed = False

    def run(self, query: str, **parameters) -> 'InMemoryResult':
        """Parse simplified Cypher and execute against in-memory store."""
        q = query.strip().upper()

        # MERGE node: MERGE (n:Label {id: $node_id}) SET n += $properties
        if q.startswith("MERGE") and "SET N +=" in q and "->" not in q and "]->" not in q:
            label = self._extract_label(query)
            node_id = parameters.get("node_id", "")
            props = parameters.get("properties", {})
            node = self._store.merge_node(node_id, label, props)
            return InMemoryResult([node])

        # MERGE edge: MATCH (src)... MATCH (tgt)... MERGE (src)-[r:TYPE]->(tgt)
        if "MERGE" in q and "]->" in q:
            rel_type = self._extract_rel_type(query)
            src = parameters.get("source_id", "")
            tgt = parameters.get("target_id", "")
            props = parameters.get("properties", {})
            edge = self._store.merge_edge(src, tgt, rel_type, props)
            return InMemoryResult([edge])

        # COUNT nodes
        if "COUNT(N)" in q and "COUNT(R)" not in q:
            return InMemoryResult([{"count": self._store.node_count()}])

        # COUNT edges
        if "COUNT(R)" in q:
            return InMemoryResult([{"count": self._store.edge_count()}])

        # DELETE all
        if "DETACH DELETE" in q and "$NODE_ID" not in q and "node_id" not in parameters:
            self._store.delete_all()
            return InMemoryResult([])

        # DELETE specific node
        if "DETACH DELETE" in q:
            node_id = parameters.get("node_id", "")
            self._store.delete_node(node_id)
            return InMemoryResult([])

        # MATCH edges
        if "MATCH" in q and "]->" in q:
            rel_type = self._extract_rel_type(query) if ":" in query.split("]-")[0].split("[")[-1] else None
            return InMemoryResult(self._store.match_edges(rel_type))

        # MATCH nodes (with optional label)
        if "MATCH" in q:
            label = self._extract_label(query) if ":" in query.split(")")[0] else None
            results = self._store.match_nodes(label)
            return InMemoryResult(results)

        return InMemoryResult([])

    def commit(self):
        self._committed = True

    def rollback(self):
        if not self._committed:
            self._store.restore_snapshot(self._snapshot)

    @staticmethod
    def _extract_label(query: str) -> str:
        """Extract node label from Cypher like MERGE (n:Verse {id: ...})."""
        import re
        m = re.search(r'\(n:(\w+)', query) or re.search(r'\(n:\{', query)
        if m:
            return m.group(1)
        # Fallback: look for label in format string pattern
        m = re.search(r':\s*(\w+)\s*\{', query)
        return m.group(1) if m else "Node"

    @staticmethod
    def _extract_rel_type(query: str) -> str:
        """Extract relationship type from Cypher like [r:SEMANTIC]."""
        import re
        m = re.search(r'\[r:(\w+)\]', query)
        return m.group(1) if m else "RELATED"


class InMemoryResult:
    """Query result backed by a list of dicts — replaces MockNeoResult.

    Actually returns stored data instead of empty lists.
    """

    def __init__(self, records: List[Any]):
        self._records = records

    def fetch(self, n: int = 1) -> List[Any]:
        return self._records[:n]

    def single(self) -> Optional[Any]:
        if self._records:
            r = self._records[0]
            # For count queries, return (count_value,) tuple
            if isinstance(r, dict) and "count" in r:
                return (r["count"],)
            return r
        return None

    def __iter__(self):
        return iter(self._records)


# Keep backward-compatible alias
MockNeoDriver = InMemoryGraphDriver


class NeoPersistence:
    """Neo4j persistence layer for hypergraph.

    Syncs Python HypergraphKB objects to Neo4j and supports
    querying the database.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
        use_mock: bool = False,
    ):
        """Initialize persistence.

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
            use_mock: Use mock driver for testing
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.use_mock = use_mock

        if use_mock:
            self.driver = InMemoryGraphDriver()
        else:
            try:
                from neo4j import GraphDatabase

                self.driver = GraphDatabase.driver(uri, auth=(username, password))
            except Exception as e:
                # Fallback to functional in-memory graph (not a stub)
                print(f"Warning: Failed to connect to Neo4j: {e}. Using in-memory graph driver.")
                self.driver = InMemoryGraphDriver()
                self.use_mock = True

    def close(self) -> None:
        """Close database connection."""
        self.driver.close()

    @contextmanager
    def transaction(self):
        """Context manager for transactions.

        Yields:
            Transaction object
        """
        session = self.driver.session()
        tx = session.begin_transaction()

        try:
            yield tx
            tx.commit()
        except Exception as e:
            tx.rollback()
            raise e
        finally:
            session.close()

    def sync_node(self, node: Node) -> None:
        """Sync node to Neo4j.

        Creates or updates node in database.

        Args:
            node: Node to sync
        """
        with self.transaction() as tx:
            # Create/merge node
            query = """
            MERGE (n:{label} {{id: $node_id}})
            SET n += $properties
            RETURN n
            """.format(label=node.entity_type)

            tx.run(
                query,
                node_id=node.node_id,
                properties=node.properties,
            )

    def sync_edge(self, edge: Hyperedge) -> None:
        """Sync hyperedge to Neo4j.

        Creates relationships between source and target nodes.

        Args:
            edge: Hyperedge to sync
        """
        with self.transaction() as tx:
            # For each source, create relationship to target
            for source_id in edge.source_ids:
                query = """
                MATCH (src {{id: $source_id}})
                MATCH (tgt {{id: $target_id}})
                MERGE (src)-[r:{rel_type}]->(tgt)
                SET r += $properties
                RETURN r
                """.format(rel_type=edge.edge_type)

                tx.run(
                    query,
                    source_id=source_id,
                    target_id=edge.target_id,
                    properties=edge.properties,
                )

    def sync_hypergraph(self, kb: HypergraphKB) -> None:
        """Sync entire hypergraph to Neo4j.

        Args:
            kb: HypergraphKB to sync
        """
        # Sync all nodes
        for node in kb.nodes.values():
            self.sync_node(node)

        # Sync all edges
        for edge in kb.edges.values():
            self.sync_edge(edge)

    def hydrate_hypergraph(self, kb: HypergraphKB) -> None:
        """Load hypergraph from persistence into a HypergraphKB.

        For the in-memory driver this iterates the stored dicts and
        reconstitutes Node / Hyperedge objects.  For real Neo4j it
        deserializes returned records.

        Args:
            kb: HypergraphKB to populate
        """
        with self.transaction() as tx:
            # Load all nodes
            result = tx.run("MATCH (n) RETURN n")
            for record in result.fetch(10000):
                if record and isinstance(record, dict):
                    node_id = record.get("id", "")
                    label = record.get("label", "unknown")
                    props = record.get("properties", {})
                    node = Node(node_id=node_id, entity_type=label, properties=props)
                    kb.nodes[node_id] = node

            # Load all edges
            result = tx.run("MATCH ()-[r]->() RETURN r")
            for record in result.fetch(10000):
                if record and isinstance(record, dict):
                    import uuid as _uuid
                    edge_id = record.get("edge_id", str(_uuid.uuid4()))
                    rel_type = record.get("type", "RELATED")
                    src = record.get("source_id", "")
                    tgt = record.get("target_id", "")
                    props = record.get("properties", {})
                    edge = Hyperedge(edge_id=edge_id, edge_type=rel_type,
                                     source_ids=[src], target_id=tgt, properties=props)
                    kb.edges[edge_id] = edge

    def query_nodes(self, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query nodes from Neo4j.

        Args:
            entity_type: Filter by entity type (optional)

        Returns:
            List of node data
        """
        with self.transaction() as tx:
            if entity_type:
                query = f"MATCH (n:{entity_type}) RETURN n"
            else:
                query = "MATCH (n) RETURN n"

            result = tx.run(query)
            return result.fetch(1000) if hasattr(result, "fetch") else []

    def query_edges(self, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query edges from Neo4j.

        Args:
            edge_type: Filter by edge type (optional)

        Returns:
            List of edge data
        """
        with self.transaction() as tx:
            if edge_type:
                query = f"MATCH ()-[r:{edge_type}]->() RETURN r"
            else:
                query = "MATCH ()-[r]->() RETURN r"

            result = tx.run(query)
            return result.fetch(1000) if hasattr(result, "fetch") else []

    def delete_node(self, node_id: str) -> None:
        """Delete node from Neo4j.

        Args:
            node_id: Node ID to delete
        """
        with self.transaction() as tx:
            query = "MATCH (n {id: $node_id}) DETACH DELETE n"
            tx.run(query, node_id=node_id)

    def delete_all(self) -> None:
        """Delete all nodes and edges from Neo4j."""
        with self.transaction() as tx:
            query = "MATCH (n) DETACH DELETE n"
            tx.run(query)

    def get_statistics(self) -> Dict[str, Any]:
        """Get Neo4j database statistics.

        Returns:
            Statistics dictionary
        """
        with self.transaction() as tx:
            # Count nodes
            result = tx.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()[0] if result else 0

            # Count edges
            result = tx.run("MATCH ()-[r]->() RETURN count(r) as count")
            edge_count = result.single()[0] if result else 0

        return {
            "node_count": node_count,
            "edge_count": edge_count,
        }

    def backup(self, filepath: str) -> None:
        """Backup graph data to file (JSON format).

        For in-memory driver uses direct snapshot; for Neo4j queries all data.

        Args:
            filepath: Path to backup file
        """
        import json

        if self.use_mock and hasattr(self.driver, 'store'):
            backup_data = self.driver.store.snapshot()
        else:
            with self.transaction() as tx:
                nodes_result = tx.run("MATCH (n) RETURN n")
                edges_result = tx.run("MATCH ()-[r]->() RETURN r")
                backup_data = {
                    "nodes": nodes_result.fetch(10000) if hasattr(nodes_result, "fetch") else [],
                    "edges": edges_result.fetch(10000) if hasattr(edges_result, "fetch") else [],
                }

        with open(filepath, "w") as f:
            json.dump(backup_data, f)

    def restore(self, filepath: str) -> None:
        """Restore Neo4j data from backup file.

        Args:
            filepath: Path to backup file
        """
        import json

        with open(filepath, "r") as f:
            backup_data = json.load(f)

        # Clear database
        self.delete_all()

        # Restore nodes and edges
        # For in-memory driver, restore directly into the store
        if self.use_mock and hasattr(self.driver, 'store'):
            self.driver.store.restore_snapshot(backup_data)
        else:
            with self.transaction() as tx:
                for node_id, node_data in backup_data.get("nodes", {}).items():
                    label = node_data.get("label", "Node")
                    props = node_data.get("properties", {})
                    query = f"MERGE (n:{label} {{id: $node_id}}) SET n += $properties RETURN n"
                    tx.run(query, node_id=node_id, properties=props)

                for edge_id, edge_data in backup_data.get("edges", {}).items():
                    rel_type = edge_data.get("type", "RELATED")
                    src = edge_data.get("source_id", "")
                    tgt = edge_data.get("target_id", "")
                    props = edge_data.get("properties", {})
                    query = (f"MATCH (src {{id: $source_id}}) "
                             f"MATCH (tgt {{id: $target_id}}) "
                             f"MERGE (src)-[r:{rel_type}]->(tgt) "
                             f"SET r += $properties RETURN r")
                    tx.run(query, source_id=src, target_id=tgt, properties=props)
