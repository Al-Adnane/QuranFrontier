"""Agriculture Models - Complete Collection."""

__version__ = "2.0.0"

from .permaculture import PermacultureNetwork, create_permaculture_network
from .aquaculture import AquacultureNetwork, create_aquaculture_network
from .agroforestry import AgroforestryNetwork, create_agroforestry_network
from .crop_rotation import CropRotationNetwork, create_crop_rotation_network

__all__ = [
    'PermacultureNetwork', 'create_permaculture_network',
    'AquacultureNetwork', 'create_aquaculture_network',
    'AgroforestryNetwork', 'create_agroforestry_network',
    'CropRotationNetwork', 'create_crop_rotation_network',
]
