"""Hypergraph Operations - Merge, filter, and transformation operations.

Provides high-level operations for manipulating hypergraph data.
"""

from typing import List, Dict, Any, Optional
from frontier_neuro_symbolic.hypergraph_kb.hypergraph import Node, Hyperedge, HypergraphKB


class FilterOps:
    """Filtering operations on hypergraph."""

    def __init__(self, kb: HypergraphKB):
        """Initialize filter operations.

        Args:
            kb: Knowledge base
        """
        self.kb = kb

    def filter_by_property(self, property_name: str, value: Any) -> List[Node]:
        """Filter nodes by exact property match.

        Args:
            property_name: Property to filter by
            value: Expected value

        Returns:
            List of matching nodes
        """
        return self.kb.query(**{property_name: value})

    def filter_by_range(
        self, property_name: str, min_val: Any = None, max_val: Any = None
    ) -> List[Node]:
        """Filter nodes by property range.

        Args:
            property_name: Property to filter
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)

        Returns:
            List of nodes in range
        """
        results = []

        for node in self.kb.nodes.values():
            value = node.properties.get(property_name)

            if value is None:
                continue

            if min_val is not None and value < min_val:
                continue

            if max_val is not None and value > max_val:
                continue

            results.append(node)

        return results

    def filter_by_entity_type(self, entity_type: str) -> List[Node]:
        """Filter nodes by entity type.

        Args:
            entity_type: Entity type

        Returns:
            List of matching nodes
        """
        return self.kb.query(entity_type=entity_type)

    def filter_by_predicate(self, predicate) -> List[Node]:
        """Filter nodes using custom predicate function.

        Args:
            predicate: Function(Node) -> bool

        Returns:
            List of matching nodes
        """
        return [node for node in self.kb.nodes.values() if predicate(node)]

    def filter_edges_by_type(self, edge_type: str) -> List[Hyperedge]:
        """Filter edges by type.

        Args:
            edge_type: Edge type

        Returns:
            List of matching edges
        """
        return self.kb.query_edges(edge_type=edge_type)

    def filter_edges_by_strength(
        self, min_strength: float = 0.0, max_strength: float = 1.0
    ) -> List[Hyperedge]:
        """Filter edges by strength property.

        Args:
            min_strength: Minimum strength
            max_strength: Maximum strength

        Returns:
            List of edges in strength range
        """
        results = []

        for edge in self.kb.edges.values():
            strength = edge.properties.get("strength", 0.5)

            if strength < min_strength or strength > max_strength:
                continue

            results.append(edge)

        return results


class MergeOps:
    """Merge operations on hypergraph nodes."""

    def __init__(self, kb: HypergraphKB):
        """Initialize merge operations.

        Args:
            kb: Knowledge base
        """
        self.kb = kb

    def merge(self, nodes: List[Node], new_node_id: Optional[str] = None) -> Node:
        """Merge multiple nodes into one.

        Properties are merged (later nodes override earlier):
        Entity type is taken from first node.

        Args:
            nodes: Nodes to merge
            new_node_id: ID for merged node (auto-generated if None)

        Returns:
            Merged node
        """
        if not nodes:
            raise ValueError("Cannot merge empty list of nodes")

        if new_node_id is None:
            new_node_id = "_".join(node.node_id for node in nodes)

        # Merge properties
        merged_props = {}
        for node in nodes:
            merged_props.update(node.properties)

        # Create merged node
        merged_node = Node(
            node_id=new_node_id,
            entity_type=nodes[0].entity_type,
            properties=merged_props,
        )

        return merged_node

    def union(self, nodes1: List[Node], nodes2: List[Node]) -> List[Node]:
        """Union of two node sets.

        Args:
            nodes1: First set
            nodes2: Second set

        Returns:
            Union of nodes (deduplicated)
        """
        seen = {node.node_id for node in nodes1}
        result = list(nodes1)

        for node in nodes2:
            if node.node_id not in seen:
                result.append(node)
                seen.add(node.node_id)

        return result

    def intersection(self, nodes1: List[Node], nodes2: List[Node]) -> List[Node]:
        """Intersection of two node sets.

        Args:
            nodes1: First set
            nodes2: Second set

        Returns:
            Intersection of nodes
        """
        ids2 = {node.node_id for node in nodes2}
        return [node for node in nodes1 if node.node_id in ids2]

    def difference(self, nodes1: List[Node], nodes2: List[Node]) -> List[Node]:
        """Difference of two node sets (nodes1 - nodes2).

        Args:
            nodes1: First set
            nodes2: Second set

        Returns:
            Nodes in first but not second set
        """
        ids2 = {node.node_id for node in nodes2}
        return [node for node in nodes1 if node.node_id not in ids2]


class TraversalOps:
    """Graph traversal operations."""

    def __init__(self, kb: HypergraphKB):
        """Initialize traversal operations.

        Args:
            kb: Knowledge base
        """
        self.kb = kb

    def find_paths(
        self, start_id: str, end_id: str, max_length: int = 5
    ) -> List[List[str]]:
        """Find all paths between two nodes.

        Args:
            start_id: Start node ID
            end_id: End node ID
            max_length: Maximum path length

        Returns:
            List of paths (each path is list of node IDs)
        """
        paths = []

        def dfs(current: str, target: str, path: List[str], visited: set):
            if len(path) > max_length:
                return

            if current == target:
                paths.append(list(path))
                return

            for neighbor in self.kb.get_neighbors(current):
                if neighbor.node_id not in visited:
                    visited.add(neighbor.node_id)
                    path.append(neighbor.node_id)
                    dfs(neighbor.node_id, target, path, visited)
                    path.pop()
                    visited.discard(neighbor.node_id)

        dfs(start_id, end_id, [start_id], {start_id})
        return paths

    def find_shortest_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """Find shortest path between two nodes (BFS).

        Args:
            start_id: Start node ID
            end_id: End node ID

        Returns:
            Shortest path or None if unreachable
        """
        visited = {start_id}
        queue = [(start_id, [start_id])]

        while queue:
            current, path = queue.pop(0)

            if current == end_id:
                return path

            for neighbor in self.kb.get_neighbors(current):
                if neighbor.node_id not in visited:
                    visited.add(neighbor.node_id)
                    queue.append((neighbor.node_id, path + [neighbor.node_id]))

        return None

    def common_neighbors(self, node_id1: str, node_id2: str) -> List[Node]:
        """Find common neighbors of two nodes.

        Args:
            node_id1: First node ID
            node_id2: Second node ID

        Returns:
            List of common neighbors
        """
        neighbors1 = set(n.node_id for n in self.kb.get_neighbors(node_id1))
        neighbors2 = set(n.node_id for n in self.kb.get_neighbors(node_id2))

        common_ids = neighbors1.intersection(neighbors2)
        return [self.kb.get_node(nid) for nid in common_ids if self.kb.get_node(nid)]

    def find_cliques(self, min_size: int = 3) -> List[List[str]]:
        """Find cliques in hypergraph (simplified).

        Args:
            min_size: Minimum clique size

        Returns:
            List of cliques (each is list of node IDs)
        """
        cliques = []

        # Simplified clique detection (not optimized)
        nodes = list(self.kb.nodes.keys())

        def is_clique(node_set: set) -> bool:
            for n1 in node_set:
                neighbors = set(nb.node_id for nb in self.kb.get_neighbors(n1))
                for n2 in node_set:
                    if n1 != n2 and n2 not in neighbors:
                        return False
            return True

        # Check subsets of size min_size
        from itertools import combinations

        for subset in combinations(nodes, min_size):
            if is_clique(set(subset)):
                cliques.append(list(subset))

        return cliques


class AggregationOps:
    """Aggregation operations on hypergraph."""

    def __init__(self, kb: HypergraphKB):
        """Initialize aggregation operations.

        Args:
            kb: Knowledge base
        """
        self.kb = kb

    def count(self, entity_type: Optional[str] = None) -> int:
        """Count nodes.

        Args:
            entity_type: Filter by type (optional)

        Returns:
            Count of nodes
        """
        if entity_type is None:
            return self.kb.node_count()
        else:
            return len(self.kb.query(entity_type=entity_type))

    def group_by(self, property_name: str) -> Dict[Any, List[Node]]:
        """Group nodes by property value.

        Args:
            property_name: Property to group by

        Returns:
            Dictionary mapping values to node lists
        """
        groups: Dict[Any, List[Node]] = {}

        for node in self.kb.nodes.values():
            value = node.properties.get(property_name)
            if value is not None:
                if value not in groups:
                    groups[value] = []
                groups[value].append(node)

        return groups

    def aggregate_properties(
        self, property_name: str, aggregation: str = "count"
    ) -> Dict[str, Any]:
        """Aggregate property values.

        Args:
            property_name: Property to aggregate
            aggregation: Aggregation type ("count", "sum", "avg", "min", "max")

        Returns:
            Aggregation result
        """
        values = [
            node.properties.get(property_name)
            for node in self.kb.nodes.values()
            if property_name in node.properties
        ]

        if not values:
            return {"count": 0}

        result = {"count": len(values)}

        if aggregation == "count":
            return result
        elif aggregation == "sum":
            result["sum"] = sum(v for v in values if isinstance(v, (int, float)))
        elif aggregation == "avg":
            numeric = [v for v in values if isinstance(v, (int, float))]
            result["avg"] = sum(numeric) / len(numeric) if numeric else None
        elif aggregation == "min":
            numeric = [v for v in values if isinstance(v, (int, float))]
            result["min"] = min(numeric) if numeric else None
        elif aggregation == "max":
            numeric = [v for v in values if isinstance(v, (int, float))]
            result["max"] = max(numeric) if numeric else None

        return result


class HypergraphOps:
    """High-level hypergraph operations combining filters, merges, traversals."""

    def __init__(self, kb: HypergraphKB):
        """Initialize operations.

        Args:
            kb: Knowledge base
        """
        self.kb = kb
        self.filter = FilterOps(kb)
        self.merge = MergeOps(kb)
        self.traverse = TraversalOps(kb)
        self.aggregate = AggregationOps(kb)
