"""Sura Clustering Tool — MPS-based analysis of Quranic structural patterns.

Analyzes the 7 canonical readings (Qira'at) of Quranic verses using
Matrix Product State (MPS) tensor networks to identify structural
correlations between surahs.

Key components:
- Hilbert Space: 7D representation of canonical readings
- Tensor Network: Matrix Product States for efficient correlation encoding
- Entanglement: Correlation metrics (entropy, state overlap, mutual information)
- Clustering: MPS-based analysis for surah structure relationships

Example:
    >>> from frontier_neuro_symbolic.sura_clustering_tool import QiraatHilbertSpace
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

from .mps_clustering import (
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
