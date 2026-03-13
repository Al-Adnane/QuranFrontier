"""Three-World Neuro-Symbolic-Categorical Architecture.

A unified framework combining:
- Neural: Transformer-based embeddings for semantic understanding
- Symbolic: Deontic logic and temporal reasoning for constraints
- Categorical: ∞-Topos and Heyting algebra for verification

This architecture is designed for reasoning about Islamic jurisprudence,
combining neural learning with symbolic logic and categorical verification.
"""

from .neural_layer import NeuralLayer
from .symbolic_layer import SymbolicLayer
from .categorical_layer import CategoricalLayer
from .fusion import ThreeWorldArchitecture, FusionGate, FeedbackLoop

__all__ = [
    "NeuralLayer",
    "SymbolicLayer",
    "CategoricalLayer",
    "ThreeWorldArchitecture",
    "FusionGate",
    "FeedbackLoop",
]
