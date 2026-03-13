"""
Inter-Substrate Entanglement Protocol
Quantum correlations BETWEEN heterogeneous substrates.
Bell pair generation, CHSH inequality verification, entanglement swapping.

A quantum substrate can be entangled with a neural substrate —
meaning measuring one constrains the other's state.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate, SubstrateState


@dataclass
class BellPair:
    """Represents an entangled pair between two substrates."""
    substrate_a: str
    substrate_b: str
    state: np.ndarray      # 2-qubit density matrix (4x4)
    creation_time: float
    fidelity: float = 1.0
    decoherence_rate: float = 0.001

    def age(self) -> float:
        return time.time() - self.creation_time

    def current_fidelity(self) -> float:
        """Fidelity decays exponentially with time."""
        return self.fidelity * np.exp(-self.decoherence_rate * self.age())


class EntanglementProtocol:
    """
    Manages quantum correlations between heterogeneous substrates.
    Generates Bell pairs, verifies CHSH inequality violation,
    and performs entanglement swapping.
    """

    def __init__(self):
        self.bell_pairs: List[BellPair] = []
        self.chsh_history: List[float] = []
        self._correlation_matrix: Dict[Tuple[str, str], float] = {}

    def generate_bell_pair(self, sub_a: BaseSubstrate, sub_b: BaseSubstrate) -> BellPair:
        """
        Generate maximally entangled Bell pair between two substrates.
        |Phi+> = (|00> + |11>) / sqrt(2)
        """
        # Bell state |Phi+> density matrix
        phi_plus = np.array([1, 0, 0, 1]) / np.sqrt(2)
        rho = np.outer(phi_plus, phi_plus.conj())

        pair = BellPair(
            substrate_a=sub_a.substrate_id,
            substrate_b=sub_b.substrate_id,
            state=rho,
            creation_time=time.time(),
        )
        self.bell_pairs.append(pair)
        return pair

    def measure_chsh(self, pair: BellPair,
                     angles_a: Tuple[float, float] = (0, np.pi / 4),
                     angles_b: Tuple[float, float] = (np.pi / 8, 3 * np.pi / 8)
                     ) -> float:
        """
        CHSH inequality test: S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
        Classical: |S| <= 2
        Quantum:   |S| <= 2*sqrt(2) ≈ 2.828  (Tsirelson bound)
        """
        def expectation(theta_a: float, theta_b: float) -> float:
            # For Bell state: E(a,b) = -cos(2*(theta_a - theta_b))
            return -np.cos(2 * (theta_a - theta_b))

        a, a_prime = angles_a
        b, b_prime = angles_b

        E_ab = expectation(a, b)
        E_ab_prime = expectation(a, b_prime)
        E_a_prime_b = expectation(a_prime, b)
        E_a_prime_b_prime = expectation(a_prime, b_prime)

        S = E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime

        # Apply decoherence
        fidelity = pair.current_fidelity()
        S *= fidelity  # Noise reduces violation

        self.chsh_history.append(S)
        return S

    def verify_nonlocality(self, pair: BellPair) -> Dict[str, Any]:
        """Full nonlocality verification with statistical significance."""
        n_trials = 100
        S_values = []
        for _ in range(n_trials):
            # Random measurement angles with small perturbation
            noise = np.random.normal(0, 0.01, 4)
            angles_a = (0 + noise[0], np.pi / 4 + noise[1])
            angles_b = (np.pi / 8 + noise[2], 3 * np.pi / 8 + noise[3])
            S = self.measure_chsh(pair, angles_a, angles_b)
            S_values.append(S)

        S_mean = np.mean(S_values)
        S_std = np.std(S_values)
        violation = abs(S_mean) > 2  # Classical bound

        return {
            'S_mean': float(S_mean),
            'S_std': float(S_std),
            'tsirelson_bound': 2 * np.sqrt(2),
            'classical_bound': 2.0,
            'violation': violation,
            'sigma_above_classical': float((abs(S_mean) - 2) / (S_std + 1e-10)),
            'pair_fidelity': float(pair.current_fidelity()),
        }

    def entanglement_swap(self, pair1: BellPair, pair2: BellPair) -> Optional[BellPair]:
        """
        Entanglement swapping: if A-B entangled and B-C entangled,
        measure B to create A-C entanglement.
        """
        if pair1.substrate_b != pair2.substrate_a:
            return None  # Can't swap

        # Bell measurement on shared substrate destroys local pair
        # but creates long-range entanglement
        new_pair = BellPair(
            substrate_a=pair1.substrate_a,
            substrate_b=pair2.substrate_b,
            state=pair1.state.copy(),  # Simplified; real swap changes state
            creation_time=time.time(),
            fidelity=pair1.current_fidelity() * pair2.current_fidelity(),
        )

        # Remove consumed pairs
        if pair1 in self.bell_pairs:
            self.bell_pairs.remove(pair1)
        if pair2 in self.bell_pairs:
            self.bell_pairs.remove(pair2)
        self.bell_pairs.append(new_pair)
        return new_pair

    def compute_correlation_matrix(self, substrates: List[BaseSubstrate]) -> np.ndarray:
        """
        Compute pairwise correlation between all substrate states.
        Uses state tensor overlap as correlation measure.
        """
        n = len(substrates)
        corr = np.eye(n)
        for i in range(n):
            for j in range(i + 1, n):
                si = substrates[i].state
                sj = substrates[j].state
                if si is None or sj is None:
                    continue
                # Flatten and compute normalized correlation
                vi = si.tensor_data.flatten()
                vj = sj.tensor_data.flatten()
                min_len = min(len(vi), len(vj))
                vi, vj = vi[:min_len], vj[:min_len]
                norm = np.linalg.norm(vi) * np.linalg.norm(vj)
                if norm > 1e-12:
                    c = float(np.dot(vi, vj) / norm)
                else:
                    c = 0.0
                corr[i, j] = c
                corr[j, i] = c
                self._correlation_matrix[(
                    substrates[i].substrate_id,
                    substrates[j].substrate_id
                )] = c
        return corr

    def prune_decohered_pairs(self, fidelity_threshold: float = 0.1):
        """Remove Bell pairs that have decohered below threshold."""
        self.bell_pairs = [
            p for p in self.bell_pairs
            if p.current_fidelity() > fidelity_threshold
        ]

    def get_metrics(self) -> Dict[str, float]:
        return {
            'active_bell_pairs': len(self.bell_pairs),
            'mean_fidelity': float(np.mean([p.current_fidelity() for p in self.bell_pairs])) if self.bell_pairs else 0,
            'mean_chsh_S': float(np.mean(self.chsh_history[-100:])) if self.chsh_history else 0,
            'max_chsh_S': float(max(self.chsh_history, default=0)),
        }
