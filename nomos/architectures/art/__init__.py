"""Art Models - Complete Collection."""

__version__ = "1.0.0"

from .impressionism import ImpressionismNetwork, create_impressionism_network
from .cubism import CubismNetwork, create_cubism_network
from .music import MusicTheoryNetwork, create_music_theory_network
from .surrealism import SurrealismNetwork, create_surrealism_network
from .abstract import AbstractArtNetwork, create_abstract_art_network

__all__ = [
    'ImpressionismNetwork', 'create_impressionism_network',
    'CubismNetwork', 'create_cubism_network',
    'MusicTheoryNetwork', 'create_music_theory_network',
    'SurrealismNetwork', 'create_surrealism_network',
    'AbstractArtNetwork', 'create_abstract_art_network',
]
