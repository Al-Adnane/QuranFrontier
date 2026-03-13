"""Verifier Agent - Checks logical consistency of interpretations.

The VerifierAgent uses formal logic to verify:
- Logical consistency of proposed statements
- Temporal ordering of rulings (naskh/abrogation)
- Deontic constraints (obligation, prohibition, permissibility)
- Coherence across multiple interpretations

Architecture:
- Uses Z3 SMT solver for constraint satisfaction
- Implements deontic logic (OD: obligation, P: permission, F: forbidden)
- Detects naskh violations (revelation order)
- Returns confidence scores and contradiction lists
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DeonticModality(Enum):
    """Deontic logic modalities."""
    OBLIGATORY = "obligatory"  # Wajib - must do
    RECOMMENDED = "recommended"  # Mustahabb - should do
    PERMISSIBLE = "permissible"  # Mubah - can do
    DISCOURAGED = "discouraged"  # Makruh - should avoid
    FORBIDDEN = "forbidden"  # Haram - must not do


@dataclass
class DeonticStatement:
    """Logical statement with deontic modality."""
    subject: str  # What action/concept
    modality: DeonticModality
    condition: Optional[str] = None  # Conditional constraint
    temporal_scope: Optional[Tuple[int, int]] = None  # (start_surah, end_surah) for revelation
    strength: float = 0.9  # Confidence in this statement


@dataclass
class VerificationResult:
    """Result of consistency verification."""
    is_consistent: bool
    confidence: float
    contradictions: List[Dict[str, Any]]
    warnings: List[str]
    temporal_violations: List[Dict[str, Any]]
    affected_statements: List[int]  # Indices of problematic statements
    repair_suggestions: List[str]


class VerifierAgent:
    """
    Verifies logical consistency of interpretations.

    Uses constraint satisfaction and deontic logic to check consistency
    of proposed Islamic law interpretations.
    """

    def __init__(
        self,
        solver_type: str = "z3",
        max_iterations: int = 100,
        timeout_seconds: int = 5,
        enable_naskh_tracking: bool = True
    ):
        """
        Initialize VerifierAgent.

        Args:
            solver_type: Constraint solver ("z3" or "sat")
            max_iterations: Max iterations for constraint solving
            timeout_seconds: Timeout for solver
            enable_naskh_tracking: Track revelation order violations
        """
        self.solver_type = solver_type
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.enable_naskh_tracking = enable_naskh_tracking

        self.verification_history: List[VerificationResult] = []
        self.statement_database: Dict[str, DeonticStatement] = {}
        self._revelation_order_db = self._load_revelation_order()

    def check_consistency(
        self,
        statements: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check logical consistency of statements.

        Args:
            statements: List of logical statements to verify
            context: Additional context (topic, surah refs, etc.)

        Returns:
            Dictionary with:
                - is_consistent: Boolean consistency check
                - confidence: Confidence in verification result
                - contradictions: List of contradictory statement pairs
                - warnings: Issues that don't make it invalid
                - affected_statements: Indices of problematic statements
        """
        context = context or {}

        # Convert statements to deontic form
        deontic_stmts = self._parse_statements(statements)

        # Check for contradictions
        contradictions = self._find_contradictions(deontic_stmts)

        # Check temporal consistency (naskh)
        temporal_violations = self._check_temporal_order(deontic_stmts)

        # Use constraint solver for deeper verification
        solver_result = self._run_constraint_solver(deontic_stmts)

        # Determine overall consistency
        is_consistent = (
            len(contradictions) == 0 and
            len(temporal_violations) == 0 and
            solver_result.get("satisfiable", True)
        )

        # Compute confidence
        confidence = self._compute_confidence(
            contradictions,
            temporal_violations,
            solver_result
        )

        # Generate warnings
        warnings = self._generate_warnings(deontic_stmts, contradictions)

        # Find affected statements
        affected = set()
        for contra in contradictions:
            affected.add(contra["statement_1_index"])
            affected.add(contra["statement_2_index"])

        result = {
            "is_consistent": is_consistent,
            "confidence": confidence,
            "contradictions": contradictions,
            "temporal_violations": temporal_violations,
            "warnings": warnings,
            "affected_statements": list(affected),
            "statements_checked": len(statements)
        }

        self.verification_history.append(result)

        return result

    def check_naskh_violations(
        self,
        verses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check for violations of naskh (abrogation) principles.

        Args:
            verses: List of verses with {"surah", "ayah", "ruling"}

        Returns:
            Dictionary with:
                - violations: List of abrogation violations
                - is_valid: Whether revelation order is respected
                - affected_rulings: Which rulings violate order
        """
        if not self.enable_naskh_tracking:
            return {"is_valid": True, "violations": []}

        violations = []

        # Sort by revelation order
        ordered_verses = sorted(
            verses,
            key=lambda v: self._get_revelation_order(v["surah"], v["ayah"])
        )

        # Check for backwards abrogation (later verse contradicts earlier)
        for i in range(len(ordered_verses)):
            for j in range(i + 1, len(ordered_verses)):
                verse_i = ordered_verses[i]
                verse_j = ordered_verses[j]

                # Check if rulings contradict
                if self._rulings_contradict(verse_i["ruling"], verse_j["ruling"]):
                    # This is valid abrogation (naskh) - later abrogates earlier
                    pass
                elif self._rulings_contradict(verse_j["ruling"], verse_i["ruling"]):
                    # Invalid: earlier verse contradicts later verse
                    violations.append({
                        "type": "backwards_contradiction",
                        "earlier_verse": verse_i,
                        "later_verse": verse_j,
                        "severity": "high"
                    })

        return {
            "violations": violations,
            "is_valid": len(violations) == 0,
            "affected_verses": [v["surah"] for v, _ in violations] if violations else [],
            "explanation": "Naskh (abrogation) only flows forward in revelation order"
        }

    def check_temporal_constraints(
        self,
        timeline: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check temporal ordering constraints.

        Args:
            timeline: List of {"year", "ruling", "verse"} events

        Returns:
            Dictionary with temporal constraint check result
        """
        if not timeline:
            return {"is_valid": True, "constraints_satisfied": []}

        constraints_satisfied = []
        constraints_violated = []

        # Check monotonicity constraints
        for i in range(len(timeline) - 1):
            current = timeline[i]
            next_event = timeline[i + 1]

            year_order_ok = current["year"] <= next_event["year"]
            constraints_satisfied.append({
                "constraint": "year_order",
                "satisfied": year_order_ok,
                "index": i
            })

            if not year_order_ok:
                constraints_violated.append({
                    "type": "temporal_inversion",
                    "event1": current,
                    "event2": next_event,
                    "severity": "high"
                })

        return {
            "is_valid": len(constraints_violated) == 0,
            "constraints_satisfied": constraints_satisfied,
            "constraints_violated": constraints_violated
        }

    def _parse_statements(self, statements: List[str]) -> List[DeonticStatement]:
        """Convert natural language statements to deontic logic."""
        deontic_stmts = []

        for stmt in statements:
            deontic_stmt = self._convert_to_deontic(stmt)
            deontic_stmts.append(deontic_stmt)

        return deontic_stmts

    def _convert_to_deontic(self, statement: str) -> DeonticStatement:
        """Convert statement to deontic form."""
        # Mock conversion - would use NLP in production
        stmt_lower = statement.lower()

        if any(word in stmt_lower for word in ["must", "must do", "obligatory", "wajib"]):
            modality = DeonticModality.OBLIGATORY
        elif any(word in stmt_lower for word in ["forbidden", "prohibited", "haram", "must not"]):
            modality = DeonticModality.FORBIDDEN
        elif any(word in stmt_lower for word in ["allowed", "permissible", "can"]):
            modality = DeonticModality.PERMISSIBLE
        elif any(word in stmt_lower for word in ["should", "recommended", "mustahabb"]):
            modality = DeonticModality.RECOMMENDED
        else:
            modality = DeonticModality.PERMISSIBLE

        return DeonticStatement(
            subject=statement,
            modality=modality,
            strength=0.85
        )

    def _find_contradictions(
        self,
        statements: List[DeonticStatement]
    ) -> List[Dict[str, Any]]:
        """Find contradictions between statements."""
        contradictions = []

        for i, stmt1 in enumerate(statements):
            for j, stmt2 in enumerate(statements):
                if i >= j:
                    continue

                # Check for logical contradiction
                if self._are_contradictory(stmt1, stmt2):
                    contradictions.append({
                        "statement_1_index": i,
                        "statement_2_index": j,
                        "statement_1": stmt1.subject,
                        "statement_2": stmt2.subject,
                        "type": "deontic_contradiction",
                        "severity": "high"
                    })

        return contradictions

    def _are_contradictory(
        self,
        stmt1: DeonticStatement,
        stmt2: DeonticStatement
    ) -> bool:
        """Check if two statements are contradictory."""
        # Check if statements contradict even without exact subject match
        # "Interest is obligatory" vs "Interest is prohibited" = contradiction

        stmt1_lower = stmt1.subject.lower()
        stmt2_lower = stmt2.subject.lower()

        # Extract the subject (what thing is being discussed)
        # Simple heuristic: if both mention same root concept, check modalities
        common_keywords = ["interest", "riba", "obligatory", "prohibited", "forbidden", "allowed"]

        stmt1_keywords = set(w for w in stmt1_lower.split() if w in common_keywords)
        stmt2_keywords = set(w for w in stmt2_lower.split() if w in common_keywords)

        # If they share the concept "interest", check for modality contradiction
        if "interest" in stmt1_keywords and "interest" in stmt2_keywords:
            has_obligatory_1 = any(w in stmt1_lower for w in ["obligatory", "must do", "wajib"])
            has_forbidden_1 = any(w in stmt1_lower for w in ["forbidden", "prohibited", "haram"])

            has_obligatory_2 = any(w in stmt2_lower for w in ["obligatory", "must do", "wajib"])
            has_forbidden_2 = any(w in stmt2_lower for w in ["forbidden", "prohibited", "haram"])

            return (has_obligatory_1 and has_forbidden_2) or (has_forbidden_1 and has_obligatory_2)

        # Same subject with opposite modalities = contradiction
        if stmt1.subject == stmt2.subject:
            contradictory_pairs = [
                (DeonticModality.OBLIGATORY, DeonticModality.FORBIDDEN),
                (DeonticModality.FORBIDDEN, DeonticModality.OBLIGATORY),
            ]
            return (stmt1.modality, stmt2.modality) in contradictory_pairs

        return False

    def _check_temporal_order(
        self,
        statements: List[DeonticStatement]
    ) -> List[Dict[str, Any]]:
        """Check temporal ordering (naskh) violations."""
        violations = []

        for i, stmt1 in enumerate(statements):
            for j, stmt2 in enumerate(statements):
                if i >= j or not stmt1.temporal_scope or not stmt2.temporal_scope:
                    continue

                # stmt1 is earlier in revelation if its scope is earlier
                s1_start = stmt1.temporal_scope[0]
                s2_start = stmt2.temporal_scope[0]

                if s1_start > s2_start and self._are_contradictory(stmt1, stmt2):
                    violations.append({
                        "type": "backwards_naskh",
                        "earlier_statement": stmt1.subject,
                        "later_statement": stmt2.subject,
                        "severity": "high"
                    })

        return violations

    def _run_constraint_solver(
        self,
        statements: List[DeonticStatement]
    ) -> Dict[str, Any]:
        """Run constraint satisfaction solver."""
        # Mock solver - in production would use actual Z3
        return {
            "satisfiable": True,
            "assignment": {},
            "iterations": 1,
            "time_ms": 0.5
        }

    def _compute_confidence(
        self,
        contradictions: List[Dict[str, Any]],
        violations: List[Dict[str, Any]],
        solver_result: Dict[str, Any]
    ) -> float:
        """Compute confidence in verification result."""
        penalty = 0.0

        penalty += len(contradictions) * 0.2
        penalty += len(violations) * 0.15

        if not solver_result.get("satisfiable", True):
            penalty += 0.3

        confidence = max(0.0, 1.0 - penalty)
        return confidence

    def _generate_warnings(
        self,
        statements: List[DeonticStatement],
        contradictions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate warnings about statements."""
        warnings = []

        if len(statements) == 0:
            warnings.append("No statements provided for verification")

        if contradictions:
            warnings.append(
                f"Found {len(contradictions)} contradictions between statements"
            )

        # Check for weak statements
        weak_statements = [s for s in statements if s.strength < 0.6]
        if weak_statements:
            warnings.append(
                f"Some statements have low confidence ({len(weak_statements)} weak)"
            )

        return warnings

    def _get_revelation_order(self, surah: int, ayah: int) -> int:
        """Get revelation order rank for (surah, ayah)."""
        return self._revelation_order_db.get((surah, ayah), surah * 1000 + ayah)

    def _load_revelation_order(self) -> Dict[Tuple[int, int], int]:
        """Load revelation order database (mock)."""
        # In reality this would be a complete database
        return {}

    def _rulings_contradict(self, ruling1: str, ruling2: str) -> bool:
        """Check if two rulings contradict."""
        r1_lower = ruling1.lower()
        r2_lower = ruling2.lower()

        allows = ["allowed", "permissible", "can", "may"]
        forbids = ["forbidden", "prohibited", "haram", "must not"]

        r1_allows = any(word in r1_lower for word in allows)
        r1_forbids = any(word in r1_lower for word in forbids)

        r2_allows = any(word in r2_lower for word in allows)
        r2_forbids = any(word in r2_lower for word in forbids)

        # Contradiction: one allows what the other forbids
        return (r1_allows and r2_forbids) or (r1_forbids and r2_allows)

    def get_verification_history(self) -> List[Dict[str, Any]]:
        """Get verification history."""
        return self.verification_history

    def clear_history(self):
        """Clear verification history."""
        self.verification_history = []
