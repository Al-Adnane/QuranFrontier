"""Particle Physics Network - Standard Model.

Inspired by: Particle Physics
"""

import torch
import torch.nn as nn


class ParticlePhysicsNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.quark = nn.Linear(input_dim, embed_dim)
        self.lepton = nn.Linear(input_dim, embed_dim)
        self.boson = nn.Linear(input_dim, embed_dim)
        self.standard_model = nn.Linear(embed_dim * 3, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        q = self.quark(x)
        l = self.lepton(x)
        b = self.boson(x)
        return {'quark': q, 'lepton': l, 'boson': b, 'standard_model': torch.sigmoid(self.standard_model(torch.cat([q, l, b], -1)))}


def create_particle_physics_network(input_dim: int = 128, embed_dim: int = 256):
    return ParticlePhysicsNetwork(input_dim, embed_dim)
