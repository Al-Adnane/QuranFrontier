"""Psychology Models - Complete Collection."""

__version__ = "1.0.0"

from .jungian_archetypes import JungianArchetypesNetwork, create_jungian_archetypes_network
from .freudian_structure import FreudianStructureNetwork, create_freudian_structure_network
from .big_five import BigFiveNetwork, create_big_five_network
from .cognitive_biases import CognitiveBiasesNetwork, create_cognitive_biases_network
from .flow_state import FlowStateNetwork, create_flow_state_network
from .enneagram import EnneagramNetwork, create_enneagram_network
from .shadow_work import ShadowWorkNetwork, create_shadow_work_network
from .spiral_dynamics import SpiralDynamicsNetwork, create_spiral_dynamics_network

__all__ = [
    'JungianArchetypesNetwork', 'create_jungian_archetypes_network',
    'FreudianStructureNetwork', 'create_freudian_structure_network',
    'BigFiveNetwork', 'create_big_five_network',
    'CognitiveBiasesNetwork', 'create_cognitive_biases_network',
    'FlowStateNetwork', 'create_flow_state_network',
    'EnneagramNetwork', 'create_enneagram_network',
    'ShadowWorkNetwork', 'create_shadow_work_network',
    'SpiralDynamicsNetwork', 'create_spiral_dynamics_network',
]
