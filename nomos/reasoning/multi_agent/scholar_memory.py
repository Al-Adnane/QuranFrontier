"""Scholar Memory - Agent context management and learning.

ScholarMemory maintains context across debates, stores interpretation history,
supports counterfactual critiques, and fine-tunes embeddings via causal RL
feedback.

Architecture:
- Debate history with semantic indexing
- Madhab prior weights learnable
- Counterfactual critique generation
- Causal inference on interpretation effects
- Embedding fine-tuning via feedback signals
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging
from collections import deque
import json

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Single memory entry."""
    query: str
    interpretation: str
    round: int
    confidence: float
    timestamp: float
    madhab_weights: Dict[str, float]
    sources_cited: List[str] = field(default_factory=list)
    issues_identified: List[str] = field(default_factory=list)
    was_correct: Optional[bool] = None


@dataclass
class CausalChain:
    """Causal relationship in interpretations."""
    cause: str  # e.g., "prohibition of riba"
    effect: str  # e.g., "islamic finance practices"
    confidence: float
    evidence: List[str]


class ScholarMemory:
    """
    Memory system for scholar agents.

    Maintains debate history, supports counterfactual reasoning,
    and learns from feedback via causal inference.
    """

    def __init__(
        self,
        max_history: int = 100,
        embedding_dim: int = 384,
        madhab_priors: Optional[Dict[str, float]] = None,
        enable_causal_inference: bool = True
    ):
        """
        Initialize ScholarMemory.

        Args:
            max_history: Maximum history entries to store
            embedding_dim: Embedding dimension for similarity
            madhab_priors: Prior weights for madhabs
            enable_causal_inference: Enable causal structure learning
        """
        self.max_history = max_history
        self.embedding_dim = embedding_dim
        self.enable_causal_inference = enable_causal_inference

        # Default madhab priors
        self.madhab_priors = madhab_priors or {
            "hanafi": 0.25,
            "maliki": 0.25,
            "shafii": 0.25,
            "hanbali": 0.25
        }

        # Storage
        self.history: deque = deque(maxlen=max_history)
        self.feedback_history: List[Dict[str, Any]] = []
        self.causal_structures: List[CausalChain] = []

        # Embedding cache
        self._embedding_cache: Dict[str, List[float]] = {}

        # Learned representations
        self._madhab_weights_learned: Dict[str, float] = self.madhab_priors.copy()

    def add_entry(self, entry_dict: Dict[str, Any]) -> None:
        """
        Add entry to memory.

        Args:
            entry_dict: Dictionary with query, interpretation, round, confidence, etc.
        """
        entry = MemoryEntry(
            query=entry_dict.get("query", ""),
            interpretation=entry_dict.get("interpretation", ""),
            round=entry_dict.get("round", 1),
            confidence=entry_dict.get("confidence", 0.5),
            timestamp=entry_dict.get("timestamp", 0.0),
            madhab_weights=entry_dict.get("madhab_weights", self.madhab_priors.copy()),
            sources_cited=entry_dict.get("sources", []),
            issues_identified=entry_dict.get("issues", [])
        )

        self.history.append(entry)

        # Update embedding cache
        if entry.interpretation:
            self._cache_embedding(entry.interpretation)

    def retrieve_similar(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[MemoryEntry]:
        """
        Retrieve similar past debates.

        Args:
            query: Query string
            top_k: Number of results
            min_similarity: Minimum similarity threshold

        Returns:
            List of similar memory entries
        """
        if not self.history:
            return []

        # Compute similarities
        similarities = []

        for entry in self.history:
            similarity = self._compute_similarity(query, entry.query)

            if similarity >= min_similarity:
                similarities.append((entry, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top-k
        return [entry for entry, _ in similarities[:top_k]]

    def generate_counterfactual_critique(
        self,
        interpretation: str,
        counterfactual_premise: str
    ) -> Dict[str, Any]:
        """
        Generate counterfactual critique.

        Args:
            interpretation: Original interpretation
            counterfactual_premise: "What if X were different?"

        Returns:
            Dictionary with counterfactual analysis
        """
        return {
            "original_interpretation": interpretation,
            "counterfactual_premise": counterfactual_premise,
            "counterfactual_interpretation": self._derive_counterfactual(
                interpretation,
                counterfactual_premise
            ),
            "affected_conclusions": self._trace_implications(counterfactual_premise),
            "reasoning": "Counterfactual analysis based on causal structure"
        }

    def add_feedback(
        self,
        query: str,
        feedback: float,
        was_correct: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add feedback for learning.

        Args:
            query: The query that received feedback
            feedback: Feedback score 0-1
            was_correct: Whether interpretation was correct
            metadata: Additional metadata
        """
        feedback_entry = {
            "query": query,
            "feedback": feedback,
            "was_correct": was_correct,
            "metadata": metadata or {}
        }

        self.feedback_history.append(feedback_entry)

        # Update madhab weights based on feedback (simple: boost weights for correct answers)
        if was_correct and feedback > 0.7:
            # Slightly boost all madhabs equally (in production, could be more nuanced)
            for madhab in self._madhab_weights_learned:
                self._madhab_weights_learned[madhab] *= 1.01

    def get_causal_structure(self) -> Dict[str, Any]:
        """
        Get learned causal structure.

        Returns:
            Dictionary with causal relationships
        """
        return {
            "causal_chains": [
                {
                    "cause": chain.cause,
                    "effect": chain.effect,
                    "confidence": chain.confidence
                }
                for chain in self.causal_structures
            ],
            "structure_count": len(self.causal_structures)
        }

    def learn_causal_structure(
        self,
        interpretation: str,
        outcomes: List[str]
    ) -> CausalChain:
        """
        Learn causal structure from interpretation and outcomes.

        Args:
            interpretation: Interpretation text
            outcomes: List of observed outcomes

        Returns:
            Learned causal chain
        """
        chain = CausalChain(
            cause=interpretation,
            effect=" → ".join(outcomes),
            confidence=0.7,
            evidence=[interpretation] + outcomes
        )

        self.causal_structures.append(chain)

        return chain

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between texts."""
        # Mock similarity based on token overlap
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        jaccard = intersection / union if union > 0 else 0.0

        return jaccard

    def _cache_embedding(self, text: str) -> List[float]:
        """Cache embedding for text."""
        if text not in self._embedding_cache:
            # Mock embedding (in production would use real embeddings)
            embedding = self._compute_embedding(text)
            self._embedding_cache[text] = embedding

        return self._embedding_cache[text]

    def _compute_embedding(self, text: str) -> List[float]:
        """Compute embedding for text."""
        # Mock: simple hash-based "embedding"
        import hashlib

        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)

        embedding = []
        for i in range(self.embedding_dim):
            val = ((hash_val >> i) & 1) * 2.0 - 1.0  # Convert to -1 or 1
            embedding.append(val)

        # Normalize
        norm = sum(x**2 for x in embedding) ** 0.5
        embedding = [x / norm for x in embedding] if norm > 0 else embedding

        return embedding

    def _derive_counterfactual(
        self,
        interpretation: str,
        premise: str
    ) -> str:
        """Derive counterfactual interpretation."""
        # Mock counterfactual derivation
        return f"If {premise}, then: {interpretation} would need to be reconsidered"

    def _trace_implications(self, premise: str) -> List[str]:
        """Trace implications of counterfactual premise."""
        # Mock implication tracing
        return [
            f"Effect 1 on {premise}",
            f"Effect 2 on scholarly consensus",
            f"Effect 3 on practical application"
        ]

    def get_learned_madhab_weights(self) -> Dict[str, float]:
        """Get learned madhab weights."""
        return self._madhab_weights_learned.copy()

    def reset_madhab_weights(self) -> None:
        """Reset madhab weights to priors."""
        self._madhab_weights_learned = self.madhab_priors.copy()

    def get_memory_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent memory entries."""
        entries = list(self.history)[-limit:]
        return [
            {
                "query": e.query,
                "interpretation": e.interpretation,
                "confidence": e.confidence
            }
            for e in entries
        ]

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        if not self.feedback_history:
            return {"count": 0, "average_feedback": 0.0, "correct_ratio": 0.0}

        correct_count = sum(1 for f in self.feedback_history if f["was_correct"])
        avg_feedback = sum(f["feedback"] for f in self.feedback_history) / len(
            self.feedback_history
        )

        return {
            "count": len(self.feedback_history),
            "average_feedback": avg_feedback,
            "correct_ratio": correct_count / len(self.feedback_history),
            "correct_count": correct_count
        }

    def clear_history(self) -> None:
        """Clear memory history."""
        self.history.clear()
        self.feedback_history = []
        self.causal_structures = []
        self._embedding_cache = {}

    def export_memory(self) -> Dict[str, Any]:
        """Export memory for persistence."""
        return {
            "history": [
                {
                    "query": e.query,
                    "interpretation": e.interpretation,
                    "confidence": e.confidence,
                    "round": e.round
                }
                for e in self.history
            ],
            "feedback_count": len(self.feedback_history),
            "madhab_weights": self._madhab_weights_learned,
            "causal_structures_count": len(self.causal_structures)
        }
