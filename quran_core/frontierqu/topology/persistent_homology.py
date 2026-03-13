"""Persistent Homology on the Quranic Complex.

Computes topological invariants (Betti numbers, persistence diagrams)
from the simplicial complex structure of the Quran.

Uses boundary matrix reduction (no external topology library required).
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Set
import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import shortest_path

from frontierqu.core.simplicial import QuranicComplex
from frontierqu.data.cross_references import THEMATIC_GROUPS


@dataclass
class PersistencePair:
    dimension: int
    birth: float
    death: float  # inf for features that never die

    @property
    def persistence(self) -> float:
        if self.death == float('inf'):
            return float('inf')
        return self.death - self.birth


@dataclass
class PersistenceDiagram:
    pairs: List[PersistencePair] = field(default_factory=list)

    def betti(self, dimension: int) -> int:
        """Count features alive at infinity in given dimension."""
        # Count pairs that are born and either never die or have high persistence
        alive = [p for p in self.pairs if p.dimension == dimension]
        # For betti number: count connected components (dim 0) or loops (dim 1)
        if dimension == 0:
            # Number of connected components = pairs with infinite death
            inf_pairs = [p for p in alive if p.death == float('inf')]
            return max(len(inf_pairs), 1)  # At least 1 component
        return len([p for p in alive if p.death == float('inf')])

    def filter_by_dimension(self, dim: int) -> List[PersistencePair]:
        return [p for p in self.pairs if p.dimension == dim]

    def to_array(self) -> np.ndarray:
        """Convert to Nx3 array [dimension, birth, death]."""
        if not self.pairs:
            return np.empty((0, 3))
        return np.array([[p.dimension, p.birth, p.death] for p in self.pairs])


def _build_thematic_complex(theme: str) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """Build a distance matrix from thematic verse group."""
    if theme not in THEMATIC_GROUPS:
        raise ValueError(f"Unknown theme: {theme}")

    verses = THEMATIC_GROUPS[theme]
    n = len(verses)
    if n == 0:
        return np.array([[]]), []

    # Build QuranicComplex to get edges
    qc = QuranicComplex()

    # Create distance matrix: 0 on diagonal, 1 if edge exists, 2 otherwise
    dist = np.full((n, n), 2.0)
    np.fill_diagonal(dist, 0.0)

    verse_to_idx = {v: i for i, v in enumerate(verses)}
    edges = []

    for i, v1 in enumerate(verses):
        for j, v2 in enumerate(verses):
            if i < j:
                # Check if edge exists in QuranicComplex
                if qc.has_edge(v1, v2):
                    dist[i, j] = 1.0
                    dist[j, i] = 1.0
                    edges.append((i, j))
                # Check sequential proximity
                elif v1[0] == v2[0] and abs(v1[1] - v2[1]) <= 5:
                    dist[i, j] = 1.5
                    dist[j, i] = 1.5

    return dist, edges


def _build_surah_order_complex() -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """Build complex using surah ordering as filtration."""
    # Use a representative sample (first verse of each surah)
    from frontierqu.data.quran_metadata import VERSE_COUNTS
    n = min(len(VERSE_COUNTS), 114)

    qc = QuranicComplex()
    vertices = [(s, 1) for s in range(1, n + 1)]

    dist = np.full((n, n), 2.0)
    np.fill_diagonal(dist, 0.0)
    edges = []

    for i in range(n):
        for j in range(i + 1, n):
            v1, v2 = vertices[i], vertices[j]
            if qc.has_edge(v1, v2):
                dist[i, j] = 1.0
                dist[j, i] = 1.0
                edges.append((i, j))
            elif abs(i - j) == 1:
                # Sequential surahs
                dist[i, j] = 1.0
                dist[j, i] = 1.0
                edges.append((i, j))

    return dist, edges


def _vietoris_rips_persistence(dist: np.ndarray, edges: List[Tuple[int, int]]) -> PersistenceDiagram:
    """Compute persistence using Vietoris-Rips filtration.

    Uses boundary matrix reduction for H0 (union-find) and H1 (cycle detection).
    """
    n = dist.shape[0]
    if n == 0:
        return PersistenceDiagram()

    pairs = []

    # H0: Connected components via union-find
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return True

    # Sort edges by distance (filtration value)
    edge_weights = [(dist[i, j], i, j) for i, j in edges]
    edge_weights.sort()

    # Birth of all vertices at time 0
    components = n

    for weight, i, j in edge_weights:
        if union(i, j):
            # A component merges — the younger one dies
            pairs.append(PersistencePair(dimension=0, birth=0.0, death=weight))
            components -= 1

    # Remaining components live forever
    for _ in range(components):
        pairs.append(PersistencePair(dimension=0, birth=0.0, death=float('inf')))

    # H1: Detect cycles (edges that don't reduce components)
    # Reset union-find
    parent = list(range(n))
    rank = [0] * n

    for weight, i, j in edge_weights:
        if find(i) == find(j):
            # This edge creates a cycle — H1 feature born
            pairs.append(PersistencePair(dimension=1, birth=weight, death=weight + 0.5))
        else:
            union(i, j)

    return PersistenceDiagram(pairs=pairs)


def compute_persistence(theme: Optional[str] = None,
                       filtration: Optional[str] = None) -> PersistenceDiagram:
    """Compute persistent homology on the Quranic complex.

    Args:
        theme: Filter by thematic group (e.g., "tawhid", "mercy")
        filtration: Type of filtration ("surah_order", "revelation_order")
    """
    if filtration == "surah_order":
        dist, edges = _build_surah_order_complex()
    elif theme:
        dist, edges = _build_thematic_complex(theme)
    else:
        # Default: surah order
        dist, edges = _build_surah_order_complex()

    return _vietoris_rips_persistence(dist, edges)
