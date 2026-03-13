"""Transportation Models - Complete Collection."""

__version__ = "2.0.0"

from .aviation import AviationNetwork, create_aviation_network
from .maritime import MaritimeNetwork, create_maritime_network
from .urban_transit import UrbanTransitNetwork, create_urban_transit_network
from .space_travel import SpaceTravelNetwork, create_space_travel_network
from .autonomous_vehicles import AutonomousVehiclesNetwork, create_autonomous_vehicles_network
from .rail import RailSystemsNetwork, create_rail_systems_network

__all__ = [
    'AviationNetwork', 'create_aviation_network',
    'MaritimeNetwork', 'create_maritime_network',
    'UrbanTransitNetwork', 'create_urban_transit_network',
    'SpaceTravelNetwork', 'create_space_travel_network',
    'AutonomousVehiclesNetwork', 'create_autonomous_vehicles_network',
    'RailSystemsNetwork', 'create_rail_systems_network',
]
