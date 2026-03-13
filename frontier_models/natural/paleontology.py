"""Paleontology Network - Evolution History.

Inspired by: Paleontology
"""

import torch
import torch.nn as nn


ERAS = ['Precambrian', 'Paleozoic', 'Mesozoic', 'Cenozoic']


class PaleontologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.eras = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(4)])
        self.fossil_record = nn.Linear(embed_dim * 4, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        era_embs = [e(x) for e in self.eras]
        return {
            'geological_eras': dict(zip(ERAS, era_embs)),
            'dominant_era': ERAS[torch.stack(era_embs).mean(dim=0).argmax(dim=-1)],
            'fossil_completeness': torch.sigmoid(self.fossil_record(torch.cat(era_embs, -1)))
        }


def create_paleontology_network(input_dim: int = 128, embed_dim: int = 256):
    return PaleontologyNetwork(input_dim, embed_dim)
