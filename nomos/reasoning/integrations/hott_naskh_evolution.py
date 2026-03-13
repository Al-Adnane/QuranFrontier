"""HoTT-Naskh Type Evolution — Abrogation as Homotopy Type Evolution.

Encodes Islamic abrogation (naskh) as type evolution in Homotopy Type Theory.
When a verse abrogates another, this is modeled as:

  1. The abrogated verse is a HoTT type at universe level N.
  2. The abrogating verse is a HoTT type at universe level N+1.
  3. A UnivalenceWitness proves the two types are equivalent (but evolved).
  4. The NaskhSolver provides the abrogation probability and homological memory.
  5. The path from old type to new type IS the abrogation event.

This bridges:
  frontier_qu_v5/architecture/self_modifying_hott.py  (SelfModifyingHoTT, HoTTType, UnivalenceWitness)
  frontier_neuro_symbolic/dag_naskh/naskh_solver.py   (NaskhSolver)
"""

import sys
import os
import time
import hashlib
import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _project_root)
sys.path.insert(0, os.path.join(_project_root, "frontier_qu_v5"))

try:
    from frontier_qu_v5.architecture.self_modifying_hott import (
        SelfModifyingHoTT,
        HoTTType,
        PathEquality,
        UnivalenceWitness,
    )
    _HAS_HOTT = True
except ImportError:
    _HAS_HOTT = False
    SelfModifyingHoTT = None
    HoTTType = None
    PathEquality = None
    UnivalenceWitness = None

try:
    from frontier_neuro_symbolic.dag_naskh.naskh_solver import NaskhSolver
    _HAS_NASKH = True
except ImportError:
    _HAS_NASKH = False
    NaskhSolver = None


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class NaskhEvolutionEvent:
    """Record of a single naskh evolution in the type universe."""
    abrogated_verse_id: str
    abrogating_verse_id: str
    abrogation_probability: float
    confidence: float
    hott_path: PathEquality
    univalence_witness: UnivalenceWitness
    homological_memory: Optional[torch.Tensor] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class TypeEvolutionChain:
    """A chain of naskh evolutions forming a directed path in the type graph."""
    verse_chain: List[str]               # Ordered list of verse IDs
    evolution_events: List[NaskhEvolutionEvent]
    total_coherence: float               # Product of univalence coherences
    chain_universe_level: int            # Highest universe level reached
    winding_number: int                  # Strange loops detected


# ---------------------------------------------------------------------------
# Main integration class
# ---------------------------------------------------------------------------

class NaskhTypeEvolution:
    """Encode abrogation (naskh) as HoTT type evolution with univalence witnesses.

    Architecture:
        1. Each Quranic verse is registered as a HoTTType in the self-modifying
           type universe.
        2. When naskh is detected (via NaskhSolver), the abrogated type evolves:
           its attributes are updated, and a PathEquality is asserted.
        3. A UnivalenceWitness is created proving the old and new types are
           equivalent (abrogation preserves semantic continuity even as rulings change).
        4. The NaskhSolver's homological memory is stored as an attribute of
           the evolved type, preserving the "trace" of abrogation.
        5. Strange loops in the type graph correspond to circular abrogation
           chains (which are theologically significant).

    Parameters:
        embedding_dim: Dimension of verse embeddings for NaskhSolver.
        stack_dimension: Algebraic dimension for derived stack.
        semantic_dim: Semantic space dimension.
        max_universe_levels: Maximum HoTT universe depth.
    """

    def __init__(
        self,
        embedding_dim: int = 128,
        stack_dimension: int = 4,
        semantic_dim: int = 64,
        max_universe_levels: int = 10,
    ):
        self.embedding_dim = embedding_dim
        self.semantic_dim = semantic_dim

        # HoTT type universe (from frontier_qu_v5)
        self.hott = SelfModifyingHoTT(max_universe_levels=max_universe_levels)

        # Naskh solver (from frontier_neuro_symbolic/dag_naskh)
        self.naskh_solver = NaskhSolver(
            embedding_dim=embedding_dim,
            stack_dimension=stack_dimension,
            semantic_dim=semantic_dim,
        )

        # Verse registry: verse_id -> (HoTTType name, embedding)
        self._verse_registry: Dict[str, Tuple[str, torch.Tensor]] = {}

        # Evolution history
        self.evolution_events: List[NaskhEvolutionEvent] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_verse(
        self,
        verse_id: str,
        embedding: torch.Tensor,
        revelation_order: int = 0,
        deontic_category: str = "permissible",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HoTTType:
        """Register a verse as a HoTT type in the universe.

        Args:
            verse_id: Unique verse identifier (e.g., "2:219").
            embedding: Dense embedding vector of shape (embedding_dim,).
            revelation_order: Temporal order of revelation.
            deontic_category: Islamic ruling category (obligatory, forbidden, etc.).
            metadata: Additional attributes.

        Returns:
            The registered HoTTType.
        """
        type_name = f"verse_{verse_id}"
        attrs = {
            "verse_id": verse_id,
            "revelation_order": revelation_order,
            "deontic_category": deontic_category,
            "embedding_norm": float(embedding.norm().item()),
            "is_abrogated": False,
            "abrogated_by": None,
            **(metadata or {}),
        }

        # Universe level corresponds to revelation order (later = higher)
        level = min(revelation_order, self.hott.max_levels - 1)
        hott_type = self.hott.register_type(type_name, level=level, attributes=attrs)

        self._verse_registry[verse_id] = (type_name, embedding)
        return hott_type

    def detect_and_evolve(
        self,
        verse_id_1: str,
        verse_id_2: str,
        threshold: float = 0.5,
    ) -> Optional[NaskhEvolutionEvent]:
        """Detect naskh between two verses and evolve the type universe.

        If verse_2 abrogates verse_1 (probability > threshold):
            1. NaskhSolver computes abrogation probability and confidence.
            2. The abrogated type evolves (attributes updated).
            3. A PathEquality is asserted from old version to new.
            4. A UnivalenceWitness proves equivalence.
            5. Homological memory is computed and stored.

        Args:
            verse_id_1: Candidate abrogated verse.
            verse_id_2: Candidate abrogating verse.
            threshold: Minimum probability to trigger evolution.

        Returns:
            NaskhEvolutionEvent if abrogation detected, else None.
        """
        reg1 = self._verse_registry.get(verse_id_1)
        reg2 = self._verse_registry.get(verse_id_2)
        if reg1 is None or reg2 is None:
            return None

        type_name_1, emb1 = reg1
        type_name_2, emb2 = reg2

        # --- Step 1: Detect abrogation via NaskhSolver ---
        prob, conf = self.naskh_solver.detect_abrogation(emb1, emb2, threshold=threshold)

        if prob < threshold:
            return None  # No abrogation detected

        # --- Step 2: Evolve the abrogated type ---
        self.hott.evolve_type(
            type_name_1,
            new_attributes={
                "is_abrogated": True,
                "abrogated_by": verse_id_2,
                "abrogation_probability": prob,
                "abrogation_confidence": conf,
            },
            reason=f"naskh_by_{verse_id_2}",
        )

        # --- Step 3: Assert path equality (type evolution path) ---
        path = self.hott.assert_path(
            type_name_1,
            type_name_2,
            proof=f"naskh_abrogation_p={prob:.3f}",
        )

        # --- Step 4: Witness univalence ---
        # Coherence reflects how "clean" the abrogation is
        coherence = conf * prob
        witness = self.hott.witness_univalence(
            type_name_1,
            type_name_2,
            coherence=coherence,
        )

        # --- Step 5: Compute homological memory ---
        homological_mem = self.naskh_solver.compute_homological_memory(emb1, emb2)

        # Store homological memory as type attribute
        self.hott.evolve_type(
            type_name_1,
            new_attributes={
                "homological_memory_norm": float(homological_mem.norm().item()),
            },
            reason="homological_memory_stored",
        )

        # Build event record
        event = NaskhEvolutionEvent(
            abrogated_verse_id=verse_id_1,
            abrogating_verse_id=verse_id_2,
            abrogation_probability=prob,
            confidence=conf,
            hott_path=path,
            univalence_witness=witness,
            homological_memory=homological_mem,
        )
        self.evolution_events.append(event)
        return event

    def build_evolution_chain(
        self,
        verse_ids: List[str],
        threshold: float = 0.5,
    ) -> TypeEvolutionChain:
        """Build a chain of naskh evolutions from an ordered list of verses.

        Processes pairs (v_i, v_{i+1}) sequentially, detecting abrogation
        at each step and building a directed path through the type graph.

        Args:
            verse_ids: Ordered list of verse IDs (by revelation order).
            threshold: Minimum abrogation probability.

        Returns:
            TypeEvolutionChain summarizing the evolution history.
        """
        events: List[NaskhEvolutionEvent] = []
        chain_verses: List[str] = [verse_ids[0]] if verse_ids else []

        for i in range(len(verse_ids) - 1):
            event = self.detect_and_evolve(verse_ids[i], verse_ids[i + 1], threshold)
            if event is not None:
                events.append(event)
                chain_verses.append(verse_ids[i + 1])

        # Compute chain metrics
        coherences = [e.univalence_witness.coherence for e in events]
        total_coherence = float(np.prod(coherences)) if coherences else 0.0

        max_level = max(
            (self.hott.types[f"verse_{vid}"].universe_level
             for vid in chain_verses if f"verse_{vid}" in self.hott.types),
            default=0,
        )

        winding = self.hott.compute_winding_number()

        return TypeEvolutionChain(
            verse_chain=chain_verses,
            evolution_events=events,
            total_coherence=total_coherence,
            chain_universe_level=max_level,
            winding_number=winding,
        )

    def transport_ruling(
        self,
        verse_id: str,
        target_verse_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Transport a deontic ruling from one verse type to another along a path.

        Uses HoTT transport: if a path exists from source to target in the
        type graph, the ruling can be "carried" along.

        Args:
            verse_id: Source verse.
            target_verse_id: Target verse.

        Returns:
            Transported ruling dict, or None if no path exists.
        """
        source_type = f"verse_{verse_id}"
        target_type = f"verse_{target_verse_id}"

        if source_type not in self.hott.types:
            return None

        source_attrs = self.hott.types[source_type].attributes
        ruling = {
            "deontic_category": source_attrs.get("deontic_category", "unknown"),
            "source_verse": verse_id,
        }

        try:
            transported = self.hott.transport(ruling, source_type, target_type)
            return transported
        except ValueError:
            return None  # No path exists

    def rank_abrogators(
        self,
        verse_id: str,
        candidate_ids: List[str],
    ) -> List[Tuple[str, float, float]]:
        """Rank candidate abrogating verses for a given verse.

        Args:
            verse_id: The potentially abrogated verse.
            candidate_ids: List of candidate abrogator verse IDs.

        Returns:
            List of (verse_id, probability, confidence) sorted by probability.
        """
        reg = self._verse_registry.get(verse_id)
        if reg is None:
            return []

        _, abrogated_emb = reg
        candidates = []
        for cid in candidate_ids:
            creg = self._verse_registry.get(cid)
            if creg is not None:
                candidates.append((cid, creg[1]))

        if not candidates:
            return []

        candidate_embs = [c[1] for c in candidates]
        rankings = self.naskh_solver.rank_abrogating_verses(abrogated_emb, candidate_embs)

        return [
            (candidates[idx][0], prob, conf)
            for idx, prob, conf in rankings
        ]

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def get_metrics(self) -> Dict[str, Any]:
        """Return type evolution metrics."""
        hott_metrics = self.hott.get_metrics()

        event_probs = [e.abrogation_probability for e in self.evolution_events]
        event_confs = [e.confidence for e in self.evolution_events]

        return {
            "hott": hott_metrics,
            "registered_verses": len(self._verse_registry),
            "evolution_events": len(self.evolution_events),
            "mean_abrogation_probability": float(np.mean(event_probs)) if event_probs else 0.0,
            "mean_confidence": float(np.mean(event_confs)) if event_confs else 0.0,
            "strange_loops": hott_metrics["strange_loops"],
            "winding_number": hott_metrics["winding_number"],
        }
