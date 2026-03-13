"""Film Models - Complete Collection."""

__version__ = "1.0.0"

from .film_theory import FilmTheoryNetwork, create_film_theory_network
from .narrative_structure import NarrativeStructureNetwork, create_narrative_structure_network

__all__ = [
    'FilmTheoryNetwork', 'create_film_theory_network',
    'NarrativeStructureNetwork', 'create_narrative_structure_network',
]
