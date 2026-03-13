"""Music Theory Network - Harmony, Melody, Rhythm.

Inspired by: Western Music Theory
"""

import torch
import torch.nn as nn


class MusicTheoryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # 12 tones
        self.tones = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(12)])
        # Chord types
        self.chords = nn.ModuleDict({
            'major': nn.Linear(input_dim, embed_dim),
            'minor': nn.Linear(input_dim, embed_dim),
            'diminished': nn.Linear(input_dim, embed_dim),
            'augmented': nn.Linear(input_dim, embed_dim),
            'dominant_7': nn.Linear(input_dim, embed_dim),
            'major_7': nn.Linear(input_dim, embed_dim)
        })
        # Progression
        self.progression = nn.Linear(embed_dim * 18, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        tone_embs = [t(x) for t in self.tones]
        chord_embs = {k: v(x) for k, v in self.chords.items()}
        tone_scores = torch.stack([t.mean(dim=-1) for t in tone_embs], -1)
        dominant_idx = int(tone_scores.argmax(dim=-1).item())
        return {
            'twelve_tones': tone_embs,
            'chords': chord_embs,
            'tonal_center': tone_embs[dominant_idx],
            'harmonic_progression': torch.sigmoid(self.progression(torch.cat(tone_embs + list(chord_embs.values()), -1)))
        }


def create_music_theory_network(input_dim: int = 128, embed_dim: int = 256):
    return MusicTheoryNetwork(input_dim, embed_dim)
