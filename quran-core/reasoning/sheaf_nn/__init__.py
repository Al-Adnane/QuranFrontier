"""Sheaf Neural Networks for Quranic complex.

A topological deep learning framework that respects the categorical structure
of simplicial complexes through sheaf theory. Implements:

1. Sheaf convolution layers (sheaf_layer.py)
   - Restriction maps F_ij: R^{d_in} -> R^{d_out}
   - Message passing with gluing axiom preservation
   - Multi-layer networks

2. Message passing with gluing constraints (message_passing.py)
   - Multi-layer sheaf message passing networks
   - Compatibility checking for gluing axioms
   - Constraint-based regularization

3. Morphological equivariance (equivariance.py)
   - Arabic root-based equivariance
   - Attention boosting for same-root words
   - Root-invariant feature extraction

4. Training pipelines (training.py)
   - Supervised + consistency loss
   - Full training and inference
   - Ensemble training for robustness
"""

from frontier_neuro_symbolic.sheaf_nn.sheaf_layer import (
    SheafConvLayer,
    MultiSheafConvLayer,
    SheafGluingValidator,
)
from frontier_neuro_symbolic.sheaf_nn.message_passing import (
    SheafMessagePassing,
    SheafGluingConstraint,
)
from frontier_neuro_symbolic.sheaf_nn.equivariance import (
    MorphologicalEquivariance,
    RootCompatibilityMatrix,
    MorphologicalEquivarianceLayer,
)
from frontier_neuro_symbolic.sheaf_nn.training import (
    SheafNNTrainer,
    SheafNNEnsembleTrainer,
)

__all__ = [
    "SheafConvLayer",
    "MultiSheafConvLayer",
    "SheafGluingValidator",
    "SheafMessagePassing",
    "SheafGluingConstraint",
    "MorphologicalEquivariance",
    "RootCompatibilityMatrix",
    "MorphologicalEquivarianceLayer",
    "SheafNNTrainer",
    "SheafNNEnsembleTrainer",
]
