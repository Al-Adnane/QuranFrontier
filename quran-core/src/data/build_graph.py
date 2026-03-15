#!/usr/bin/env python3
"""Build and manage the Neo4j theological knowledge graph.

Usage:
    python build_graph.py --uri neo4j://localhost:7687 --user neo4j --password password
    python build_graph.py --mode sample  # Use sample data for testing
    python build_graph.py --export graph_export.cypher
    python build_graph.py --report graph_report.json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from quran_core.src.data.neo4j_builder import Neo4jGraphBuilder
from quran_core.src.data.graph_queries import TheologicalGraphQueries


def setup_arguments() -> argparse.ArgumentParser:
    """Set up command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Build and manage Neo4j theological knowledge graph"
    )

    parser.add_argument(
        "--uri",
        default="neo4j://localhost:7687",
        help="Neo4j server URI (default: neo4j://localhost:7687)",
    )
    parser.add_argument(
        "--user",
        default="neo4j",
        help="Database username (default: neo4j)",
    )
    parser.add_argument(
        "--password",
        default="password",
        help="Database password (default: password)",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "sample", "test"],
        default="sample",
        help="Build mode: full (100K+ nodes), sample (smaller), test (minimal)",
    )
    parser.add_argument(
        "--export",
        help="Export graph to Cypher file",
    )
    parser.add_argument(
        "--report",
        help="Generate report file (JSON)",
    )
    parser.add_argument(
        "--queries",
        action="store_true",
        help="Run sample queries after building",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear database before building",
    )

    return parser


def clear_database(builder: Neo4jGraphBuilder) -> bool:
    """Clear all data from database.

    Args:
        builder: Neo4jGraphBuilder instance

    Returns:
        True if successful
    """
    print("Clearing database...")
    try:
        builder._execute_query("MATCH (n) DETACH DELETE n")
        print("Database cleared successfully")
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        return False


def build_graph(
    uri: str,
    user: str,
    password: str,
    mode: str = "sample",
) -> Neo4jGraphBuilder:
    """Build the knowledge graph.

    Args:
        uri: Neo4j URI
        user: Username
        password: Password
        mode: Build mode (full, sample, test)

    Returns:
        Neo4jGraphBuilder instance with built graph
    """
    builder = Neo4jGraphBuilder(uri, user, password)

    sample_config = {
        "test": {
            "sample_verses": 50,
            "tafsirs": 20,
            "hadiths": 20,
            "narrators": 30,
            "explained_by": 50,
            "supported_by": 50,
            "madhab_ruling": 20,
            "narrated_by": 30,
            "linguistic_root": 30,
        },
        "sample": {
            "sample_verses": 500,
            "tafsirs": 100,
            "hadiths": 100,
            "narrators": 100,
            "explained_by": 200,
            "supported_by": 200,
            "madhab_ruling": 50,
            "narrated_by": 100,
            "linguistic_root": 100,
        },
        "full": {
            "sample_verses": 6236,
            "tafsirs": 50000,
            "hadiths": 30000,
            "narrators": 10000,
            "explained_by": 100000,
            "supported_by": 80000,
            "madhab_ruling": 20000,
            "narrated_by": 50000,
            "linguistic_root": 50000,
        },
    }

    config = sample_config.get(mode, sample_config["sample"])
    sample_mode = mode != "full"

    # Build graph
    stats = builder.build_complete_graph(sample_mode=sample_mode)

    return builder


def export_report(stats: dict, output_file: str) -> bool:
    """Export statistics to JSON report.

    Args:
        stats: Statistics dictionary
        output_file: Output file path

    Returns:
        True if successful
    """
    print(f"\nExporting report to {output_file}...")
    try:
        report = {
            "timestamp": datetime.now().isoformat(),
            "graph_statistics": stats,
            "node_types": list(stats.get("nodes", {}).keys()),
            "relationship_types": list(stats.get("relationships", {}).keys()),
            "summary": {
                "total_nodes": stats.get("nodes", {}).get("TOTAL", 0),
                "total_relationships": stats.get("relationships", {}).get("TOTAL", 0),
                "average_degree": stats.get("graph_metrics", {}).get("average_degree", 0),
            },
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Report exported to {output_file}")
        return True
    except Exception as e:
        print(f"Error exporting report: {e}")
        return False


def run_sample_queries_from_builder(builder: Neo4jGraphBuilder) -> bool:
    """Run sample queries against built graph.

    Args:
        builder: Neo4jGraphBuilder instance

    Returns:
        True if queries executed successfully
    """
    print("\nRunning sample queries...")
    try:
        with builder.driver.session() as session:
            queries = TheologicalGraphQueries(session)

            print("\n1. Graph Statistics:")
            result = queries.get_graph_statistics()
            if result.success:
                if result.data:
                    stats = result.data[0].get("statistics", {})
                    print(f"   Total Nodes: {stats.get('total_nodes', 0)}")
                    print(f"   Total Relationships: {stats.get('total_relationships', 0)}")
                    print(f"   Average Degree: {stats.get('average_degree', 0):.2f}")
            else:
                print(f"   Error: {result.error}")

            # Try to find a verse to query
            print("\n2. Sample Verse Query (2:183 - Fasting):")
            result = queries.get_verse_with_tafsirs(2, 183)
            if result.success:
                print(f"   Query executed in {result.execution_time_ms:.2f}ms")
                if result.data and result.data[0].get("tafsirs"):
                    print(f"   Found {len(result.data[0]['tafsirs'])} tafsirs")
                else:
                    print("   No tafsirs found (expected for small sample)")
            else:
                print(f"   Error: {result.error}")

        return True
    except Exception as e:
        print(f"Error running sample queries: {e}")
        return False


def main():
    """Main execution."""
    parser = setup_arguments()
    args = parser.parse_args()

    print("=" * 80)
    print("Neo4j Theological Knowledge Graph Builder")
    print("=" * 80)
    print(f"Mode: {args.mode}")
    print(f"URI: {args.uri}")
    print()

    # Build graph
    builder = build_graph(args.uri, args.user, args.password, args.mode)

    # Get final statistics
    final_stats = builder.get_graph_statistics()

    # Export report if requested
    if args.report:
        export_report(final_stats, args.report)

    # Export graph if requested
    if args.export:
        builder.export_graph_to_cypher(args.export)

    # Run sample queries if requested
    if args.queries:
        run_sample_queries_from_builder(builder)

    # Close connection
    builder.close()

    print("\n" + "=" * 80)
    print("Build Complete!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
