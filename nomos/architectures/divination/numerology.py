"""Numerology Network - Number Meanings.

Inspired by: Numerology
"""

import torch
import torch.nn as nn


class NumerologyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Core numbers 1-9
        self.core_numbers = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(9)])
        # Master numbers 11, 22, 33
        self.master_numbers = nn.ModuleDict({
            '11': nn.Linear(input_dim, embed_dim),
            '22': nn.Linear(input_dim, embed_dim),
            '33': nn.Linear(input_dim, embed_dim)
        })
        # Life path calculation
        self.life_path = nn.Linear(embed_dim * 12, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        core = [n(x) for n in self.core_numbers]
        master = {k: v(x) for k, v in self.master_numbers.items()}
        core_scores = torch.stack([c.mean(dim=-1) for c in core], -1)
        dominant_idx = int(core_scores.argmax(dim=-1).item())
        all_nums = core + list(master.values())
        return {
            'core_numbers': {str(i+1): c for i, c in enumerate(core)},
            'master_numbers': master,
            'life_path_number': dominant_idx + 1,
            'numerology_chart': torch.sigmoid(self.life_path(torch.cat(all_nums, -1)))
        }


def create_numerology_network(input_dim: int = 128, embed_dim: int = 256):
    return NumerologyNetwork(input_dim, embed_dim)
