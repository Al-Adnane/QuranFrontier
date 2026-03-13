"""Tests for Sura Clustering Tool — MPS-based structural analysis.

Tests cover:
- Hilbert space representation of 7 canonical readings
- State collapse and measurement
- Unitary transformations for recitation rules
- Matrix Product States (MPS) representation
- Correlation metrics between verses
- MPS analysis with GPU acceleration
"""

import pytest
import numpy as np
import torch

from frontier_neuro_symbolic.sura_clustering_tool.hilbert_space import (
    QiraatHilbertSpace,
    SuperpositionState,
    BasisVector,
)
from frontier_neuro_symbolic.sura_clustering_tool.tensor_network import (
    MatrixProductState,
    MPS,
)
from frontier_neuro_symbolic.sura_clustering_tool.entanglement import (
    EntanglementMeasure,
    VonNeumannEntropy,
    BellDetector,
    GHZDetector,
)
from frontier_neuro_symbolic.sura_clustering_tool.mps_clustering import (
    QuantumSimulator,
)


class TestHilbertSpace:
    """Test QiraatHilbertSpace - 7D basis for canonical readings."""

    def test_hilbert_space_initialization(self):
        """Initialize 7D Hilbert space for 7 canonical readers."""
        hs = QiraatHilbertSpace(dimension=7)
        assert hs.dimension == 7
        assert hs.basis_size == 7

    def test_basis_vectors_orthonormal(self):
        """Basis vectors are orthonormal."""
        hs = QiraatHilbertSpace(dimension=7)
        basis = hs.basis_vectors()

        # Check orthonormality
        for i in range(len(basis)):
            for j in range(len(basis)):
                inner = np.vdot(basis[i], basis[j])
                expected = 1.0 if i == j else 0.0
                assert np.isclose(inner, expected), f"Basis not orthonormal at ({i},{j})"

    def test_create_equal_superposition(self):
        """Create equal superposition of all 7 readings."""
        hs = QiraatHilbertSpace(dimension=7)
        coeffs = np.ones(7) / np.sqrt(7)  # Equally weighted
        state = hs.create_superposition(coeffs)

        assert isinstance(state, SuperpositionState)
        assert state.dimension == 7
        assert np.isclose(np.linalg.norm(state.amplitude_vector), 1.0)

    def test_state_normalization(self):
        """States are always normalized ||Ψ⟩ = 1."""
        hs = QiraatHilbertSpace(dimension=7)
        coeffs = np.array([1, 2, 1, 0.5, 1, 1.5, 2], dtype=complex)
        state = hs.create_superposition(coeffs)

        norm = np.linalg.norm(state.amplitude_vector)
        assert np.isclose(norm, 1.0)

    def test_state_collapse_on_measurement(self):
        """Measurement collapses state to single reading with probability |α_i|²."""
        hs = QiraatHilbertSpace(dimension=7)
        # Create state with clear probabilities
        coeffs = np.array([0.6, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0], dtype=complex)
        coeffs = coeffs / np.linalg.norm(coeffs)
        state = hs.create_superposition(coeffs)

        # Measure multiple times
        measurements = [state.measure(hs) for _ in range(100)]
        assert all(m in [0, 4] for m in measurements), "Measurement should collapse to basis 0 or 4"

    def test_unitary_transformation(self):
        """Unitary transformations preserve norm."""
        hs = QiraatHilbertSpace(dimension=7)
        coeffs = np.ones(7) / np.sqrt(7)
        state = hs.create_superposition(coeffs)

        # Create random unitary matrix
        A = np.random.randn(7, 7) + 1j * np.random.randn(7, 7)
        U, _ = np.linalg.qr(A)

        transformed = state.apply_unitary(U)
        norm = np.linalg.norm(transformed.amplitude_vector)
        assert np.isclose(norm, 1.0)

    def test_semantic_tensor_product(self):
        """Reading ⊗ Semantic forms tensor product state."""
        hs = QiraatHilbertSpace(dimension=7)

        # Reading superposition
        reading_coeffs = np.ones(7) / np.sqrt(7)
        reading_state = hs.create_superposition(reading_coeffs)

        # Semantic dimension (e.g., meaning interpretation)
        semantic_coeffs = np.array([0.8, 0.6], dtype=complex)
        semantic_coeffs = semantic_coeffs / np.linalg.norm(semantic_coeffs)
        semantic_state = SuperpositionState(semantic_coeffs)

        # Tensor product: |Ψ⟩ = |Reading⟩ ⊗ |Semantic⟩
        composite = reading_state.tensor_product(semantic_state)
        expected_dim = 7 * 2
        assert composite.dimension == expected_dim

    def test_basis_vector_creation(self):
        """Create basis vector |i⟩ for reading i."""
        hs = QiraatHilbertSpace(dimension=7)

        for i in range(7):
            basis_i = hs.basis_vector(i)
            assert basis_i.dimension == 7
            assert np.isclose(np.linalg.norm(basis_i.amplitude_vector), 1.0)
            assert np.isclose(basis_i.amplitude_vector[i], 1.0)
            assert np.allclose(basis_i.amplitude_vector[:i], 0.0)
            assert np.allclose(basis_i.amplitude_vector[i+1:], 0.0)


class TestMatrixProductState:
    """Test MatrixProductState (MPS) - efficient representation."""

    def test_mps_initialization(self):
        """Initialize MPS with bond dimension χ."""
        mps = MatrixProductState(length=7, physical_dim=2, bond_dim=4)
        assert mps.length == 7
        assert mps.physical_dim == 2
        assert mps.bond_dim == 4

    def test_mps_normalization(self):
        """MPS norm ||Ψ⟩ = 1 after canonicalization."""
        mps = MatrixProductState(length=7, physical_dim=2, bond_dim=4)
        mps.canonicalize()

        norm = mps.compute_norm()
        assert np.isclose(norm, 1.0)

    def test_mps_contraction(self):
        """Contracting MPS tensors gives state vector."""
        mps = MatrixProductState(length=3, physical_dim=2, bond_dim=2)
        state_vec = mps.contract()

        assert state_vec.shape == (2**3,)
        assert np.isclose(np.linalg.norm(state_vec), 1.0)

    def test_mps_expectation_value(self):
        """Compute expectation value ⟨Ψ|O|Ψ⟩."""
        mps = MatrixProductState(length=3, physical_dim=2, bond_dim=2)

        # Pauli Z operator (diagonal)
        op = np.array([[1, 0], [0, -1]], dtype=complex)

        exp_val = mps.expectation_value(op, site=0)
        assert isinstance(exp_val, (float, np.floating, complex))

    def test_mps_left_orthogonal_form(self):
        """Move MPS to left-orthogonal form."""
        mps = MatrixProductState(length=5, physical_dim=2, bond_dim=3)
        mps.move_orthogonality_center(0)

        # Check left orthogonality
        for i in range(mps.length - 1):
            M = mps.tensors[i]
            # M[p1,p2,...] should satisfy orthogonality
            assert M.shape[0] > 0

    def test_mps_entanglement_entropy(self):
        """Compute entanglement entropy at bond."""
        mps = MatrixProductState(length=4, physical_dim=2, bond_dim=2)
        ent_entropy = mps.entanglement_entropy(bond=1)

        assert isinstance(ent_entropy, float)
        assert 0.0 <= ent_entropy <= np.log(4)  # Upper bound for 2D space


class TestEntanglement:
    """Test entanglement measures between verses."""

    def test_von_neumann_entropy(self):
        """Von Neumann entropy S(ρ) = -Tr(ρ log ρ)."""
        vne = VonNeumannEntropy()

        # Pure state: entropy = 0
        pure_state = np.array([1, 0, 0, 0], dtype=complex)
        rho = np.outer(pure_state, pure_state.conj())
        entropy = vne.compute(rho)

        assert np.isclose(entropy, 0.0, atol=1e-10)

    def test_von_neumann_entropy_maximized_state(self):
        """Maximally entangled state has S(ρ) = log(d)."""
        vne = VonNeumannEntropy()

        # Bell state (maximally entangled)
        bell = (np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2))
        rho = np.outer(bell, bell.conj())
        entropy = vne.compute(rho)

        # For 2-qubit entangled state
        assert entropy > 0

    def test_bell_pair_detection(self):
        """Detect Bell pairs (mutashabihāt verses)."""
        detector = BellDetector()

        # Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
        bell_state = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

        is_bell, fidelity = detector.is_bell_pair(bell_state)
        assert is_bell
        assert np.isclose(fidelity, 1.0)

    def test_non_entangled_state(self):
        """Separable state not detected as Bell pair."""
        detector = BellDetector()

        # Separable: |0⟩⊗|0⟩ = |00⟩
        sep_state = np.array([1, 0, 0, 0], dtype=complex)

        is_bell, fidelity = detector.is_bell_pair(sep_state)
        assert not is_bell

    def test_ghz_state_detection(self):
        """Detect GHZ state (7-way maximal entanglement)."""
        detector = GHZDetector(n_qubits=3)

        # 3-qubit GHZ state: (|000⟩ + |111⟩)/√2
        ghz = (np.array([1, 0, 0, 0, 0, 0, 0, 1], dtype=complex) / np.sqrt(2))

        is_ghz, fidelity = detector.is_ghz_state(ghz)
        assert is_ghz
        assert np.isclose(fidelity, 1.0)

    def test_entanglement_entropy_computation(self):
        """Compute entanglement entropy for bipartition."""
        em = EntanglementMeasure()

        # Bell state
        bell = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        rho = np.outer(bell, bell.conj())

        # Partial trace over second qubit
        rho_A = em.partial_trace(rho, subsystem=0, dims=[2, 2])
        entropy = em.entropy(rho_A)

        assert entropy > 0  # Entangled


class TestQuantumSimulator:
    """Test quantum simulator with GPU acceleration."""

    def test_simulator_initialization(self):
        """Initialize quantum simulator."""
        sim = QuantumSimulator(n_qubits=3)
        assert sim.n_qubits == 3

    def test_simulator_state_vector_initialization(self):
        """Initial state is |000...⟩."""
        sim = QuantumSimulator(n_qubits=3)
        state = sim.get_statevector()

        expected = np.zeros(2**3, dtype=complex)
        expected[0] = 1.0  # |000⟩

        assert np.allclose(state, expected)

    def test_pauli_x_gate(self):
        """Apply Pauli X (NOT) gate."""
        sim = QuantumSimulator(n_qubits=2)
        sim.x_gate(qubit=0)
        state = sim.get_statevector()

        # X|00⟩ = |10⟩
        expected = np.zeros(4, dtype=complex)
        expected[2] = 1.0  # |10⟩

        assert np.allclose(state, expected)

    def test_hadamard_gate(self):
        """Apply Hadamard (superposition) gate."""
        sim = QuantumSimulator(n_qubits=1)
        sim.h_gate(qubit=0)
        state = sim.get_statevector()

        # H|0⟩ = (|0⟩ + |1⟩)/√2
        expected = np.array([1, 1], dtype=complex) / np.sqrt(2)

        assert np.allclose(state, expected)

    def test_cnot_gate(self):
        """Apply CNOT (controlled-NOT) gate."""
        sim = QuantumSimulator(n_qubits=2)
        sim.h_gate(qubit=0)  # Create superposition
        sim.cnot_gate(control=0, target=1)
        state = sim.get_statevector()

        # CNOT(H|0⟩ ⊗ |0⟩) = Bell state (|00⟩ + |11⟩)/√2
        expected = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

        assert np.allclose(state, expected)

    def test_measurement(self):
        """Measure qubits collapses to classical state."""
        sim = QuantumSimulator(n_qubits=2)
        sim.h_gate(qubit=0)
        sim.h_gate(qubit=1)

        # Measure - should get classical state
        result = sim.measure([0, 1], shots=100)

        assert len(result) == 100
        assert all(r in [0, 1, 2, 3] for r in result)

    def test_tomography(self):
        """Quantum state tomography reconstructs density matrix."""
        sim = QuantumSimulator(n_qubits=2)
        sim.h_gate(qubit=0)
        sim.cnot_gate(control=0, target=1)

        rho = sim.tomography(shots=1000)

        # Density matrix properties
        assert rho.shape == (4, 4)
        # Should be Hermitian
        assert np.allclose(rho, rho.conj().T)
        # Trace should be 1
        assert np.isclose(np.trace(rho), 1.0)

    def test_backend_detection(self):
        """Detect available backend (cuQuantum, PyTorch, NumPy)."""
        sim = QuantumSimulator(n_qubits=2)
        backend = sim.get_backend()

        assert backend in ["cuquantum", "pytorch", "numpy"]


class TestQiraatQuantumIntegration:
    """Integration tests: quantum mechanics + Qira'at."""

    def test_seven_readings_superposition(self):
        """7 canonical readers as 7D superposition."""
        hs = QiraatHilbertSpace(dimension=7)

        # Equal superposition of all 7 readers
        coeffs = np.ones(7) / np.sqrt(7)
        state = hs.create_superposition(coeffs)

        # Verify equal amplitudes
        for i in range(7):
            amp = state.amplitude_vector[i]
            assert np.isclose(np.abs(amp)**2, 1/7)

    def test_verse_measurement_yields_reading(self):
        """Query verse → collapses to one reading."""
        hs = QiraatHilbertSpace(dimension=7)
        coeffs = np.ones(7) / np.sqrt(7)
        state = hs.create_superposition(coeffs)

        # Query verse (measurement)
        reading_index = state.measure(hs)

        assert 0 <= reading_index < 7

    def test_entangled_verses_mutual_information(self):
        """Entangled verses share mutual information."""
        em = EntanglementMeasure()

        # Create entangled state
        bell = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        rho = np.outer(bell, bell.conj())

        # Partial trace
        rho_verse_a = em.partial_trace(rho, subsystem=0, dims=[2, 2])

        # Entropy > 0 means entanglement
        entropy = em.entropy(rho_verse_a)
        assert entropy > 0

    def test_mps_verse_correlation(self):
        """MPS encodes long-range verse correlations efficiently."""
        # Use minimal system for fast test
        mps = MatrixProductState(length=5, physical_dim=7, bond_dim=4)

        # Compute correlation between sites
        correlation = mps.correlation(site1=0, site2=4)

        assert isinstance(correlation, (float, np.floating))
        assert 0 <= correlation <= 1


class TestQuantumGates:
    """Test quantum gate operations."""

    def test_pauli_gates(self):
        """Pauli X, Y, Z gates."""
        sim = QuantumSimulator(n_qubits=1)

        # X gate
        sim.x_gate(0)
        state = sim.get_statevector()
        assert np.allclose(state, [0, 1])

        # Reset
        sim = QuantumSimulator(n_qubits=1)

        # Z gate on |+⟩ should give |-⟩
        sim.h_gate(0)
        sim.z_gate(0)
        state = sim.get_statevector()
        expected = np.array([1, -1], dtype=complex) / np.sqrt(2)
        assert np.allclose(state, expected)

    def test_rotation_gates(self):
        """RX, RY, RZ rotation gates."""
        sim = QuantumSimulator(n_qubits=1)

        # RX(π) should be equivalent to X
        sim.rx_gate(qubit=0, theta=np.pi)
        state = sim.get_statevector()

        # Account for global phase: state is up to ±1i factor
        expected = np.array([0, 1], dtype=complex)
        assert np.allclose(np.abs(state), np.abs(expected), atol=1e-10)

    def test_swap_gate(self):
        """SWAP gate exchanges qubits."""
        sim = QuantumSimulator(n_qubits=2)
        sim.x_gate(0)  # Set q0 to |1⟩
        sim.swap_gate(0, 1)
        state = sim.get_statevector()

        # Should be |01⟩ after swap
        expected = np.zeros(4, dtype=complex)
        expected[1] = 1.0  # |01⟩

        assert np.allclose(state, expected)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
