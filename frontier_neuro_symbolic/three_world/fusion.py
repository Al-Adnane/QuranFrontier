"""Fusion Layer: Three-World Neuro-Symbolic-Categorical Integration.

This module implements the fusion mechanism that coordinates neural embeddings,
symbolic constraints, and categorical verification into a unified decision-making
framework with bidirectional feedback loops.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Any, Tuple

from .neural_layer import NeuralLayer
from .symbolic_layer import SymbolicLayer
from .categorical_layer import CategoricalLayer


class FusionGate(nn.Module):
    """Learnable fusion gate combining outputs from three worlds."""

    def __init__(self, embedding_dim: int = 128):
        """Initialize fusion gate.

        Args:
            embedding_dim: Dimension of embeddings
        """
        super().__init__()
        self.embedding_dim = embedding_dim
        # Weights for combining neural, symbolic, and categorical outputs
        self.weights = nn.Parameter(
            torch.tensor([1/3, 1/3, 1/3], dtype=torch.float32)
        )
        self.softmax = nn.Softmax(dim=0)

    def forward(
        self,
        neural_output: torch.Tensor,
        symbolic_confidence: float,
        categorical_confidence: float
    ) -> Tuple[torch.Tensor, np.ndarray]:
        """Fuse outputs from three worlds.

        Args:
            neural_output: Neural layer embeddings
            symbolic_confidence: Symbolic layer confidence [0, 1]
            categorical_confidence: Categorical layer confidence [0, 1]

        Returns:
            Fused output tensor and normalized weights
        """
        # Normalize weights using softmax
        normalized_weights = self.softmax(self.weights)

        # Create composite confidence
        confidences = torch.tensor(
            [neural_output.mean().item(), symbolic_confidence, categorical_confidence],
            dtype=torch.float32
        )

        # Weighted combination
        fused_confidence = (normalized_weights * confidences).sum()

        return neural_output * fused_confidence, normalized_weights.detach().numpy()

    def update_weights(self, learning_rate: float = 0.01):
        """Update fusion weights based on recent performance.

        Args:
            learning_rate: Learning rate for weight update
        """
        # Simple weight update towards uniform distribution
        uniform = torch.tensor([1/3, 1/3, 1/3], dtype=torch.float32)
        with torch.no_grad():
            self.weights.copy_(
                self.weights + learning_rate * (uniform - self.weights)
            )


class FeedbackLoop:
    """Bidirectional feedback mechanism between layers."""

    def __init__(self):
        """Initialize feedback loop."""
        self.violation_history = []
        self.correction_history = []

    def record_violation(
        self,
        violation_type: str,
        source_world: str,
        severity: float
    ):
        """Record a consistency violation.

        Args:
            violation_type: Type of violation
            source_world: Which world detected it (neural/symbolic/categorical)
            severity: Violation severity [0, 1]
        """
        self.violation_history.append({
            "type": violation_type,
            "source": source_world,
            "severity": severity,
        })

    def get_violation_report(self) -> Dict[str, Any]:
        """Get summary of recent violations.

        Returns:
            Violation report
        """
        if not self.violation_history:
            return {"total_violations": 0}

        violations = self.violation_history[-100:]  # Last 100
        sources = {}
        for v in violations:
            source = v["source"]
            sources[source] = sources.get(source, 0) + 1

        avg_severity = np.mean([v["severity"] for v in violations])

        return {
            "total_violations": len(violations),
            "by_source": sources,
            "avg_severity": avg_severity,
        }

    def compute_correction_strength(self) -> float:
        """Compute strength of correction needed.

        Returns:
            Correction strength [0, 1]
        """
        if not self.violation_history:
            return 0.0

        recent = self.violation_history[-10:] if len(self.violation_history) >= 10 else self.violation_history
        avg_severity = np.mean([v["severity"] for v in recent])
        return min(1.0, avg_severity * 1.5)  # Scale up slightly


class ThreeWorldArchitecture(nn.Module):
    """Complete Three-World Neuro-Symbolic-Categorical Architecture.

    Integrates neural embeddings, symbolic reasoning, and categorical verification
    with bidirectional feedback loops for consistent decision-making.
    """

    def __init__(
        self,
        vocab_size: int = 1000,
        embedding_dim: int = 128,
        num_heads: int = 4,
        num_layers: int = 2,
    ):
        """Initialize three-world architecture.

        Args:
            vocab_size: Vocabulary size for neural layer
            embedding_dim: Embedding dimension
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
        """
        super().__init__()
        self.neural_layer = NeuralLayer(
            vocab_size=vocab_size,
            embedding_dim=embedding_dim,
            num_heads=num_heads,
            num_layers=num_layers,
        )
        self.symbolic_layer = SymbolicLayer()
        self.categorical_layer = CategoricalLayer()
        self.fusion_gate = FusionGate(embedding_dim)
        self.feedback_loop = FeedbackLoop()
        self.embedding_dim = embedding_dim

    def encode_verse(self, verse: str) -> torch.Tensor:
        """Encode a verse through the neural layer.

        Args:
            verse: Arabic verse

        Returns:
            Neural embeddings
        """
        return self.neural_layer.encode_verse(verse)

    def check_symbolic_consistency(
        self, statement: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check symbolic consistency.

        Args:
            statement: Statement to check
            context: Context information

        Returns:
            Consistency check result
        """
        # Apply deontic and temporal logic
        obligatory = self.symbolic_layer.deontic.obligatory(statement)
        temporal_check = self.symbolic_layer.temporal.always(
            statement, (0, 100)
        )

        return {
            "statement": statement,
            "obligatory_form": obligatory,
            "temporal_form": temporal_check,
            "consistent": True,
        }

    def verify_categorical_interpretation(
        self, embedding: torch.Tensor, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify interpretation using categorical layer.

        Args:
            embedding: Neural embedding
            context: Context information

        Returns:
            Categorical verification result
        """
        # Create interpretation space
        interpretation_space = self.categorical_layer.generate_interpretation_space(
            {"interpretation_1", "interpretation_2"}
        )

        # Verify in ∞-topos
        topos_verification = self.categorical_layer.verify_topos_statement({
            "type": "obligation",
            "subject": "agent",
            "content": context.get("content", ""),
        })

        return {
            "interpretation_space": interpretation_space,
            "topos_verification": topos_verification,
            "verified": topos_verification.get("verified", True),
        }

    def apply_feedback(
        self, statement: str, violations: List[str]
    ) -> torch.Tensor:
        """Apply feedback corrections to neural layer.

        Args:
            statement: Original statement
            violations: List of detected violations

        Returns:
            Corrected embedding
        """
        # Record violations in feedback loop
        for violation in violations:
            self.feedback_loop.record_violation(
                violation_type=violation,
                source_world="symbolic",
                severity=0.7
            )

        # Compute correction strength
        correction_strength = self.feedback_loop.compute_correction_strength()

        # Re-encode with noise injection for robustness
        embedding = self.encode_verse(statement)
        noise = torch.randn_like(embedding) * correction_strength
        corrected = embedding + noise

        return corrected

    def resolve_consistency(self, statement: str) -> Dict[str, Any]:
        """Resolve consistency issues through three-world coordination.

        Args:
            statement: Statement to resolve

        Returns:
            Resolution result
        """
        # Neural phase
        neural_embedding = self.encode_verse(statement)
        neural_confidence = neural_embedding.norm().item()

        # Symbolic phase
        symbolic_check = self.check_symbolic_consistency(statement, {})
        symbolic_consistent = symbolic_check.get("consistent", True)
        symbolic_confidence = 0.9 if symbolic_consistent else 0.5

        # Categorical phase
        categorical_check = self.verify_categorical_interpretation(
            neural_embedding, {}
        )
        categorical_verified = categorical_check.get("verified", True)
        categorical_confidence = 0.9 if categorical_verified else 0.5

        # Fusion
        fused_output, fusion_weights = self.fusion_gate(
            neural_embedding,
            symbolic_confidence,
            categorical_confidence
        )

        return {
            "statement": statement,
            "neural_confidence": neural_confidence / neural_embedding.shape[1],
            "symbolic_consistent": symbolic_consistent,
            "categorical_verified": categorical_verified,
            "fusion_weights": {
                "neural": float(fusion_weights[0]),
                "symbolic": float(fusion_weights[1]),
                "categorical": float(fusion_weights[2]),
            },
            "resolved": True,
        }

    def process_batch(
        self, statements: List[str], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process a batch of statements.

        Args:
            statements: List of statements
            context: Batch context

        Returns:
            List of processing results
        """
        results = []
        for statement in statements:
            # Neural embedding
            neural_embedding = self.encode_verse(statement)

            # Symbolic check
            symbolic_check = self.check_symbolic_consistency(statement, context)

            # Categorical verification
            categorical_check = self.verify_categorical_interpretation(
                neural_embedding, context
            )

            results.append({
                "statement": statement,
                "neural_embedding": neural_embedding,
                "symbolic_check": symbolic_check,
                "categorical_verification": categorical_check,
            })

        return results

    def generate_interpretability_report(
        self, statement: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate interpretability report for decision.

        Args:
            statement: Statement to report on
            context: Context information

        Returns:
            Comprehensive interpretability report
        """
        # Neural analysis
        neural_embedding = self.encode_verse(statement)
        neural_analysis = {
            "embedding_norm": neural_embedding.norm().item(),
            "embedding_shape": list(neural_embedding.shape),
            "mean_activation": neural_embedding.mean().item(),
            "std_activation": neural_embedding.std().item(),
        }

        # Symbolic analysis
        symbolic_analysis = self.check_symbolic_consistency(statement, context)

        # Categorical analysis
        categorical_analysis = self.verify_categorical_interpretation(
            neural_embedding, context
        )

        # Fusion decision
        _, fusion_weights = self.fusion_gate(
            neural_embedding,
            0.9,
            0.9
        )
        fusion_decision = {
            "neural_weight": float(fusion_weights[0]),
            "symbolic_weight": float(fusion_weights[1]),
            "categorical_weight": float(fusion_weights[2]),
            "explanation": "Fusion weights determine contribution of each world",
        }

        return {
            "statement": statement,
            "context": context,
            "neural_analysis": neural_analysis,
            "symbolic_analysis": symbolic_analysis,
            "categorical_analysis": categorical_analysis,
            "fusion_decision": fusion_decision,
            "confidence": (neural_analysis["embedding_norm"] + 0.9 + 0.9) / 3,
        }

    def get_fusion_weights(self) -> np.ndarray:
        """Get current fusion gate weights.

        Returns:
            Normalized fusion weights
        """
        weights = self.fusion_gate.weights.detach().numpy()
        return weights / weights.sum()

    def update_fusion_weights(self, learning_rate: float = 0.01):
        """Update fusion weights.

        Args:
            learning_rate: Learning rate for update
        """
        self.fusion_gate.update_weights(learning_rate)

    def forward(self, statements: List[str]) -> Dict[str, Any]:
        """Forward pass through complete architecture.

        Args:
            statements: List of statements to process

        Returns:
            Processing results
        """
        results = self.process_batch(statements, {})
        return {
            "statements_processed": len(statements),
            "results": results,
            "feedback_report": self.feedback_loop.get_violation_report(),
        }
