"""Quantum Hilbert Space for Qira'at (7 Canonical Readings as Superposition).

This module implements a quantum-mechanical framework where the 7 canonical
readers (Qira'at) are represented as basis vectors in a 7-dimensional Hilbert
space. Each Quranic verse can exist in a superposition of readings before
measurement (query).

Key concepts:
- Hilbert space: Complete inner-product space for quantum states
- Basis: 7 canonical readers (Asim, Hamza, etc.)
- Superposition: |Ψ⟩ = Σ α_i |Reading_i⟩ ⊗ |Semantic_i⟩
- Measurement: Query collapses superposition to classical reading
- Unitary: Recitation rules as U-transformations preserving norm
"""

import numpy as np
from typing import Tuple, List, Optional, Union
from dataclasses import dataclass
import warnings


@dataclass
class BasisVector:
    """Represents a basis vector |i⟩ for reading i."""

    index: int
    dimension: int
    amplitude_vector: np.ndarray

    def __post_init__(self):
        """Ensure basis vector is normalized."""
        norm = np.linalg.norm(self.amplitude_vector)
        if not np.isclose(norm, 1.0):
            self.amplitude_vector = self.amplitude_vector / norm


class SuperpositionState:
    """Quantum superposition state |Ψ⟩ with amplitudes for each basis."""

    def __init__(self, amplitude_vector: np.ndarray):
        """Initialize superposition with complex amplitudes.

        Args:
            amplitude_vector: Complex array of amplitudes [α_0, α_1, ..., α_{d-1}]
        """
        self.amplitude_vector = np.asarray(amplitude_vector, dtype=complex)
        self.dimension = len(self.amplitude_vector)

        # Normalize
        norm = np.linalg.norm(self.amplitude_vector)
        if not np.isclose(norm, 1.0):
            self.amplitude_vector = self.amplitude_vector / norm

    def measure(self, hilbert_space: 'QiraatHilbertSpace') -> int:
        """Measure the state, collapsing to a single reading.

        The probability of measuring basis i is P(i) = |α_i|².

        Args:
            hilbert_space: The Hilbert space context (unused but kept for API compatibility)

        Returns:
            Index (0-6) of the collapsed reading
        """
        probabilities = np.abs(self.amplitude_vector) ** 2
        # Ensure probabilities sum to 1 (numerical stability)
        probabilities = probabilities / np.sum(probabilities)

        result = np.random.choice(
            len(self.amplitude_vector),
            p=probabilities
        )
        return int(result)

    def apply_unitary(self, U: np.ndarray) -> 'SuperpositionState':
        """Apply unitary transformation |Ψ'⟩ = U|Ψ⟩.

        Preserves norm: ||Ψ'|| = ||Ψ|| = 1

        Args:
            U: Unitary matrix (d × d, U†U = I)

        Returns:
            New superposition state after transformation
        """
        # Verify unitary
        if not np.allclose(U @ U.conj().T, np.eye(U.shape[0])):
            warnings.warn("Matrix U may not be unitary")

        new_amplitude = U @ self.amplitude_vector
        return SuperpositionState(new_amplitude)

    def tensor_product(self, other: 'SuperpositionState') -> 'SuperpositionState':
        """Compute tensor product |Ψ₁⟩ ⊗ |Ψ₂⟩.

        Args:
            other: Another superposition state

        Returns:
            Composite state with dimension = d1 × d2
        """
        composite_amplitude = np.kron(self.amplitude_vector, other.amplitude_vector)
        return SuperpositionState(composite_amplitude)

    def inner_product(self, other: 'SuperpositionState') -> complex:
        """Compute ⟨Ψ₁|Ψ₂⟩."""
        return np.vdot(self.amplitude_vector, other.amplitude_vector)

    def expectation_value(self, operator: np.ndarray) -> complex:
        """Compute expectation value ⟨Ψ|O|Ψ⟩."""
        return np.vdot(
            self.amplitude_vector,
            operator @ self.amplitude_vector
        )


class QiraatHilbertSpace:
    """7-Dimensional Hilbert space for Qira'at (canonical readings).

    Implements quantum superposition of 7 canonical readers:
    1. Asim (Hafs)
    2. Hamza
    3. Al-Kisa'i
    4. Abu Amr
    5. Ibn Kathir
    6. Nafi
    7. Ibn Amir

    Plus semantic dimension for meaning interpretation.
    """

    # Canonical reader names
    CANONICAL_READERS = [
        "Asim (Hafs)",
        "Hamza",
        "Al-Kisa'i",
        "Abu Amr",
        "Ibn Kathir",
        "Nafi",
        "Ibn Amir",
    ]

    def __init__(self, dimension: int = 7):
        """Initialize 7D Hilbert space for canonical readings.

        Args:
            dimension: Size of Hilbert space (default 7 for 7 canonical readers)
        """
        self.dimension = dimension
        self.basis_size = dimension
        self._basis_vectors = None

    def basis_vectors(self) -> List[np.ndarray]:
        """Get orthonormal basis vectors {|0⟩, |1⟩, ..., |d-1⟩}.

        Returns:
            List of d orthonormal basis vectors (standard basis)
        """
        if self._basis_vectors is None:
            self._basis_vectors = [
                np.eye(self.dimension)[i]
                for i in range(self.dimension)
            ]
        return self._basis_vectors

    def basis_vector(self, index: int) -> SuperpositionState:
        """Create basis vector |i⟩.

        Args:
            index: Which basis vector (0 ≤ i < d)

        Returns:
            Basis vector as superposition state
        """
        if not 0 <= index < self.dimension:
            raise ValueError(f"Index {index} out of range [0, {self.dimension})")

        vec = np.zeros(self.dimension, dtype=complex)
        vec[index] = 1.0
        return SuperpositionState(vec)

    def create_superposition(
        self,
        coefficients: np.ndarray,
        semantic_dim: Optional[int] = None
    ) -> SuperpositionState:
        """Create superposition |Ψ⟩ = Σ α_i |Reading_i⟩.

        Args:
            coefficients: Complex amplitudes [α_0, ..., α_{d-1}]
            semantic_dim: Optional semantic dimension (for ⊗ semantic space)

        Returns:
            Normalized superposition state
        """
        coefficients = np.asarray(coefficients, dtype=complex)

        if len(coefficients) != self.dimension:
            raise ValueError(
                f"Expected {self.dimension} coefficients, got {len(coefficients)}"
            )

        state = SuperpositionState(coefficients)

        # Optionally extend to semantic space
        if semantic_dim is not None:
            semantic_basis = np.ones(semantic_dim) / np.sqrt(semantic_dim)
            semantic_state = SuperpositionState(semantic_basis)
            state = state.tensor_product(semantic_state)

        return state

    def zero_state(self) -> SuperpositionState:
        """Create zero state |0...0⟩."""
        vec = np.zeros(self.dimension, dtype=complex)
        vec[0] = 1.0
        return SuperpositionState(vec)

    def uniform_superposition(self) -> SuperpositionState:
        """Create uniform superposition (equal weights for all readings).

        |Ψ⟩ = (1/√d) Σ |i⟩
        """
        coeffs = np.ones(self.dimension, dtype=complex) / np.sqrt(self.dimension)
        return SuperpositionState(coeffs)

    def ghz_state(self) -> SuperpositionState:
        """Create GHZ-like state for 7 readers (maximal entanglement analog).

        |GHZ⟩₇ = (1/√2) [|0⟩⊗⁷ + |6⟩⊗⁷]  (approximate in 7D)
        """
        vec = np.zeros(self.dimension, dtype=complex)
        vec[0] = 1.0 / np.sqrt(2)
        vec[-1] = 1.0 / np.sqrt(2)
        return SuperpositionState(vec)

    def apply_hadamard_like(self) -> np.ndarray:
        """Create Hadamard-like unitary for superposition.

        Useful for creating uniform superposition: H|0⟩ = superposition.
        """
        # Fourier matrix (generalization of Hadamard)
        H = np.zeros((self.dimension, self.dimension), dtype=complex)
        for i in range(self.dimension):
            for j in range(self.dimension):
                H[i, j] = np.exp(2j * np.pi * i * j / self.dimension) / np.sqrt(self.dimension)
        return H

    def apply_phase_gate(self, phase: float) -> np.ndarray:
        """Create phase gate diag(1, e^{iθ}, e^{2iθ}, ...).

        Rotates phases of basis states - useful for encoding reading properties.
        """
        phases = np.exp(1j * phase * np.arange(self.dimension))
        return np.diag(phases)

    def measurement_basis(self) -> List[SuperpositionState]:
        """Get computational basis for measurements.

        Returns:
            List of 7 orthonormal basis states
        """
        return [self.basis_vector(i) for i in range(self.dimension)]

    def gram_matrix(self, states: List[SuperpositionState]) -> np.ndarray:
        """Compute Gram matrix (inner products) of states.

        G[i,j] = ⟨Ψ_i|Ψ_j⟩
        """
        n = len(states)
        G = np.zeros((n, n), dtype=complex)
        for i in range(n):
            for j in range(n):
                G[i, j] = states[i].inner_product(states[j])
        return G

    def purify_state(self, rho: np.ndarray) -> SuperpositionState:
        """Convert density matrix to pure state (if possible).

        Args:
            rho: Density matrix (d × d)

        Returns:
            Pure state (eigenvector with eigenvalue 1)
        """
        eigenvalues, eigenvectors = np.linalg.eigh(rho)
        # Get eigenvector with eigenvalue closest to 1
        idx = np.argmax(eigenvalues)
        return SuperpositionState(eigenvectors[:, idx])

    def partial_trace(
        self,
        rho: np.ndarray,
        subsystem: int,
        dims: List[int]
    ) -> np.ndarray:
        """Compute partial trace (reduced density matrix).

        Tr_B(ρ_{AB}) over subsystem B.

        Args:
            rho: Full density matrix
            subsystem: Which subsystem to trace out (0 or 1 for bipartite)
            dims: Dimensions [d_A, d_B]

        Returns:
            Reduced density matrix
        """
        d_A, d_B = dims
        rho_full = rho.reshape((d_A, d_B, d_A, d_B))

        if subsystem == 1:  # Trace out B
            rho_reduced = np.zeros((d_A, d_A), dtype=complex)
            for i in range(d_B):
                rho_reduced += rho_full[:, i, :, i]
        else:  # Trace out A
            rho_reduced = np.zeros((d_B, d_B), dtype=complex)
            for i in range(d_A):
                rho_reduced += rho_full[i, :, i, :]

        return rho_reduced

    def __repr__(self) -> str:
        return f"QiraatHilbertSpace(dimension={self.dimension})"


class RecitationRuleTransform:
    """Unitary transformations representing Tajweed/recitation rules.

    Maps one reading to another via phonetic/semantic rules.
    """

    def __init__(self, hilbert_space: QiraatHilbertSpace):
        self.hs = hilbert_space

    def vowel_permutation(self, perm: List[int]) -> np.ndarray:
        """Create unitary permuting readings based on vowel rules.

        Args:
            perm: Permutation [p_0, ..., p_{d-1}] where σ(i) = p_i

        Returns:
            Permutation unitary matrix
        """
        U = np.zeros((self.hs.dimension, self.hs.dimension), dtype=complex)
        for i, j in enumerate(perm):
            U[j, i] = 1.0
        return U

    def phonetic_rotation(self, angle: float) -> np.ndarray:
        """Create rotation in reading space by phonetic distance.

        Args:
            angle: Rotation angle (radians)

        Returns:
            2D rotation unitary (embeds in larger space)
        """
        c, s = np.cos(angle), np.sin(angle)
        U = np.eye(self.hs.dimension, dtype=complex)
        U[0, 0] = c
        U[0, 1] = -1j * s
        U[1, 0] = 1j * s
        U[1, 1] = c
        return U

    def semantic_phase_encoding(self, meanings: np.ndarray) -> np.ndarray:
        """Encode semantic interpretation as phase angles.

        Args:
            meanings: Array of meaning scores [m_0, ..., m_{d-1}]

        Returns:
            Diagonal unitary: diag(e^{iθ_0}, ..., e^{iθ_{d-1}})
        """
        meanings = np.asarray(meanings)
        meanings = meanings - np.min(meanings)
        meanings = 2 * np.pi * meanings / np.max(meanings)
        phases = np.exp(1j * meanings)
        return np.diag(phases)
