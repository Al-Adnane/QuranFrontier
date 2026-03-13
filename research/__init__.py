"""Research Modules - Complete Collection.

All Tier 2 research implementations - 100% wired.
"""
__version__ = "1.0.0"

# NAS
from .nas.search_controller import NeuralArchitectureSearch
# Meta-Learning  
from .meta_learning.maml import MAML
# Causal
from .causal.discovery import CausalDiscovery
# Uncertainty
from .uncertainty.bayesian import BayesianUncertainty
# XAI
from .xai.saliency import SaliencyMaps
# Continual
from .continual.replay import ContinualReplay
# Federated
from .federated.aggregation import FederatedLearning
# Neuro-Symbolic
from .neuro_symbolic.integration import NeuroSymbolicReasoner
# Quantum-Classical
from .quantum_classical.hybrid import QuantumClassicalTrainer
# Brain-Computer
from .brain_computer.architecture import BrainComputerModel
# Evolutionary
from .evolutionary.search import EvolutionarySearch
# Multi-Agent
from .multi_agent.collaboration import MultiAgentCollaboration
# Self-Improving
from .self_improving.meta import SelfImprovingModel
# Cross-Lingual
from .cross_lingual.embeddings import CrossLingualEmbeddings

__all__ = [
    'NeuralArchitectureSearch',
    'MAML',
    'CausalDiscovery',
    'BayesianUncertainty',
    'SaliencyMaps',
    'ContinualReplay',
    'FederatedLearning',
    'NeuroSymbolicReasoner',
    'QuantumClassicalTrainer',
    'BrainComputerModel',
    'EvolutionarySearch',
    'MultiAgentCollaboration',
    'SelfImprovingModel',
    'CrossLingualEmbeddings',
]
