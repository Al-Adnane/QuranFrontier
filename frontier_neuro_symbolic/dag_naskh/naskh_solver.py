"""Naskh Solver using Derived Algebraic Geometry.

This module implements the core naskh detection algorithm by modeling abrogation
as a derived intersection in algebraic geometry. The solver:

1. Embeds verses in a derived stack
2. Computes derived intersections (modeling naskh events)
3. Tracks homological memory of abrogated verses
4. Classifies abrogation with probability and confidence
"""

from typing import Tuple, Optional, List
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from .stacks import DerivedStack, DerivedPoint
from .cohomology import CohomologyComputer, BettiAnalyzer


class NaskhSolver(nn.Module):
    """Solver for naskh (abrogation) detection using derived algebraic geometry.

    The solver models naskh as a derived intersection phenomenon:
    - Two verses are in naskh relation if they intersect in the derived stack
    - The intersection is computed homologically
    - Homological memory preserves the "trace" of abrogation

    Attributes:
        embedding_dim: Dimension of verse embeddings
        stack_dimension: Algebraic dimension of the derived stack
        semantic_dim: Dimension of semantic interpretation space
    """

    def __init__(
        self,
        embedding_dim: int,
        stack_dimension: int,
        semantic_dim: int,
        device: Optional[torch.device] = None
    ):
        """Initialize NaskhSolver.

        Args:
            embedding_dim: Dimension of verse embeddings
            stack_dimension: Algebraic dimension of the derived stack
            semantic_dim: Dimension of semantic interpretations
            device: Device to compute on (default: cpu)
        """
        super().__init__()

        self.embedding_dim = embedding_dim
        self.stack_dimension = stack_dimension
        self.semantic_dim = semantic_dim
        self.device = device or torch.device('cpu')

        # Initialize derived stack
        self.derived_stack = DerivedStack(
            dimension=stack_dimension,
            ambient_dim=embedding_dim,
            name="Quranic Naskh Interpretation Space"
        )

        # Learnable projection matrix for homological correction
        self.homological_projection = nn.Linear(
            embedding_dim,
            semantic_dim,
            bias=True
        )

        # Semantic similarity network
        self.semantic_similarity = nn.Sequential(
            nn.Linear(2 * embedding_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

        # Confidence scorer
        self.confidence_scorer = nn.Sequential(
            nn.Linear(embedding_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

        # Cohomology analyzer
        self.cohomology_computer = CohomologyComputer(
            dimension=stack_dimension,
            embedding_dim=embedding_dim,
            max_degree=3
        )

        self.betti_analyzer = BettiAnalyzer(
            dimension=stack_dimension,
            max_degree=3
        )

        # Move to device
        self.to(self.device)

    def forward(
        self,
        verse1: torch.Tensor,
        verse2: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass: detect naskh relationship between two verses.

        Args:
            verse1: Embedding of first verse (embedding_dim,)
            verse2: Embedding of second verse (embedding_dim,)

        Returns:
            Tuple of (abrogation_probability, confidence)
        """
        prob, conf = self.detect_abrogation(verse1, verse2)
        return torch.tensor(prob, device=self.device), torch.tensor(conf, device=self.device)

    def model_naskh(
        self,
        verse1: torch.Tensor,
        verse2: torch.Tensor
    ) -> torch.Tensor:
        """Model naskh as derived intersection point.

        In derived algebraic geometry, the intersection is computed
        at the homological level, preserving structure.

        Args:
            verse1: Embedding of verse 1
            verse2: Embedding of verse 2

        Returns:
            Derived intersection point (torch.Tensor)
        """
        # Ensure tensors are on correct device
        verse1 = verse1.to(self.device)
        verse2 = verse2.to(self.device)

        # Create derived points with semantic interpretation
        sem1 = self.homological_projection(verse1)
        sem2 = self.homological_projection(verse2)

        point1 = DerivedPoint(
            position=verse1,
            verse_ref=(0, 0),  # Placeholder
            semantic_dimension=self.semantic_dim,
        )

        point2 = DerivedPoint(
            position=verse2,
            verse_ref=(0, 0),  # Placeholder
            semantic_dimension=self.semantic_dim,
        )

        # Update homological memory with semantic interpretations
        point1.cohomology_class = sem1
        point2.cohomology_class = sem2

        # Compute derived intersection
        intersection = self.derived_stack.compute_intersection(
            point1, point2, use_homological=True
        )

        return intersection

    def detect_abrogation(
        self,
        verse1: torch.Tensor,
        verse2: torch.Tensor,
        threshold: float = 0.5
    ) -> Tuple[float, float]:
        """Detect naskh (abrogation) relationship between verses.

        Computes:
        1. Semantic similarity (probability of naskh)
        2. Confidence in the prediction

        Args:
            verse1: Embedding of verse 1
            verse2: Embedding of verse 2
            threshold: Threshold for positive classification

        Returns:
            Tuple of (naskh_probability, confidence)
        """
        # Ensure tensors are on correct device
        verse1 = verse1.to(self.device)
        verse2 = verse2.to(self.device)

        # Compute naskh model
        intersection = self.model_naskh(verse1, verse2)

        # Semantic similarity via concatenation
        combined = torch.cat([verse1, verse2], dim=-1)
        semantic_prob = float(self.semantic_similarity(combined).item())

        # Confidence from verse1 and verse2
        conf1 = float(self.confidence_scorer(verse1).item())
        conf2 = float(self.confidence_scorer(verse2).item())
        confidence = 0.5 * (conf1 + conf2)

        # Incorporate homological signal
        homoological_signal = self._compute_homological_signal(
            verse1, verse2, intersection
        )

        # Final probability combines semantic and homological signals
        naskh_probability = 0.6 * semantic_prob + 0.4 * homoological_signal

        return float(naskh_probability), float(confidence)

    def _compute_homological_signal(
        self,
        verse1: torch.Tensor,
        verse2: torch.Tensor,
        intersection: torch.Tensor
    ) -> float:
        """Compute homological signal for naskh detection.

        Measures how "aligned" the verses are in homological sense.

        Args:
            verse1: First verse embedding
            verse2: Second verse embedding
            intersection: Derived intersection point

        Returns:
            Homological signal in [0, 1]
        """
        # Compute semantic projection for both verses
        sem1 = self.homological_projection(verse1)
        sem2 = self.homological_projection(verse2)

        # Similarity in semantic space
        semantic_similarity = F.cosine_similarity(
            sem1.unsqueeze(0),
            sem2.unsqueeze(0)
        ).item()

        # Distance to intersection (should be small for related verses)
        inter_dist1 = torch.norm(verse1 - intersection)
        inter_dist2 = torch.norm(verse2 - intersection)
        intersection_penalty = float(
            1.0 / (1.0 + inter_dist1.item() + inter_dist2.item())
        )

        # Combine: high similarity + small distance to intersection = naskh
        signal = 0.6 * abs(semantic_similarity) + 0.4 * intersection_penalty

        return float(np.clip(signal, 0.0, 1.0))

    def compute_homological_memory(
        self,
        abrogated: torch.Tensor,
        abrogating: torch.Tensor
    ) -> torch.Tensor:
        """Compute homological memory of an abrogated verse.

        The homological memory is a persistent record that captures:
        - Which verse abrogated it
        - In what semantic dimension
        - With what cohomological multiplicity

        Args:
            abrogated: Embedding of the abrogated verse
            abrogating: Embedding of the abrogating verse

        Returns:
            Memory tensor (torch.Tensor) of shape (semantic_dim, semantic_dim)
        """
        # Ensure tensors are on correct device
        abrogated = abrogated.to(self.device)
        abrogating = abrogating.to(self.device)

        # Project to semantic space
        sem_abrogated = self.homological_projection(abrogated)
        sem_abrogating = self.homological_projection(abrogating)

        # Memory is computed via outer product in semantic space
        # This captures the "direction" of abrogation
        memory = torch.outer(sem_abrogating, sem_abrogated)

        # Normalize memory
        memory = memory / (torch.norm(memory) + 1e-8)

        return memory

    def rank_abrogating_verses(
        self,
        abrogated: torch.Tensor,
        candidate_abrogators: List[torch.Tensor]
    ) -> List[Tuple[int, float, float]]:
        """Rank candidate abrogating verses by naskh probability.

        Args:
            abrogated: Embedding of the abrogated verse
            candidate_abrogators: List of candidate abrogating verse embeddings

        Returns:
            List of (index, probability, confidence) tuples, ranked by probability
        """
        results = []

        for i, abrogator in enumerate(candidate_abrogators):
            prob, conf = self.detect_abrogation(abrogated, abrogator)
            results.append((i, prob, conf))

        # Sort by probability (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    def analyze_interpretation_space(
        self,
        verses: List[torch.Tensor]
    ) -> dict:
        """Analyze topological properties of verse interpretation space.

        Args:
            verses: List of verse embeddings

        Returns:
            Dictionary with topological analysis
        """
        if len(verses) == 0:
            return {}

        # Stack verses into batch
        X = torch.stack(verses)

        # Compute cohomology
        cohom_groups = self.cohomology_computer.compute_cohomology_groups(X)

        # Compute Betti numbers
        betti_numbers = self.betti_analyzer.compute_betti_numbers(X)

        # Compute semantic cohesion
        cohesion = self.cohomology_computer.compute_semantic_cohesion(X)

        # Compute Euler characteristic
        euler_char = self.betti_analyzer.compute_euler_characteristic(betti_numbers)

        # Check if space is homologically spherical
        is_spherical = self.betti_analyzer.is_homologically_spherical(betti_numbers)

        return {
            "cohomology_groups": cohom_groups,
            "betti_numbers": betti_numbers,
            "semantic_cohesion": cohesion,
            "euler_characteristic": euler_char,
            "is_homologically_spherical": is_spherical,
            "n_verses": len(verses),
        }

    def save_solver(self, path: str) -> None:
        """Save solver state to disk.

        Args:
            path: Path to save to
        """
        torch.save(self.state_dict(), path)

    def load_solver(self, path: str) -> None:
        """Load solver state from disk.

        Args:
            path: Path to load from
        """
        self.load_state_dict(torch.load(path, map_location=self.device))

    def to(self, device: torch.device):
        """Move solver to device.

        Args:
            device: Target device

        Returns:
            Self
        """
        self.device = device
        return super().to(device)
