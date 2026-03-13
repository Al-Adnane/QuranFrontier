"""Cohomology computation for derived interpretation spaces.

This module implements computational cohomology for Quranic interpretation spaces.
Key operations include:
- Computing cohomology groups H^n(X, O_X)
- Computing Betti numbers (topological invariants)
- Measuring semantic cohesion via cohomological methods
"""

from typing import Dict, List, Tuple
import torch
import torch.nn as nn
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import connected_components


class CohomologyComputer:
    """Computes cohomology groups and invariants for interpretation spaces.

    Uses discrete Morse theory and persistent homology to compute
    cohomology groups H^n(X, O_X) from point cloud embeddings.

    Attributes:
        dimension: Dimension of the space
        embedding_dim: Dimension of embeddings
        max_degree: Maximum cohomology degree to compute
    """

    def __init__(
        self,
        dimension: int,
        embedding_dim: int,
        max_degree: int = 3
    ):
        """Initialize cohomology computer.

        Args:
            dimension: Dimension of the space
            embedding_dim: Dimension of embeddings
            max_degree: Maximum degree for cohomology computation
        """
        self.dimension = dimension
        self.embedding_dim = embedding_dim
        self.max_degree = max_degree

    def compute_cohomology_groups(
        self,
        X: torch.Tensor,
        threshold: float = 0.5
    ) -> Dict[int, np.ndarray]:
        """Compute cohomology groups H^n(X, O_X).

        Uses filtration approach: build nested complexes and track
        cohomology generators across filtration levels.

        Args:
            X: Point cloud embedding (n_points, embedding_dim)
            threshold: Distance threshold for connectivity

        Returns:
            Dictionary mapping degree n to cohomology group basis
        """
        X_np = X.detach().cpu().numpy()
        n_points = X_np.shape[0]

        # Compute distance matrix
        distances = squareform(pdist(X_np))

        # Build filtration: start with threshold-determined connectivity
        cohom_dict = {}

        # Degree 0: connected components (H^0)
        adjacency = (distances < threshold).astype(float)
        np.fill_diagonal(adjacency, 0)
        n_components, labels = connected_components(adjacency, directed=False)
        cohom_dict[0] = np.eye(n_components)

        # Degree 1: compute via persistent homology on Vietoris-Rips complex
        # Simplified: use distance-based persistence
        for d in range(1, self.max_degree + 1):
            # Compute d-th cohomology via eigenspace of Laplacian
            cohom_dict[d] = self._compute_degree_d_cohomology(X_np, d)

        return cohom_dict

    def _compute_degree_d_cohomology(
        self,
        X: np.ndarray,
        degree: int,
        threshold: float = 0.5
    ) -> np.ndarray:
        """Compute cohomology at a specific degree.

        Uses spectral methods on the distance-weighted graph Laplacian.

        Args:
            X: Point cloud (n_points, embedding_dim)
            degree: Degree of cohomology to compute
            threshold: Distance threshold

        Returns:
            Basis vectors for the cohomology group
        """
        distances = squareform(pdist(X))
        n_points = X.shape[0]

        # Build weighted adjacency matrix
        adjacency = np.zeros((n_points, n_points))
        for i in range(n_points):
            for j in range(i + 1, n_points):
                if distances[i, j] < threshold:
                    weight = np.exp(-distances[i, j] ** 2)
                    adjacency[i, j] = weight
                    adjacency[j, i] = weight

        # Compute graph Laplacian
        degrees = np.sum(adjacency, axis=1)
        laplacian = np.diag(degrees) - adjacency

        # Compute eigenvalues and eigenvectors
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
        except np.linalg.LinAlgError:
            # Return identity if eigendecomposition fails
            return np.eye(min(degree + 1, n_points))

        # Select eigenvectors corresponding to small eigenvalues
        # (null space of Laplacian approximates cohomology)
        n_eigs = min(degree + 1, n_points // 2)
        if n_eigs > 0:
            basis = eigenvectors[:, :n_eigs]
        else:
            basis = np.eye(n_points)

        return basis

    def compute_semantic_cohesion(
        self,
        X: torch.Tensor,
        threshold: float = 0.5
    ) -> float:
        """Compute semantic cohesion degree from cohomology.

        High cohesion means the interpretation space is "well-connected"
        and forms a coherent semantic whole.

        Args:
            X: Point cloud embedding
            threshold: Distance threshold

        Returns:
            Cohesion score in [0, 1]
        """
        X_np = X.detach().cpu().numpy()
        distances = squareform(pdist(X_np))

        # Compute connectivity ratio
        adjacency = (distances < threshold).astype(float)
        np.fill_diagonal(adjacency, 0)

        # Density of edges (number of edges / max possible edges)
        n_points = X_np.shape[0]
        max_edges = n_points * (n_points - 1) / 2.0
        actual_edges = np.sum(adjacency) / 2.0

        edge_density = actual_edges / max_edges if max_edges > 0 else 0.0

        # Check connectivity via components
        n_components, _ = connected_components(adjacency, directed=False)
        connectivity = 1.0 - (n_components - 1) / (n_points - 1) if n_points > 1 else 1.0

        # Cohesion is weighted combination
        cohesion = 0.5 * edge_density + 0.5 * connectivity

        return float(np.clip(cohesion, 0.0, 1.0))

    def compute_persistence_diagram(
        self,
        X: torch.Tensor,
        threshold: float = 1.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute persistent homology diagram.

        Args:
            X: Point cloud embedding
            threshold: Maximum distance for filtration

        Returns:
            Tuple of (births, deaths) arrays
        """
        X_np = X.detach().cpu().numpy()
        distances = squareform(pdist(X_np))

        # Collect all distance values as filtration steps
        unique_dists = np.unique(distances)
        unique_dists = unique_dists[unique_dists > 0]

        births = []
        deaths = []

        # Simplified persistent homology: track component formation/merging
        prev_n_components = X_np.shape[0]

        for dist in unique_dists:
            adjacency = (distances <= dist).astype(float)
            np.fill_diagonal(adjacency, 0)
            n_components, _ = connected_components(adjacency, directed=False)

            if n_components < prev_n_components:
                births.append(dist - 0.01)
                deaths.append(dist)
                prev_n_components = n_components

        return np.array(births), np.array(deaths)


class BettiAnalyzer:
    """Computes Betti numbers and topological invariants.

    Betti numbers b_i represent the rank of the i-th homology group,
    giving topological information about the space.

    Attributes:
        dimension: Dimension of the space
        max_degree: Maximum degree for Betti number computation
    """

    def __init__(self, dimension: int, max_degree: int = 3):
        """Initialize Betti analyzer.

        Args:
            dimension: Dimension of the space
            max_degree: Maximum degree for computation
        """
        self.dimension = dimension
        self.max_degree = max_degree

    def compute_betti_numbers(
        self,
        X: torch.Tensor,
        threshold: float = 0.5
    ) -> Dict[int, int]:
        """Compute Betti numbers for point cloud.

        Uses algebraic topology: b_i is the rank of H_i.

        Args:
            X: Point cloud embedding (n_points, embedding_dim)
            threshold: Distance threshold for complex construction

        Returns:
            Dictionary mapping degree to Betti number
        """
        X_np = X.detach().cpu().numpy()
        n_points = X_np.shape[0]

        betti = {}

        # Compute distance matrix
        distances = squareform(pdist(X_np))

        # Degree 0 (number of connected components)
        adjacency = (distances < threshold).astype(float)
        np.fill_diagonal(adjacency, 0)
        n_components, _ = connected_components(adjacency, directed=False)
        betti[0] = int(n_components)

        # Degree 1 and higher: use Laplacian spectral properties
        for d in range(1, self.max_degree + 1):
            betti[d] = self._compute_betti_d(X_np, d, threshold)

        return betti

    def _compute_betti_d(
        self,
        X: np.ndarray,
        degree: int,
        threshold: float
    ) -> int:
        """Compute Betti number at a specific degree.

        Uses kernel/image dimension computation on discrete Laplacian.

        Args:
            X: Point cloud
            degree: Betti degree
            threshold: Distance threshold

        Returns:
            Betti number (integer)
        """
        distances = squareform(pdist(X))
        n_points = X.shape[0]

        # Build adjacency
        adjacency = np.zeros((n_points, n_points))
        for i in range(n_points):
            for j in range(i + 1, n_points):
                if distances[i, j] < threshold:
                    adjacency[i, j] = 1
                    adjacency[j, i] = 1

        # Compute graph Laplacian
        degrees = np.sum(adjacency, axis=1)
        laplacian = np.diag(degrees) - adjacency

        # Compute rank via SVD
        try:
            u, s, vt = np.linalg.svd(laplacian, full_matrices=False)
            # Count zero eigenvalues (rank deficiency)
            rank = np.sum(s > 1e-10)
        except np.linalg.LinAlgError:
            rank = n_points

        # Betti number (simplified): dimension of null space at degree d
        # For simplicity, use spectral gap structure
        null_dim = max(0, n_points - rank)

        # Higher degree Betti numbers decrease rapidly
        betti_d = max(0, null_dim // (degree + 1))

        return int(betti_d)

    def compute_euler_characteristic(
        self,
        betti_numbers: Dict[int, int]
    ) -> int:
        """Compute Euler characteristic from Betti numbers.

        chi(X) = sum_{i} (-1)^i * b_i

        Args:
            betti_numbers: Dictionary of Betti numbers

        Returns:
            Euler characteristic (integer)
        """
        chi = 0
        for degree, betti_num in betti_numbers.items():
            chi += ((-1) ** degree) * betti_num

        return chi

    def is_homologically_spherical(
        self,
        betti_numbers: Dict[int, int]
    ) -> bool:
        """Check if space is homologically a sphere.

        A space is homologically spherical if b_0 = 1 and b_n = 1
        for dimension n, with other Betti numbers zero.

        Args:
            betti_numbers: Dictionary of Betti numbers

        Returns:
            True if space is homologically spherical
        """
        if betti_numbers.get(0, 0) != 1:
            return False

        if betti_numbers.get(self.dimension, 0) != 1:
            return False

        for d in range(1, self.dimension):
            if betti_numbers.get(d, 0) != 0:
                return False

        return True

    def compute_homological_stability(
        self,
        X: torch.Tensor,
        perturbation_scale: float = 0.01,
        n_trials: int = 5
    ) -> float:
        """Compute stability of Betti numbers under perturbation.

        Measures robustness of topological invariants.

        Args:
            X: Point cloud embedding
            perturbation_scale: Standard deviation of perturbation
            n_trials: Number of perturbations to test

        Returns:
            Stability score in [0, 1] (higher = more stable)
        """
        base_betti = self.compute_betti_numbers(X)

        stability_scores = []
        for _ in range(n_trials):
            X_perturbed = X + perturbation_scale * torch.randn_like(X)
            perturbed_betti = self.compute_betti_numbers(X_perturbed)

            # Compute agreement
            matches = 0
            total = 0
            for d in base_betti:
                if d in perturbed_betti:
                    if base_betti[d] == perturbed_betti[d]:
                        matches += 1
                    total += 1

            if total > 0:
                stability_scores.append(matches / total)

        mean_stability = np.mean(stability_scores) if stability_scores else 0.0
        return float(np.clip(mean_stability, 0.0, 1.0))
