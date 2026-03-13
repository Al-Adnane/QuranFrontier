"""Meridians Network - TCM Energy Pathways.

Inspired by: Traditional Chinese Medicine
"""

import torch
import torch.nn as nn


MERIDIANS = [
    'Lung', 'Large_Intestine', 'Stomach', 'Spleen',
    'Heart', 'Small_Intestine', 'Bladder', 'Kidney',
    'Pericardium', 'Triple_Burner', 'Gallbladder', 'Liver'
]


class MeridiansNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.meridians = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, embed_dim), nn.GELU())
            for _ in range(12)
        ])
        self.qi_flow = nn.Linear(embed_dim * 12, 1)
        self.yin_yang = nn.Linear(embed_dim * 2, 2)
        
    def forward(self, x: torch.Tensor) -> dict:
        meridian_embs = [m(x) for m in self.meridians]
        yin_embs = torch.stack([meridian_embs[i] for i in [0, 3, 4, 7, 8, 11]], 0).mean(0)
        yang_embs = torch.stack([meridian_embs[i] for i in [1, 2, 5, 6, 9, 10]], 0).mean(0)
        return {
            'meridians': dict(zip(MERIDIANS, meridian_embs)),
            'qi_flow': torch.sigmoid(self.qi_flow(torch.cat(meridian_embs, -1))),
            'yin_yang_balance': torch.softmax(self.yin_yang(torch.cat([yin_embs, yang_embs], -1)), -1),
            'blockages': 1 - torch.stack([m.mean(dim=-1) for m in meridian_embs], -1).sigmoid()
        }


def create_meridians_network(input_dim: int = 128, embed_dim: int = 256):
    return MeridiansNetwork(input_dim, embed_dim)
