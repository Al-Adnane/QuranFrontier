"""RQL Compiler - Converts AST to Execution Plan.

Implements query optimization and generates execution plans
for hypergraph traversal with constraint satisfaction.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from frontier_neuro_symbolic.rql.parser import (
    QueryAST,
    Condition,
    FunctionCall,
)


# Type to avoid circular imports
List_type = List


@dataclass
class ExecutionStep:
    """Single step in execution plan."""

    step_type: str  # "scan", "filter", "traverse", "aggregate"
    target: Optional[str] = None
    filters: List[Dict[str, Any]] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Complete execution plan for query."""

    query_type: str  # "find", "match"
    steps: List[ExecutionStep] = field(default_factory=list)
    index_hints: Dict[str, Any] = field(default_factory=dict)
    estimated_cost: float = 0.0
    cardinality_estimates: Dict[str, int] = field(default_factory=dict)


class RQLCompiler:
    """Compiles RQL AST to execution plans."""

    def __init__(self):
        """Initialize compiler."""
        self.schema_stats = self._load_schema_stats()

    def compile(self, ast: QueryAST) -> ExecutionPlan:
        """Compile AST to execution plan.

        Args:
            ast: Query abstract syntax tree

        Returns:
            ExecutionPlan: Optimized execution plan
        """
        if ast.operation == "FIND":
            return self._compile_find(ast)
        elif ast.operation == "MATCH":
            return self._compile_match(ast)
        else:
            raise ValueError(f"Unknown operation: {ast.operation}")

    def _compile_find(self, ast: QueryAST) -> ExecutionPlan:
        """Compile FIND query."""
        plan = ExecutionPlan(query_type="find")

        # Step 1: Table scan on entity type (always first)
        if ast.entity_type:
            scan_step = ExecutionStep(
                step_type="scan",
                target=ast.entity_type,
                properties={"indexed": False},
            )
            plan.steps.insert(0, scan_step)  # Always at beginning

        # Step 2: Apply filters for each condition
        if ast.conditions:
            # Handle both single conditions and compound (nested) conditions
            self._add_filter_steps(plan, ast.conditions)

        # Step 3: Project return fields if specified
        if ast.return_fields:
            project_step = ExecutionStep(
                step_type="project",
                properties={"fields": ast.return_fields},
            )
            plan.steps.append(project_step)

        # Optimize and estimate cost
        self._optimize_plan(plan, ast)

        return plan

    def _add_filter_steps(self, plan: ExecutionPlan, conditions: List[Any]) -> None:
        """Add filter steps for conditions (handles nested conditions)."""
        if not conditions:
            return

        for condition in conditions:
            if isinstance(condition, Condition):
                # Check if it's a compound condition (with left/right nested)
                if hasattr(condition, "left") and isinstance(condition.left, Condition):
                    # Recursively add filters for left
                    self._add_filter_steps(plan, [condition.left])
                if hasattr(condition, "right") and isinstance(condition.right, Condition):
                    # Recursively add filters for right
                    self._add_filter_steps(plan, [condition.right])
                elif not isinstance(condition.left, Condition):
                    # Simple condition (not compound)
                    filter_step = self._condition_to_filter_step(condition)
                    plan.steps.append(filter_step)
            else:
                # Function call or other
                filter_step = self._condition_to_filter_step(condition)
                plan.steps.append(filter_step)

    def _compile_match(self, ast: QueryAST) -> ExecutionPlan:
        """Compile MATCH query (graph pattern matching)."""
        plan = ExecutionPlan(query_type="match")

        # Parse graph pattern
        pattern_parts = self._parse_graph_pattern(ast.pattern)

        # Step 1: Scan first node
        if pattern_parts:
            first_node = pattern_parts[0]
            scan_step = ExecutionStep(
                step_type="scan",
                target=first_node["label"],
                properties={"indexed": True},
            )
            plan.steps.append(scan_step)

            # Step 2: Traverse edges
            for i in range(1, len(pattern_parts), 2):
                if i + 1 < len(pattern_parts):
                    edge_info = pattern_parts[i]
                    target_node = pattern_parts[i + 1]

                    traverse_step = ExecutionStep(
                        step_type="traverse",
                        properties={
                            "edge_type": edge_info["type"],
                            "target_label": target_node["label"],
                        },
                    )
                    plan.steps.append(traverse_step)

        # Step 3: Apply WHERE conditions
        for condition in ast.conditions:
            filter_step = self._condition_to_filter_step(condition)
            plan.steps.append(filter_step)

        # Step 4: Project fields
        if ast.return_fields:
            project_step = ExecutionStep(
                step_type="project",
                properties={"fields": ast.return_fields},
            )
            plan.steps.append(project_step)

        self._optimize_plan(plan, ast)

        return plan

    def _condition_to_filter_step(self, condition: Any) -> ExecutionStep:
        """Convert condition to filter step."""
        if isinstance(condition, Condition):
            return ExecutionStep(
                step_type="filter",
                filters=[
                    {
                        "field": condition.left,
                        "operator": condition.operator,
                        "value": condition.right,
                    }
                ],
            )
        elif isinstance(condition, FunctionCall):
            return ExecutionStep(
                step_type="function_filter",
                properties={
                    "function": condition.name,
                    "arguments": condition.arguments,
                },
            )
        else:
            # Handle compound conditions
            return ExecutionStep(
                step_type="filter",
                filters=[{"raw": str(condition)}],
            )

    def _parse_graph_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Parse graph pattern into components.

        Pattern format: (var:Label)-[rel:RelType]->(var2:Label2)
        """
        parts = []

        # Extract nodes and edges
        import re

        # Find node patterns
        node_pattern = r"\((\w+):(\w+)\)"
        for match in re.finditer(node_pattern, pattern):
            var, label = match.groups()
            parts.append({"type": "node", "var": var, "label": label})

        # Find edge patterns
        edge_pattern = r"\[(\w+):(\w+)\]"
        for match in re.finditer(edge_pattern, pattern):
            var, rel_type = match.groups()
            parts.append({"type": "edge", "var": var, "rel_type": rel_type})

        return parts

    def _optimize_plan(self, plan: ExecutionPlan, ast: QueryAST) -> None:
        """Optimize execution plan.

        Applies heuristics:
        - Reorder filters (selectivity-first)
        - Add index hints
        - Estimate cardinality
        """
        # Separate scans from other steps
        scans = [s for s in plan.steps if s.step_type == "scan"]
        non_scans = [s for s in plan.steps if s.step_type != "scan"]

        # Categorize non-scan steps
        filters = [s for s in non_scans if s.step_type in ("filter", "function_filter")]
        traversals = [s for s in non_scans if s.step_type == "traverse"]
        projects = [s for s in non_scans if s.step_type == "project"]

        # Reorder: scans -> filters -> traversals -> projections
        plan.steps = scans + filters + traversals + projects

        # Generate index hints
        for step in plan.steps:
            if step.step_type == "scan" and step.target:
                if self._is_indexed(step.target):
                    plan.index_hints[step.target] = {"use_index": True}

        # Estimate cost
        plan.estimated_cost = self._estimate_cost(plan)

    def _estimate_cost(self, plan: ExecutionPlan) -> float:
        """Estimate query execution cost."""
        cost = 0.0

        for step in plan.steps:
            if step.step_type == "scan":
                # Full table scan cost
                target = step.target or "unknown"
                cost += self.schema_stats.get(target, {}).get("row_count", 1000)
            elif step.step_type == "filter":
                # Filter selectivity
                cost *= 0.5  # Assume 50% selectivity
            elif step.step_type == "traverse":
                # Edge traversal cost
                cost *= 2.0  # Approximate branching factor
            elif step.step_type == "project":
                # Projection is cheap
                cost *= 1.1

        return cost

    def _is_indexed(self, field: str) -> bool:
        """Check if field has index."""
        indexed_fields = {"surah", "ayah", "entity_type", "category"}
        return field in indexed_fields

    def _load_schema_stats(self) -> Dict[str, Dict[str, Any]]:
        """Load schema statistics for cardinality estimation."""
        return {
            "verse": {
                "row_count": 6236,  # ~Quranic verses
                "avg_width": 150,
            },
            "hadith": {
                "row_count": 100000,
                "avg_width": 500,
            },
            "tajweed_rule": {
                "row_count": 50,
                "avg_width": 50,
            },
            "maqasid_goal": {
                "row_count": 15,
                "avg_width": 30,
            },
        }
