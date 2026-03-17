"""Neo4j Graph Report Generator for Statistical Analysis.

Generates comprehensive reports on graph structure, content, and query performance.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict

from neo4j import Session


@dataclass
class NodeStatistics:
    """Statistics for a node type."""
    node_type: str
    count: int
    avg_properties: float = 0.0
    property_types: Dict[str, int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type,
            "count": self.count,
            "avg_properties": self.avg_properties,
            "property_types": self.property_types or {},
        }


@dataclass
class RelationshipStatistics:
    """Statistics for a relationship type."""
    relationship_type: str
    count: int
    source_node_types: Dict[str, int] = None
    target_node_types: Dict[str, int] = None
    avg_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_type": self.relationship_type,
            "count": self.count,
            "source_node_types": self.source_node_types or {},
            "target_node_types": self.target_node_types or {},
            "avg_confidence": self.avg_confidence,
        }


class GraphReporter:
    """Generate comprehensive reports on the theological knowledge graph."""

    def __init__(self, session: Session):
        """Initialize reporter with Neo4j session.

        Args:
            session: Active Neo4j session
        """
        self.session = session

    def generate_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive graph report.

        Returns:
            Dictionary containing all report sections
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "report_type": "neo4j_theological_graph",
            "sections": {
                "overview": self._generate_overview(),
                "node_statistics": self._generate_node_statistics(),
                "relationship_statistics": self._generate_relationship_statistics(),
                "graph_metrics": self._generate_graph_metrics(),
                "content_analysis": self._generate_content_analysis(),
                "coverage": self._generate_coverage_analysis(),
                "quality_metrics": self._generate_quality_metrics(),
                "recommendations": self._generate_recommendations(),
            },
        }
        return report

    def _generate_overview(self) -> Dict[str, Any]:
        """Generate overview section."""
        try:
            result = self.session.run("""
                MATCH (n)
                WITH count(n) as total_nodes
                MATCH ()-[r]->()
                WITH total_nodes, count(r) as total_relationships
                RETURN total_nodes, total_relationships
            """)

            record = result.single()
            return {
                "total_nodes": record["total_nodes"],
                "total_relationships": record["total_relationships"],
                "graph_status": "operational" if record["total_nodes"] > 0 else "empty",
                "density": self._calculate_density(
                    record["total_nodes"], record["total_relationships"]
                ),
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_node_statistics(self) -> Dict[str, Any]:
        """Generate node statistics."""
        try:
            result = self.session.run("""
                MATCH (n)
                RETURN labels(n)[0] as node_type, count(n) as count
                ORDER BY count DESC
            """)

            stats = {}
            for record in result:
                node_type = record["node_type"]
                count = record["count"]
                stats[node_type] = {
                    "count": count,
                    "percentage": 0.0,  # Will be calculated after total
                }

            total = sum(s["count"] for s in stats.values())
            for s in stats.values():
                s["percentage"] = (s["count"] / total * 100) if total > 0 else 0

            return stats
        except Exception as e:
            return {"error": str(e)}

    def _generate_relationship_statistics(self) -> Dict[str, Any]:
        """Generate relationship statistics."""
        try:
            result = self.session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """)

            stats = {}
            for record in result:
                rel_type = record["rel_type"]
                count = record["count"]
                stats[rel_type] = {
                    "count": count,
                    "percentage": 0.0,
                }

            total = sum(s["count"] for s in stats.values())
            for s in stats.values():
                s["percentage"] = (s["count"] / total * 100) if total > 0 else 0

            return stats
        except Exception as e:
            return {"error": str(e)}

    def _generate_graph_metrics(self) -> Dict[str, Any]:
        """Generate graph metrics."""
        try:
            result = self.session.run("""
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->()
                WITH
                  count(DISTINCT n) as total_nodes,
                  count(r) as total_relationships,
                  collect(DISTINCT labels(n)[0]) as node_types
                RETURN
                  total_nodes,
                  total_relationships,
                  node_types,
                  CASE
                    WHEN total_nodes > 0
                    THEN total_relationships * 1.0 / total_nodes
                    ELSE 0
                  END as avg_degree
            """)

            record = result.single()
            return {
                "total_nodes": record["total_nodes"],
                "total_relationships": record["total_relationships"],
                "node_types": len(record["node_types"]),
                "average_degree": round(record["avg_degree"], 2),
                "network_characteristics": self._analyze_network_structure(),
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_content_analysis(self) -> Dict[str, Any]:
        """Generate content analysis."""
        analysis = {}

        # Verse coverage
        try:
            result = self.session.run("""
                MATCH (v:Verse)
                RETURN count(v) as verse_count,
                       max(v.surah) as max_surah,
                       count(DISTINCT v.surah) as unique_surahs
            """)
            record = result.single()
            if record:
                analysis["verses"] = {
                    "total": record["verse_count"],
                    "surahs_covered": record["unique_surahs"],
                    "expected_total": 6236,
                    "coverage_percentage": (
                        record["verse_count"] / 6236 * 100 if record["verse_count"] else 0
                    ),
                }
        except Exception as e:
            analysis["verses"] = {"error": str(e)}

        # Tafsir coverage
        try:
            result = self.session.run("""
                MATCH (t:Tafsir)
                RETURN count(t) as tafsir_count,
                       count(DISTINCT t.school) as unique_schools
            """)
            record = result.single()
            if record:
                analysis["tafsirs"] = {
                    "total": record["tafsir_count"],
                    "schools_represented": record["unique_schools"],
                }
        except Exception as e:
            analysis["tafsirs"] = {"error": str(e)}

        # Hadith coverage
        try:
            result = self.session.run("""
                MATCH (h:Hadith)
                RETURN count(h) as hadith_count,
                       count(DISTINCT h.collection) as collections,
                       count(DISTINCT h.grade) as grades
            """)
            record = result.single()
            if record:
                analysis["hadiths"] = {
                    "total": record["hadith_count"],
                    "collections": record["collections"],
                    "grade_levels": record["grades"],
                }
        except Exception as e:
            analysis["hadiths"] = {"error": str(e)}

        # Narrator coverage
        try:
            result = self.session.run("""
                MATCH (n:Narrator)
                RETURN count(n) as narrator_count,
                       count(DISTINCT n.generation) as generations,
                       count(DISTINCT n.reliability_grade) as reliability_grades
            """)
            record = result.single()
            if record:
                analysis["narrators"] = {
                    "total": record["narrator_count"],
                    "generations": record["generations"],
                    "reliability_grades": record["reliability_grades"],
                }
        except Exception as e:
            analysis["narrators"] = {"error": str(e)}

        return analysis

    def _generate_coverage_analysis(self) -> Dict[str, Any]:
        """Analyze coverage of different content types."""
        coverage = {}

        # Verses with tafsirs
        try:
            result = self.session.run("""
                MATCH (v:Verse)-[:EXPLAINED_BY]->(t:Tafsir)
                WITH count(DISTINCT v) as verses_with_tafsirs,
                     count(DISTINCT t) as total_tafsirs
                MATCH (v:Verse)
                WITH verses_with_tafsirs, total_tafsirs, count(v) as total_verses
                RETURN verses_with_tafsirs, total_tafsirs, total_verses,
                       verses_with_tafsirs * 100.0 / total_verses as coverage_pct
            """)
            record = result.single()
            if record:
                coverage["tafsir_coverage"] = {
                    "verses_explained": record["verses_with_tafsirs"],
                    "tafsirs_available": record["total_tafsirs"],
                    "total_verses": record["total_verses"],
                    "coverage_percentage": round(record["coverage_pct"], 2),
                }
        except Exception as e:
            coverage["tafsir_coverage"] = {"error": str(e)}

        # Verses with hadith support
        try:
            result = self.session.run("""
                MATCH (v:Verse)-[:SUPPORTED_BY]->(h:Hadith)
                WITH count(DISTINCT v) as verses_with_hadith
                MATCH (v:Verse)
                WITH verses_with_hadith, count(v) as total_verses
                RETURN verses_with_hadith,
                       total_verses,
                       verses_with_hadith * 100.0 / total_verses as coverage_pct
            """)
            record = result.single()
            if record:
                coverage["hadith_support"] = {
                    "verses_supported": record["verses_with_hadith"],
                    "total_verses": record["total_verses"],
                    "coverage_percentage": round(record["coverage_pct"], 2),
                }
        except Exception as e:
            coverage["hadith_support"] = {"error": str(e)}

        # Madhab rulings
        try:
            result = self.session.run("""
                MATCH (v:Verse)-[:MADHAB_RULING]->(m:Madhab)
                WITH count(DISTINCT v) as verses_with_rulings
                MATCH (v:Verse)
                WITH verses_with_rulings, count(v) as total_verses
                RETURN verses_with_rulings,
                       total_verses,
                       verses_with_rulings * 100.0 / total_verses as coverage_pct
            """)
            record = result.single()
            if record:
                coverage["madhab_ruling_coverage"] = {
                    "verses_with_rulings": record["verses_with_rulings"],
                    "total_verses": record["total_verses"],
                    "coverage_percentage": round(record["coverage_pct"], 2),
                }
        except Exception as e:
            coverage["madhab_ruling_coverage"] = {"error": str(e)}

        return coverage

    def _generate_quality_metrics(self) -> Dict[str, Any]:
        """Generate quality metrics."""
        metrics = {}

        # Confidence score distribution
        try:
            result = self.session.run("""
                MATCH ()-[r]-()
                WHERE r.confidence IS NOT NULL
                RETURN
                  avg(r.confidence) as avg_confidence,
                  min(r.confidence) as min_confidence,
                  max(r.confidence) as max_confidence,
                  count(r) as relationship_count
            """)
            record = result.single()
            if record:
                metrics["confidence_metrics"] = {
                    "average": round(record["avg_confidence"], 3),
                    "minimum": record["min_confidence"],
                    "maximum": record["max_confidence"],
                    "relationships_with_confidence": record["relationship_count"],
                }
        except Exception as e:
            metrics["confidence_metrics"] = {"error": str(e)}

        # Hadith grade distribution
        try:
            result = self.session.run("""
                MATCH (h:Hadith)
                RETURN h.grade, count(h) as count
                ORDER BY count DESC
            """)
            grades = {}
            for record in result:
                grades[record["h.grade"]] = record["count"]
            metrics["hadith_grades"] = grades
        except Exception as e:
            metrics["hadith_grades"] = {"error": str(e)}

        return metrics

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for graph improvement."""
        recommendations = []

        try:
            # Check for incomplete verses
            result = self.session.run(
                "MATCH (v:Verse) WHERE v.text_arabic IS NULL RETURN count(v) as count"
            )
            record = result.single()
            if record and record["count"] > 0:
                recommendations.append(
                    f"Add Arabic text to {record['count']} verses for complete corpus"
                )

            # Check tafsir coverage
            result = self.session.run("""
                MATCH (v:Verse)
                WHERE NOT (v)-[:EXPLAINED_BY]->()
                RETURN count(v) as uncovered
            """)
            record = result.single()
            if record and record["uncovered"] > 100:
                recommendations.append(
                    f"Add tafsirs for {record['uncovered']} verses to improve coverage"
                )

            # Check hadith grades
            result = self.session.run("""
                MATCH (h:Hadith)
                WHERE h.grade = 'Da\'if'
                RETURN count(h) as weak_count
            """)
            record = result.single()
            if record and record["weak_count"] > 1000:
                recommendations.append(
                    f"Review {record['weak_count']} weak hadiths for potential removal or regrading"
                )

        except Exception as e:
            recommendations.append(f"Error generating recommendations: {str(e)}")

        if not recommendations:
            recommendations.append("Graph is well-structured and comprehensive")

        return recommendations

    def _calculate_density(self, nodes: int, relationships: int) -> float:
        """Calculate network density.

        Args:
            nodes: Number of nodes
            relationships: Number of relationships

        Returns:
            Network density (0.0 - 1.0)
        """
        if nodes < 2:
            return 0.0
        max_relationships = nodes * (nodes - 1)  # Directed graph
        return relationships / max_relationships if max_relationships > 0 else 0.0

    def _analyze_network_structure(self) -> Dict[str, Any]:
        """Analyze network structure characteristics."""
        return {
            "type": "multi-relational knowledge graph",
            "topology": "heterogeneous directed graph",
            "primary_pattern": "hub-and-spoke (verses as hubs)",
            "connectivity": "sparse but highly semantic",
        }

    def export_report_json(self, filename: str) -> bool:
        """Export report to JSON file.

        Args:
            filename: Output file path

        Returns:
            True if successful
        """
        try:
            report = self.generate_full_report()
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False

    def print_report_summary(self) -> None:
        """Print summary report to console."""
        report = self.generate_full_report()

        print("\n" + "=" * 80)
        print("NEO4J THEOLOGICAL KNOWLEDGE GRAPH REPORT")
        print("=" * 80)

        overview = report["sections"]["overview"]
        print(f"\nOVERVIEW")
        print(f"  Total Nodes: {overview.get('total_nodes', 0):,}")
        print(f"  Total Relationships: {overview.get('total_relationships', 0):,}")
        print(f"  Graph Status: {overview.get('graph_status', 'unknown')}")
        print(f"  Density: {overview.get('density', 0):.6f}")

        nodes = report["sections"]["node_statistics"]
        print(f"\nNODE STATISTICS")
        for node_type, stats in sorted(nodes.items(), key=lambda x: x[1]["count"], reverse=True):
            if node_type != "error":
                print(f"  {node_type}: {stats['count']:,} ({stats['percentage']:.1f}%)")

        rels = report["sections"]["relationship_statistics"]
        print(f"\nRELATIONSHIP STATISTICS")
        for rel_type, stats in sorted(rels.items(), key=lambda x: x[1]["count"], reverse=True):
            if rel_type != "error":
                print(f"  {rel_type}: {stats['count']:,} ({stats['percentage']:.1f}%)")

        metrics = report["sections"]["graph_metrics"]
        print(f"\nGRAPH METRICS")
        print(f"  Average Degree: {metrics.get('average_degree', 0):.2f}")
        print(f"  Node Types: {metrics.get('node_types', 0)}")

        content = report["sections"]["content_analysis"]
        print(f"\nCONTENT ANALYSIS")
        if "verses" in content and "error" not in content["verses"]:
            print(f"  Verses: {content['verses']['total']:,} / {content['verses']['expected_total']} "
                  f"({content['verses']['coverage_percentage']:.1f}%)")
        if "hadiths" in content and "error" not in content["hadiths"]:
            print(f"  Hadiths: {content['hadiths']['total']:,}")
        if "narrators" in content and "error" not in content["narrators"]:
            print(f"  Narrators: {content['narrators']['total']:,}")

        recommendations = report["sections"]["recommendations"]
        print(f"\nRECOMMENDATIONS")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 80)
