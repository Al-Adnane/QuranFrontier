"""Biology Models - Complete Collection."""

__version__ = "1.0.0"

from .dna import DNANetwork, create_dna_network
from .plasticity import NeuralPlasticityNetwork, create_neural_plasticity_network
from .evolution import EvolutionNetwork, create_evolution_network
from .immune import ImmuneNetwork, create_immune_network
from .metabolic import MetabolicNetwork, create_metabolic_network
from .neuroscience import NeuroscienceNetwork, create_neuroscience_network
from .genetics import GeneticsNetwork, create_genetics_network

__all__ = [
    'DNANetwork', 'create_dna_network',
    'NeuralPlasticityNetwork', 'create_neural_plasticity_network',
    'EvolutionNetwork', 'create_evolution_network',
    'ImmuneNetwork', 'create_immune_network',
    'MetabolicNetwork', 'create_metabolic_network',
    'NeuroscienceNetwork', 'create_neuroscience_network',
    'GeneticsNetwork', 'create_genetics_network',
]
