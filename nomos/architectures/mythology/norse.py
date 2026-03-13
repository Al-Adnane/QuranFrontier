"""Norse Mythology Network - Nine Worlds and Yggdrasil.

Inspired by: Norse Mythology
"""

import torch
import torch.nn as nn


NINE_WORLDS = ['Asgard', 'Midgard', 'Jotunheim', 'Vanaheim', 'Alfheim',
               'Svartalfheim', 'Niflheim', 'Muspelheim', 'Hel']

AESIR = ['Odin', 'Frigg', 'Thor', 'Tyr', 'Baldur', 'Heimdall']
VANIR = ['Freyr', 'Freya', 'Njord']


class NorseMythologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.worlds = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(9)])
        self.aesir = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(6)])
        self.vanir = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(3)])
        self.yggdrasil = nn.Linear(embed_dim * 18, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        world_embs = [w(x) for w in self.worlds]
        aesir_embs = [a(x) for a in self.aesir]
        vanir_embs = [v(x) for v in self.vanir]
        world_scores = torch.stack([w.mean(dim=-1) for w in world_embs], -1)
        dominant_idx = int(world_scores.argmax(dim=-1).item())
        return {
            'nine_worlds': dict(zip(NINE_WORLDS, world_embs)),
            'aesir': dict(zip(AESIR, aesir_embs)),
            'vanir': dict(zip(VANIR, vanir_embs)),
            'realm_affiliation': NINE_WORLDS[dominant_idx],
            'yggdrasil_connection': torch.sigmoid(self.yggdrasil(torch.cat(world_embs + aesir_embs + vanir_embs, -1)))
        }


def create_norse_mythology_network(input_dim: int = 128, embed_dim: int = 256):
    return NorseMythologyNetwork(input_dim, embed_dim)
