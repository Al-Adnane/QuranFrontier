"""Poetry Forms Network - Metrical Patterns.

Inspired by: Poetic Forms
"""

import torch
import torch.nn as nn


class PoetryFormsNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Metrical feet
        self.iambic = nn.Linear(input_dim, embed_dim)
        self.trochaic = nn.Linear(input_dim, embed_dim)
        self.anapestic = nn.Linear(input_dim, embed_dim)
        self.dactylic = nn.Linear(input_dim, embed_dim)
        # Forms
        self.forms = nn.ModuleDict({
            'sonnet': nn.Linear(input_dim, embed_dim),
            'haiku': nn.Linear(input_dim, embed_dim),
            'villanelle': nn.Linear(input_dim, embed_dim),
            'limerick': nn.Linear(input_dim, embed_dim),
            'free_verse': nn.Linear(input_dim, embed_dim),
            'epic': nn.Linear(input_dim, embed_dim)
        })
        
    def forward(self, x: torch.Tensor) -> dict:
        forms = {k: v(x) for k, v in self.forms.items()}
        return {
            'metrical_feet': {
                'iambic': self.iambic(x),
                'trochaic': self.trochaic(x),
                'anapestic': self.anapestic(x),
                'dactylic': self.dactylic(x)
            },
            'forms': forms,
            'preferred_form': max(forms.keys(), key=lambda k: forms[k].mean(dim=-1).max().item()),
            'poetic_quality': torch.sigmoid(torch.stack(list(forms.values())).mean(dim=0).mean(dim=-1, keepdim=True))
        }


def create_poetry_forms_network(input_dim: int = 128, embed_dim: int = 256):
    return PoetryFormsNetwork(input_dim, embed_dim)
