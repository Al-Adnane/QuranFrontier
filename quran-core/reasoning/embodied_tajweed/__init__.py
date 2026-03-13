"""
Embodied Tajweed: Morphogenetic Field PDEs for Quranic Recitation.

Implements multimodal learning combining:
1. Morphogenetic PDEs (vocal tract dynamics)
2. Active inference (predictive processing)
3. Articulatory phonetics (makharij)
4. Combined loss functions (semantic + physical)

This module enables fine-tuning of Quranic recitations to preserve meaning
while respecting tajweed phonetic rules.
"""

from .vocal_tract import MorphogeneticField, VocalTractManifold
from .active_inference import ActiveInference, VariationalFreeEnergy, PrecisionWeighting
from .articulatory_features import TajweedPhonetics, AcousticFeatureExtractor
from .embodied_loss import (
    EmbodiedLoss,
    SemanticLoss,
    TajweedLoss,
    ArticulatoryConstraintLoss,
    ProgressiveLoss,
)

__all__ = [
    "MorphogeneticField",
    "VocalTractManifold",
    "ActiveInference",
    "VariationalFreeEnergy",
    "PrecisionWeighting",
    "TajweedPhonetics",
    "AcousticFeatureExtractor",
    "EmbodiedLoss",
    "SemanticLoss",
    "TajweedLoss",
    "ArticulatoryConstraintLoss",
    "ProgressiveLoss",
]
