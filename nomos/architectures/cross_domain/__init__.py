"""Cross-Domain Models - Complete Collection."""

__version__ = "1.0.0"

# Physics (6)
from .physics.quantum_field import QuantumFieldNetwork, create_quantum_field_network
from .physics.relativity import RelativityNetwork, create_relativity_network
from .physics.thermodynamics import ThermodynamicsNetwork, create_thermodynamics_network
from .physics.electromagnetic import ElectromagneticNetwork, create_electromagnetic_network
from .physics.string_theory import StringTheoryNetwork, create_string_theory_network
from .physics.particle import ParticlePhysicsNetwork, create_particle_physics_network

# Biology (7)
from .bio.dna import DNANetwork, create_dna_network
from .bio.plasticity import NeuralPlasticityNetwork, create_neural_plasticity_network
from .bio.evolution import EvolutionNetwork, create_evolution_network
from .bio.immune import ImmuneNetwork, create_immune_network
from .bio.metabolic import MetabolicNetwork, create_metabolic_network
from .bio.neuroscience import NeuroscienceNetwork, create_neuroscience_network
from .bio.genetics import GeneticsNetwork, create_genetics_network

# Chemistry (5)
from .chem.molecular import MolecularNetwork, create_molecular_network
from .chem.reaction import ReactionNetwork, create_reaction_network
from .chem.periodic import PeriodicNetwork, create_periodic_network
from .chem.crystallography import CrystallographyNetwork, create_crystallography_network
from .chem.organic import OrganicChemistryNetwork, create_organic_chemistry_network

# Mathematics (5)
from .math.graph_theory import GraphTheoryNetwork, create_graph_theory_network
from .math.topology import TopologyNetwork, create_topology_network
from .math.number_theory import NumberTheoryNetwork, create_number_theory_network
from .math.calculus import CalculusNetwork, create_calculus_network
from .math.network_science import NetworkScienceNetwork, create_network_science_network

# Art (5)
from .art.impressionism import ImpressionismNetwork, create_impressionism_network
from .art.cubism import CubismNetwork, create_cubism_network
from .art.music import MusicTheoryNetwork, create_music_theory_network
from .art.surrealism import SurrealismNetwork, create_surrealism_network
from .art.abstract import AbstractArtNetwork, create_abstract_art_network

# Architecture (2)
from .architecture.structural import ArchitectureNetwork, create_architecture_network
from .architecture.gothic import GothicNetwork, create_gothic_network

# Ecology (2)
from .eco.food_web import EcosystemNetwork, create_ecosystem_network
from .eco.climate import ClimateNetwork, create_climate_network

# Medicine (3)
from .med.diagnosis import DiagnosisNetwork, create_diagnosis_network
from .med.pharmacology import PharmacologyNetwork, create_pharmacology_network
from .med.epidemiology import EpidemiologyNetwork, create_epidemiology_network

# Economics (3)
from .econ.supply_demand import SupplyDemandNetwork, create_supply_demand_network
from .econ.game_theory import GameTheoryNetwork, create_game_theory_network
from .econ.behavioral import BehavioralEconomicsNetwork, create_behavioral_economics_network

# Linguistics (3)
from .lingua.syntax import SyntaxNetwork, create_syntax_network
from .lingua.semantics import SemanticsNetwork, create_semantics_network
from .lingua.phonology import PhonologyNetwork, create_phonology_network

# Anthropology (1)
from .anthropology.culture import AnthropologyNetwork, create_anthropology_network

__all__ = [
    # Physics
    'QuantumFieldNetwork', 'create_quantum_field_network',
    'RelativityNetwork', 'create_relativity_network',
    'ThermodynamicsNetwork', 'create_thermodynamics_network',
    'ElectromagneticNetwork', 'create_electromagnetic_network',
    'StringTheoryNetwork', 'create_string_theory_network',
    'ParticlePhysicsNetwork', 'create_particle_physics_network',
    
    # Biology
    'DNANetwork', 'create_dna_network',
    'NeuralPlasticityNetwork', 'create_neural_plasticity_network',
    'EvolutionNetwork', 'create_evolution_network',
    'ImmuneNetwork', 'create_immune_network',
    'MetabolicNetwork', 'create_metabolic_network',
    'NeuroscienceNetwork', 'create_neuroscience_network',
    'GeneticsNetwork', 'create_genetics_network',
    
    # Chemistry
    'MolecularNetwork', 'create_molecular_network',
    'ReactionNetwork', 'create_reaction_network',
    'PeriodicNetwork', 'create_periodic_network',
    'CrystallographyNetwork', 'create_crystallography_network',
    'OrganicChemistryNetwork', 'create_organic_chemistry_network',
    
    # Mathematics
    'GraphTheoryNetwork', 'create_graph_theory_network',
    'TopologyNetwork', 'create_topology_network',
    'NumberTheoryNetwork', 'create_number_theory_network',
    'CalculusNetwork', 'create_calculus_network',
    'NetworkScienceNetwork', 'create_network_science_network',
    
    # Art
    'ImpressionismNetwork', 'create_impressionism_network',
    'CubismNetwork', 'create_cubism_network',
    'MusicTheoryNetwork', 'create_music_theory_network',
    'SurrealismNetwork', 'create_surrealism_network',
    'AbstractArtNetwork', 'create_abstract_art_network',
    
    # Architecture
    'ArchitectureNetwork', 'create_architecture_network',
    'GothicNetwork', 'create_gothic_network',
    
    # Ecology
    'EcosystemNetwork', 'create_ecosystem_network',
    'ClimateNetwork', 'create_climate_network',
    
    # Medicine
    'DiagnosisNetwork', 'create_diagnosis_network',
    'PharmacologyNetwork', 'create_pharmacology_network',
    'EpidemiologyNetwork', 'create_epidemiology_network',
    
    # Economics
    'SupplyDemandNetwork', 'create_supply_demand_network',
    'GameTheoryNetwork', 'create_game_theory_network',
    'BehavioralEconomicsNetwork', 'create_behavioral_economics_network',
    
    # Linguistics
    'SyntaxNetwork', 'create_syntax_network',
    'SemanticsNetwork', 'create_semantics_network',
    'PhonologyNetwork', 'create_phonology_network',
    
    # Anthropology
    'AnthropologyNetwork', 'create_anthropology_network',
]
