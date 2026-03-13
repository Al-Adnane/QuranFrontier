"""Divination Models - Complete Collection."""

__version__ = "1.0.0"

from .tarot import TarotNetwork, create_tarot_network
from .astrology import AstrologyNetwork, create_astrology_network
from .runes import RunesNetwork, create_runes_network
from .numerology import NumerologyNetwork, create_numerology_network
from .geomancy import GeomancyNetwork, create_geomancy_network

__all__ = [
    'TarotNetwork', 'create_tarot_network',
    'AstrologyNetwork', 'create_astrology_network',
    'RunesNetwork', 'create_runes_network',
    'NumerologyNetwork', 'create_numerology_network',
    'GeomancyNetwork', 'create_geomancy_network',
]
