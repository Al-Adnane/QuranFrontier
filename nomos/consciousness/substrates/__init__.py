"""
FrontierQu v6.0 Year 2 — Exotic Substrate Expansion
5 new substrates: Morphogenetic, Holographic, Memristive, Reservoir, StochasticThermodynamic
"""
from .morphogenetic import MorphogeneticSubstrate
from .holographic import HolographicSubstrate
from .memristive import MemristiveSubstrate
from .reservoir import ReservoirSubstrate
from .stochastic_thermo import StochasticThermodynamicSubstrate

__all__ = [
    'MorphogeneticSubstrate',
    'HolographicSubstrate',
    'MemristiveSubstrate',
    'ReservoirSubstrate',
    'StochasticThermodynamicSubstrate',
]
