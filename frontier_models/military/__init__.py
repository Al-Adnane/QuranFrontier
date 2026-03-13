"""Military Strategy Models - Complete Collection."""

__version__ = "1.0.0"

from .sun_tzu import SunTzuNetwork, create_sun_tzu_network
from .clausewitz import ClausewitzNetwork, create_clausewitz_network

__all__ = [
    'SunTzuNetwork', 'create_sun_tzu_network',
    'ClausewitzNetwork', 'create_clausewitz_network',
]
