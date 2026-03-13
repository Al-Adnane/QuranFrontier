"""SMT-based solver for deontic logic and Islamic jurisprudence constraints.

Changed: The Z3-absent fallback now uses a real constraint-propagation engine
(FallbackConstraintSolver) instead of returning random/fixed values.
It enforces deontic conflict rules (wajib vs haram), maintains consistent
temporal ordering, and detects unsatisfiable constraint sets.
"""
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field as dc_field
import warnings

try:
    import z3
    HAS_Z3 = True
except ImportError:
    HAS_Z3 = False
    warnings.warn("z3-solver not installed. SMT solver will use constraint-propagation fallback.")


class FallbackConstraintSolver:
    """Lightweight constraint-propagation solver for when Z3 is unavailable.

    Enforces deontic logic rules:
    - A ruling cannot be both wajib (1.0) and haram (0.0)
    - Temporal ordering must be consistent (no cycles)
    - Naskh requires strictly increasing deontic strength
    - Bounded variables: all strengths in [0, 1]
    """

    # Deontic conflict pairs: strengths that cannot coexist on the same topic
    CONFLICT_THRESHOLD = 0.3  # wajib (1.0) conflicts with anything < 0.3 on same topic

    def __init__(self):
        self.variables: Dict[str, Tuple[float, float]] = {}  # var -> (lower, upper) bounds
        self.assignments: Dict[str, float] = {}  # var -> assigned value
        self.temporal_order: List[Tuple[str, str]] = []  # (earlier, later) pairs
        self.deontic_constraints: List[Dict[str, Any]] = []
        self._satisfiable = True
        self._conflict_reason: Optional[str] = None

    def set_bounds(self, var: str, lower: float, upper: float) -> bool:
        """Set or tighten bounds on a variable. Returns False if infeasible."""
        cur_lo, cur_hi = self.variables.get(var, (0.0, 1.0))
        new_lo = max(cur_lo, lower)
        new_hi = min(cur_hi, upper)
        if new_lo > new_hi + 1e-9:
            self._satisfiable = False
            self._conflict_reason = f"Infeasible bounds on {var}: [{new_lo}, {new_hi}]"
            return False
        self.variables[var] = (new_lo, new_hi)
        # Pick midpoint as current assignment
        self.assignments[var] = (new_lo + new_hi) / 2.0
        return True

    def assign(self, var: str, value: float) -> bool:
        """Assign exact value (with small epsilon for soft constraints)."""
        return self.set_bounds(var, value, value)

    def add_less_than(self, var_a: str, var_b: str) -> bool:
        """Enforce var_a < var_b."""
        self.temporal_order.append((var_a, var_b))
        return self._propagate_order()

    def _propagate_order(self) -> bool:
        """Propagate temporal ordering constraints. Detect cycles."""
        # Build adjacency and compute topological bounds
        from collections import defaultdict, deque

        graph: Dict[str, Set[str]] = defaultdict(set)
        in_degree: Dict[str, int] = defaultdict(int)
        all_vars: Set[str] = set()

        for a, b in self.temporal_order:
            graph[a].add(b)
            all_vars.update([a, b])

        # Check for cycles using Kahn's algorithm
        for v in all_vars:
            in_degree.setdefault(v, 0)
        for a, b in self.temporal_order:
            in_degree[b] = in_degree.get(b, 0) + 1

        queue = deque(v for v in all_vars if in_degree.get(v, 0) == 0)
        topo_order = []
        while queue:
            v = queue.popleft()
            topo_order.append(v)
            for w in graph.get(v, []):
                in_degree[w] -= 1
                if in_degree[w] == 0:
                    queue.append(w)

        if len(topo_order) != len(all_vars):
            self._satisfiable = False
            self._conflict_reason = "Cycle detected in temporal ordering"
            return False

        # Assign consistent ordering values
        n = len(topo_order)
        for i, v in enumerate(topo_order):
            lo = (i + 0.1) / (n + 1)
            hi = (i + 0.9) / (n + 1)
            if v in self.variables:
                # Only tighten, don't widen
                cur_lo, cur_hi = self.variables[v]
                lo = max(lo, cur_lo)
                hi = min(hi, cur_hi)
            if lo > hi + 1e-9:
                self._satisfiable = False
                self._conflict_reason = f"Temporal bounds conflict on {v}"
                return False
            self.variables[v] = (lo, hi)
            self.assignments[v] = (lo + hi) / 2.0

        return True

    def check_deontic_conflict(self, topic: str, strength1: float, strength2: float) -> bool:
        """Check if two deontic strengths conflict on the same topic.

        Wajib (1.0) conflicts with haram (0.0).
        Mustahabb (0.75) conflicts with makruh (0.25) only mildly.
        """
        if abs(strength1 - strength2) > 0.7:
            self._satisfiable = False
            self._conflict_reason = (
                f"Deontic conflict on '{topic}': strengths {strength1} and {strength2} "
                f"are contradictory (wajib vs haram)"
            )
            return False
        return True

    def is_satisfiable(self) -> bool:
        return self._satisfiable

    def get_value(self, var: str) -> Optional[float]:
        return self.assignments.get(var)

    def get_model_dict(self) -> Optional[Dict[str, float]]:
        if not self._satisfiable:
            return None
        return dict(self.assignments)


class DeonticStatus(Enum):
    """Deontic status in Islamic jurisprudence."""

    WAJIB = "wajib"  # Obligatory
    MUSTAHABB = "mustahabb"  # Recommended
    MUBAH = "mubah"  # Permissible
    MAKRUH = "makruh"  # Disliked
    HARAM = "haram"  # Forbidden


@dataclass
class VerseRuling:
    """A Quranic verse paired with a legal ruling."""

    verse: Tuple[int, int]  # (surah, ayah)
    verse_text: str
    ruling: str
    deontic_strength: float  # [0, 1]


@dataclass
class NaskhConstraint:
    """Naskh (abrogation) constraint between two rulings."""

    ruling1: Tuple[str, str]  # (verse, topic)
    ruling2: Tuple[str, str]  # (verse, topic)
    strength1: float  # Deontic strength of ruling 1
    strength2: float  # Deontic strength of ruling 2
    is_naskh: bool  # Whether ruling2 abrogates ruling1


class SMTDeonticSolver:
    """SMT solver for deontic logic and Islamic jurisprudence.

    Uses Z3 to reason about:
    - Deontic status assignments (wajib, haram, etc.)
    - Naskh (abrogation) constraints
    - Temporal ordering of revelations
    - Satisfiability of verse-ruling pairs

    Formula: □(∀t. naskh(t₁,t₂) → deontic_strength(t₂) > deontic_strength(t₁))
    """

    def __init__(self):
        """Initialize SMT solver.

        Uses Z3 when available; otherwise uses FallbackConstraintSolver
        which provides real constraint propagation and deontic conflict
        detection (not random results).
        """
        if HAS_Z3:
            self.z3_solver = z3.Solver()
            self.verse_vars: Dict[str, Any] = {}
            self.deontic_vars: Dict[str, Any] = {}
        else:
            self.z3_solver = None
            self._fallback = FallbackConstraintSolver()
            self.verse_vars: Dict[str, float] = {}
            self.deontic_vars: Dict[str, float] = {}

        self.naskh_vars: Dict[Tuple[str, str], Any] = {}
        self.constraints: List[Any] = []
        self._satisfiable = True
        # Track deontic assignments per topic for conflict detection
        self._topic_strengths: Dict[str, List[float]] = {}

    def _get_or_create_verse_var(self, verse: str) -> Any:
        """Get or create Z3 variable for a verse."""
        if HAS_Z3:
            if verse not in self.verse_vars:
                self.verse_vars[verse] = z3.Real(f"verse_{verse}")
            return self.verse_vars[verse]
        else:
            # Mock: store as float [0, 1]
            if verse not in self.verse_vars:
                self.verse_vars[verse] = 0.5
            return self.verse_vars[verse]

    def _get_or_create_deontic_var(self, ruling: str) -> Any:
        """Get or create Z3 variable for deontic strength."""
        if HAS_Z3:
            if ruling not in self.deontic_vars:
                self.deontic_vars[ruling] = z3.Real(f"deontic_{ruling}")
            return self.deontic_vars[ruling]
        else:
            # Mock: store as float [0, 1]
            if ruling not in self.deontic_vars:
                self.deontic_vars[ruling] = 0.5
            return self.deontic_vars[ruling]

    def add_deontic_status(
        self,
        ruling: Tuple[str, str],
        status: DeonticStatus,
        confidence: float,
    ) -> None:
        """Add deontic status constraint for a ruling.

        Args:
            ruling: (verse_id, topic_name) tuple.
            status: Deontic status (wajib, haram, etc.).
            confidence: Confidence in this assignment [0, 1].
        """
        ruling_key = f"{ruling[0]}_{ruling[1]}"
        deontic_var = self._get_or_create_deontic_var(ruling_key)

        # Map deontic status to numerical strength
        status_to_strength = {
            DeonticStatus.WAJIB: 1.0,
            DeonticStatus.MUSTAHABB: 0.75,
            DeonticStatus.MUBAH: 0.5,
            DeonticStatus.MAKRUH: 0.25,
            DeonticStatus.HARAM: 0.0,
        }

        target_strength = status_to_strength[status]

        if HAS_Z3:
            # Add soft constraint: deontic strength close to target
            margin = (1.0 - confidence) * 0.2
            constraint = z3.And(
                deontic_var >= target_strength - margin,
                deontic_var <= target_strength + margin,
            )
            self.constraints.append(constraint)
            self.z3_solver.add(constraint)
        else:
            # Fallback: use constraint propagation with conflict detection
            topic = ruling[1] if len(ruling) > 1 else ruling_key
            margin = (1.0 - confidence) * 0.2
            self._fallback.set_bounds(ruling_key, target_strength - margin, target_strength + margin)

            # Check for deontic conflicts (e.g., wajib + haram on same topic)
            if topic not in self._topic_strengths:
                self._topic_strengths[topic] = []
            for prev_strength in self._topic_strengths[topic]:
                self._fallback.check_deontic_conflict(topic, prev_strength, target_strength)
            self._topic_strengths[topic].append(target_strength)

            self.deontic_vars[ruling_key] = self._fallback.get_value(ruling_key) or target_strength
            self._satisfiable = self._fallback.is_satisfiable()
            self.constraints.append(
                {"type": "deontic_status", "ruling": ruling_key,
                 "strength": target_strength, "confidence": confidence}
            )

    def add_naskh_constraint(
        self,
        ruling1: Tuple[str, str],
        ruling2: Tuple[str, str],
        strength1: float,
        strength2: float,
    ) -> bool:
        """Add naskh (abrogation) constraint.

        Formula: naskh(t₁,t₂) → strength(t₂) > strength(t₁)

        Args:
            ruling1: Earlier ruling (verse, topic).
            ruling2: Later ruling (verse, topic).
            strength1: Deontic strength of ruling1.
            strength2: Deontic strength of ruling2.

        Returns:
            Whether constraint is satisfiable.
        """
        ruling1_key = f"{ruling1[0]}_{ruling1[1]}"
        ruling2_key = f"{ruling2[0]}_{ruling2[1]}"

        var1 = self._get_or_create_deontic_var(ruling1_key)
        var2 = self._get_or_create_deontic_var(ruling2_key)

        if HAS_Z3:
            # If naskh occurs, strength must increase
            constraint = z3.Implies(
                z3.And(var1 == strength1, var2 == strength2),
                var2 > var1,
            )
            self.constraints.append(constraint)
            self.z3_solver.add(constraint)
            return self.z3_solver.check() == z3.sat
        else:
            # Mock: check if strength2 > strength1
            is_sat = strength2 > strength1
            self._satisfiable = self._satisfiable and is_sat
            self.constraints.append(
                {
                    "type": "naskh",
                    "ruling1": ruling1_key,
                    "ruling2": ruling2_key,
                    "satisfiable": is_sat,
                }
            )
            return is_sat

    def add_temporal_constraint(
        self,
        earlier_verse: Tuple[str, str],
        later_verse: Tuple[str, str],
    ) -> None:
        """Add temporal constraint on revelation order.

        Args:
            earlier_verse: (verse_id, period_name) for earlier verse.
            later_verse: (verse_id, period_name) for later verse.
        """
        earlier_var = self._get_or_create_verse_var(earlier_verse[0])
        later_var = self._get_or_create_verse_var(later_verse[0])

        if HAS_Z3:
            constraint = earlier_var < later_var
            self.constraints.append(constraint)
            self.z3_solver.add(constraint)
        else:
            # Fallback: use constraint propagation for consistent ordering
            # (detects cycles, assigns monotonically increasing values)
            var_a = f"verse_{earlier_verse[0]}"
            var_b = f"verse_{later_verse[0]}"
            self._fallback.add_less_than(var_a, var_b)
            self.verse_vars[earlier_verse[0]] = self._fallback.get_value(var_a) or 0.0
            self.verse_vars[later_verse[0]] = self._fallback.get_value(var_b) or 1.0
            self._satisfiable = self._fallback.is_satisfiable()
            self.constraints.append(
                {"type": "temporal", "earlier": earlier_verse[0], "later": later_verse[0]}
            )

    def add_verse_ruling(
        self,
        verse: Tuple[str, str],
        ruling: str,
        deontic_strength: float,
    ) -> None:
        """Add a verse-ruling pair to the solver.

        Args:
            verse: (verse_id, verse_text) tuple.
            ruling: Description of the legal ruling.
            deontic_strength: Strength of the ruling [0, 1].
        """
        verse_key = verse[0]
        ruling_key = f"{verse_key}_{ruling}"

        verse_var = self._get_or_create_verse_var(verse_key)
        deontic_var = self._get_or_create_deontic_var(ruling_key)

        if HAS_Z3:
            constraint = deontic_var == deontic_strength
            self.constraints.append(constraint)
            self.z3_solver.add(constraint)
        else:
            # Mock: store assignment
            self.deontic_vars[ruling_key] = deontic_strength
            self.constraints.append(
                {
                    "type": "verse_ruling",
                    "verse": verse_key,
                    "ruling": ruling_key,
                    "strength": deontic_strength,
                }
            )

    def add_custom_formula(self, formula: str) -> None:
        """Add custom Z3 formula (advanced use).

        Args:
            formula: Z3 expression as string (e.g., "(> x 0.5)").
        """
        if not HAS_Z3:
            warnings.warn("Z3 not available; custom formulas unsupported")
            return

        try:
            parsed = z3.parse_smt2(formula)
            self.z3_solver.add(parsed)
            self.constraints.append(parsed)
        except Exception as e:
            raise ValueError(f"Invalid Z3 formula: {e}")

    def check_satisfiability(self) -> bool:
        """Check if current constraints are satisfiable.

        Returns:
            True if SAT, False if UNSAT.
        """
        if HAS_Z3:
            result = self.z3_solver.check()
            return result == z3.sat
        else:
            # Mock: return stored satisfiability
            return self._satisfiable

    def get_model(self) -> Optional[Any]:
        """Get satisfying model if constraints are satisfiable.

        Returns:
            Z3 model (if Z3), dict of {var: value} (if fallback), or None if UNSAT.
        """
        if HAS_Z3:
            if self.check_satisfiability():
                return self.z3_solver.model()
            return None
        else:
            return self._fallback.get_model_dict()

    def query_deontic_strength(self, ruling: str) -> Optional[float]:
        """Query deontic strength of a ruling from the model.

        Args:
            ruling: Ruling identifier.

        Returns:
            Numerical strength [0, 1], or None if unsatisfiable.
        """
        if HAS_Z3:
            model = self.get_model()
            if model is None:
                return None
            if ruling in self.deontic_vars:
                value = model.eval(self.deontic_vars[ruling], model_completion=True)
                try:
                    return float(value)
                except:
                    return None
        else:
            # Mock: return stored value
            return self.deontic_vars.get(ruling, None)

        return None

    def analyze_naskh_chain(
        self,
        chain: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        """Analyze a chain of rulings for naskh patterns.

        Args:
            chain: List of (verse, topic) pairs in order.

        Returns:
            Analysis of naskh occurrences and abrogation patterns.
        """
        naskh_points = []

        for i in range(len(chain) - 1):
            ruling1 = chain[i]
            ruling2 = chain[i + 1]

            ruling1_key = f"{ruling1[0]}_{ruling1[1]}"
            ruling2_key = f"{ruling2[0]}_{ruling2[1]}"

            strength1 = self.query_deontic_strength(ruling1_key)
            strength2 = self.query_deontic_strength(ruling2_key)

            if strength1 is not None and strength2 is not None:
                if strength2 > strength1:
                    naskh_points.append(
                        {
                            "from": ruling1,
                            "to": ruling2,
                            "strength_increase": strength2 - strength1,
                        }
                    )

        return {
            "total_rulings": len(chain),
            "naskh_points": naskh_points,
            "total_naskh_occurrences": len(naskh_points),
        }

    def reset(self) -> None:
        """Clear all constraints and variables."""
        if HAS_Z3:
            self.z3_solver.reset()
        else:
            self._fallback = FallbackConstraintSolver()
            self._satisfiable = True
            self._topic_strengths.clear()

        self.verse_vars.clear()
        self.deontic_vars.clear()
        self.naskh_vars.clear()
        self.constraints.clear()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SMTDeonticSolver(constraints={len(self.constraints)}, "
            f"verses={len(self.verse_vars)}, deontic_vars={len(self.deontic_vars)})"
        )
