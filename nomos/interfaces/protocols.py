"""
NOMOS Interface Protocols — Abstract contracts for all 5 layers.

These are the universal abstractions. Each layer's implementation
can be swapped without changing the pipeline contract.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


# ── Layer 1: Neural Foundation ─────────────────────────────────────────────

@dataclass
class EmbeddingResult:
    vector: Any          # numpy array or tensor
    dim: int
    model_name: str
    confidence: float


class NeuralFoundationProtocol(ABC):
    """Layer 1: Universal neural embedding and pattern recognition."""

    @abstractmethod
    def embed(self, input_data: Any, modality: str = "text") -> EmbeddingResult:
        """Encode any input modality into a vector representation."""
        ...

    @abstractmethod
    def predict(self, context: Any, task: str) -> Dict[str, Any]:
        """Run prediction for a given task."""
        ...


# ── Layer 2: Trimodal Reasoner ─────────────────────────────────────────────

@dataclass
class TriModalOutput:
    physical: Any        # World 1: empirical/data-grounded
    mental: Any          # World 2: conceptual/intentional
    abstract: Any        # World 3: formal/mathematical
    fusion: Any          # integrated result
    confidence: float


class TriModalProtocol(ABC):
    """
    Layer 2: Three-world neuro-symbolic reasoning.
    Generalizes ThreeWorldArchitecture beyond Islamic context.
    Popper's ontology: Physical (W1) / Mental (W2) / Abstract (W3).
    """

    @abstractmethod
    def reason(self, query: Any, mode: str = "hybrid") -> TriModalOutput:
        """Execute reasoning across all three worlds."""
        ...

    @abstractmethod
    def explain(self, result: TriModalOutput) -> str:
        """Generate human-readable explanation of reasoning chain."""
        ...


# ── Layer 3: Constraint Engine ─────────────────────────────────────────────

@dataclass
class ConstraintResult:
    satisfiable: bool
    assignments: Dict[str, Any]
    conflicts: List[str]
    resolution: Optional[str]
    proof: Optional[Any]


class ConstraintEngineProtocol(ABC):
    """
    Layer 3: Universal Z3 SMT constraint solving.
    Generalizes DeonticSolver / MaqasidOptimizer / NaskhTheory.
    Works for any normative system: law, contracts, policy, ethics.
    """

    @abstractmethod
    def add_norm(self, norm_id: str, norm_type: str, condition: Any,
                 strength: float = 1.0, jurisdiction: str = "universal") -> None:
        """
        Add an obligation, permission, or prohibition.
        norm_type: "obligatory" | "permitted" | "prohibited" | "recommended"
        """
        ...

    @abstractmethod
    def solve(self) -> ConstraintResult:
        """Solve the constraint system and return satisfiability result."""
        ...

    @abstractmethod
    def resolve_conflict(self, norm_a: str, norm_b: str,
                         strategy: str = "temporal") -> str:
        """
        Resolve conflict between two norms.
        Generalizes NaskhTheory (temporal supersession).
        strategy: "temporal" | "specificity" | "hierarchy" | "utility"
        """
        ...


# ── Layer 4: Value Alignment ───────────────────────────────────────────────

@dataclass
class AlignmentMetrics:
    phi: float                  # IIT Φ integrated information
    gwt_active: bool            # Global Workspace Theory ignition
    coherence_score: float      # Value-action coherence
    deception_risk: float       # Risk of misaligned behavior
    goal_stability: float       # Stability of objectives over time
    safety_grade: str           # "A+" | "A" | "B" | "C" | "F"


class ValueAlignmentProtocol(ABC):
    """
    Layer 4: Consciousness metrics and value alignment measurement.
    Generic interface for consciousness metrics across AI systems.
    """

    @abstractmethod
    def measure(self, system: Any, n_steps: int = 10) -> AlignmentMetrics:
        """Measure consciousness and value alignment of a system."""
        ...

    @abstractmethod
    def safety_report(self, metrics: AlignmentMetrics) -> Dict[str, Any]:
        """Generate a regulatory-ready safety report."""
        ...


# ── Layer 5: Formal Verification ───────────────────────────────────────────

@dataclass
class VerificationResult:
    verified: bool
    proof: Optional[Any]
    counterexample: Optional[Any]
    certificate_hash: Optional[str]
    duration_ms: float


class FormalVerifierProtocol(ABC):
    """
    Layer 5: Lean 4 formal verification as a service.
    Generalizes FrontierQu Lean proofs to any domain.
    """

    @abstractmethod
    def verify(self, spec: Any, implementation: Any) -> VerificationResult:
        """Verify an implementation against a formal specification."""
        ...

    @abstractmethod
    def export_certificate(self, result: VerificationResult,
                           fmt: str = "json") -> Dict[str, Any]:
        """Export a verifiable proof certificate."""
        ...


# ── Tradition Adapter ──────────────────────────────────────────────────────

class TraditionAdapter(ABC):
    """
    Pluggable tradition adapter.
    Each ethical/legal tradition (Islamic, utilitarian, deontological…)
    implements this interface to plug into NormativeEngine.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tradition name: 'islamic', 'utilitarian', 'kantian', etc."""
        ...

    @abstractmethod
    def load_norms(self, domain: str = "general") -> List[Dict[str, Any]]:
        """Return a list of norms for a given domain."""
        ...

    @abstractmethod
    def resolve_conflict(self, norm_a: Dict, norm_b: Dict) -> Dict:
        """Tradition-specific conflict resolution rule."""
        ...

    @abstractmethod
    def evaluate(self, action: Any, context: Any) -> float:
        """Score an action 0.0–1.0 under this tradition."""
        ...
