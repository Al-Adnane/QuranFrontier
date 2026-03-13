"""Chess Strategy Network - Openings, Middlegame, Endgame.

Inspired by: Chess Theory
"""

import torch
import torch.nn as nn


OPENINGS = ['Ruy_Lopez', 'Sicilian', 'French', 'Caro_Kann', 'Queens_Gambit',
            'Kings_Indian', 'Nimzo_Indian', 'English', 'Reti', 'Birds']


class ChessStrategyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Game phases
        self.opening = nn.Linear(input_dim, embed_dim)
        self.middlegame = nn.Linear(input_dim, embed_dim)
        self.endgame = nn.Linear(input_dim, embed_dim)
        # Piece values
        self.pieces = nn.ModuleDict({
            'pawn': nn.Linear(input_dim, embed_dim // 4),
            'knight': nn.Linear(input_dim, embed_dim // 2),
            'bishop': nn.Linear(input_dim, embed_dim // 2),
            'rook': nn.Linear(input_dim, embed_dim),
            'queen': nn.Linear(input_dim, embed_dim * 2),
            'king': nn.Linear(input_dim, embed_dim * 2)
        })
        # Opening repertoire
        self.openings = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(10)])
        # Checkmate detection
        self.checkmate = nn.Linear(embed_dim * 5, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        opening = self.opening(x)
        middlegame = self.middlegame(x)
        endgame = self.endgame(x)
        piece_embs = {k: v(x) for k, v in self.pieces.items()}
        opening_embs = [o(x) for o in self.openings]
        opening_scores = torch.stack([o.mean(dim=-1) for o in opening_embs], -1)
        dominant_idx = int(opening_scores.argmax(dim=-1).item())
        return {
            'phases': {'opening': opening, 'middlegame': middlegame, 'endgame': endgame},
            'pieces': piece_embs,
            'opening_repertoire': dict(zip(OPENINGS, opening_embs)),
            'preferred_opening': OPENINGS[dominant_idx],
            'checkmate_probability': torch.sigmoid(self.checkmate(torch.cat([opening, middlegame, endgame, piece_embs['queen'], piece_embs['king']], -1)))
        }


def create_chess_strategy_network(input_dim: int = 128, embed_dim: int = 256):
    return ChessStrategyNetwork(input_dim, embed_dim)
