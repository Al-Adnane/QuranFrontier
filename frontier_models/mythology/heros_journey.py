"""Hero's Journey Network - Campbell's Monomyth.

Inspired by: Joseph Campbell's Hero with a Thousand Faces
"""

import torch
import torch.nn as nn


STAGES = [
    'Ordinary_World', 'Call_to_Adventure', 'Refusal_of_Call',
    'Meeting_Mentor', 'Crossing_Threshold', 'Tests_Allies_Enemies',
    'Approach', 'Ordeal', 'Reward', 'Road_Back',
    'Resurrection', 'Return_Elixir'
]


class HerosJourneyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.stages = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(12)
        ])
        self.journey_complete = nn.Linear(embed_dim * 12, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        stage_embs = [s(x) for s in self.stages]
        stage_scores = torch.stack([s.mean(dim=-1) for s in stage_embs], -1)
        current_stage = stage_scores.argmax(dim=-1)
        return {
            'journey_stages': dict(zip(STAGES, stage_embs)),
            'stage_scores': torch.sigmoid(stage_scores),
            'current_stage': STAGES[current_stage],
            'journey_progress': current_stage.float() / 11,
            'journey_complete': torch.sigmoid(self.journey_complete(torch.cat(stage_embs, -1)))
        }


def create_heros_journey_network(input_dim: int = 128, embed_dim: int = 256):
    return HerosJourneyNetwork(input_dim, embed_dim)
