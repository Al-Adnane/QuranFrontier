"""RQL Executor - Executes compiled query plans on hypergraph.

Performs constraint satisfaction, graph traversal, and result assembly.
"""

from typing import List, Dict, Any, Optional
from frontier_neuro_symbolic.rql.compiler import ExecutionPlan, ExecutionStep
from frontier_neuro_symbolic.rql.parser import Condition, FunctionCall


class RQLExecutor:
    """Executes RQL queries on hypergraph knowledge base."""

    def __init__(self, kb: Any):
        """Initialize executor with knowledge base.

        Args:
            kb: HypergraphKB instance
        """
        self.kb = kb
        self.results = []
        self.visited = set()

    def execute(self, plan: ExecutionPlan) -> List[Any]:
        """Execute query plan.

        Args:
            plan: Compiled execution plan

        Returns:
            List of result nodes/edges
        """
        self.results = []
        self.visited = set()

        # Execute steps sequentially
        current_results = None

        for i, step in enumerate(plan.steps):
            if step.step_type == "scan":
                current_results = self._execute_scan(step)
            elif step.step_type == "filter":
                if current_results is None:
                    # Scan must come first
                    continue
                current_results = self._execute_filter(step, current_results)
            elif step.step_type == "function_filter":
                if current_results is None:
                    continue
                current_results = self._execute_function_filter(step, current_results)
            elif step.step_type == "traverse":
                if current_results is None:
                    continue
                current_results = self._execute_traverse(step, current_results)
            elif step.step_type == "project":
                if current_results is None:
                    continue
                current_results = self._execute_project(step, current_results)

        self.results = current_results if current_results is not None else []
        return self.results

    def _execute_scan(self, step: ExecutionStep) -> List[Any]:
        """Execute table scan step.

        Args:
            step: Scan step

        Returns:
            List of matching nodes
        """
        if not step.target:
            return []

        # Query KB for nodes of given type
        results = self.kb.query(entity_type=step.target)
        return results

    def _execute_filter(self, step: ExecutionStep, results: List[Any]) -> List[Any]:
        """Execute filter step.

        Args:
            step: Filter step
            results: Input results

        Returns:
            Filtered results
        """
        if not results:
            return []

        filtered = []

        for result in results:
            match = True

            for filter_spec in step.filters:
                if "field" not in filter_spec:
                    continue

                field = filter_spec["field"]
                operator = filter_spec["operator"]
                expected_value = filter_spec["value"]

                # Get actual value from result
                actual_value = result.properties.get(field) if hasattr(result, "properties") else None

                # Apply operator
                if not self._evaluate_condition(actual_value, operator, expected_value):
                    match = False
                    break

            if match:
                filtered.append(result)

        return filtered

    def _evaluate_condition(self, actual: Any, operator: str, expected: Any) -> bool:
        """Evaluate comparison condition.

        Args:
            actual: Actual value
            operator: Comparison operator
            expected: Expected value

        Returns:
            True if condition is met
        """
        if operator == "=":
            return actual == expected
        elif operator == ">":
            return actual is not None and actual > expected
        elif operator == "<":
            return actual is not None and actual < expected
        elif operator == ">=":
            return actual is not None and actual >= expected
        elif operator == "<=":
            return actual is not None and actual <= expected
        elif operator == "!=":
            return actual != expected
        else:
            return False

    def _execute_function_filter(self, step: ExecutionStep, results: List[Any]) -> List[Any]:
        """Execute function filter (e.g., naskh(abrogates: '2:180')).

        Args:
            step: Function filter step
            results: Input results

        Returns:
            Filtered results
        """
        if not results:
            return []

        function_name = step.properties.get("function")
        arguments = step.properties.get("arguments", {})

        filtered = []

        for result in results:
            if self._evaluate_function(function_name, arguments, result):
                filtered.append(result)

        return filtered

    def _evaluate_function(self, func_name: str, args: Dict[str, Any], node: Any) -> bool:
        """Evaluate function for node.

        Args:
            func_name: Function name
            args: Function arguments
            node: Node to evaluate

        Returns:
            True if function matches
        """
        if func_name == "naskh":
            # Check if node abrogates given verse
            abrogates_value = args.get("abrogates")
            node_abrogates = node.properties.get("abrogates") if hasattr(node, "properties") else None
            return node_abrogates == abrogates_value

        elif func_name == "tajweed":
            # Check if node has given tajweed rule
            rule_value = args.get("rule")
            node_rules = node.properties.get("rules", []) if hasattr(node, "properties") else []
            return rule_value in node_rules

        elif func_name == "maqasid":
            # Check if node has given maqasid goal
            goal_value = args.get("goal")
            node_goals = node.properties.get("goals", []) if hasattr(node, "properties") else []
            return goal_value in node_goals

        else:
            return False

    def _execute_traverse(self, step: ExecutionStep, results: List[Any]) -> List[Any]:
        """Execute graph traversal step.

        Args:
            step: Traverse step
            results: Input results (source nodes)

        Returns:
            Traversed results (target nodes)
        """
        if not results:
            return []

        edge_type = step.properties.get("edge_type")
        target_label = step.properties.get("target_label")

        traversed = []

        for result in results:
            neighbors = self.kb.get_neighbors(result.node_id)

            for neighbor in neighbors:
                if target_label and neighbor.entity_type != target_label:
                    continue

                traversed.append(neighbor)

        return traversed

    def _execute_project(self, step: ExecutionStep, results: List[Any]) -> List[Any]:
        """Execute projection step (select fields).

        Args:
            step: Project step
            results: Input results

        Returns:
            Projected results
        """
        if not results:
            return []

        fields = step.properties.get("fields", [])

        if not fields:
            return results

        projected = []

        for result in results:
            projected_props = {}

            for field in fields:
                if hasattr(result, "properties"):
                    projected_props[field] = result.properties.get(field)
                elif hasattr(result, field):
                    projected_props[field] = getattr(result, field)

            # Create projection object
            class ProjectedNode:
                def __init__(self, props):
                    self.properties = props

            projected.append(ProjectedNode(projected_props))

        return projected
