"""Debate Engine - Orchestrates multi-agent formal argumentation.

The DebateEngine coordinates the three agents (Proposer, Critic, Verifier)
in a formal debate loop using LangGraph state machine and Dung argumentation
framework semantics.

Architecture:
- LangGraph state machine for multi-turn coordination
- Dung abstract argumentation framework
- Iterative refinement until convergence
- Tracks argument justification and attack relations
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ArgumentStatus(Enum):
    """Status of an argument in debate."""
    PROPOSED = "proposed"
    CHALLENGED = "challenged"
    DEFENDED = "defended"
    ACCEPTABLE = "acceptable"
    REJECTED = "rejected"


@dataclass
class Argument:
    """Formal argument in debate."""
    id: str
    text: str
    agent: str  # "proposer", "critic", "verifier"
    round: int
    status: ArgumentStatus
    supports: List[str] = field(default_factory=list)  # IDs of supported arguments
    attacks: List[str] = field(default_factory=list)  # IDs of attacked arguments
    justification: Optional[Dict[str, Any]] = None
    confidence: float = 0.8


@dataclass
class RoundResult:
    """Result from single debate round."""
    round_number: int
    proposer_interpretation: str
    critic_assessment: Dict[str, Any]
    verifier_consistency: Dict[str, Any]
    arguments: List[Argument]
    new_issues: List[str]
    resolved_issues: List[str]
    convergence_delta: float


class DebateEngine:
    """
    Coordinates multi-agent debate with formal argumentation.

    Uses LangGraph to maintain state and Dung semantics to resolve conflicts.
    Agents iteratively refine interpretation until convergence.
    """

    def __init__(
        self,
        proposer: Any,
        critic: Any,
        verifier: Any,
        memory: Optional[Any] = None,
        max_rounds: int = 5,
        convergence_threshold: float = 0.85,
        enable_conflict_resolution: bool = True
    ):
        """
        Initialize DebateEngine.

        Args:
            proposer: ProposerAgent instance
            critic: CriticAgent instance
            verifier: VerifierAgent instance
            memory: Optional ScholarMemory instance
            max_rounds: Maximum debate rounds
            convergence_threshold: Convergence criteria (0-1)
            enable_conflict_resolution: Use Dung semantics for resolution
        """
        self.proposer = proposer
        self.critic = critic
        self.verifier = verifier
        self.memory = memory
        self.max_rounds = max_rounds
        self.convergence_threshold = convergence_threshold
        self.enable_conflict_resolution = enable_conflict_resolution

        self.debate_history: List[RoundResult] = []
        self.argument_graph: Dict[str, Argument] = {}
        self.state: Dict[str, Any] = self._initialize_state()
        self._round_counter = 0

    def debate(
        self,
        query: str,
        context: List[Dict[str, Any]],
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run complete debate on query.

        Args:
            query: Question to debate
            context: Retrieved sources
            topic: Optional topic classification

        Returns:
            Dictionary with:
                - final_interpretation: Converged interpretation
                - rounds: List of all round results
                - convergence_score: How much debate converged
                - conflict_resolution: How conflicts resolved
                - alternative_positions: Other valid views
        """
        self.state = self._initialize_state()
        self._round_counter = 0
        self.argument_graph = {}

        logger.info(f"Starting debate on: {query}")

        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"Debate round {round_num}/{self.max_rounds}")

            round_result = self.run_round(query, context, round_num)
            self.debate_history.append(round_result)

            # Check convergence
            if self._is_converged(round_result):
                logger.info(f"Debate converged after {round_num} rounds")
                break

        # Compute final interpretation
        final_interpretation = self._compute_final_interpretation()

        # Apply Dung semantics to resolve remaining conflicts
        if self.enable_conflict_resolution:
            conflict_resolution = self._apply_dung_semantics()
        else:
            conflict_resolution = None

        # Find alternative positions
        alternatives = self._extract_alternative_positions()

        # Compute convergence score
        convergence_score = self._compute_convergence_score()

        result = {
            "query": query,
            "final_interpretation": final_interpretation,
            "rounds": self.debate_history,
            "convergence_score": convergence_score,
            "total_rounds": len(self.debate_history),
            "conflict_resolution": conflict_resolution,
            "alternative_positions": alternatives,
            "state_trace": self.state
        }

        # Store in memory if available
        if self.memory:
            self.memory.add_entry({
                "query": query,
                "interpretation": final_interpretation,
                "confidence": convergence_score,
                "rounds": len(self.debate_history)
            })

        return result

    def run_round(
        self,
        query: str,
        context: List[Dict[str, Any]],
        round_num: int
    ) -> RoundResult:
        """
        Run single debate round.

        Args:
            query: Question being debated
            context: Retrieved sources
            round_num: Round number

        Returns:
            RoundResult with agent outputs and convergence metrics
        """
        self._round_counter = round_num

        # Phase 1: Proposer generates interpretation
        interpretation = self.proposer.generate(
            query,
            context if round_num == 1 else self._get_refined_context(query, context)
        )

        # Phase 2: Critic evaluates
        sources = self._extract_sources_from_context(context)
        critique = self.critic.evaluate(interpretation["interpretation"], sources)

        # Phase 3: Verifier checks consistency
        statements = [interpretation["interpretation"]]
        consistency = self.verifier.check_consistency(statements)

        # Track arguments
        arguments = self._track_arguments(
            round_num,
            interpretation,
            critique,
            consistency
        )

        # Compute deltas
        prev_result = self.debate_history[-1] if self.debate_history else None
        new_issues = self._identify_new_issues(critique, prev_result)
        resolved_issues = self._identify_resolved_issues(critique, prev_result)

        convergence_delta = self._compute_convergence_delta(
            critique,
            consistency,
            prev_result
        )

        # Update state
        self.state["current_round"] = round_num
        self.state["current_interpretation"] = interpretation
        self.state["issues"] = new_issues

        round_result = RoundResult(
            round_number=round_num,
            proposer_interpretation=interpretation["interpretation"],
            critic_assessment=critique,
            verifier_consistency=consistency,
            arguments=arguments,
            new_issues=new_issues,
            resolved_issues=resolved_issues,
            convergence_delta=convergence_delta
        )

        return round_result

    def _initialize_state(self) -> Dict[str, Any]:
        """Initialize LangGraph state machine."""
        return {
            "current_round": 0,
            "current_interpretation": None,
            "issues": [],
            "arguments": [],
            "converged": False,
            "convergence_history": []
        }

    def _track_arguments(
        self,
        round_num: int,
        interpretation: Dict[str, Any],
        critique: Dict[str, Any],
        consistency: Dict[str, Any]
    ) -> List[Argument]:
        """Track arguments in formal graph."""
        arguments = []

        # Proposer's argument
        prop_arg = Argument(
            id=f"prop_r{round_num}",
            text=interpretation["interpretation"],
            agent="proposer",
            round=round_num,
            status=ArgumentStatus.PROPOSED,
            confidence=interpretation.get("confidence", 0.8)
        )
        arguments.append(prop_arg)
        self.argument_graph[prop_arg.id] = prop_arg

        # Critic's counter-argument
        if critique.get("issues"):
            crit_arg = Argument(
                id=f"crit_r{round_num}",
                text=f"Issues: {', '.join(critique['issues'])}",
                agent="critic",
                round=round_num,
                status=ArgumentStatus.CHALLENGED,
                attacks=[prop_arg.id],
                confidence=1.0 - critique.get("overall_strength", 0.5)
            )
            arguments.append(crit_arg)
            self.argument_graph[crit_arg.id] = crit_arg

            # Update proposer argument status
            prop_arg.status = ArgumentStatus.CHALLENGED

        # Verifier's assessment
        if not consistency.get("is_consistent", True):
            ver_arg = Argument(
                id=f"ver_r{round_num}",
                text=f"Inconsistencies: {consistency.get('contradictions', [])}",
                agent="verifier",
                round=round_num,
                status=ArgumentStatus.CHALLENGED,
                attacks=[prop_arg.id],
                confidence=consistency.get("confidence", 0.7)
            )
            arguments.append(ver_arg)
            self.argument_graph[ver_arg.id] = ver_arg

        return arguments

    def _is_converged(self, round_result: RoundResult) -> bool:
        """Check if debate has converged."""
        # Converged if issues are resolved and consistency improves
        if not round_result.critic_assessment.get("issues"):
            return True

        if round_result.convergence_delta > 0 and len(round_result.new_issues) < 2:
            if round_result.verifier_consistency.get("is_consistent", True):
                return True

        return False

    def _apply_dung_semantics(self) -> Dict[str, Any]:
        """Apply Dung argumentation framework to resolve conflicts."""
        # Extract attack relations
        attacks = {}
        for arg_id, arg in self.argument_graph.items():
            attacks[arg_id] = arg.attacks

        # Compute admissible sets (arguments not attacked by other defended arguments)
        acceptable_args = self._compute_acceptable_arguments(attacks)

        return {
            "framework_type": "Dung_abstract_argumentation",
            "acceptable_arguments": acceptable_args,
            "conflicting_sets": self._find_conflict_sets(attacks),
            "resolution_method": "preferred_semantics"
        }

    def _compute_acceptable_arguments(self, attacks: Dict[str, List[str]]) -> List[str]:
        """Compute acceptable arguments under Dung semantics."""
        acceptable = []

        for arg_id in self.argument_graph:
            # Argument is acceptable if it attacks all arguments attacking it
            attackers = [
                other_id for other_id, targets in attacks.items()
                if arg_id in targets
            ]

            # Check if this argument defends itself
            defends_self = all(
                any(att in attacks.get(arg_id, []) for att in attackers)
                for attacker in attackers
            )

            if defends_self or not attackers:
                acceptable.append(arg_id)

        return acceptable

    def _find_conflict_sets(self, attacks: Dict[str, List[str]]) -> List[Tuple[str, str]]:
        """Find sets of conflicting arguments."""
        conflicts = []

        for attacker_id, targets in attacks.items():
            for target_id in targets:
                conflicts.append((attacker_id, target_id))

        return conflicts

    def _compute_final_interpretation(self) -> str:
        """Compute final interpretation from all rounds."""
        if not self.debate_history:
            return "No interpretation generated"

        # Use final round's interpretation
        final_round = self.debate_history[-1]
        interpretation = final_round.proposer_interpretation

        # Add caveats based on residual issues
        if final_round.critic_assessment.get("issues"):
            issues_str = ", ".join(final_round.critic_assessment["issues"])
            interpretation += f"\n\nCaveats: {issues_str}"

        return interpretation

    def _extract_alternative_positions(self) -> List[str]:
        """Extract alternative valid positions from debate."""
        alternatives = []

        for round_result in self.debate_history:
            interp = round_result.proposer_interpretation
            if interp not in alternatives and interp:
                # Track distinct interpretations that were debated
                if len(alternatives) < 3:
                    alternatives.append(interp)

        return alternatives

    def _compute_convergence_score(self) -> float:
        """Compute how much debate converged to consensus."""
        if not self.debate_history:
            return 0.0

        # Measure: fewer issues, better consistency, higher confidence across rounds
        total_convergence = 0.0
        round_count = len(self.debate_history)

        for round_result in self.debate_history:
            issue_reduction = 1.0 - min(
                len(round_result.new_issues) / 5.0, 1.0
            )
            consistency_score = 1.0 if (
                round_result.verifier_consistency.get("is_consistent", True)
            ) else 0.5
            confidence_score = round_result.critic_assessment.get("overall_strength", 0.5)

            round_convergence = (
                issue_reduction * 0.3 +
                consistency_score * 0.4 +
                confidence_score * 0.3
            )
            total_convergence += round_convergence

        return total_convergence / round_count if round_count > 0 else 0.6

    def _compute_convergence_delta(
        self,
        critique: Dict[str, Any],
        consistency: Dict[str, Any],
        prev_result: Optional[RoundResult]
    ) -> float:
        """Compute change in convergence from previous round."""
        if not prev_result:
            return 0.5

        prev_issues = len(prev_result.critic_assessment.get("issues", []))
        curr_issues = len(critique.get("issues", []))
        issue_delta = (prev_issues - curr_issues) / max(prev_issues, 1)

        prev_consistency = 1.0 if (
            prev_result.verifier_consistency.get("is_consistent", True)
        ) else 0.0
        curr_consistency = 1.0 if consistency.get("is_consistent", True) else 0.0
        consistency_delta = curr_consistency - prev_consistency

        return (issue_delta * 0.5 + consistency_delta * 0.5)

    def _identify_new_issues(
        self,
        critique: Dict[str, Any],
        prev_result: Optional[RoundResult]
    ) -> List[str]:
        """Identify new issues raised in this round."""
        curr_issues = set(critique.get("issues", []))

        if not prev_result:
            return list(curr_issues)

        prev_issues = set(prev_result.critic_assessment.get("issues", []))
        new_issues = curr_issues - prev_issues

        return list(new_issues)

    def _identify_resolved_issues(
        self,
        critique: Dict[str, Any],
        prev_result: Optional[RoundResult]
    ) -> List[str]:
        """Identify issues resolved since last round."""
        if not prev_result:
            return []

        prev_issues = set(prev_result.critic_assessment.get("issues", []))
        curr_issues = set(critique.get("issues", []))
        resolved = prev_issues - curr_issues

        return list(resolved)

    def _get_refined_context(
        self,
        query: str,
        original_context: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Refine context based on issues identified."""
        # In production, would re-retrieve context focusing on issues
        return original_context

    def _extract_sources_from_context(
        self,
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract source types from raw context."""
        sources = {"quran": [], "hadith": []}

        for item in context:
            if "surah" in item:
                sources["quran"].append((item.get("surah"), item.get("ayah")))
            elif "hadith" in item:
                sources["hadith"].append(item.get("reference", ""))

        return sources

    def get_debate_history(self) -> List[RoundResult]:
        """Get debate history."""
        return self.debate_history

    def get_argument_graph(self) -> Dict[str, Argument]:
        """Get formal argument graph."""
        return self.argument_graph
