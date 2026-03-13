"""Quantum Superposition Embedding - Quantum NLP Representations.

This model implements quantum-inspired text embeddings where meanings
exist in superposition until "measured" (queried). Uses Hilbert space
representations and quantum operations.

Architecture:
    State Vector: |ψ⟩ = Σ α_i |meaning_i⟩ in Hilbert space
    Superposition: Multiple meanings coexist with amplitudes
    Measurement: Collapse to specific meaning based on query
    Interference: Meanings can interfere constructively/destructively
    Entanglement: Correlated meanings across texts

Based on frontier_neuro_symbolic.quantum_qiraat for Qira'at superposition.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class QuantumState:
    """Quantum state representation."""
    state_vector: torch.Tensor      # |ψ⟩ in Hilbert space
    basis_states: List[str]          # Basis state labels
    amplitudes: torch.Tensor         # Complex amplitudes (real, imag)
    probabilities: torch.Tensor      # |α_i|^2
    phase: torch.Tensor              # Phase angles


@dataclass
class MeasurementResult:
    """Result of quantum measurement."""
    collapsed_state: str
    probability: float
    post_measurement_state: torch.Tensor
    all_outcomes: List[Tuple[str, float]]


class HilbertSpaceEmbedding(nn.Module):
    """Embeds text into Hilbert space for quantum operations."""
    
    def __init__(
        self,
        vocab_size: int,
        hilbert_dim: int = 64,
        num_basis_states: int = 10
    ):
        super().__init__()
        
        self.hilbert_dim = hilbert_dim
        self.num_basis_states = num_basis_states
        
        # Word embeddings as state vectors
        self.word_embed = nn.Embedding(vocab_size, hilbert_dim * 2)  # Real + Imag
        
        # Basis state embeddings
        self.basis_embed = nn.Embedding(num_basis_states, hilbert_dim)
        
        # Phase embeddings
        self.phase_embed = nn.Embedding(vocab_size, hilbert_dim)
        
    def forward(
        self,
        input_ids: torch.Tensor
    ) -> QuantumState:
        """Create quantum state from text.
        
        Args:
            input_ids: [batch, seq_len] token ids
        Returns:
            QuantumState representing the text
        """
        batch_size, seq_len = input_ids.shape
        
        # Get word embeddings (real + imaginary parts)
        word_emb = self.word_embed(input_ids)  # [batch, seq_len, hilbert*2]
        
        # Split into real and imaginary
        real = word_emb[:, :, :self.hilbert_dim]
        imag = word_emb[:, :, self.hilbert_dim:]
        
        # Create complex state vector (superposition of word states)
        # Normalize to unit vector
        state_vector = torch.complex(real, imag)
        
        # Mean pooling (creates superposition of word meanings)
        mask = (input_ids != 0).unsqueeze(-1).float()
        state_pooled = (state_vector * mask).sum(dim=1) / (mask.sum(dim=1) + 1e-9)
        
        # Normalize to unit vector (quantum states must be normalized)
        norm = torch.norm(state_pooled, dim=-1, keepdim=True) + 1e-9
        state_normalized = state_pooled / norm
        
        # Compute probabilities |α_i|^2
        probabilities = torch.abs(state_normalized) ** 2
        
        # Compute phase
        phase = torch.angle(state_normalized)
        
        return QuantumState(
            state_vector=state_normalized,
            basis_states=[f"|{i}⟩" for i in range(self.hilbert_dim)],
            amplitudes=torch.stack([real.mean(dim=1), imag.mean(dim=1)], dim=-1),
            probabilities=probabilities,
            phase=phase
        )


class QuantumSuperposition(nn.Module):
    """Creates and manipulates superpositions of meanings."""
    
    def __init__(self, hilbert_dim: int):
        super().__init__()
        self.hilbert_dim = hilbert_dim
        
        # Superposition weights (learnable)
        self.superposition_weight = nn.Parameter(torch.ones(hilbert_dim))
        
    def create_superposition(
        self,
        states: List[QuantumState],
        weights: Optional[torch.Tensor] = None
    ) -> QuantumState:
        """Create superposition of multiple quantum states.
        
        |ψ⟩ = Σ w_i |ψ_i⟩ / normalization
        
        Args:
            states: List of QuantumState to superpose
            weights: Optional weights for each state
        Returns:
            Combined QuantumState
        """
        if len(states) == 0:
            raise ValueError("Need at least one state")
        
        # Stack state vectors
        stacked = torch.stack([s.state_vector for s in states], dim=0)
        
        # Apply weights
        if weights is None:
            weights = torch.ones(len(states), device=stacked.device)
        
        # Weighted superposition
        superposed = (stacked * weights.view(-1, 1, 1)).sum(dim=0)
        
        # Normalize
        norm = torch.norm(superposed, dim=-1, keepdim=True) + 1e-9
        normalized = superposed / norm
        
        # Compute probabilities
        probabilities = torch.abs(normalized) ** 2
        
        return QuantumState(
            state_vector=normalized,
            basis_states=states[0].basis_states,
            amplitudes=torch.stack([normalized.real, normalized.imag], dim=-1),
            probabilities=probabilities,
            phase=torch.angle(normalized)
        )
    
    def apply_unitary(
        self,
        state: QuantumState,
        unitary_matrix: torch.Tensor
    ) -> QuantumState:
        """Apply unitary transformation to state.
        
        |ψ'⟩ = U|ψ⟩ where U is unitary (U†U = I)
        
        Args:
            state: Input quantum state
            unitary_matrix: [hilbert_dim, hilbert_dim] unitary matrix
        Returns:
            Transformed QuantumState
        """
        # Apply unitary
        new_state = unitary_matrix @ state.state_vector.unsqueeze(-1)
        new_state = new_state.squeeze(-1)
        
        # Normalize
        norm = torch.norm(new_state, dim=-1, keepdim=True) + 1e-9
        new_state = new_state / norm
        
        return QuantumState(
            state_vector=new_state,
            basis_states=state.basis_states,
            amplitudes=torch.stack([new_state.real, new_state.imag], dim=-1),
            probabilities=torch.abs(new_state) ** 2,
            phase=torch.angle(new_state)
        )


class QuantumMeasurement(nn.Module):
    """Implements quantum measurement (state collapse)."""
    
    def __init__(self, hilbert_dim: int):
        super().__init__()
        self.hilbert_dim = hilbert_dim
        
    def measure(
        self,
        state: QuantumState,
        basis: Optional[torch.Tensor] = None,
        deterministic: bool = False
    ) -> MeasurementResult:
        """Measure quantum state (collapse to basis state).
        
        Args:
            state: Quantum state to measure
            basis: Optional measurement basis (default: computational)
            deterministic: If True, return most probable outcome
        Returns:
            MeasurementResult with collapsed state
        """
        probs = state.probabilities
        
        if deterministic:
            # Return most probable outcome
            outcome_idx = probs.argmax(dim=-1)
        else:
            # Sample from probability distribution
            # Convert to numpy for multinomial
            probs_np = probs.cpu().numpy()
            outcome_idx = torch.multinomial(probs, num_samples=1)
        
        outcome_idx = outcome_idx.item() if outcome_idx.numel() == 1 else outcome_idx
        
        # Create collapsed state (basis vector)
        collapsed = torch.zeros_like(state.state_vector)
        if isinstance(outcome_idx, int):
            collapsed[outcome_idx] = 1.0
            probability = probs[outcome_idx].item()
            collapsed_state = state.basis_states[outcome_idx]
        else:
            collapsed.scatter_(1, outcome_idx.unsqueeze(-1), 1.0)
            probability = probs.gather(1, outcome_idx.unsqueeze(-1)).squeeze(-1)
            collapsed_state = [state.basis_states[i] for i in outcome_idx.tolist()]
        
        # Compute all possible outcomes
        all_outcomes = []
        if isinstance(probs, torch.Tensor) and probs.dim() == 1:
            for i, (p, basis) in enumerate(zip(probs.tolist(), state.basis_states)):
                if p > 0.01:  # Only include significant outcomes
                    all_outcomes.append((basis, p))
        
        return MeasurementResult(
            collapsed_state=collapsed_state,
            probability=probability,
            post_measurement_state=collapsed,
            all_outcomes=all_outcomes
        )


class QuantumInterference(nn.Module):
    """Implements quantum interference between states."""
    
    def __init__(self, hilbert_dim: int):
        super().__init__()
        self.hilbert_dim = hilbert_dim
        
    def interfere(
        self,
        state1: QuantumState,
        state2: QuantumState,
        phase_shift: float = 0.0
    ) -> QuantumState:
        """Create interference between two states.
        
        |ψ⟩ = (|ψ₁⟩ + e^{iφ}|ψ₂⟩) / √2
        
        Args:
            state1: First quantum state
            state2: Second quantum state
            phase_shift: Phase difference φ
        Returns:
            Interfered QuantumState
        """
        # Apply phase shift to second state
        phase_factor = torch.complex(
            torch.cos(torch.tensor(phase_shift)),
            torch.sin(torch.tensor(phase_shift))
        )
        phase_factor = phase_factor.to(state2.state_vector.device)
        
        # Superpose with phase
        interfered = (state1.state_vector + phase_factor * state2.state_vector) / np.sqrt(2)
        
        # Normalize
        norm = torch.norm(interfered, dim=-1, keepdim=True) + 1e-9
        interfered = interfered / norm
        
        return QuantumState(
            state_vector=interfered,
            basis_states=state1.basis_states,
            amplitudes=torch.stack([interfered.real, interfered.imag], dim=-1),
            probabilities=torch.abs(interfered) ** 2,
            phase=torch.angle(interfered)
        )


class QuantumEntanglement(nn.Module):
    """Creates entangled states between texts."""
    
    def __init__(self, hilbert_dim: int):
        super().__init__()
        self.hilbert_dim = hilbert_dim
        
        # Entanglement parameters
        self.entangle_weight = nn.Parameter(torch.ones(hilbert_dim, hilbert_dim))
        
    def create_entangled_state(
        self,
        state1: QuantumState,
        state2: QuantumState
    ) -> torch.Tensor:
        """Create entangled state from two inputs.
        
        |Ψ⟩ = Σ α_ij |i⟩⊗|j⟩ (bipartite entanglement)
        
        Args:
            state1: First quantum state
            state2: Second quantum state
        Returns:
            Entangled state vector in tensor product space
        """
        # Tensor product of states
        # |ψ₁⟩⊗|ψ₂⟩
        psi1 = state1.state_vector.unsqueeze(-1)  # [batch, dim, 1]
        psi2 = state2.state_vector.unsqueeze(-2)  # [batch, 1, dim]
        
        # Outer product = tensor product
        entangled = psi1 @ psi2  # [batch, dim, dim]
        
        # Apply entanglement weights
        entangled = entangled * self.entangle_weight.unsqueeze(0)
        
        # Normalize
        norm = torch.norm(entangled, dim=(-2, -1), keepdim=True) + 1e-9
        entangled = entangled / norm
        
        return entangled
    
    def bell_state(self) -> torch.Tensor:
        """Create maximally entangled Bell state.
        
        |Φ+⟩ = (|00⟩ + |11⟩) / √2
        """
        bell = torch.zeros(self.hilbert_dim, self.hilbert_dim, dtype=torch.complex64)
        bell[0, 0] = 1 / np.sqrt(2)
        bell[-1, -1] = 1 / np.sqrt(2)
        return bell


class QuantumSuperpositionEmbedding(nn.Module):
    """Main Quantum Superposition Embedding model.
    
    Provides quantum-inspired text representations with:
    - Superposition of meanings
    - Measurement-based query resolution
    - Interference for semantic combination
    - Entanglement for cross-text correlations
    """
    
    def __init__(
        self,
        vocab_size: int,
        hilbert_dim: int = 64,
        num_basis_states: int = 10
    ):
        super().__init__()
        
        self.embedding = HilbertSpaceEmbedding(
            vocab_size, hilbert_dim, num_basis_states
        )
        self.superposition = QuantumSuperposition(hilbert_dim)
        self.measurement = QuantumMeasurement(hilbert_dim)
        self.interference = QuantumInterference(hilbert_dim)
        self.entanglement = QuantumEntanglement(hilbert_dim)
        
        self.hilbert_dim = hilbert_dim
        
        # Learnable unitary transformations
        self.unitaries = nn.ParameterList([
            nn.Parameter(self._random_unitary(hilbert_dim))
            for _ in range(4)
        ])
        
    def _random_unitary(self, dim: int) -> torch.Tensor:
        """Generate random unitary matrix."""
        # QR decomposition of random complex matrix
        real = torch.randn(dim, dim)
        imag = torch.randn(dim, dim)
        complex_matrix = torch.complex(real, imag)
        
        Q, R = torch.linalg.qr(complex_matrix)
        
        # Make R have positive diagonal
        Lambda = torch.diag(R.diag() / torch.abs(R.diag()))
        return Q @ Lambda
    
    def encode(
        self,
        input_ids: torch.Tensor
    ) -> QuantumState:
        """Encode text as quantum state.
        
        Args:
            input_ids: [batch, seq_len] token ids
        Returns:
            QuantumState representation
        """
        return self.embedding(input_ids)
    
    def query(
        self,
        text_state: QuantumState,
        query_ids: torch.Tensor,
        k: int = 5
    ) -> MeasurementResult:
        """Query text via quantum measurement.
        
        Args:
            text_state: Quantum state of text
            query_ids: Query token ids (defines measurement basis)
            k: Number of top outcomes to return
        Returns:
            MeasurementResult with query answers
        """
        # Encode query as measurement basis
        query_state = self.embedding(query_ids)
        
        # Compute overlap (inner product)
        overlap = torch.abs((text_state.state_vector.conj() * query_state.state_vector).sum(dim=-1)) ** 2
        
        # Create measurement outcomes
        all_outcomes = [
            (f"outcome_{i}", overlap[0, i].item())
            for i in range(min(k, self.hilbert_dim))
        ]
        all_outcomes.sort(key=lambda x: -x[1])
        
        # Measure
        result = self.measurement.measure(text_state, deterministic=True)
        result.all_outcomes = all_outcomes[:k]
        
        return result
    
    def combine_meanings(
        self,
        states: List[QuantumState],
        method: str = "superposition"
    ) -> QuantumState:
        """Combine multiple meaning states.
        
        Args:
            states: List of quantum states to combine
            method: "superposition", "interference", or "entangle"
        Returns:
            Combined QuantumState
        """
        if method == "superposition":
            return self.superposition.create_superposition(states)
        elif method == "interference":
            if len(states) >= 2:
                result = states[0]
                for s in states[1:]:
                    result = self.interference.interfere(result, s)
                return result
        elif method == "entangle":
            if len(states) >= 2:
                return QuantumState(
                    state_vector=self.entanglement.create_entangled_state(states[0], states[1]).flatten(),
                    basis_states=states[0].basis_states,
                    amplitudes=torch.zeros(self.hilbert_dim, 2),
                    probabilities=torch.zeros(self.hilbert_dim),
                    phase=torch.zeros(self.hilbert_dim)
                )
        
        return states[0]
    
    def forward(
        self,
        input_ids: torch.Tensor,
        query_ids: Optional[torch.Tensor] = None
    ) -> Dict[str, Any]:
        """Forward pass.
        
        Args:
            input_ids: [batch, seq_len] text token ids
            query_ids: Optional [batch, query_len] query tokens
        Returns:
            Dict with quantum state and optional measurement
        """
        # Encode text
        state = self.encode(input_ids)
        
        result = {
            'state_vector': state.state_vector,
            'probabilities': state.probabilities,
            'phase': state.phase
        }
        
        # Apply unitary transformations
        for U in self.unitaries:
            state = self.superposition.apply_unitary(state, U)
        
        result['transformed_state'] = state.state_vector
        
        # Measure if query provided
        if query_ids is not None:
            measurement = self.query(state, query_ids)
            result['measurement'] = {
                'collapsed_state': measurement.collapsed_state,
                'probability': measurement.probability,
                'outcomes': measurement.all_outcomes
            }
        
        return result


def create_quantum_embedding(
    vocab_size: int = 30000,
    hilbert_dim: int = 64
) -> QuantumSuperpositionEmbedding:
    """Create QuantumSuperpositionEmbedding."""
    return QuantumSuperpositionEmbedding(
        vocab_size=vocab_size,
        hilbert_dim=hilbert_dim
    )
