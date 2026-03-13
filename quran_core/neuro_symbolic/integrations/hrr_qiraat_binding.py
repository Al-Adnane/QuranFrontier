"""HRR-Qiraat Binding — Holographic Memory for 7 Canonical Readings.

Binds the 7 Qiraat reading variants into a Holographic Reduced Representation
(HRR) memory, enabling content-addressable retrieval of readings by semantic
query. Each reading is encoded as a holographic vector and bound with its
reader identity, allowing:

- Superposition storage (all 7 readings in one distributed vector)
- Content-addressable retrieval by partial semantic cue
- Associative recall (query one reading, retrieve related variants)

Cross-subsystem integration:
  frontier_models/wild/holographic_memory.py  (HRR bind/unbind/store/retrieve)
  frontier_neuro_symbolic/quantum_qiraat/hilbert_space.py  (QiraatHilbertSpace)
"""

import sys
import os
import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Resolve imports across subsystem boundaries
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _project_root)

from frontier_models.wild.holographic_memory import (
    HolographicMemory,
    HolographicEncoder,
    MemoryTrace,
)
from frontier_neuro_symbolic.quantum_qiraat.hilbert_space import (
    QiraatHilbertSpace,
    SuperpositionState,
    RecitationRuleTransform,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ReadingVariant:
    """A single Qiraat reading variant."""
    reader_index: int          # 0-6 for the 7 canonical readers
    reader_name: str           # e.g. "Asim (Hafs)"
    text: str                  # Arabic text of this reading
    semantic_embedding: Optional[torch.Tensor] = None  # Dense vector
    phonetic_features: Dict[str, float] = field(default_factory=dict)


@dataclass
class BoundReadingSet:
    """Result of binding all 7 readings into holographic memory."""
    superposition_vector: torch.Tensor     # Single HRR vector encoding all 7
    reader_role_vectors: Dict[int, torch.Tensor]  # Role vectors per reader
    quantum_state: Optional[SuperpositionState] = None  # Parallel quantum repr
    binding_fidelity: float = 0.0          # Quality metric [0, 1]


@dataclass
class RetrievalResult:
    """Result of retrieving a reading from holographic memory."""
    reader_index: int
    reader_name: str
    similarity: float
    confidence: float
    retrieved_vector: torch.Tensor


# ---------------------------------------------------------------------------
# Main integration class
# ---------------------------------------------------------------------------

class QiraatHolographicBinding:
    """Bind 7 Qiraat variants into HRR holographic memory.

    Architecture:
        1. Each reader gets a fixed random *role vector* (identity key).
        2. Each reading's semantic embedding is *bound* (circular convolution)
           with its reader role vector.
        3. All 7 bound pairs are *superposed* (summed) into one distributed
           holographic vector.
        4. Retrieval: unbind a role vector from the superposition to recover
           the approximate semantic embedding of that reading.

    The parallel QiraatHilbertSpace representation maintains a quantum
    superposition of amplitudes that can be measured / collapsed.
    """

    def __init__(
        self,
        holographic_dim: int = 1024,
        semantic_dim: int = 768,
        num_readers: int = 7,
    ):
        self.holographic_dim = holographic_dim
        self.semantic_dim = semantic_dim
        self.num_readers = num_readers

        # HRR subsystem
        self.encoder = HolographicEncoder(
            item_dim=semantic_dim,
            holographic_dim=holographic_dim,
        )
        self.memory = HolographicMemory(
            holographic_dim=holographic_dim,
            capacity=num_readers * 10,  # room for multiple verse-sets
        )

        # Quantum Qiraat subsystem
        self.hilbert_space = QiraatHilbertSpace(dimension=num_readers)
        self.recitation_transform = RecitationRuleTransform(self.hilbert_space)

        # Fixed random role vectors (one per canonical reader)
        torch.manual_seed(42)
        self._role_vectors: Dict[int, torch.Tensor] = {
            i: F.normalize(torch.randn(holographic_dim), dim=0)
            for i in range(num_readers)
        }

        # Storage of bound sets keyed by verse_id
        self._bound_sets: Dict[str, BoundReadingSet] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encode_reading(
        self,
        variant: ReadingVariant,
    ) -> torch.Tensor:
        """Encode a single reading variant into holographic space.

        Steps:
            1. Project semantic embedding through HolographicEncoder.
            2. Bind with the reader's role vector via circular convolution.

        Args:
            variant: A ReadingVariant with a populated semantic_embedding.

        Returns:
            Bound holographic vector (holographic_dim,).
        """
        if variant.semantic_embedding is None:
            raise ValueError(
                f"ReadingVariant for reader {variant.reader_name} has no semantic_embedding"
            )

        # Project to holographic space
        with torch.no_grad():
            projected = self.encoder(variant.semantic_embedding.unsqueeze(0)).squeeze(0)

        # Bind with role vector (circular convolution via FFT)
        role = self._role_vectors[variant.reader_index]
        bound = self.memory.bind(projected, role)
        return bound

    def bind_readings(
        self,
        verse_id: str,
        variants: List[ReadingVariant],
    ) -> BoundReadingSet:
        """Bind up to 7 reading variants into a single holographic superposition.

        Also builds the parallel quantum superposition in QiraatHilbertSpace
        with amplitudes proportional to each reading's embedding norm.

        Args:
            verse_id: Unique identifier for the verse.
            variants: List of ReadingVariant (one per reader, up to 7).

        Returns:
            BoundReadingSet with the superposed holographic vector.
        """
        if len(variants) > self.num_readers:
            raise ValueError(
                f"Expected at most {self.num_readers} variants, got {len(variants)}"
            )

        bound_vectors: List[torch.Tensor] = []
        role_vectors: Dict[int, torch.Tensor] = {}
        amplitudes = np.zeros(self.num_readers, dtype=complex)

        for variant in variants:
            bound = self.encode_reading(variant)
            bound_vectors.append(bound)
            role_vectors[variant.reader_index] = self._role_vectors[variant.reader_index]

            # Amplitude for quantum representation ~ norm of semantic embedding
            norm = variant.semantic_embedding.norm().item() if variant.semantic_embedding is not None else 1.0
            amplitudes[variant.reader_index] = norm

        # Superpose all bound vectors
        superposition = torch.stack(bound_vectors).sum(dim=0)

        # Store in holographic memory for later content-addressable retrieval
        with torch.no_grad():
            self.memory.store(superposition)

        # Build quantum superposition state
        quantum_state = self.hilbert_space.create_superposition(amplitudes)

        # Compute binding fidelity via round-trip test on first variant
        fidelity = self._compute_fidelity(superposition, variants, role_vectors)

        result = BoundReadingSet(
            superposition_vector=superposition,
            reader_role_vectors=role_vectors,
            quantum_state=quantum_state,
            binding_fidelity=fidelity,
        )
        self._bound_sets[verse_id] = result
        return result

    def retrieve_by_similarity(
        self,
        query_embedding: torch.Tensor,
        top_k: int = 3,
    ) -> List[RetrievalResult]:
        """Retrieve readings from holographic memory by semantic similarity.

        Uses content-addressable retrieval: the query embedding is projected
        into holographic space and compared against all stored superpositions.
        Then each stored superposition is unbound with every role vector to
        find the best-matching reader.

        Args:
            query_embedding: Semantic query vector (semantic_dim,).
            top_k: Number of results to return.

        Returns:
            List of RetrievalResult sorted by similarity.
        """
        with torch.no_grad():
            query_holo = self.encoder(query_embedding.unsqueeze(0)).squeeze(0)

        # Retrieve from holographic memory
        traces: List[MemoryTrace] = self.memory.retrieve(query_holo, k=top_k)

        results: List[RetrievalResult] = []
        reader_names = QiraatHilbertSpace.CANONICAL_READERS

        for trace in traces:
            # For each retrieved superposition, unbind each role to find
            # which reader's content best matches the query
            best_sim = -1.0
            best_reader = 0
            for reader_idx, role in self._role_vectors.items():
                unbound = self.memory.unbind(trace.retrieved, role)
                sim = F.cosine_similarity(
                    query_holo.unsqueeze(0),
                    unbound.unsqueeze(0),
                ).item()
                if sim > best_sim:
                    best_sim = sim
                    best_reader = reader_idx

            reader_name = reader_names[best_reader] if best_reader < len(reader_names) else f"Reader_{best_reader}"
            results.append(RetrievalResult(
                reader_index=best_reader,
                reader_name=reader_name,
                similarity=best_sim,
                confidence=trace.confidence,
                retrieved_vector=trace.retrieved,
            ))

        # Sort by similarity descending
        results.sort(key=lambda r: r.similarity, reverse=True)
        return results[:top_k]

    def retrieve_reader(
        self,
        verse_id: str,
        reader_index: int,
    ) -> Optional[torch.Tensor]:
        """Retrieve a specific reader's content from a bound verse set.

        Unbinds the reader's role vector from the stored superposition.

        Args:
            verse_id: Verse identifier.
            reader_index: 0-6 index of the canonical reader.

        Returns:
            Approximate semantic vector for that reader's reading, or None.
        """
        bound_set = self._bound_sets.get(verse_id)
        if bound_set is None:
            return None

        role = self._role_vectors.get(reader_index)
        if role is None:
            return None

        return self.memory.unbind(bound_set.superposition_vector, role)

    def measure_quantum_state(self, verse_id: str) -> Optional[int]:
        """Collapse the quantum Qiraat superposition for a verse.

        Measures the parallel QiraatHilbertSpace state, returning the
        index of the reader that the measurement collapses to.

        Args:
            verse_id: Verse identifier.

        Returns:
            Reader index (0-6) or None if verse not bound.
        """
        bound_set = self._bound_sets.get(verse_id)
        if bound_set is None or bound_set.quantum_state is None:
            return None
        return bound_set.quantum_state.measure(self.hilbert_space)

    def apply_recitation_rule(
        self,
        verse_id: str,
        phonetic_rotation_angle: float = 0.1,
    ) -> Optional[SuperpositionState]:
        """Apply a recitation rule (unitary transform) to the quantum state.

        Uses RecitationRuleTransform.phonetic_rotation to rotate the
        Qiraat superposition in Hilbert space.

        Args:
            verse_id: Verse identifier.
            phonetic_rotation_angle: Rotation angle in radians.

        Returns:
            Transformed SuperpositionState or None.
        """
        bound_set = self._bound_sets.get(verse_id)
        if bound_set is None or bound_set.quantum_state is None:
            return None

        U = self.recitation_transform.phonetic_rotation(phonetic_rotation_angle)
        new_state = bound_set.quantum_state.apply_unitary(U)
        bound_set.quantum_state = new_state
        return new_state

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_fidelity(
        self,
        superposition: torch.Tensor,
        variants: List[ReadingVariant],
        role_vectors: Dict[int, torch.Tensor],
    ) -> float:
        """Compute round-trip binding fidelity.

        Unbinds each reader's role from the superposition and measures
        cosine similarity to the original projected embedding.
        """
        if not variants:
            return 0.0

        sims = []
        for variant in variants:
            if variant.semantic_embedding is None:
                continue
            with torch.no_grad():
                original = self.encoder(variant.semantic_embedding.unsqueeze(0)).squeeze(0)
            role = role_vectors.get(variant.reader_index)
            if role is None:
                continue
            recovered = self.memory.unbind(superposition, role)
            sim = F.cosine_similarity(
                original.unsqueeze(0),
                recovered.unsqueeze(0),
            ).item()
            sims.append(max(0.0, sim))

        return float(np.mean(sims)) if sims else 0.0

    def get_metrics(self) -> Dict[str, float]:
        """Return integration metrics."""
        fidelities = [
            bs.binding_fidelity for bs in self._bound_sets.values()
        ]
        return {
            "bound_verses": len(self._bound_sets),
            "memory_slots_used": self.memory.memory_count,
            "mean_binding_fidelity": float(np.mean(fidelities)) if fidelities else 0.0,
            "holographic_dim": self.holographic_dim,
            "num_readers": self.num_readers,
        }
