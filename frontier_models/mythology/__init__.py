"""Mythology Models - Complete Collection."""

__version__ = "1.0.0"

from .greek import GreekMythologyNetwork, create_greek_mythology_network
from .norse import NorseMythologyNetwork, create_norse_mythology_network
from .heros_journey import HerosJourneyNetwork, create_heros_journey_network

__all__ = [
    'GreekMythologyNetwork', 'create_greek_mythology_network',
    'NorseMythologyNetwork', 'create_norse_mythology_network',
    'HerosJourneyNetwork', 'create_heros_journey_network',
]
