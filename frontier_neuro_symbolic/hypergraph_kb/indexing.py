"""Hypergraph Indexing - Fast O(log n) lookups on properties.

Implements B-tree-like indexing for efficient node/edge queries.
"""

from typing import List, Dict, Any, Optional, Tuple
from sortedcontainers import SortedDict
from frontier_neuro_symbolic.hypergraph_kb.hypergraph import Node, Hyperedge, HypergraphKB


class HypergraphIndex:
    """Index for fast property lookups on hypergraph."""

    def __init__(self, kb: HypergraphKB, property_name: str):
        """Initialize index on property.

        Args:
            kb: Knowledge base
            property_name: Property to index
        """
        self.kb = kb
        self.property_name = property_name
        self.index: Dict[Any, List[Node]] = {}
        self._build_index()

    def _build_index(self) -> None:
        """Build index from current KB state."""
        self.index = {}

        for node in self.kb.nodes.values():
            value = node.properties.get(self.property_name)
            if value is not None:
                if value not in self.index:
                    self.index[value] = []
                self.index[value].append(node)

    def lookup(self, **kwargs) -> List[Node]:
        """Lookup nodes by indexed property.

        Args:
            **kwargs: Single property filter (key-value pair)

        Returns:
            List of matching nodes
        """
        if len(kwargs) != 1:
            raise ValueError("Lookup requires exactly one property filter")

        key, value = list(kwargs.items())[0]

        if key != self.property_name:
            raise ValueError(f"Index is on {self.property_name}, not {key}")

        return self.index.get(value, [])

    def range_lookup(self, min_value: Any = None, max_value: Any = None) -> List[Node]:
        """Range lookup on indexed property.

        Args:
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            List of matching nodes
        """
        results = []

        for value, nodes in self.index.items():
            if min_value is not None and value < min_value:
                continue
            if max_value is not None and value > max_value:
                continue
            results.extend(nodes)

        return results

    def add_node(self, node: Node) -> None:
        """Add/update node in index.

        Args:
            node: Node to index
        """
        value = node.properties.get(self.property_name)
        if value is not None:
            if value not in self.index:
                self.index[value] = []
            if node not in self.index[value]:
                self.index[value].append(node)

    def remove_node(self, node: Node) -> None:
        """Remove node from index.

        Args:
            node: Node to remove
        """
        for value_list in self.index.values():
            if node in value_list:
                value_list.remove(node)


class CompositeIndex:
    """Composite index on multiple properties.

    Useful for queries filtering on multiple properties.
    """

    def __init__(self, kb: HypergraphKB, property_names: List[str]):
        """Initialize composite index.

        Args:
            kb: Knowledge base
            property_names: Properties to index (in priority order)
        """
        self.kb = kb
        self.property_names = property_names
        self.indexes: List[HypergraphIndex] = []

        for prop_name in property_names:
            self.indexes.append(HypergraphIndex(kb, prop_name))

    def lookup(self, **filters) -> List[Node]:
        """Lookup with multiple filters.

        Args:
            **filters: Property filters (AND logic)

        Returns:
            List of matching nodes
        """
        if not filters:
            return list(self.kb.nodes.values())

        # Start with most selective index
        results = None

        for prop_name, value in filters.items():
            # Find index for this property
            idx = None
            for index in self.indexes:
                if index.property_name == prop_name:
                    idx = index
                    break

            if idx is None:
                # No index, do linear scan
                candidates = [
                    n for n in self.kb.nodes.values()
                    if n.properties.get(prop_name) == value
                ]
            else:
                candidates = idx.lookup(**{prop_name: value})

            # Intersect with results
            if results is None:
                results = set(candidates)
            else:
                results = results.intersection(set(candidates))

        return list(results) if results is not None else []


class RangeIndex:
    """B-tree-like range index for efficient range queries."""

    def __init__(self, kb: HypergraphKB, property_name: str):
        """Initialize range index.

        Args:
            kb: Knowledge base
            property_name: Property to index
        """
        self.kb = kb
        self.property_name = property_name
        self.sorted_values: SortedDict = SortedDict()
        self._build_index()

    def _build_index(self) -> None:
        """Build sorted index."""
        for node in self.kb.nodes.values():
            value = node.properties.get(self.property_name)
            if value is not None:
                if value not in self.sorted_values:
                    self.sorted_values[value] = []
                self.sorted_values[value].append(node)

    def range_query(
        self, min_value: Any = None, max_value: Any = None
    ) -> List[Node]:
        """Query range of values.

        Args:
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            List of matching nodes
        """
        results = []

        for value, nodes in self.sorted_values.items():
            if min_value is not None and value < min_value:
                continue
            if max_value is not None and value > max_value:
                break
            results.extend(nodes)

        return results

    def point_query(self, value: Any) -> List[Node]:
        """Query exact value.

        Args:
            value: Value to search

        Returns:
            List of nodes with this value
        """
        return self.sorted_values.get(value, [])


class EdgeIndex:
    """Index for efficient edge queries."""

    def __init__(self, kb: HypergraphKB):
        """Initialize edge index.

        Args:
            kb: Knowledge base
        """
        self.kb = kb
        self.by_type: Dict[str, List[Hyperedge]] = {}
        self.by_source: Dict[str, List[Hyperedge]] = {}
        self.by_target: Dict[str, List[Hyperedge]] = {}
        self._build_index()

    def _build_index(self) -> None:
        """Build edge indexes."""
        for edge in self.kb.edges.values():
            # Index by type
            if edge.edge_type not in self.by_type:
                self.by_type[edge.edge_type] = []
            self.by_type[edge.edge_type].append(edge)

            # Index by source
            for source_id in edge.source_ids:
                if source_id not in self.by_source:
                    self.by_source[source_id] = []
                self.by_source[source_id].append(edge)

            # Index by target
            if edge.target_id not in self.by_target:
                self.by_target[edge.target_id] = []
            self.by_target[edge.target_id].append(edge)

    def edges_by_type(self, edge_type: str) -> List[Hyperedge]:
        """Get edges by type.

        Args:
            edge_type: Edge type

        Returns:
            List of edges
        """
        return self.by_type.get(edge_type, [])

    def edges_from_source(self, source_id: str) -> List[Hyperedge]:
        """Get edges from source node.

        Args:
            source_id: Source node ID

        Returns:
            List of edges
        """
        return self.by_source.get(source_id, [])

    def edges_to_target(self, target_id: str) -> List[Hyperedge]:
        """Get edges to target node.

        Args:
            target_id: Target node ID

        Returns:
            List of edges
        """
        return self.by_target.get(target_id, [])

    def add_edge(self, edge: Hyperedge) -> None:
        """Add edge to index.

        Args:
            edge: Hyperedge to add
        """
        if edge.edge_type not in self.by_type:
            self.by_type[edge.edge_type] = []
        self.by_type[edge.edge_type].append(edge)

        for source_id in edge.source_ids:
            if source_id not in self.by_source:
                self.by_source[source_id] = []
            self.by_source[source_id].append(edge)

        if edge.target_id not in self.by_target:
            self.by_target[edge.target_id] = []
        self.by_target[edge.target_id].append(edge)
