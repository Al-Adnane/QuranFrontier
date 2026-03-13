"""Entanglement Measures Between Quranic Verses.

Quantifies the quantum correlations (entanglement) between distant verses
using information-theoretic measures:
- Von Neumann entropy: S(ρ) = -Tr(ρ log ρ)
- Bell pair detection: Mutashabihāt (similar verses)
- GHZ state: Maximal 7-way entanglement
- Mutual information: I(A:B) = S(ρ_A) + S(ρ_B) - S(ρ_{AB})
"""

import numpy as np
from typing import Tuple, Optional
from scipy.linalg import expm, eigvalsh
import warnings


class VonNeumannEntropy:
    """Compute Von Neumann entropy S(ρ) = -Tr(ρ log ρ)."""

    def __init__(self, base: float = 2.0):
        """Initialize entropy calculator.

        Args:
            base: Logarithm base (2 for bits, e for nats, 10 for dits)
        """
        self.base = base
        self.log_func = np.log2 if base == 2 else (np.log if base == np.e else np.log10)

    def compute(self, rho: np.ndarray, regularize: bool = True) -> float:
        """Compute S(ρ) = -Tr(ρ log ρ).

        Args:
            rho: Density matrix (d × d, Hermitian, positive semidefinite)
            regularize: Add small regularization to avoid log(0)

        Returns:
            Von Neumann entropy (non-negative)
        """
        rho = np.asarray(rho, dtype=complex)

        # Ensure Hermitian
        if not np.allclose(rho, rho.conj().T):
            warnings.warn("Input not Hermitian; symmetrizing")
            rho = (rho + rho.conj().T) / 2

        # Eigenvalue decomposition
        eigenvalues = eigvalsh(rho)
        eigenvalues = np.real(eigenvalues)

        # Regularize to avoid log(0)
        if regularize:
            eigenvalues = eigenvalues[eigenvalues > 1e-14]

        if len(eigenvalues) == 0:
            return 0.0

        # S = -Σ λ_i log(λ_i)
        entropy = -np.sum(eigenvalues * self.log_func(eigenvalues))
        return np.real(entropy)

    def purity(self, rho: np.ndarray) -> float:
        """Compute purity P = Tr(ρ²).

        Measures how pure vs mixed the state is.
        - P = 1: Pure state
        - P = 1/d: Maximally mixed
        """
        return np.real(np.trace(rho @ rho))

    def __call__(self, rho: np.ndarray) -> float:
        return self.compute(rho)


class EntanglementMeasure:
    """Quantify entanglement between verses."""

    def __init__(self):
        self.vne = VonNeumannEntropy()

    def entropy(self, rho: np.ndarray) -> float:
        """Von Neumann entropy of density matrix."""
        return self.vne.compute(rho)

    def mutual_information(
        self,
        rho_ab: np.ndarray,
        dims: Tuple[int, int]
    ) -> float:
        """Compute mutual information I(A:B) = S(A) + S(B) - S(AB).

        Args:
            rho_ab: Joint density matrix
            dims: (d_A, d_B) dimensions

        Returns:
            Mutual information (non-negative)
        """
        S_ab = self.entropy(rho_ab)
        rho_a = self.partial_trace(rho_ab, subsystem=1, dims=dims)
        rho_b = self.partial_trace(rho_ab, subsystem=0, dims=dims)
        S_a = self.entropy(rho_a)
        S_b = self.entropy(rho_b)

        I = S_a + S_b - S_ab
        return max(0, np.real(I))  # Mutual info is non-negative

    def partial_trace(
        self,
        rho: np.ndarray,
        subsystem: int,
        dims: Tuple[int, int]
    ) -> np.ndarray:
        """Trace out one subsystem (reduced density matrix).

        Tr_B(ρ_{AB}) traces out system B, returning ρ_A.

        Args:
            rho: Full density matrix
            subsystem: Which subsystem to trace out (0 or 1)
            dims: (d_A, d_B) dimensions

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

    def concurrence(self, rho: np.ndarray) -> float:
        """Compute concurrence C (entanglement of 2-qubit state).

        C = max(0, λ_1 - λ_2 - λ_3 - λ_4)

        where λ_i are eigenvalues of R = √√ρ σ_y⊗σ_y ρ* σ_y⊗σ_y √√ρ

        Args:
            rho: 2-qubit density matrix

        Returns:
            Concurrence (0 for separable, 1 for maximally entangled)
        """
        if rho.shape != (4, 4):
            warnings.warn("Concurrence defined for 2-qubit states only")
            return 0.0

        # Pauli Y ⊗ Y
        sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        Y_Y = np.kron(sigma_y, sigma_y)

        # Compute R matrix
        sqrt_rho = expm(0.5 * np.log(rho + 1e-10 * np.eye(4)))
        R = sqrt_rho @ Y_Y @ rho.conj() @ Y_Y @ sqrt_rho

        # Eigenvalues of R (sorted descending)
        eigenvalues = np.sort(eigvalsh(R))[::-1]

        # Concurrence
        C = max(0, eigenvalues[0] - eigenvalues[1] - eigenvalues[2] - eigenvalues[3])
        return np.real(C)

    def negativity(self, rho: np.ndarray, dims: Tuple[int, int]) -> float:
        """Compute negativity (entanglement witness).

        N = (||ρ^{T_B}||_1 - 1) / 2

        where ||·||_1 is trace norm and T_B is partial transpose.

        Args:
            rho: Density matrix
            dims: (d_A, d_B)

        Returns:
            Negativity (0 for separable, >0 for entangled)
        """
        d_A, d_B = dims
        rho_PT = self._partial_transpose(rho, subsystem=1, dims=dims)

        # Eigenvalues of ρ^{T_B}
        eigenvalues = eigvalsh(rho_PT)

        # Trace norm = sum of absolute eigenvalues
        trace_norm = np.sum(np.abs(eigenvalues))

        negativity = (trace_norm - 1) / 2
        return max(0, np.real(negativity))

    def _partial_transpose(
        self,
        rho: np.ndarray,
        subsystem: int,
        dims: Tuple[int, int]
    ) -> np.ndarray:
        """Partial transpose ρ^{T_B}."""
        d_A, d_B = dims
        rho_full = rho.reshape((d_A, d_B, d_A, d_B))

        if subsystem == 1:  # Transpose B
            rho_PT = np.zeros_like(rho_full)
            for i in range(d_A):
                for j in range(d_B):
                    for k in range(d_A):
                        for l in range(d_B):
                            rho_PT[i, l, k, j] = rho_full[i, j, k, l]
        else:  # Transpose A
            rho_PT = np.zeros_like(rho_full)
            for i in range(d_A):
                for j in range(d_B):
                    for k in range(d_A):
                        for l in range(d_B):
                            rho_PT[k, j, i, l] = rho_full[i, j, k, l]

        return rho_PT.reshape(rho.shape)


class BellDetector:
    """Detect Bell pairs (maximally entangled 2-qubit states)."""

    def __init__(self, threshold: float = 0.95):
        """Initialize detector.

        Args:
            threshold: Fidelity threshold for detection (0-1)
        """
        self.threshold = threshold
        self.em = EntanglementMeasure()

        # Bell basis states
        self.bell_states = self._create_bell_basis()

    def _create_bell_basis(self) -> np.ndarray:
        """Create 4 Bell states.

        |Φ+⟩ = (|00⟩ + |11⟩)/√2
        |Φ-⟩ = (|00⟩ - |11⟩)/√2
        |Ψ+⟩ = (|01⟩ + |10⟩)/√2
        |Ψ-⟩ = (|01⟩ - |10⟩)/√2
        """
        bells = []

        # |Φ+⟩
        psi_plus = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        bells.append(psi_plus)

        # |Φ-⟩
        psi_minus = np.array([1, 0, 0, -1], dtype=complex) / np.sqrt(2)
        bells.append(psi_minus)

        # |Ψ+⟩
        psi_plus_01 = np.array([0, 1, 1, 0], dtype=complex) / np.sqrt(2)
        bells.append(psi_plus_01)

        # |Ψ-⟩
        psi_minus_01 = np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)
        bells.append(psi_minus_01)

        return np.array(bells)

    def is_bell_pair(self, state: np.ndarray) -> Tuple[bool, float]:
        """Detect if state is a Bell pair.

        Args:
            state: 4D state vector for 2 qubits

        Returns:
            (is_bell_pair, fidelity) tuple
        """
        state = np.asarray(state, dtype=complex)
        if len(state) != 4:
            return False, 0.0

        state = state / np.linalg.norm(state)

        max_fidelity = 0.0
        for bell in self.bell_states:
            # Fidelity = |⟨ψ|φ⟩|²
            fidelity = np.abs(np.vdot(bell, state)) ** 2
            max_fidelity = max(max_fidelity, fidelity)

        is_bell = max_fidelity > self.threshold
        return is_bell, max_fidelity


class GHZDetector:
    """Detect GHZ states (n-way maximal entanglement)."""

    def __init__(self, n_qubits: int = 3, threshold: float = 0.9):
        """Initialize GHZ detector.

        Args:
            n_qubits: Number of qubits
            threshold: Fidelity threshold
        """
        self.n_qubits = n_qubits
        self.threshold = threshold

    def is_ghz_state(self, state: np.ndarray) -> Tuple[bool, float]:
        """Detect n-qubit GHZ state.

        GHZ_n = (|0⟩^⊗n + |1⟩^⊗n) / √2

        Args:
            state: State vector (length 2^n)

        Returns:
            (is_ghz, fidelity) tuple
        """
        state = np.asarray(state, dtype=complex)
        expected_dim = 2 ** self.n_qubits

        if len(state) != expected_dim:
            return False, 0.0

        state = state / np.linalg.norm(state)

        # GHZ state has only two non-zero amplitudes
        # at |00...0⟩ and |11...1⟩
        ghz = np.zeros(expected_dim, dtype=complex)
        ghz[0] = 1.0 / np.sqrt(2)
        ghz[-1] = 1.0 / np.sqrt(2)

        # Check if amplitudes match GHZ pattern
        nonzero_count = np.sum(np.abs(state) > 1e-6)
        if nonzero_count != 2:
            return False, 0.0

        # Fidelity with ideal GHZ
        fidelity = np.abs(np.vdot(ghz, state)) ** 2

        is_ghz = (fidelity > self.threshold) and np.isclose(
            np.abs(state[0]), 1.0 / np.sqrt(2), atol=0.1
        ) and np.isclose(
            np.abs(state[-1]), 1.0 / np.sqrt(2), atol=0.1
        )

        return is_ghz, fidelity

    def gme_measure(self, state: np.ndarray) -> float:
        """Genuine Multipartite Entanglement (GME) measure.

        Quantifies n-way entanglement (not just 2-way).

        Args:
            state: n-qubit state vector

        Returns:
            GME score (0 to 1)
        """
        state = np.asarray(state, dtype=complex)
        state = state / np.linalg.norm(state)

        # Simplified: check 3-way entanglement
        # (full GME measure is more complex)

        # Create GHZ and check overlap
        expected_dim = 2 ** self.n_qubits
        ghz = np.zeros(expected_dim, dtype=complex)
        ghz[0] = 1.0 / np.sqrt(2)
        ghz[-1] = 1.0 / np.sqrt(2)

        fidelity = np.abs(np.vdot(ghz, state)) ** 2
        return np.real(fidelity)


class EntanglementEntropy:
    """Compute entanglement entropy for bipartitions."""

    @staticmethod
    def bipartition_entropy(
        rho: np.ndarray,
        partition: Tuple[int, ...]
    ) -> float:
        """Compute S_A for bipartition A|B.

        Args:
            rho: Full density matrix
            partition: Indices in subsystem A

        Returns:
            Entanglement entropy
        """
        warnings.warn("Bipartition entropy not fully implemented")
        vne = VonNeumannEntropy()
        return vne.compute(rho)

    @staticmethod
    def average_entanglement(
        rho_list: list,
        weights: Optional[np.ndarray] = None
    ) -> float:
        """Average entanglement over ensemble.

        Args:
            rho_list: List of density matrices
            weights: Optional weights for averaging

        Returns:
            Average entropy
        """
        if weights is None:
            weights = np.ones(len(rho_list)) / len(rho_list)

        vne = VonNeumannEntropy()
        total = sum(
            w * vne.compute(rho)
            for w, rho in zip(weights, rho_list)
        )
        return total
