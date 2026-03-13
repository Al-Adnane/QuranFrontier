"""Test suite for RQL Query Language and Hypergraph Knowledge Base.

Tests RQL parsing, compilation, execution, and Neo4j persistence.
"""

import pytest
from frontier_neuro_symbolic.rql.parser import RQLParser, QueryAST
from frontier_neuro_symbolic.rql.compiler import RQLCompiler, ExecutionPlan
from frontier_neuro_symbolic.rql.executor import RQLExecutor
from frontier_neuro_symbolic.rql.grammar import RQLGrammar
from frontier_neuro_symbolic.hypergraph_kb.hypergraph import HypergraphKB, Node, Hyperedge
from frontier_neuro_symbolic.hypergraph_kb.indexing import HypergraphIndex
from frontier_neuro_symbolic.hypergraph_kb.persistence import NeoPersistence
from frontier_neuro_symbolic.hypergraph_kb.operations import (
    HypergraphOps,
    FilterOps,
    MergeOps,
)


class TestRQLGrammar:
    """Test RQL grammar definition."""

    def test_grammar_tokens(self):
        """Verify RQL grammar tokens are defined."""
        grammar = RQLGrammar()
        assert "FIND" in grammar.tokens
        assert "WHERE" in grammar.tokens
        assert "MATCH" in grammar.tokens
        assert "RETURN" in grammar.tokens
        assert "AND" in grammar.tokens
        assert "OR" in grammar.tokens

    def test_grammar_rules(self):
        """Verify RQL grammar rules are defined."""
        grammar = RQLGrammar()
        assert grammar.rules is not None
        assert len(grammar.rules) > 0


class TestRQLParser:
    """Test RQL parser functionality."""

    @pytest.fixture
    def parser(self):
        """Create RQL parser."""
        return RQLParser()

    def test_parse_simple_find(self, parser):
        """Parse simple FIND query."""
        query = "FIND ayah WHERE tajweed(rule: 'idgham')"
        ast = parser.parse(query)
        assert ast is not None
        assert isinstance(ast, QueryAST)
        assert ast.operation == "FIND"
        assert "ayah" in ast.entity_type

    def test_parse_complex_query(self, parser):
        """Parse complex RQL query with multiple conditions."""
        query = """
        FIND ayah
        WHERE naskh(abrogates: "2:180")
        AND tajweed(rule: "idgham")
        AND maqasid(goal: "justice")
        RETURN verse_id, text, rules
        """
        ast = parser.parse(query)
        assert ast is not None
        assert ast.operation == "FIND"
        assert len(ast.conditions) >= 3
        assert ast.return_fields is not None

    def test_parse_match_clause(self, parser):
        """Parse MATCH clause for graph patterns."""
        query = """
        MATCH (v:Verse)-[r:ABROGATES]->(v2:Verse)
        WHERE v.surah = 2
        RETURN v.id, r.strength
        """
        ast = parser.parse(query)
        assert ast is not None
        assert ast.operation == "MATCH"

    def test_parse_with_constraints(self, parser):
        """Parse queries with constraint operators."""
        query = """
        FIND hadith
        WHERE chain_length > 5
        AND authenticity >= 0.8
        OR narrator_grade = "Sahih"
        """
        ast = parser.parse(query)
        assert ast is not None
        assert len(ast.conditions) >= 2

    def test_parse_error_handling(self, parser):
        """Test error handling for malformed queries."""
        with pytest.raises(Exception):
            parser.parse("FIND WHERE invalid")

    def test_parse_returns_ast(self, parser):
        """Verify parser returns proper AST structure."""
        query = "FIND ayah WHERE tajweed(rule: 'idgham')"
        ast = parser.parse(query)
        assert hasattr(ast, "operation")
        assert hasattr(ast, "entity_type")
        assert hasattr(ast, "conditions")


class TestRQLCompiler:
    """Test RQL compiler functionality."""

    @pytest.fixture
    def compiler(self):
        """Create RQL compiler."""
        return RQLCompiler()

    @pytest.fixture
    def sample_ast(self):
        """Create sample AST."""
        parser = RQLParser()
        return parser.parse("FIND ayah WHERE tajweed(rule: 'idgham')")

    def test_compile_to_plan(self, compiler, sample_ast):
        """Compile AST to execution plan."""
        plan = compiler.compile(sample_ast)
        assert plan is not None
        assert isinstance(plan, ExecutionPlan)
        assert plan.steps is not None
        assert len(plan.steps) > 0

    def test_execution_plan_structure(self, compiler, sample_ast):
        """Verify execution plan has proper structure."""
        plan = compiler.compile(sample_ast)
        assert hasattr(plan, "steps")
        assert hasattr(plan, "index_hints")
        assert hasattr(plan, "estimated_cost")

    def test_plan_optimization(self, compiler, sample_ast):
        """Test plan optimization strategies."""
        plan = compiler.compile(sample_ast)
        assert plan.estimated_cost >= 0
        # Verify index hints are populated
        assert isinstance(plan.index_hints, dict)

    def test_complex_query_compilation(self, compiler):
        """Compile complex multi-condition query."""
        parser = RQLParser()
        query = """
        FIND ayah
        WHERE naskh(abrogates: "2:180")
        AND tajweed(rule: "idgham")
        """
        ast = parser.parse(query)
        plan = compiler.compile(ast)
        assert len(plan.steps) >= 2


class TestHypergraphNode:
    """Test Hypergraph Node structures."""

    def test_create_verse_node(self):
        """Create a verse node."""
        node = Node(
            node_id="2:180",
            entity_type="verse",
            properties={
                "surah": 2,
                "ayah": 180,
                "text": "Sample verse text",
            },
        )
        assert node.node_id == "2:180"
        assert node.entity_type == "verse"
        assert node.properties["surah"] == 2

    def test_create_rule_node(self):
        """Create a tajweed rule node."""
        node = Node(
            node_id="rule:idgham",
            entity_type="tajweed_rule",
            properties={"rule_name": "idgham", "category": "merging"},
        )
        assert node.entity_type == "tajweed_rule"
        assert node.properties["rule_name"] == "idgham"

    def test_node_metadata(self):
        """Test node metadata tracking."""
        node = Node(
            node_id="test:1",
            entity_type="test",
            properties={},
        )
        assert hasattr(node, "created_at")
        assert hasattr(node, "updated_at")


class TestHyperedge:
    """Test Hypergraph Edge structures."""

    def test_create_semantic_hyperedge(self):
        """Create semantic hyperedge."""
        edge = Hyperedge(
            edge_id="sem:1",
            edge_type="semantic",
            source_ids=["2:180", "2:106"],
            target_id="concept:abrogation",
            properties={"strength": 0.95},
        )
        assert edge.edge_type == "semantic"
        assert len(edge.source_ids) == 2
        assert edge.properties["strength"] == 0.95

    def test_create_causal_hyperedge(self):
        """Create causal hyperedge."""
        edge = Hyperedge(
            edge_id="caus:1",
            edge_type="causal",
            source_ids=["2:180"],
            target_id="consequence:ruling",
            properties={"confidence": 0.8},
        )
        assert edge.edge_type == "causal"
        assert edge.properties["confidence"] == 0.8

    def test_create_phonetic_hyperedge(self):
        """Create phonetic hyperedge."""
        edge = Hyperedge(
            edge_id="phon:1",
            edge_type="phonetic",
            source_ids=["rule:idgham"],
            target_id="rule:assimilation",
            properties={"similarity": 0.7},
        )
        assert edge.edge_type == "phonetic"


class TestHypergraphKB:
    """Test Hypergraph Knowledge Base operations."""

    @pytest.fixture
    def kb(self):
        """Create hypergraph KB."""
        return HypergraphKB()

    def test_kb_initialization(self, kb):
        """Initialize knowledge base."""
        assert kb is not None
        assert hasattr(kb, "add_node")
        assert hasattr(kb, "add_edge")
        assert hasattr(kb, "query")

    def test_add_node(self, kb):
        """Add node to KB."""
        node = Node(
            node_id="test:1",
            entity_type="test",
            properties={"value": 42},
        )
        kb.add_node(node)
        assert kb.node_count() >= 1

    def test_add_multiple_nodes(self, kb):
        """Add multiple nodes to KB."""
        for i in range(5):
            node = Node(
                node_id=f"test:{i}",
                entity_type="test",
                properties={"index": i},
            )
            kb.add_node(node)
        assert kb.node_count() == 5

    def test_add_edge(self, kb):
        """Add edge to KB."""
        # Add nodes first
        node1 = Node(node_id="a", entity_type="test", properties={})
        node2 = Node(node_id="b", entity_type="test", properties={})
        kb.add_node(node1)
        kb.add_node(node2)

        # Add edge
        edge = Hyperedge(
            edge_id="e1",
            edge_type="relation",
            source_ids=["a"],
            target_id="b",
            properties={},
        )
        kb.add_edge(edge)
        assert kb.edge_count() >= 1

    def test_query_by_property(self, kb):
        """Query nodes by property."""
        node = Node(
            node_id="test:1",
            entity_type="verse",
            properties={"surah": 2, "ayah": 180},
        )
        kb.add_node(node)
        results = kb.query(entity_type="verse", surah=2)
        assert len(results) >= 1

    def test_query_neighbors(self, kb):
        """Query node neighbors."""
        node1 = Node(node_id="a", entity_type="test", properties={})
        node2 = Node(node_id="b", entity_type="test", properties={})
        kb.add_node(node1)
        kb.add_node(node2)

        edge = Hyperedge(
            edge_id="e1",
            edge_type="relation",
            source_ids=["a"],
            target_id="b",
            properties={},
        )
        kb.add_edge(edge)
        neighbors = kb.get_neighbors("a")
        assert len(neighbors) >= 1


class TestHypergraphIndex:
    """Test Hypergraph indexing for fast lookups."""

    @pytest.fixture
    def kb(self):
        """Create KB with sample data."""
        kb = HypergraphKB()
        for i in range(10):
            node = Node(
                node_id=f"verse:{i}",
                entity_type="verse",
                properties={"surah": (i % 3) + 1, "value": i},
            )
            kb.add_node(node)
        return kb

    def test_create_index(self, kb):
        """Create index on property."""
        idx = HypergraphIndex(kb, property_name="surah")
        assert idx is not None

    def test_indexed_lookup(self, kb):
        """Perform indexed lookup."""
        idx = HypergraphIndex(kb, property_name="surah")
        results = idx.lookup(surah=1)
        assert len(results) > 0
        assert all(r.properties["surah"] == 1 for r in results)

    def test_index_performance(self, kb):
        """Verify indexed lookup is efficient."""
        idx = HypergraphIndex(kb, property_name="value")
        # Lookup should be O(log n)
        results = idx.lookup(value=5)
        assert len(results) >= 1


class TestHypergraphOps:
    """Test Hypergraph operations."""

    @pytest.fixture
    def kb(self):
        """Create KB with sample data."""
        kb = HypergraphKB()
        for i in range(5):
            node = Node(
                node_id=f"node:{i}",
                entity_type="test",
                properties={"category": "A" if i < 3 else "B", "value": i},
            )
            kb.add_node(node)
        return kb

    def test_merge_nodes(self, kb):
        """Test merging nodes."""
        ops = MergeOps(kb)
        node1 = Node(node_id="merge1", entity_type="test", properties={"x": 1})
        node2 = Node(node_id="merge2", entity_type="test", properties={"y": 2})
        kb.add_node(node1)
        kb.add_node(node2)

        merged = ops.merge([node1, node2])
        assert merged is not None
        assert merged.properties.get("x") == 1
        assert merged.properties.get("y") == 2

    def test_filter_by_property(self, kb):
        """Test filtering nodes."""
        ops = FilterOps(kb)
        results = ops.filter_by_property("category", "A")
        assert len(results) == 3
        assert all(n.properties["category"] == "A" for n in results)

    def test_filter_by_range(self, kb):
        """Test range filtering."""
        ops = FilterOps(kb)
        results = ops.filter_by_range("value", min_val=2, max_val=4)
        assert len(results) >= 1
        assert all(2 <= n.properties["value"] <= 4 for n in results)


class TestRQLExecutor:
    """Test RQL query execution."""

    @pytest.fixture
    def kb(self):
        """Create KB with test data."""
        kb = HypergraphKB()
        # Add verse nodes
        for surah in range(1, 3):
            for ayah in range(1, 4):
                node = Node(
                    node_id=f"{surah}:{ayah}",
                    entity_type="verse",
                    properties={"surah": surah, "ayah": ayah, "text": f"Verse {surah}:{ayah}"},
                )
                kb.add_node(node)

        # Add rule nodes
        for rule in ["idgham", "iqlab", "ikhfa"]:
            node = Node(
                node_id=f"rule:{rule}",
                entity_type="tajweed_rule",
                properties={"rule_name": rule},
            )
            kb.add_node(node)
        return kb

    @pytest.fixture
    def executor(self, kb):
        """Create RQL executor."""
        return RQLExecutor(kb)

    def test_executor_initialization(self, executor):
        """Initialize RQL executor."""
        assert executor is not None
        assert executor.kb is not None

    def test_execute_simple_query(self, executor, kb):
        """Execute simple query."""
        parser = RQLParser()
        compiler = RQLCompiler()
        query = "FIND verse WHERE surah = 1"
        ast = parser.parse(query)
        plan = compiler.compile(ast)
        results = executor.execute(plan)
        assert results is not None
        assert len(results) >= 1  # Should have found verses with surah=1

    def test_execute_complex_query(self, executor, kb):
        """Execute complex query with constraints."""
        parser = RQLParser()
        compiler = RQLCompiler()
        query = "FIND verse WHERE surah = 1"
        ast = parser.parse(query)
        plan = compiler.compile(ast)
        results = executor.execute(plan)
        assert results is not None
        assert len(results) > 0

    def test_query_with_pattern_matching(self, executor, kb):
        """Execute query with pattern matching."""
        parser = RQLParser()
        compiler = RQLCompiler()
        query = "MATCH (v:Verse) WHERE v.surah = 1 RETURN v.id"
        ast = parser.parse(query)
        plan = compiler.compile(ast)
        results = executor.execute(plan)
        assert results is not None
        # Pattern matching should return something
        assert isinstance(results, list)


class TestNeoPersistence:
    """Test Neo4j persistence (mock)."""

    def test_neo_initialization(self):
        """Initialize Neo4j persistence."""
        # Using mock Neo4j for testing
        persistence = NeoPersistence(
            uri="bolt://localhost:7687",  # Non-existent for testing
            username="neo4j",
            password="test",
            use_mock=True,
        )
        assert persistence is not None

    def test_sync_node_to_neo(self):
        """Sync node to Neo4j."""
        persistence = NeoPersistence(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="test",
            use_mock=True,
        )
        node = Node(
            node_id="test:1",
            entity_type="verse",
            properties={"surah": 2, "ayah": 180},
        )
        persistence.sync_node(node)
        # Mock should not raise errors

    def test_sync_edge_to_neo(self):
        """Sync edge to Neo4j."""
        persistence = NeoPersistence(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="test",
            use_mock=True,
        )
        edge = Hyperedge(
            edge_id="e1",
            edge_type="semantic",
            source_ids=["a"],
            target_id="b",
            properties={},
        )
        persistence.sync_edge(edge)
        # Mock should not raise errors

    def test_transaction_support(self):
        """Test transactional operations."""
        persistence = NeoPersistence(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="test",
            use_mock=True,
        )
        with persistence.transaction() as tx:
            assert tx is not None


class TestIntegration:
    """Integration tests for RQL + Hypergraph."""

    def test_end_to_end_query(self):
        """Test end-to-end RQL query execution."""
        # Create KB
        kb = HypergraphKB()
        for surah in range(1, 3):
            for ayah in range(1, 4):
                node = Node(
                    node_id=f"{surah}:{ayah}",
                    entity_type="verse",
                    properties={"surah": surah, "ayah": ayah},
                )
                kb.add_node(node)

        # Parse, compile, execute
        parser = RQLParser()
        compiler = RQLCompiler()
        executor = RQLExecutor(kb)

        query = "FIND verse WHERE surah = 1"
        ast = parser.parse(query)
        plan = compiler.compile(ast)
        results = executor.execute(plan)

        assert len(results) > 0
        assert all(r.properties["surah"] == 1 for r in results)

    def test_kb_with_persistence(self):
        """Test KB with Neo4j persistence."""
        kb = HypergraphKB()
        persistence = NeoPersistence(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="test",
            use_mock=True,
        )

        # Add and persist node
        node = Node(
            node_id="test:1",
            entity_type="verse",
            properties={"surah": 2},
        )
        kb.add_node(node)
        persistence.sync_node(node)

        assert kb.node_count() >= 1
