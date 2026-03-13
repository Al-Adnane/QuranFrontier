"""Greek Mythology Network - Olympians and Titans.

Inspired by: Greek Mythology
"""

import torch
import torch.nn as nn


OLYMPIANS = ['Zeus', 'Hera', 'Poseidon', 'Demeter', 'Athena', 'Apollo', 
             'Artemis', 'Ares', 'Aphrodite', 'Hephaestus', 'Hermes', 'Hestia']

TITANS = ['Cronus', 'Rhea', 'Oceanus', 'Tethys', 'Hyperion', 'Theia',
          'Coeus', 'Phoebe', 'Crius', 'Iapetus', 'Mnemosyne', 'Themis']


class GreekMythologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.olympians = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(12)])
        self.titans = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(12)])
        self.pantheon = nn.Linear(embed_dim * 24, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        olymp_embs = [o(x) for o in self.olympians]
        titan_embs = [t(x) for t in self.titans]
        olymp_scores = torch.stack([o.mean(dim=-1) for o in olymp_embs], -1)
        dominant_idx = int(olymp_scores.argmax(dim=-1).item())
        return {
            'olympians': dict(zip(OLYMPIANS, olymp_embs)),
            'titans': dict(zip(TITANS, titan_embs)),
            'patron_deity': OLYMPIANS[dominant_idx],
            'pantheon_blessing': torch.sigmoid(self.pantheon(torch.cat(olymp_embs + titan_embs, -1)))
        }


def create_greek_mythology_network(input_dim: int = 128, embed_dim: int = 256):
    return GreekMythologyNetwork(input_dim, embed_dim)
