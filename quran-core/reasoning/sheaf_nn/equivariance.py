"""Morphological equivariance for Arabic roots in Quranic complex.

Implements equivariant feature extraction with respect to morphological
symmetries, where words sharing the same root are treated as symmetrical.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple, Optional, List


class MorphologicalEquivariance(nn.Module):
    """Equivariant feature extraction for Arabic roots.

    Arabic morphology is based on root systems: words sharing the same
    consonantal root (tri-literal structure) are semantically related.
    This module implements equivariance w.r.t. these morphological symmetries.

    For words w1, w2 with the same root r:
    - They belong to the same equivalence class [r]
    - Features should be equivariant under morphological transformations
    - Attention between words in the same class is boosted
    """

    def __init__(
        self,
        num_roots: int,
        embedding_dim: int,
        num_words: int,
        attention_boost_factor: float = 1.5,
    ):
        """Initialize morphological equivariance module.

        Args:
            num_roots: Number of distinct Arabic roots.
            embedding_dim: Dimension of morphological embeddings.
            num_words: Total number of distinct words.
            attention_boost_factor: Factor to boost attention for same-root pairs.
        """
        super().__init__()

        self.num_roots = num_roots
        self.embedding_dim = embedding_dim
        self.num_words = num_words
        self.attention_boost_factor = attention_boost_factor

        # Root embeddings: each root has a canonical representation
        self.root_embeddings = nn.Parameter(
            torch.Tensor(num_roots, embedding_dim)
        )

        # Word-to-root mapping will be stored
        self._root_mapping: Optional[Dict[int, int]] = None

        # Morphological transformation matrices (learned)
        # F_r: morphological automorphisms for root r
        self.morpho_transforms = nn.Parameter(
            torch.Tensor(num_roots, embedding_dim, embedding_dim)
        )

        # Bias terms for root-specific features
        self.root_bias = nn.Parameter(torch.Tensor(num_roots, embedding_dim))

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize parameters."""
        nn.init.kaiming_uniform_(self.root_embeddings, a=1.0, mode="fan_in")
        nn.init.kaiming_uniform_(self.morpho_transforms, a=1.0, mode="fan_in")
        nn.init.zeros_(self.root_bias)

    def register_root_mapping(
        self,
        word_indices: torch.Tensor,
        root_indices: torch.Tensor,
    ) -> None:
        """Register mapping from words to roots.

        Args:
            word_indices: Tensor of word indices of shape (num_words,).
            root_indices: Tensor of corresponding root indices of shape (num_words,).
        """
        self._root_mapping = {}
        for w_idx, r_idx in zip(word_indices.tolist(), root_indices.tolist()):
            self._root_mapping[w_idx] = r_idx

    def extract_roots(self, word_indices: torch.Tensor) -> torch.Tensor:
        """Extract root indices for given words.

        Args:
            word_indices: Tensor of word indices.

        Returns:
            Tensor of corresponding root indices.
        """
        if self._root_mapping is None:
            raise ValueError("Root mapping not registered. Call register_root_mapping first.")

        root_indices = []
        for w_idx in word_indices.tolist():
            if w_idx in self._root_mapping:
                root_indices.append(self._root_mapping[w_idx])
            else:
                # Default to root 0 if not mapped
                root_indices.append(0)

        return torch.tensor(root_indices, dtype=torch.long, device=word_indices.device)

    def boost_attention(
        self,
        word_indices: torch.Tensor,
        attention_weights: torch.Tensor,
    ) -> torch.Tensor:
        """Boost attention for words sharing the same root.

        Args:
            word_indices: Tensor of word indices of shape (num_words,).
            attention_weights: Tensor of attention weights of shape (num_words,).

        Returns:
            Boosted attention weights.
        """
        boosted_weights = attention_weights.clone()

        if self._root_mapping is None:
            return boosted_weights

        # Extract roots for all words
        roots = self.extract_roots(word_indices)

        # For each pair of words, boost attention if they share a root
        for i in range(len(word_indices)):
            for j in range(len(word_indices)):
                if i != j and roots[i] == roots[j]:
                    # Boost attention from word i to word j
                    boost_factor = self.attention_boost_factor
                    boosted_weights[i] = boosted_weights[i] * boost_factor

        # Normalize to maintain attention sum
        boosted_weights = F.softmax(torch.log(boosted_weights + 1e-8), dim=0)

        return boosted_weights

    def extract_equivariant_features(
        self,
        word_indices: torch.Tensor,
    ) -> torch.Tensor:
        """Extract equivariant features respecting morphological symmetries.

        For each word, we compute features that are equivariant w.r.t.
        its root's symmetry group. Words with the same root get related features.

        Args:
            word_indices: Tensor of word indices of shape (num_words,).

        Returns:
            Equivariant features of shape (num_words, embedding_dim).
        """
        # Extract roots
        root_indices = self.extract_roots(word_indices)

        # Get root embeddings
        root_embs = self.root_embeddings[root_indices]  # (num_words, embedding_dim)

        # Apply morphological transformations
        # For root r, apply F_r to the root embedding
        morpho_matrices = self.morpho_transforms[root_indices]  # (num_words, emb_dim, emb_dim)

        # Apply transformation: feature_i = F_{r_i} @ root_emb_i
        # Using batch matrix multiplication
        transformed = torch.einsum("nij,nj->ni", morpho_matrices, root_embs)
        # transformed: (num_words, embedding_dim)

        # Add root-specific bias
        biases = self.root_bias[root_indices]  # (num_words, embedding_dim)
        features = transformed + biases

        return features

    def compute_root_invariant(
        self,
        features: torch.Tensor,
        word_indices: torch.Tensor,
    ) -> torch.Tensor:
        """Compute root-invariant features (projections onto root subspace).

        Features that are invariant across words sharing the same root
        can be used for downstream tasks.

        Args:
            features: Word features of shape (num_words, feature_dim).
            word_indices: Word indices of shape (num_words,).

        Returns:
            Root-invariant features averaged within each root class.
        """
        root_indices = self.extract_roots(word_indices)

        # Aggregate features by root (average within each root)
        root_invariants = {}
        for i, r_idx in enumerate(root_indices.tolist()):
            if r_idx not in root_invariants:
                root_invariants[r_idx] = []
            root_invariants[r_idx].append(features[i])

        # Average within each root
        averaged_features = []
        for i, r_idx in enumerate(root_indices.tolist()):
            avg_feature = torch.stack(root_invariants[r_idx]).mean(dim=0)
            averaged_features.append(avg_feature)

        return torch.stack(averaged_features)

    def measure_equivariance_violation(
        self,
        features: torch.Tensor,
        word_indices: torch.Tensor,
    ) -> torch.Tensor:
        """Measure how much features violate equivariance w.r.t. morphological symmetries.

        Lower values indicate better equivariance.

        Args:
            features: Word features of shape (num_words, feature_dim).
            word_indices: Word indices of shape (num_words,).

        Returns:
            Scalar violation score.
        """
        if self._root_mapping is None:
            return torch.tensor(0.0, device=features.device, dtype=features.dtype)

        root_indices = self.extract_roots(word_indices)

        # For words with the same root, their features should be "close"
        violation = torch.tensor(0.0, device=features.device, dtype=features.dtype)
        count = 0

        for i in range(len(word_indices)):
            for j in range(i + 1, len(word_indices)):
                if root_indices[i] == root_indices[j]:
                    # These words share a root, their features should be similar
                    distance = torch.norm(features[i] - features[j], p=2)
                    violation = violation + distance
                    count += 1

        if count > 0:
            violation = violation / count

        return violation

    def extra_repr(self) -> str:
        """Return extra representation string."""
        return (
            f"num_roots={self.num_roots}, "
            f"embedding_dim={self.embedding_dim}, "
            f"num_words={self.num_words}, "
            f"attention_boost_factor={self.attention_boost_factor}"
        )


class RootCompatibilityMatrix(nn.Module):
    """Learns compatibility between roots (semantic closeness).

    Some roots are semantically related (e.g., related to divine attributes,
    or actions). This module learns a compatibility matrix between roots.
    """

    def __init__(self, num_roots: int, hidden_dim: int = 64):
        """Initialize root compatibility matrix.

        Args:
            num_roots: Number of roots.
            hidden_dim: Hidden dimension for learning the matrix.
        """
        super().__init__()
        self.num_roots = num_roots

        # Learnable compatibility matrix parameters
        self.compat_matrix = nn.Parameter(
            torch.Tensor(num_roots, num_roots)
        )

        # Optional: transformation networks to learn compatibility non-linearly
        self.compat_transform = nn.Sequential(
            nn.Linear(num_roots, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_roots),
        )

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize parameters symmetrically."""
        nn.init.eye_(self.compat_matrix)

    def forward(
        self,
        root_indices: torch.Tensor,
    ) -> torch.Tensor:
        """Compute pairwise compatibility for given roots.

        Args:
            root_indices: Tensor of root indices of shape (num_words,).

        Returns:
            Pairwise compatibility matrix of shape (num_words, num_words).
        """
        # Get compatibility matrix for selected roots
        compat_submatrix = self.compat_matrix[root_indices]  # (num_words, num_roots)

        # Select rows for target roots (gather again)
        # compat_submatrix[i, j] = compatibility(root_indices[i], root_indices[j])
        pairwise_compat = compat_submatrix[:, root_indices]  # (num_words, num_words)

        return pairwise_compat

    def get_root_relations(self) -> torch.Tensor:
        """Get the full root compatibility matrix.

        Returns:
            Full compatibility matrix of shape (num_roots, num_roots).
        """
        return self.compat_matrix


class MorphologicalEquivarianceLayer(nn.Module):
    """Full layer combining sheaf features with morphological equivariance.

    This layer integrates sheaf neural network outputs with morphological
    structure, boosting signal in words that share semantic roots.
    """

    def __init__(
        self,
        in_channels: int,
        num_roots: int,
        num_words: int,
        attention_boost_factor: float = 1.5,
    ):
        """Initialize morphological equivariance layer.

        Args:
            in_channels: Input feature dimension.
            num_roots: Number of roots.
            num_words: Number of words.
            attention_boost_factor: Attention boost for same-root pairs.
        """
        super().__init__()

        self.in_channels = in_channels
        self.num_roots = num_roots
        self.num_words = num_words

        self.morpho_eq = MorphologicalEquivariance(
            num_roots=num_roots,
            embedding_dim=in_channels,
            num_words=num_words,
            attention_boost_factor=attention_boost_factor,
        )

        self.root_compat = RootCompatibilityMatrix(num_roots)

        # Projection to learned equivariant subspace
        self.proj = nn.Linear(in_channels, in_channels)

    def forward(
        self,
        x: torch.Tensor,
        word_indices: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass with morphological equivariance.

        Args:
            x: Features of shape (num_words, in_channels).
            word_indices: Word indices of shape (num_words,).

        Returns:
            Equivariant features of shape (num_words, in_channels).
        """
        # Extract morphologically equivariant features
        morpho_features = self.morpho_eq.extract_equivariant_features(word_indices)

        # Project and combine with input
        combined = x + self.proj(morpho_features)

        return combined

    def extra_repr(self) -> str:
        """Return extra representation string."""
        return (
            f"in_channels={self.in_channels}, "
            f"num_roots={self.num_roots}, "
            f"num_words={self.num_words}"
        )
