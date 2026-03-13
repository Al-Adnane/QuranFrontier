"""Cultural Models - Complete Collection."""

__version__ = "1.0.0"

from .fashion import FashionNetwork, create_fashion_network
from .culinary import CulinaryNetwork, create_culinary_network
from .interior_design import InteriorDesignNetwork, create_interior_design_network

__all__ = [
    'FashionNetwork', 'create_fashion_network',
    'CulinaryNetwork', 'create_culinary_network',
    'InteriorDesignNetwork', 'create_interior_design_network',
]
