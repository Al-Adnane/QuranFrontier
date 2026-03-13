"""Quantum Hilbert Space for Qira'at (7 Canonical Readings).

Module 2 of FrontierQu framework implements quantum mechanics for Quranic
exegesis, where 7 canonical readings exist in superposition until measured.

Key components:
- Hilbert Space: 7D superposition of readings
- Tensor Network: Matrix Product States for efficient correlation encoding
- Entanglement: Quantum metrics (entropy, Bell pairs, GHZ states)
- Simulator: GPU-accelerated quantum circuit simulation

Example:
    >>> from frontier_neuro_symbolic.quantum_qiraat import QiraatHilbertSpace
    >>> hs = QiraatHilbertSpace(dimension=7)
    >>> state = hs.uniform_superposition()
    >>> reading = state.measure(hs)  # Collapse to one reading
    >>> print(f"Verse measurement yielded reading {reading}")
"""

from .hilbert_space import (
    QiraatHilbertSpace,
    SuperpositionState,
    BasisVector,
    RecitationRuleTransform,
)

from .tensor_network import (
    MatrixProductState,
    MPS,
    TensorNetworkContraction,
    SymmetryAwareeMPS,
)

from .entanglement import (
    EntanglementMeasure,
    VonNeumannEntropy,
    BellDetector,
    GHZDetector,
    EntanglementEntropy,
)

from .quantum_simulator import (
    QuantumSimulator,
    QuantumCircuit,
    NoiseModel,
    CuQuantumSimulator,
)

__all__ = [
    # Hilbert Space
    "QiraatHilbertSpace",
    "SuperpositionState",
    "BasisVector",
    "RecitationRuleTransform",
    # Tensor Network
    "MatrixProductState",
    "MPS",
    "TensorNetworkContraction",
    "SymmetryAwareeMPS",
    # Entanglement
    "EntanglementMeasure",
    "VonNeumannEntropy",
    "BellDetector",
    "GHZDetector",
    "EntanglementEntropy",
    # Simulator
    "QuantumSimulator",
    "QuantumCircuit",
    "NoiseModel",
    "CuQuantumSimulator",
]

__version__ = "1.0.0"
__author__ = "FrontierQu Development Team"
