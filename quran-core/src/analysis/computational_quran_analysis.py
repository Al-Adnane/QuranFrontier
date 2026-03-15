"""
COMPUTATIONAL QURAN ANALYSIS: 5 Advanced Methods

This module implements 5 computational analysis methods:

1. Network Graph Analysis - Build directed graphs of principles and supporting verses
2. Information Theory Analysis - Calculate entropy and information density per principle
3. Semantic Clustering - Root-word co-occurrence and semantic space analysis
4. Category Theory - Functorial mappings and algebraic structures
5. Ring Composition - Identify chiastic structures in surahs

Each method reveals different aspects of Quranic structure and principle relationships.
"""

import numpy as np
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
import json
import math


# ============================================================================
# 1. NETWORK GRAPH ANALYSIS
# ============================================================================

@dataclass
class Verse:
    """Represents a Quranic verse"""
    surah: int
    ayah: int
    text: str
    root_words: List[str]

    @property
    def reference(self) -> str:
        return f"Q{self.surah}:{self.ayah}"


@dataclass
class PrincipleNode:
    """A principle as a node in the principle network"""
    name: str
    quranic_reference: str
    domain: str
    supporting_verses: List[Verse]
    related_principles: List[str] = None

    def __post_init__(self):
        if self.related_principles is None:
            self.related_principles = []


@dataclass
class NetworkEdge:
    """An edge in the principle network"""
    source: str
    target: str
    weight: float  # Strength of relationship
    relationship_type: str  # "supports", "contrasts", "complements", "enables"


class PrincipleNetworkGraph:
    """Graph structure for principle relationships"""

    def __init__(self):
        self.nodes: Dict[str, PrincipleNode] = {}
        self.edges: List[NetworkEdge] = []
        self.adjacency: Dict[str, List[Tuple[str, float]]] = defaultdict(list)

    def add_principle(self, principle: PrincipleNode) -> None:
        """Add a principle node to the graph"""
        self.nodes[principle.name] = principle

    def add_relationship(self, source: str, target: str, weight: float,
                        relationship_type: str = "supports") -> None:
        """Add a relationship between two principles"""
        edge = NetworkEdge(source, target, weight, relationship_type)
        self.edges.append(edge)
        self.adjacency[source].append((target, weight))

    def get_principle_network_density(self) -> float:
        """Calculate network density (connectivity)"""
        n = len(self.nodes)
        if n <= 1:
            return 0.0
        max_edges = n * (n - 1) / 2
        actual_edges = len(self.edges)
        return actual_edges / max_edges

    def get_principle_centrality(self, principle_name: str) -> float:
        """Calculate centrality score (importance) of a principle"""
        if principle_name not in self.nodes:
            return 0.0

        # In-degree centrality: how many principles support this one
        in_degree = sum(1 for edge in self.edges if edge.target == principle_name)

        # Out-degree centrality: how many principles this supports
        out_degree = sum(1 for edge in self.edges if edge.source == principle_name)

        # Weighted by edge weights
        weighted_in = sum(edge.weight for edge in self.edges if edge.target == principle_name)
        weighted_out = sum(edge.weight for edge in self.edges if edge.source == principle_name)

        return (in_degree + out_degree + weighted_in + weighted_out) / 4

    def get_principle_clusters(self) -> List[List[str]]:
        """Identify clusters of related principles"""
        visited = set()
        clusters = []

        for node_name in self.nodes:
            if node_name not in visited:
                cluster = self._dfs_cluster(node_name, visited)
                clusters.append(cluster)

        return clusters

    def _dfs_cluster(self, start: str, visited: set) -> List[str]:
        """DFS to find connected components (clusters)"""
        cluster = []
        stack = [start]

        while stack:
            node = stack.pop()
            if node in visited:
                continue

            visited.add(node)
            cluster.append(node)

            # Add neighbors
            for neighbor, _ in self.adjacency.get(node, []):
                if neighbor not in visited:
                    stack.append(neighbor)

        return cluster

    def to_dict(self) -> Dict:
        """Convert graph to dictionary representation"""
        return {
            "nodes": {name: {
                "reference": node.quranic_reference,
                "domain": node.domain,
                "verses": len(node.supporting_verses),
                "centrality": self.get_principle_centrality(name)
            } for name, node in self.nodes.items()},
            "edges": [{
                "source": edge.source,
                "target": edge.target,
                "weight": edge.weight,
                "type": edge.relationship_type
            } for edge in self.edges],
            "metrics": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "density": self.get_principle_network_density(),
                "clusters": len(self.get_principle_clusters())
            }
        }


# ============================================================================
# 2. INFORMATION THEORY ANALYSIS
# ============================================================================

class InformationTheoryAnalyzer:
    """Analyzes information content and entropy of principles"""

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calculate Shannon entropy of a text"""
        if not text:
            return 0.0

        # Count character frequencies
        char_freq = Counter(text)
        total = len(text)

        # Calculate entropy
        entropy = 0.0
        for count in char_freq.values():
            probability = count / total
            entropy -= probability * math.log2(probability)

        return entropy

    @staticmethod
    def calculate_compression_ratio(text: str) -> float:
        """Calculate theoretical compression ratio using entropy"""
        entropy = InformationTheoryAnalyzer.calculate_entropy(text)
        # Compression ratio is entropy / 8 (bits per character / 8 bits per byte)
        return entropy / 8.0

    @staticmethod
    def calculate_information_density(text: str, verse_count: int) -> float:
        """
        Information density = information content per unit
        Measured as bits of information per verse (semantic unit)
        """
        entropy = InformationTheoryAnalyzer.calculate_entropy(text)
        if verse_count == 0:
            return 0.0

        return entropy / verse_count

    @staticmethod
    def analyze_principle_information(principle_name: str, verses: List[Verse]) -> Dict:
        """Analyze information content of a principle's supporting verses"""
        if not verses:
            return {
                "principle": principle_name,
                "entropy": 0.0,
                "compression_ratio": 0.0,
                "information_density": 0.0,
                "verse_count": 0
            }

        # Combine all verse texts
        combined_text = " ".join(verse.text for verse in verses)

        entropy = InformationTheoryAnalyzer.calculate_entropy(combined_text)
        compression = InformationTheoryAnalyzer.calculate_compression_ratio(combined_text)
        density = InformationTheoryAnalyzer.calculate_information_density(
            combined_text, len(verses)
        )

        return {
            "principle": principle_name,
            "entropy": entropy,
            "compression_ratio": compression,
            "information_density": density,
            "verse_count": len(verses),
            "total_characters": len(combined_text),
            "average_verse_length": len(combined_text) / len(verses)
        }


# ============================================================================
# 3. SEMANTIC CLUSTERING (ROOT-WORD CO-OCCURRENCE)
# ============================================================================

class SemanticClusterAnalyzer:
    """Analyzes semantic relationships through root-word co-occurrence"""

    def __init__(self):
        self.root_word_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.principle_roots: Dict[str, Set[str]] = {}

    def register_principle_verses(self, principle_name: str, verses: List[Verse]) -> None:
        """Register verses for a principle"""
        roots = set()
        for verse in verses:
            roots.update(verse.root_words)

        self.principle_roots[principle_name] = roots

    def build_cooccurrence_matrix(self) -> Dict[str, Dict[str, int]]:
        """Build co-occurrence matrix for all root words"""
        matrix = defaultdict(lambda: defaultdict(int))

        # For each principle
        for principle_name, roots in self.principle_roots.items():
            # For each pair of roots in that principle
            root_list = list(roots)
            for i, root1 in enumerate(root_list):
                for root2 in root_list[i+1:]:
                    matrix[root1][root2] += 1
                    matrix[root2][root1] += 1

        return dict(matrix)

    def calculate_semantic_similarity(self, principle1: str, principle2: str) -> float:
        """Calculate semantic similarity between two principles via root-word overlap"""
        if principle1 not in self.principle_roots or principle2 not in self.principle_roots:
            return 0.0

        roots1 = self.principle_roots[principle1]
        roots2 = self.principle_roots[principle2]

        if not roots1 or not roots2:
            return 0.0

        intersection = len(roots1 & roots2)
        union = len(roots1 | roots2)

        return intersection / union  # Jaccard similarity

    def find_semantic_clusters(self, threshold: float = 0.5) -> List[List[str]]:
        """Find clusters of semantically similar principles"""
        clusters = []
        visited = set()

        principles = list(self.principle_roots.keys())

        for principle in principles:
            if principle in visited:
                continue

            cluster = [principle]
            visited.add(principle)

            for other in principles:
                if other not in visited:
                    sim = self.calculate_semantic_similarity(principle, other)
                    if sim >= threshold:
                        cluster.append(other)
                        visited.add(other)

            clusters.append(cluster)

        return clusters

    def get_root_word_statistics(self) -> Dict:
        """Get statistics about root word usage"""
        all_roots = set()
        for roots in self.principle_roots.values():
            all_roots.update(roots)

        root_frequency = Counter()
        for roots in self.principle_roots.values():
            root_frequency.update(roots)

        return {
            "total_unique_roots": len(all_roots),
            "total_principles": len(self.principle_roots),
            "most_common_roots": root_frequency.most_common(10),
            "average_roots_per_principle": sum(len(r) for r in self.principle_roots.values()) / len(self.principle_roots)
        }


# ============================================================================
# 4. CATEGORY THEORY & ALGEBRAIC STRUCTURES
# ============================================================================

class CategoryTheoryAnalyzer:
    """Analyzes algebraic and categorical structures in Quran"""

    @staticmethod
    def identify_functorial_relationships(network: PrincipleNetworkGraph) -> Dict:
        """
        Identify functorial mappings between principle groups
        A functor is a structure-preserving map between categories
        """
        clusters = network.get_principle_clusters()

        functors = {}
        for i, cluster1 in enumerate(clusters):
            for j, cluster2 in enumerate(clusters):
                if i < j:
                    # Calculate structural similarity
                    similarity = CategoryTheoryAnalyzer._calculate_cluster_similarity(
                        cluster1, cluster2, network
                    )
                    if similarity > 0.6:
                        functors[f"F_{i}_to_{j}"] = {
                            "source_cluster": cluster1,
                            "target_cluster": cluster2,
                            "similarity": similarity,
                            "preserves_relationships": True
                        }

        return functors

    @staticmethod
    def _calculate_cluster_similarity(cluster1: List[str], cluster2: List[str],
                                     network: PrincipleNetworkGraph) -> float:
        """Calculate structural similarity between two clusters"""
        # Compare internal connectivity patterns
        internal_edges1 = sum(1 for edge in network.edges
                            if edge.source in cluster1 and edge.target in cluster1)
        internal_edges2 = sum(1 for edge in network.edges
                            if edge.source in cluster2 and edge.target in cluster2)

        if not cluster1 or not cluster2:
            return 0.0

        density1 = internal_edges1 / (len(cluster1) * (len(cluster1) - 1))
        density2 = internal_edges2 / (len(cluster2) * (len(cluster2) - 1))

        # Similarity is 1 minus the difference in densities
        return 1.0 - abs(density1 - density2)

    @staticmethod
    def identify_recursive_patterns(principles: Dict[str, PrincipleNode]) -> Dict:
        """Identify self-referential and recursive patterns in Quran"""
        patterns = {}

        for principle_name, principle in principles.items():
            # Check for self-reinforcing patterns in verses
            verse_themes = [verse.text for verse in principle.supporting_verses]

            # Look for recursive mentions of core concepts
            theme_frequency = Counter()
            for text in verse_themes:
                words = text.split()
                theme_frequency.update(words)

            recurring = theme_frequency.most_common(3)
            if recurring:
                patterns[principle_name] = {
                    "recurring_themes": [word for word, count in recurring],
                    "theme_frequency": dict(recurring)
                }

        return patterns


# ============================================================================
# 5. RING COMPOSITION ANALYSIS (CHIASMUS)
# ============================================================================

class RingCompositionAnalyzer:
    """
    Analyzes ring composition (chiasmus) structures in Quranic surahs
    Ring composition: ABCDEF-FEDCBA (concentric structure)
    """

    @staticmethod
    def analyze_surah_structure(surah_number: int, verses: List[Verse]) -> Dict:
        """
        Analyze ring composition in a surah
        Identifies mirrored themes between beginning and end
        """
        if len(verses) < 4:
            return {"surah": surah_number, "is_ring_composition": False}

        # Simplified analysis: check if first and last verses share themes
        first_verses = verses[:max(2, len(verses) // 4)]
        last_verses = verses[min(-2, -len(verses) // 4):]

        # Calculate theme overlap
        first_roots = set()
        for v in first_verses:
            first_roots.update(v.root_words)

        last_roots = set()
        for v in last_verses:
            last_roots.update(v.root_words)

        overlap = len(first_roots & last_roots)
        max_possible = max(len(first_roots), len(last_roots))

        theme_match_ratio = overlap / max_possible if max_possible > 0 else 0.0

        # Check for numerical patterns (e.g., 7 sections)
        surah_length = len(verses)
        is_structurally_significant = surah_length % 7 == 0 or surah_length == 19 or surah_length == 12

        return {
            "surah": surah_number,
            "is_ring_composition": theme_match_ratio > 0.3,
            "theme_match_ratio": theme_match_ratio,
            "length": surah_length,
            "is_structurally_significant": is_structurally_significant,
            "center_point": surah_length // 2,
            "first_section_roots": list(first_roots)[:5],
            "last_section_roots": list(last_roots)[:5],
        }

    @staticmethod
    def identify_central_emphasis(surah_verses: List[Verse]) -> Dict:
        """
        Identify the central theme emphasized by ring composition
        In ring composition, the center point emphasizes the main idea
        """
        if len(surah_verses) < 3:
            return {"central_verse_index": None, "emphasis": None}

        center_index = len(surah_verses) // 2
        center_verse = surah_verses[center_index]

        # The central verse should contain the most important roots
        context_verses = surah_verses[max(0, center_index-2):min(len(surah_verses), center_index+3)]

        all_roots = set()
        for v in context_verses:
            all_roots.update(v.root_words)

        return {
            "central_verse_index": center_index,
            "central_verse": center_verse.reference,
            "central_text": center_verse.text,
            "central_roots": list(all_roots),
            "context_verses": [v.reference for v in context_verses],
            "emphasis_strength": len(center_verse.root_words) / (len(center_verse.text) / 10)
        }


# ============================================================================
# INTEGRATED ANALYZER - COMBINES ALL 5 METHODS
# ============================================================================

class ComputationalQuranAnalyzer:
    """
    Master analyzer that combines all 5 computational methods
    """

    def __init__(self):
        self.network_graph = PrincipleNetworkGraph()
        self.info_analyzer = InformationTheoryAnalyzer()
        self.semantic_analyzer = SemanticClusterAnalyzer()
        self.category_analyzer = CategoryTheoryAnalyzer()
        self.ring_analyzer = RingCompositionAnalyzer()

        self.principles: Dict[str, PrincipleNode] = {}
        self.analysis_results = {}

    def add_principle(self, principle: PrincipleNode) -> None:
        """Register a principle for analysis"""
        self.principles[principle.name] = principle
        self.network_graph.add_principle(principle)
        self.semantic_analyzer.register_principle_verses(principle.name, principle.supporting_verses)

    def analyze_all(self) -> Dict:
        """Run all 5 analytical methods"""
        print("\nRunning Computational Analysis...")
        print("="*70)

        results = {
            "timestamp": "2026-03-15",
            "total_principles": len(self.principles),
            "analysis_methods": 5
        }

        # Method 1: Network Graph Analysis
        print("1. Network Graph Analysis...", end=" ")
        results["network_graph"] = self._analyze_network()
        print("✓")

        # Method 2: Information Theory Analysis
        print("2. Information Theory Analysis...", end=" ")
        results["information_theory"] = self._analyze_information()
        print("✓")

        # Method 3: Semantic Clustering
        print("3. Semantic Clustering Analysis...", end=" ")
        results["semantic_clustering"] = self._analyze_semantics()
        print("✓")

        # Method 4: Category Theory
        print("4. Category Theory Analysis...", end=" ")
        results["category_theory"] = self._analyze_category()
        print("✓")

        # Method 5: Ring Composition
        print("5. Ring Composition Analysis...", end=" ")
        results["ring_composition"] = self._analyze_ring_structure()
        print("✓")

        print("\nAnalysis complete!")
        return results

    def _analyze_network(self) -> Dict:
        """Execute network graph analysis"""
        # Build network from principles
        for principle in self.principles.values():
            for related in principle.related_principles:
                if related in self.principles:
                    # Add relationship
                    self.network_graph.add_relationship(
                        principle.name, related, 0.8, "complements"
                    )

        return self.network_graph.to_dict()

    def _analyze_information(self) -> Dict:
        """Execute information theory analysis"""
        info_results = []
        for name, principle in self.principles.items():
            analysis = self.info_analyzer.analyze_principle_information(
                name, principle.supporting_verses
            )
            info_results.append(analysis)

        # Calculate average information density
        densities = [a["information_density"] for a in info_results if a["verse_count"] > 0]
        avg_density = sum(densities) / len(densities) if densities else 0.0

        return {
            "principles_analyzed": len(info_results),
            "average_information_density": avg_density,
            "principle_details": info_results
        }

    def _analyze_semantics(self) -> Dict:
        """Execute semantic clustering analysis"""
        clusters = self.semantic_analyzer.find_semantic_clusters(threshold=0.4)
        stats = self.semantic_analyzer.get_root_word_statistics()

        return {
            "semantic_clusters": clusters,
            "cluster_count": len(clusters),
            "root_word_statistics": stats
        }

    def _analyze_category(self) -> Dict:
        """Execute category theory analysis"""
        functors = self.category_analyzer.identify_functorial_relationships(self.network_graph)
        recursive = self.category_analyzer.identify_recursive_patterns(self.principles)

        return {
            "functorial_mappings": functors,
            "recursive_patterns": recursive
        }

    def _analyze_ring_structure(self) -> Dict:
        """Execute ring composition analysis"""
        ring_results = []

        # Group principles by domain/surah
        # This is simplified - in reality would analyze actual surahs
        for name, principle in self.principles.items():
            # Use first verse as representative
            if principle.supporting_verses:
                surah_num = principle.supporting_verses[0].surah
                analysis = self.ring_analyzer.analyze_surah_structure(
                    surah_num, principle.supporting_verses
                )
                ring_results.append(analysis)

        return {
            "surahs_analyzed": len(ring_results),
            "surah_analyses": ring_results
        }

    def generate_report(self, output_path: str) -> None:
        """Generate comprehensive analysis report"""
        report = self.analyze_all()

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport generated: {output_path}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\nINITIALIZING COMPUTATIONAL QURAN ANALYSIS")
    print("="*70)

    # Create example principles with example verses
    example_verses_tayyib = [
        Verse(2, 168, "O mankind, eat from the earth what is lawful and good", ["eat", "lawful", "good"]),
        Verse(5, 88, "Eat from that which is lawful and good", ["eat", "lawful", "good"]),
    ]

    example_verses_knowledge = [
        Verse(96, 1, "Read in the name of your Lord who created", ["read", "Lord", "created"]),
        Verse(96, 2, "Created mankind from a clot", ["created", "mankind"]),
    ]

    principle_tayyib = PrincipleNode(
        name="Tayyib (Good Food)",
        quranic_reference="Q2:168",
        domain="Healthcare",
        supporting_verses=example_verses_tayyib,
        related_principles=["Knowledge Acquisition"]
    )

    principle_knowledge = PrincipleNode(
        name="Knowledge Acquisition",
        quranic_reference="Q96:1-5",
        domain="Cognition",
        supporting_verses=example_verses_knowledge,
        related_principles=["Tayyib (Good Food)"]
    )

    # Create analyzer and run analysis
    analyzer = ComputationalQuranAnalyzer()
    analyzer.add_principle(principle_tayyib)
    analyzer.add_principle(principle_knowledge)

    # Run all analyses
    results = analyzer.analyze_all()

    # Print summary
    print("\n" + "="*70)
    print("ANALYSIS RESULTS SUMMARY")
    print("="*70)
    print(f"Total Principles Analyzed: {results['total_principles']}")
    print(f"Methods Executed: {results['analysis_methods']}")

    # Show network metrics
    if "network_graph" in results:
        net = results["network_graph"]
        print(f"\nNetwork Metrics:")
        print(f"  - Total Nodes: {net['metrics']['total_nodes']}")
        print(f"  - Total Edges: {net['metrics']['total_edges']}")
        print(f"  - Network Density: {net['metrics']['density']:.3f}")
        print(f"  - Principle Clusters: {net['metrics']['clusters']}")

    # Show information theory results
    if "information_theory" in results:
        info = results["information_theory"]
        print(f"\nInformation Theory Metrics:")
        print(f"  - Principles Analyzed: {info['principles_analyzed']}")
        print(f"  - Average Information Density: {info['average_information_density']:.3f}")

    # Show semantic results
    if "semantic_clustering" in results:
        sem = results["semantic_clustering"]
        print(f"\nSemantic Clustering Results:")
        print(f"  - Semantic Clusters Found: {sem['cluster_count']}")
        print(f"  - Unique Root Words: {sem['root_word_statistics']['total_unique_roots']}")

    # Export to JSON
    output_path = "/Users/mac/Desktop/QuranFrontier/quran-core/docs/computational_analysis_results.json"
    analyzer.generate_report(output_path)
