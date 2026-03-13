"""Music and Sports Models - Complete Collection."""

__version__ = "1.0.0"

from .music_theory import MusicTheoryNetwork, create_music_theory_network
from .chess import ChessStrategyNetwork, create_chess_strategy_network

__all__ = [
    'MusicTheoryNetwork', 'create_music_theory_network',
    'ChessStrategyNetwork', 'create_chess_strategy_network',
]
