"""Hypergraph Knowledge Base - Core data structures and operations.

Implements Node and Hyperedge abstractions, and HypergraphKB for
managing Quranic knowledge with semantic, causal, and phonetic relations.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Node:
    """Represents a node in hypergraph (verse, rule, hadith, etc.)."""

    node_id: str
    entity_type: str  # "verse", "hadith", "tajweed_rule", "maqasid_goal"
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __hash__(self):
        return hash(self.node_id)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.node_id == other.node_id


@dataclass
class Hyperedge:
    """Represents a hyperedge connecting multiple nodes.

    Supports different edge types:
    - semantic: meaning/concept relations
    - causal: cause-effect relations
    - deontic: obligation/permission relations
    - phonetic: pronunciation/tajweed relations
    """

    edge_id: str
    edge_type: str  # "semantic", "causal", "deontic", "phonetic"
    source_ids: List[str]  # Multiple sources for hyperedge
    target_id: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __hash__(self):
        return hash(self.edge_id)

    def __eq__(self, other):
        if not isinstance(other, Hyperedge):
            return False
        return self.edge_id == other.edge_id


class HypergraphKB:
    """Hypergraph Knowledge Base for Islamic knowledge."""

    def __init__(self):
        """Initialize knowledge base."""
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Hyperedge] = {}
        self.adjacency: Dict[str, Set[str]] = {}  # node_id -> set of connected node_ids
        self.reverse_adjacency: Dict[str, Set[str]] = {}  # target_id -> set of source node_ids

    def add_node(self, node: Node) -> None:
        """Add node to knowledge base.

        Args:
            node: Node to add
        """
        if node.node_id in self.nodes:
            # Update existing node
            self.nodes[node.node_id].updated_at = datetime.now()
            self.nodes[node.node_id].properties.update(node.properties)
        else:
            # Add new node
            self.nodes[node.node_id] = node
            self.adjacency[node.node_id] = set()
            self.reverse_adjacency[node.node_id] = set()

    def remove_node(self, node_id: str) -> None:
        """Remove node from knowledge base.

        Args:
            node_id: ID of node to remove
        """
        if node_id in self.nodes:
            del self.nodes[node_id]

            # Clean up adjacency
            if node_id in self.adjacency:
                del self.adjacency[node_id]
            if node_id in self.reverse_adjacency:
                del self.reverse_adjacency[node_id]

            # Remove from adjacency of other nodes
            for neighbors in self.adjacency.values():
                neighbors.discard(node_id)
            for predecessors in self.reverse_adjacency.values():
                predecessors.discard(node_id)

    def add_edge(self, edge: Hyperedge) -> None:
        """Add hyperedge to knowledge base.

        Args:
            edge: Hyperedge to add
        """
        if edge.edge_id in self.edges:
            # Update existing edge
            self.edges[edge.edge_id].updated_at = datetime.now()
            self.edges[edge.edge_id].properties.update(edge.properties)
        else:
            # Add new edge
            self.edges[edge.edge_id] = edge

            # Update adjacency
            for source_id in edge.source_ids:
                if source_id in self.adjacency:
                    self.adjacency[source_id].add(edge.target_id)

            if edge.target_id in self.reverse_adjacency:
                for source_id in edge.source_ids:
                    self.reverse_adjacency[edge.target_id].add(source_id)

    def remove_edge(self, edge_id: str) -> None:
        """Remove hyperedge from knowledge base.

        Args:
            edge_id: ID of edge to remove
        """
        if edge_id in self.edges:
            edge = self.edges[edge_id]
            del self.edges[edge_id]

            # Update adjacency
            for source_id in edge.source_ids:
                if source_id in self.adjacency:
                    self.adjacency[source_id].discard(edge.target_id)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node or None
        """
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[Hyperedge]:
        """Get edge by ID.

        Args:
            edge_id: Edge ID

        Returns:
            Hyperedge or None
        """
        return self.edges.get(edge_id)

    def query(self, entity_type: Optional[str] = None, **properties) -> List[Node]:
        """Query nodes by entity type and properties.

        Args:
            entity_type: Entity type to filter by
            **properties: Property filters (AND logic)

        Returns:
            List of matching nodes
        """
        results = []

        for node in self.nodes.values():
            # Check entity type
            if entity_type and node.entity_type != entity_type:
                continue

            # Check properties
            matches = True
            for key, expected_value in properties.items():
                actual_value = node.properties.get(key)
                if actual_value != expected_value:
                    matches = False
                    break

            if matches:
                results.append(node)

        return results

    def query_edges(self, edge_type: Optional[str] = None, **properties) -> List[Hyperedge]:
        """Query edges by type and properties.

        Args:
            edge_type: Edge type to filter by
            **properties: Property filters (AND logic)

        Returns:
            List of matching edges
        """
        results = []

        for edge in self.edges.values():
            if edge_type and edge.edge_type != edge_type:
                continue

            matches = True
            for key, expected_value in properties.items():
                actual_value = edge.properties.get(key)
                if actual_value != expected_value:
                    matches = False
                    break

            if matches:
                results.append(edge)

        return results

    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[Node]:
        """Get neighboring nodes.

        Args:
            node_id: Source node ID
            edge_type: Filter by edge type (optional)

        Returns:
            List of neighbor nodes
        """
        neighbors = []

        if node_id not in self.adjacency:
            return neighbors

        for target_id in self.adjacency[node_id]:
            if target_id in self.nodes:
                neighbors.append(self.nodes[target_id])

        return neighbors

    def get_predecessors(self, node_id: str, edge_type: Optional[str] = None) -> List[Node]:
        """Get nodes that point to this node.

        Args:
            node_id: Target node ID
            edge_type: Filter by edge type (optional)

        Returns:
            List of predecessor nodes
        """
        predecessors = []

        if node_id not in self.reverse_adjacency:
            return predecessors

        for source_id in self.reverse_adjacency[node_id]:
            if source_id in self.nodes:
                predecessors.append(self.nodes[source_id])

        return predecessors

    def breadth_first_search(self, start_id: str, max_depth: int = 5) -> List[Node]:
        """Breadth-first traversal from start node.

        Args:
            start_id: Starting node ID
            max_depth: Maximum traversal depth

        Returns:
            List of visited nodes
        """
        visited = set()
        queue = [(start_id, 0)]
        results = []

        while queue:
            node_id, depth = queue.pop(0)

            if node_id in visited or depth > max_depth:
                continue

            visited.add(node_id)
            if node_id in self.nodes:
                results.append(self.nodes[node_id])

                # Add neighbors to queue
                for neighbor in self.get_neighbors(node_id):
                    if neighbor.node_id not in visited:
                        queue.append((neighbor.node_id, depth + 1))

        return results

    def depth_first_search(self, start_id: str, max_depth: int = 5) -> List[Node]:
        """Depth-first traversal from start node.

        Args:
            start_id: Starting node ID
            max_depth: Maximum traversal depth

        Returns:
            List of visited nodes
        """
        visited = set()
        results = []

        def dfs(node_id: str, depth: int):
            if node_id in visited or depth > max_depth:
                return

            visited.add(node_id)
            if node_id in self.nodes:
                results.append(self.nodes[node_id])

                for neighbor in self.get_neighbors(node_id):
                    dfs(neighbor.node_id, depth + 1)

        dfs(start_id, 0)
        return results

    def node_count(self) -> int:
        """Get total node count."""
        return len(self.nodes)

    def edge_count(self) -> int:
        """Get total edge count."""
        return len(self.edges)

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics.

        Returns:
            Statistics dictionary
        """
        entity_counts = {}
        edge_counts = {}

        for node in self.nodes.values():
            entity_counts[node.entity_type] = entity_counts.get(node.entity_type, 0) + 1

        for edge in self.edges.values():
            edge_counts[edge.edge_type] = edge_counts.get(edge.edge_type, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "entities_by_type": entity_counts,
            "edges_by_type": edge_counts,
            "avg_degree": (
                sum(len(neighbors) for neighbors in self.adjacency.values()) / len(self.adjacency)
                if self.adjacency
                else 0
            ),
        }
