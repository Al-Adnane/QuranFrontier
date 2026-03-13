"""QuranicComplex: The entire Quran as a single holistic simplicial complex.

Represents all 6236 verses as vertices in one connected simplicial complex,
with edges encoding sequential, cross-referential, thematic, and munasabat
relationships. Higher-dimensional simplices (triangles) arise from thematic
groups of size >= 3.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Optional, Set, Tuple

import torch

from frontierqu.data.quran_metadata import VERSE_COUNTS, SURAH_METADATA
from frontierqu.data.cross_references import CROSS_REFERENCES, THEMATIC_GROUPS

# Type alias: (surah_number, verse_number)
VerseKey = Tuple[int, int]


class QuranicComplex:
    """The entire Quran as a single simplicial complex.

    Vertices: 6236 verses, each identified by (surah, verse).
    Edges (1-simplices): sequential, cross_reference, thematic, munasabat.
    Triangles (2-simplices): from thematic groups of size >= 3.
    """

    def __init__(self) -> None:
        # --- Vertex indices ---
        self._vertex_to_idx: Dict[VerseKey, int] = {}
        self._idx_to_vertex: Dict[int, VerseKey] = {}
        idx = 0
        for surah in sorted(VERSE_COUNTS.keys()):
            for verse in range(1, VERSE_COUNTS[surah] + 1):
                key = (surah, verse)
                self._vertex_to_idx[key] = idx
                self._idx_to_vertex[idx] = key
                idx += 1
        self.num_vertices: int = idx  # should be 6236

        # --- Edges ---
        # Keyed by frozenset of two VerseKeys for undirected lookup.
        # Value: {"types": set of str, "weight": float}
        self._edges: Dict[frozenset, Dict] = {}

        # --- Build edges ---
        self._build_sequential_edges()
        self._build_cross_reference_edges()
        self._build_thematic_edges()
        self._build_munasabat_edges()

        # --- Triangles (2-simplices) ---
        self._triangles: List[Tuple[VerseKey, VerseKey, VerseKey]] = []
        self._build_triangles()

        # --- Per-vertex theme membership (for filter_by_theme) ---
        self._vertex_themes: Dict[VerseKey, Set[str]] = {}
        for theme, verses in THEMATIC_GROUPS.items():
            for v in verses:
                if v in self._vertex_to_idx:
                    self._vertex_themes.setdefault(v, set()).add(theme)

    # ------------------------------------------------------------------
    # Edge construction helpers
    # ------------------------------------------------------------------

    def _add_edge(self, v1: VerseKey, v2: VerseKey, edge_type: str, weight: float) -> None:
        """Add or merge an edge between v1 and v2."""
        if v1 not in self._vertex_to_idx or v2 not in self._vertex_to_idx:
            return
        if v1 == v2:
            return
        key = frozenset((v1, v2))
        if key in self._edges:
            self._edges[key]["types"].add(edge_type)
            # Keep the highest weight
            self._edges[key]["weight"] = max(self._edges[key]["weight"], weight)
        else:
            self._edges[key] = {"types": {edge_type}, "weight": weight}

    def _build_sequential_edges(self) -> None:
        """Connect consecutive verses within each surah (weight 1.0)."""
        for surah in sorted(VERSE_COUNTS.keys()):
            for verse in range(1, VERSE_COUNTS[surah]):
                self._add_edge((surah, verse), (surah, verse + 1), "sequential", 1.0)

    def _build_cross_reference_edges(self) -> None:
        """Connect verses from CROSS_REFERENCES data (weight 0.8)."""
        for v1, v2, rel_type in CROSS_REFERENCES:
            self._add_edge(v1, v2, "cross_reference", 0.8)

    def _build_thematic_edges(self) -> None:
        """Connect all pairs within each thematic group (weight 0.5)."""
        for theme, verses in THEMATIC_GROUPS.items():
            valid = [v for v in verses if v in self._vertex_to_idx]
            for a, b in combinations(valid, 2):
                self._add_edge(a, b, "thematic", 0.5)

    def _build_munasabat_edges(self) -> None:
        """Connect last verse of each surah to first verse of next surah (weight 0.6)."""
        sorted_surahs = sorted(VERSE_COUNTS.keys())
        for i in range(len(sorted_surahs) - 1):
            s1 = sorted_surahs[i]
            s2 = sorted_surahs[i + 1]
            last_verse = (s1, VERSE_COUNTS[s1])
            first_verse = (s2, 1)
            self._add_edge(last_verse, first_verse, "munasabat", 0.6)

    def _build_triangles(self) -> None:
        """Build 2-simplices from thematic groups of size >= 3."""
        for theme, verses in THEMATIC_GROUPS.items():
            valid = [v for v in verses if v in self._vertex_to_idx]
            if len(valid) >= 3:
                for triple in combinations(valid, 3):
                    self._triangles.append(triple)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def has_edge(self, v1: VerseKey, v2: VerseKey) -> bool:
        """Return True if an edge exists between v1 and v2."""
        return frozenset((v1, v2)) in self._edges

    def get_edge(self, v1: VerseKey, v2: VerseKey) -> Optional[Dict]:
        """Return edge data {"types": set, "weight": float} or None."""
        key = frozenset((v1, v2))
        edge = self._edges.get(key)
        if edge is None:
            return None
        # Return a copy so callers cannot mutate internals
        return {"types": set(edge["types"]), "weight": edge["weight"]}

    def get_simplices(self, dimension: int, containing: Optional[VerseKey] = None) -> List:
        """Return simplices of the given dimension.

        dimension=0: vertices (as VerseKey tuples)
        dimension=1: edges (as pairs of VerseKey)
        dimension=2: triangles (as triples of VerseKey)

        If `containing` is given, only return simplices that include that vertex.
        """
        if dimension == 0:
            verts = list(self._vertex_to_idx.keys())
            if containing is not None:
                verts = [v for v in verts if v == containing]
            return verts

        if dimension == 1:
            edges = [tuple(sorted(k)) for k in self._edges.keys()]
            if containing is not None:
                edges = [e for e in edges if containing in e]
            return edges

        if dimension == 2:
            triangles = self._triangles
            if containing is not None:
                triangles = [t for t in triangles if containing in t]
            return triangles

        return []

    def adjacency_matrix(self) -> torch.Tensor:
        """Return a sparse COO tensor of shape (6236, 6236).

        Values are edge weights. The matrix is symmetric.
        """
        rows = []
        cols = []
        vals = []
        for key, data in self._edges.items():
            endpoints = list(key)
            i = self._vertex_to_idx[endpoints[0]]
            j = self._vertex_to_idx[endpoints[1]]
            w = data["weight"]
            rows.extend([i, j])
            cols.extend([j, i])
            vals.extend([w, w])

        indices = torch.tensor([rows, cols], dtype=torch.long)
        values = torch.tensor(vals, dtype=torch.float32)
        return torch.sparse_coo_tensor(indices, values, (self.num_vertices, self.num_vertices))

    def filter_by_theme(self, theme: str) -> "QuranicComplex":
        """Return a sub-complex containing only vertices in the given theme.

        Includes all edges that connect two vertices in the sub-complex.
        """
        theme_lower = theme.lower()

        # Collect vertices belonging to this theme
        theme_vertices: Set[VerseKey] = set()

        # From THEMATIC_GROUPS
        if theme_lower in THEMATIC_GROUPS:
            for v in THEMATIC_GROUPS[theme_lower]:
                if v in self._vertex_to_idx:
                    theme_vertices.add(v)

        # From SURAH_METADATA themes
        for surah, meta in SURAH_METADATA.items():
            if theme_lower in meta.get("themes", []):
                for verse in range(1, VERSE_COUNTS[surah] + 1):
                    theme_vertices.add((surah, verse))

        # Build sub-complex
        sub = QuranicComplex.__new__(QuranicComplex)
        sub._vertex_to_idx = {}
        sub._idx_to_vertex = {}
        for idx_new, v in enumerate(sorted(theme_vertices)):
            sub._vertex_to_idx[v] = idx_new
            sub._idx_to_vertex[idx_new] = v
        sub.num_vertices = len(sub._vertex_to_idx)

        # Copy edges where both endpoints are in the sub-complex
        sub._edges = {}
        for key, data in self._edges.items():
            endpoints = list(key)
            if endpoints[0] in sub._vertex_to_idx and endpoints[1] in sub._vertex_to_idx:
                sub._edges[key] = {"types": set(data["types"]), "weight": data["weight"]}

        # Copy triangles where all three vertices are in the sub-complex
        sub._triangles = [
            t for t in self._triangles
            if all(v in sub._vertex_to_idx for v in t)
        ]

        sub._vertex_themes = {
            v: themes for v, themes in self._vertex_themes.items()
            if v in sub._vertex_to_idx
        }

        return sub

    def vertex_to_index(self, v: VerseKey) -> int:
        """Map a (surah, verse) key to its integer index 0..6235."""
        return self._vertex_to_idx[v]

    def index_to_vertex(self, i: int) -> VerseKey:
        """Map an integer index back to (surah, verse)."""
        return self._idx_to_vertex[i]

    def neighbors(self, v: VerseKey) -> List[VerseKey]:
        """Return all vertices adjacent to v."""
        result = []
        for key in self._edges:
            if v in key:
                other = [x for x in key if x != v]
                if other:
                    result.append(other[0])
        return result

    def edge_count(self) -> int:
        """Return the total number of edges in the complex."""
        return len(self._edges)
