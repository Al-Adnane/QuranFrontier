"""Shadow Work Network - Jungian Shadow Integration.

Inspired by: Carl Jung's Shadow Psychology
"""

import torch
import torch.nn as nn


class ShadowWorkNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.persona = nn.Linear(input_dim, embed_dim)  # Mask we show the world
        self.shadow = nn.Linear(input_dim, embed_dim)  # Repressed aspects
        self.anima_animus = nn.Linear(input_dim, embed_dim)  # Contrasexual aspects
        self.self = nn.Linear(input_dim, embed_dim)  # True self
        self.integration = nn.Linear(embed_dim * 4, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        persona = self.persona(x)
        shadow = self.shadow(x)
        anima_animus = self.anima_animus(x)
        true_self = self.self(x)
        integrated = torch.cat([persona, shadow, anima_animus, true_self], -1)
        return {
            'persona': persona,
            'shadow': shadow,
            'anima_animus': anima_animus,
            'true_self': true_self,
            'integration': torch.sigmoid(self.integration(integrated)),
            'shadow_work_progress': torch.sigmoid((shadow + true_self).mean(dim=-1, keepdim=True))
        }


def create_shadow_work_network(input_dim: int = 128, embed_dim: int = 256):
    return ShadowWorkNetwork(input_dim, embed_dim)
