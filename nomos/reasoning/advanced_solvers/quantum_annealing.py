"""Quantum annealing-based isnad verification using QUBO formulation."""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class IsnadResult:
    """Result of isnad verification."""

    chain: List[str]
    consistency_score: float
    selected_nodes: Dict[str, bool]
    ground_energy: float


class QuantumAnnealingIsnad:
    """Quantum annealer for isnad (transmission chain) verification.

    Maps isnad DAG to QUBO (Quadratic Unconstrained Binary Optimization):
    - Qubit per transmitter
    - Coupling J_ij for edges (chains)
    - Field h_i = authenticity score
    - Ground state = maximal consistent isnad subgraph

    Falls back to classical solver if D-Wave unavailable.
    """

    def __init__(self, use_dwave: bool = False):
        """Initialize quantum annealer.

        Args:
            use_dwave: Whether to use D-Wave quantum processor (requires credentials).
        """
        self.use_dwave = use_dwave
        self.qubo_cache: Dict = {}

    def generate_qubo(
        self,
        edges: List[Tuple[str, str]],
        authenticity_scores: Dict[str, float],
    ) -> Tuple[np.ndarray, Dict[str, int]]:
        """Generate QUBO matrix for isnad verification.

        QUBO formulation:
        - Energy = Σ h_i x_i + Σ J_ij x_i x_j
        - h_i = -authenticity_score (want to maximize consistent nodes)
        - J_ij = -coupling strength for connected nodes

        Args:
            edges: List of (source, target) transmitter pairs.
            authenticity_scores: Dict of transmitter -> confidence score [0, 1].

        Returns:
            qubo: Numpy array of shape (n_nodes, n_nodes).
            node_to_qubit: Mapping from node name to qubit index.
        """
        # Get unique nodes
        nodes = set()
        for src, tgt in edges:
            nodes.add(src)
            nodes.add(tgt)

        nodes = sorted(list(nodes))
        n_qubits = len(nodes)

        # Map nodes to qubit indices
        node_to_qubit = {node: i for i, node in enumerate(nodes)}

        # Initialize QUBO matrix (symmetric)
        qubo = np.zeros((n_qubits, n_qubits))

        # Set linear terms (h_i): negative of authenticity score
        # (maximizing authenticity = minimizing -authenticity)
        for node, score in authenticity_scores.items():
            if node in node_to_qubit:
                idx = node_to_qubit[node]
                qubo[idx, idx] = -score

        # Set quadratic terms (J_ij): encourage consistency along chains
        for src, tgt in edges:
            if src in node_to_qubit and tgt in node_to_qubit:
                i = node_to_qubit[src]
                j = node_to_qubit[tgt]

                # Coupling strength: encourage edge consistency
                # Both nodes selected together vs. separately
                coupling = -0.5  # Negative = attractive coupling

                qubo[i, j] = coupling
                qubo[j, i] = coupling  # Symmetric

        return qubo, node_to_qubit

    def solve_qubo_classical(self, qubo: np.ndarray) -> Tuple[np.ndarray, float]:
        """Solve QUBO using classical optimization (brute force for small, heuristic for large).

        Args:
            qubo: QUBO matrix of shape (n_qubits, n_qubits).

        Returns:
            x: Solution vector (binary assignments).
            energy: Energy of solution (ground energy estimate).
        """
        n_qubits = qubo.shape[0]

        # For small problems, brute force enumeration
        if n_qubits <= 12:
            best_x = None
            best_energy = float("inf")

            for state in range(2**n_qubits):
                x = np.array([(state >> i) & 1 for i in range(n_qubits)])
                energy = x @ qubo @ x

                if energy < best_energy:
                    best_energy = energy
                    best_x = x

            return best_x, best_energy

        # For larger problems, use greedy heuristic
        else:
            x = np.zeros(n_qubits)

            # Greedy: flip each qubit if it lowers energy
            for iteration in range(10):  # Multiple passes
                for i in range(n_qubits):
                    x_trial = x.copy()
                    x_trial[i] = 1 - x_trial[i]

                    energy_old = x @ qubo @ x
                    energy_new = x_trial @ qubo @ x_trial

                    if energy_new < energy_old:
                        x = x_trial

            energy = x @ qubo @ x
            return x, float(energy)

    def solve_isnad(
        self,
        edges: List[Tuple[str, str]],
        authenticity_scores: Dict[str, float],
        use_dwave: Optional[bool] = None,
    ) -> IsnadResult:
        """Solve isnad verification via QUBO.

        Args:
            edges: Transmission chain edges.
            authenticity_scores: Transmitter confidence scores.
            use_dwave: Override default D-Wave usage.

        Returns:
            IsnadResult with optimal chain and consistency score.
        """
        use_dwave = use_dwave if use_dwave is not None else self.use_dwave

        # Generate QUBO
        qubo, node_to_qubit = self.generate_qubo(edges, authenticity_scores)

        # Solve (fallback to classical if D-Wave unavailable)
        if use_dwave:
            try:
                x, energy = self._solve_dwave(qubo)
            except Exception:
                # Fallback to classical
                x, energy = self.solve_qubo_classical(qubo)
        else:
            x, energy = self.solve_qubo_classical(qubo)

        # Decode solution
        qubit_to_node = {v: k for k, v in node_to_qubit.items()}
        selected_nodes = {
            qubit_to_node[i]: bool(x[i]) for i in range(len(x))
        }
        selected_chain = [
            node for node, selected in selected_nodes.items() if selected
        ]

        # Compute consistency score (normalized by total nodes)
        n_nodes = len(authenticity_scores)
        consistency = 1.0 / (
            1.0 + abs(energy) / n_nodes
        )  # Energy-based consistency metric

        return IsnadResult(
            chain=selected_chain,
            consistency_score=float(consistency),
            selected_nodes=selected_nodes,
            ground_energy=float(energy),
        )

    def _solve_dwave(self, qubo: np.ndarray) -> Tuple[np.ndarray, float]:
        """Solve QUBO using D-Wave quantum annealer.

        Requires D-Wave credentials and ocean-sdk installation.

        Args:
            qubo: QUBO matrix.

        Returns:
            x: Solution vector.
            energy: Solution energy.
        """
        try:
            from dwave.system import DWaveSampler, EmbeddingContext
            from dimod import BinaryQuadraticModel

            # Convert QUBO to BQM
            n = qubo.shape[0]
            linear = {i: qubo[i, i] for i in range(n)}
            quadratic = {
                (i, j): qubo[i, j]
                for i in range(n)
                for j in range(i + 1, n)
                if qubo[i, j] != 0
            }

            bqm = BinaryQuadraticModel(linear, quadratic, 0.0, "BINARY")

            # Sample from D-Wave
            sampler = DWaveSampler()
            response = sampler.sample(bqm, num_reads=100)

            # Get best solution
            solution = response.first.sample
            x = np.array([solution[i] for i in range(n)])
            energy = response.first.energy

            return x, energy

        except ImportError:
            raise RuntimeError(
                "D-Wave not installed. Install with: pip install dwave-ocean-sdk"
            )

    def verify_isnad_authenticity(
        self,
        edges: List[Tuple[str, str]],
        authenticity_scores: Dict[str, float],
        threshold: float = 0.7,
    ) -> Dict[str, any]:
        """Verify isnad authenticity against a threshold.

        Args:
            edges: Transmission chain.
            authenticity_scores: Scores per transmitter.
            threshold: Minimum consistency score to accept chain.

        Returns:
            Verdict with is_authentic boolean and detailed explanation.
        """
        result = self.solve_isnad(edges, authenticity_scores)

        is_authentic = result.consistency_score >= threshold

        return {
            "is_authentic": is_authentic,
            "consistency_score": result.consistency_score,
            "selected_chain": result.chain,
            "ground_energy": result.ground_energy,
            "verdict": "SAHIH" if is_authentic else "DA'IF",
        }

    def analyze_chain_robustness(
        self,
        edges: List[Tuple[str, str]],
        authenticity_scores: Dict[str, float],
    ) -> Dict[str, any]:
        """Analyze robustness of isnad by perturbing scores.

        Args:
            edges: Transmission chain.
            authenticity_scores: Original scores.

        Returns:
            Robustness analysis with sensitivity to score variations.
        """
        baseline = self.solve_isnad(edges, authenticity_scores)

        # Test perturbations
        perturbations = []
        for node in authenticity_scores:
            for delta in [-0.1, 0.1]:
                perturbed_scores = authenticity_scores.copy()
                perturbed_scores[node] = max(
                    0, min(1, perturbed_scores[node] + delta)
                )

                result = self.solve_isnad(edges, perturbed_scores)
                perturbations.append(
                    {
                        "node": node,
                        "delta": delta,
                        "consistency_change": result.consistency_score
                        - baseline.consistency_score,
                    }
                )

        # Compute sensitivity metrics
        sensitivities = [p["consistency_change"] for p in perturbations]
        max_sensitivity = max(abs(s) for s in sensitivities)

        return {
            "baseline_consistency": baseline.consistency_score,
            "max_sensitivity": float(max_sensitivity),
            "is_robust": max_sensitivity < 0.15,  # Arbitrary threshold
            "perturbation_details": perturbations,
        }
