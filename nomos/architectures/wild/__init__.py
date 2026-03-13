"""FrontierQu Wild Models - Cutting Edge Experimental Architectures."""

__version__ = "3.0.0"

from .memetic_evolution import MemeticEvolutionNetwork, create_memetic_network
from .holographic_memory import HolographicMemoryNetwork, create_holographic_network
from .consciousness_network import ConsciousnessIntegrationNetwork, create_consciousness_network
from .causal_intervention import CausalInterventionNetwork, create_causal_network
from .temporal_prediction import TemporalPredictionNetwork, create_temporal_prediction_network
from .fractal_network import FractalNeuralNetwork, create_fractal_network
from .neuromorphic_spiking import NeuromorphicSpikingNetwork, create_neuromorphic_network
from .synesthesia_network import CrossModalSynesthesiaNetwork, create_synesthesia_network
from .dream_network import DreamNetwork, create_dream_network
from .morphogenetic_network import MorphogeneticNetwork, create_morphogenetic_network
from .energy_based import EnergyBasedNetwork, create_energy_based_network
from .neural_ode import NeuralODENetwork, create_neural_ode
from .hyperbolic_network import HyperbolicNeuralNetwork, create_hyperbolic_network
from .mixture_of_experts import MoENetwork, create_moe_network
from .world_model import WorldModel, create_world_model
from .liquid_network import LiquidNeuralNetwork, create_liquid_network
from .state_space import StateSpaceModel, create_state_space_model
from .kolmogorov_arnold import KolmogorovArnoldNetwork, create_kan
from .diffusion_model import DiffusionModel, create_diffusion_model
from .meta_learning import MetaLearner, create_meta_learner
# NEW: Disruptive architectures inspired by world religious traditions
from .codex_network import CodexNetwork, create_codex_network
from .songline_network import SonglineNetwork, create_songline_network
from .abhidhamma_network import AbhidhammaNetwork, create_abhidhamma_network
from .tao_network import TaoNetwork, create_tao_network

__all__ = [
    # Evolution & Memory
    'MemeticEvolutionNetwork', 'create_memetic_network',
    'HolographicMemoryNetwork', 'create_holographic_network',
    
    # Consciousness & Cognition
    'ConsciousnessIntegrationNetwork', 'create_consciousness_network',
    'CausalInterventionNetwork', 'create_causal_network',
    'DreamNetwork', 'create_dream_network',
    
    # Structure & Prediction
    'TemporalPredictionNetwork', 'create_temporal_prediction_network',
    'FractalNeuralNetwork', 'create_fractal_network',
    'MorphogeneticNetwork', 'create_morphogenetic_network',
    
    # Bio-Inspired
    'NeuromorphicSpikingNetwork', 'create_neuromorphic_network',
    'CrossModalSynesthesiaNetwork', 'create_synesthesia_network',
    
    # Modern Architectures
    'EnergyBasedNetwork', 'create_energy_based_network',
    'NeuralODENetwork', 'create_neural_ode',
    'HyperbolicNeuralNetwork', 'create_hyperbolic_network',
    'MoENetwork', 'create_moe_network',
    'WorldModel', 'create_world_model',
    'LiquidNeuralNetwork', 'create_liquid_network',
    'StateSpaceModel', 'create_state_space_model',
    'KolmogorovArnoldNetwork', 'create_kan',
    'DiffusionModel', 'create_diffusion_model',
    'MetaLearner', 'create_meta_learner',
    
    # NEW: Disruptive (World Tradition Inspired)
    'CodexNetwork', 'create_codex_network',
    'SonglineNetwork', 'create_songline_network',
    'AbhidhammaNetwork', 'create_abhidhamma_network',
    'TaoNetwork', 'create_tao_network',
]
