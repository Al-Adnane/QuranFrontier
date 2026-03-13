"""Natural Sciences Models - Complete Collection."""

__version__ = "2.0.0"

from .geology import GeologyNetwork, create_geology_network
from .oceanography import OceanographyNetwork, create_oceanography_network
from .meteorology import MeteorologyNetwork, create_meteorology_network
from .cosmology import CosmologyNetwork, create_cosmology_network
from .astronomy import AstronomyNetwork, create_astronomy_network
from .paleontology import PaleontologyNetwork, create_paleontology_network
from .botany import BotanyNetwork, create_botany_network
from .zoology import ZoologyNetwork, create_zoology_network
from .environmental import EnvironmentalScienceNetwork, create_environmental_science_network
from .seismology import SeismologyNetwork, create_seismology_network
from .hydrology import HydrologyNetwork, create_hydrology_network
from .glaciology import GlaciologyNetwork, create_glaciology_network
from .volcanology import VolcanologyNetwork, create_volcanology_network

__all__ = [
    'GeologyNetwork', 'create_geology_network',
    'OceanographyNetwork', 'create_oceanography_network',
    'MeteorologyNetwork', 'create_meteorology_network',
    'CosmologyNetwork', 'create_cosmology_network',
    'AstronomyNetwork', 'create_astronomy_network',
    'PaleontologyNetwork', 'create_paleontology_network',
    'BotanyNetwork', 'create_botany_network',
    'ZoologyNetwork', 'create_zoology_network',
    'EnvironmentalScienceNetwork', 'create_environmental_science_network',
    'SeismologyNetwork', 'create_seismology_network',
    'HydrologyNetwork', 'create_hydrology_network',
    'GlaciologyNetwork', 'create_glaciology_network',
    'VolcanologyNetwork', 'create_volcanology_network',
]
