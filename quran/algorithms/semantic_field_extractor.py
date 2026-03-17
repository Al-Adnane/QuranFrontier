"""
Algorithm 1: Semantic Field Extraction

Extracts semantic fields from Quranic text by:
1. Loading verses and concept mappings
2. Building a concept-to-verses index
3. Computing co-occurrence scores between concept pairs
4. Building a weighted networkx graph
5. Clustering using greedy_modularity_communities
6. Returning structured semantic fields
"""

import json
import os
from dataclasses import dataclass, field
from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Optional, Tuple

import networkx as nx
from networkx.algorithms import community


@dataclass
class SemanticField:
    name: str
    core_concepts: List[str]
    all_concepts: List[str]
    frequency: int
    density: float
    verse_refs: List[str]  # verse_ids covered


class SemanticFieldExtractor:
    def __init__(self, corpus_path: str, concepts_path: str):
        """Load corpus and concept mappings from file paths."""
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus_data = json.load(f)

        # Support both {"verses": [...]} and flat list formats
        if isinstance(corpus_data, list):
            self.verses = corpus_data
        elif isinstance(corpus_data, dict) and "verses" in corpus_data:
            self.verses = corpus_data["verses"]
        else:
            self.verses = []

        # Build verse lookup: verse_id -> verse dict
        self.verse_lookup: Dict[str, dict] = {}
        for v in self.verses:
            # Support verse_id or verse_key field names
            vid = v.get("verse_id") or v.get("verse_key") or v.get("verse_ref")
            if vid is None:
                surah = v.get("surah")
                ayah = v.get("ayah")
                if surah is not None and ayah is not None:
                    vid = f"{surah}:{ayah}"
            if vid:
                self.verse_lookup[str(vid)] = v

        with open(concepts_path, "r", encoding="utf-8") as f:
            concepts_data = json.load(f)

        # Support {"mappings": {...}} or flat dict of verse_id -> list
        if isinstance(concepts_data, dict) and "mappings" in concepts_data:
            self.raw_mappings: Dict[str, list] = concepts_data["mappings"]
        elif isinstance(concepts_data, dict):
            self.raw_mappings = concepts_data
        else:
            self.raw_mappings = {}

    # ------------------------------------------------------------------ #
    # Helper: parse verse_id -> (surah_int, ayah_int)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_verse_id(verse_id: str) -> Tuple[int, int]:
        parts = str(verse_id).split(":")
        return int(parts[0]), int(parts[1])

    # ------------------------------------------------------------------ #
    # Step 1: Build concept_id -> [verse_ids] index
    # ------------------------------------------------------------------ #
    def build_concept_index(self) -> Dict[str, List[str]]:
        """Returns concept_id -> list of verse_ids that mention the concept."""
        index: Dict[str, List[str]] = defaultdict(list)
        for verse_id, concepts in self.raw_mappings.items():
            for c in concepts:
                if isinstance(c, dict):
                    cid = c.get("concept_id")
                else:
                    cid = str(c)
                if cid:
                    index[cid].append(str(verse_id))
        return dict(index)

    # ------------------------------------------------------------------ #
    # Step 2: Compute co-occurrence between two concepts
    # ------------------------------------------------------------------ #
    def compute_co_occurrence(
        self,
        concept_a: str,
        concept_b: str,
        concept_index: Dict[str, List[str]],
    ) -> Dict[str, int]:
        """
        Returns {exact, nearby, same_surah, total} co-occurrence counts.

        - exact: both concepts appear in the exact same verse
        - nearby: same surah, |ayah_a - ayah_b| <= 10 (but not exact)
        - same_surah: same surah but not nearby (|diff| > 10)
        total = exact*3 + nearby*2 + same_surah*1
        """
        verses_a = set(concept_index.get(concept_a, []))
        verses_b = set(concept_index.get(concept_b, []))

        exact = len(verses_a & verses_b)

        # Group by surah
        def by_surah(verse_ids):
            d: Dict[int, List[int]] = defaultdict(list)
            for vid in verse_ids:
                s, a = self._parse_verse_id(vid)
                d[s].append(a)
            return d

        surah_a = by_surah(verses_a)
        surah_b = by_surah(verses_b)

        nearby = 0
        same_surah = 0

        common_surahs = set(surah_a.keys()) & set(surah_b.keys())
        for s in common_surahs:
            ayahs_a = surah_a[s]
            ayahs_b = surah_b[s]
            for aa in ayahs_a:
                for ab in ayahs_b:
                    if aa == ab:
                        # This is the exact match, already counted above
                        continue
                    diff = abs(aa - ab)
                    if diff <= 10:
                        nearby += 1
                    else:
                        same_surah += 1

        # Avoid double-counting nearby pairs (a->b and b->a)
        # We count ordered pairs here; callers use the raw score for edge weight
        total = exact * 3 + nearby * 2 + same_surah * 1
        return {
            "exact": exact,
            "nearby": nearby,
            "same_surah": same_surah,
            "total": total,
        }

    # ------------------------------------------------------------------ #
    # Step 3: Build weighted graph
    # ------------------------------------------------------------------ #
    def build_graph(
        self,
        concept_index: Dict[str, List[str]],
        min_co_occurrence: int = 2,
    ) -> nx.Graph:
        """
        Build a weighted undirected graph.
        Nodes = concept_ids with frequency >= 2 verse mappings.
        Edges = pairs with total co-occurrence score >= min_co_occurrence.
        """
        # Filter to "core" concepts: appear in >= 2 verse mappings
        filtered = {
            cid: verses
            for cid, verses in concept_index.items()
            if len(verses) >= 2
        }

        G = nx.Graph()
        for cid, verses in filtered.items():
            G.add_node(cid, frequency=len(verses), verse_count=len(set(verses)))

        concept_ids = list(filtered.keys())
        for ca, cb in combinations(concept_ids, 2):
            score = self.compute_co_occurrence(ca, cb, filtered)
            if score["total"] >= min_co_occurrence:
                G.add_edge(ca, cb, weight=score["total"], **score)

        return G

    # ------------------------------------------------------------------ #
    # Step 4: Extract semantic fields via community detection
    # ------------------------------------------------------------------ #
    def extract_fields(self) -> Dict[str, "SemanticField"]:
        """
        Run community detection on the concept graph and return named fields.
        """
        concept_index = self.build_concept_index()
        G = self.build_graph(concept_index)

        if G.number_of_nodes() == 0:
            return {}

        # Use greedy modularity communities
        communities = list(community.greedy_modularity_communities(G))

        fields: Dict[str, SemanticField] = {}
        for cluster in communities:
            cluster_concepts = list(cluster)
            if not cluster_concepts:
                continue

            # Dominant concept: highest frequency node in cluster
            dominant = max(
                cluster_concepts,
                key=lambda c: G.nodes[c].get("frequency", 0),
            )

            # Core concepts: top 5 by frequency within cluster
            sorted_by_freq = sorted(
                cluster_concepts,
                key=lambda c: G.nodes[c].get("frequency", 0),
                reverse=True,
            )
            core = sorted_by_freq[:5]

            # Collect all verse_refs covered by this cluster
            verse_refs: List[str] = []
            for c in cluster_concepts:
                verse_refs.extend(concept_index.get(c, []))
            verse_refs = sorted(set(verse_refs))

            # Density = edges within cluster / max possible edges
            n = len(cluster_concepts)
            max_edges = n * (n - 1) / 2 if n > 1 else 1
            actual_edges = G.subgraph(cluster_concepts).number_of_edges()
            density = actual_edges / max_edges if max_edges > 0 else 0.0

            frequency = sum(
                G.nodes[c].get("frequency", 0) for c in cluster_concepts
            )

            sf = SemanticField(
                name=dominant,
                core_concepts=core,
                all_concepts=cluster_concepts,
                frequency=frequency,
                density=round(density, 4),
                verse_refs=verse_refs,
            )
            fields[dominant] = sf

        return fields

    # ------------------------------------------------------------------ #
    # Step 5: Full pipeline
    # ------------------------------------------------------------------ #
    def run(self) -> Dict:
        """
        Full pipeline returning:
        {
            "fields": {name: SemanticField, ...},
            "graph_stats": {nodes, edges, components, density},
            "top_concepts": [(concept_id, frequency), ...]  # top 10
        }
        """
        concept_index = self.build_concept_index()
        G = self.build_graph(concept_index)
        fields = self.extract_fields()

        graph_stats = {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "components": nx.number_connected_components(G) if G.number_of_nodes() > 0 else 0,
            "density": round(nx.density(G), 6) if G.number_of_nodes() > 0 else 0.0,
        }

        # Top 10 concepts by frequency
        top_concepts = sorted(
            [(cid, len(verses)) for cid, verses in concept_index.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        return {
            "fields": fields,
            "graph_stats": graph_stats,
            "top_concepts": top_concepts,
        }


# --------------------------------------------------------------------------- #
# Standalone script entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    corpus_path = os.path.join(
        base_dir, "corpus_extraction", "output", "complete_corpus.json"
    )
    concepts_path = os.path.join(
        base_dir, "corpus_extraction", "ontology", "verse_to_concepts_real.json"
    )

    if not os.path.exists(corpus_path):
        print(f"ERROR: corpus not found at {corpus_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(concepts_path):
        print(f"ERROR: concepts not found at {concepts_path}", file=sys.stderr)
        sys.exit(1)

    extractor = SemanticFieldExtractor(corpus_path, concepts_path)
    result = extractor.run()

    print(f"\n=== Semantic Field Extraction Results ===")
    print(f"Graph stats: {result['graph_stats']}")
    print(f"Number of semantic fields: {len(result['fields'])}")
    print(f"\nTop 10 concepts by frequency:")
    for cid, freq in result["top_concepts"]:
        print(f"  {cid}: {freq} verses")

    print(f"\nTop 5 semantic fields (by frequency):")
    sorted_fields = sorted(
        result["fields"].values(), key=lambda f: f.frequency, reverse=True
    )
    for sf in sorted_fields[:5]:
        print(f"  Field '{sf.name}': {sf.frequency} occurrences, "
              f"{len(sf.all_concepts)} concepts, density={sf.density}")
        print(f"    Core: {sf.core_concepts[:3]}")
        print(f"    Verses: {len(sf.verse_refs)} verse refs")
