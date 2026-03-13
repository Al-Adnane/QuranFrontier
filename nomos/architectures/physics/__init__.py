"""Physics Models - Complete Collection."""

__version__ = "1.0.0"

from .quantum_field import QuantumFieldNetwork, create_quantum_field_network
from .relativity import RelativityNetwork, create_relativity_network
from .thermodynamics import ThermodynamicsNetwork, create_thermodynamics_network
from .electromagnetic import ElectromagneticNetwork, create_electromagnetic_network
from .string_theory import StringTheoryNetwork, create_string_theory_network
from .particle import ParticlePhysicsNetwork, create_particle_physics_network

__all__ = [
    'QuantumFieldNetwork', 'create_quantum_field_network',
    'RelativityNetwork', 'create_relativity_network',
    'ThermodynamicsNetwork', 'create_thermodynamics_network',
    'ElectromagneticNetwork', 'create_electromagnetic_network',
    'StringTheoryNetwork', 'create_string_theory_network',
    'ParticlePhysicsNetwork', 'create_particle_physics_network',
]
