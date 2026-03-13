"""Molecular Network - Chemical Bonds.

Inspired by: Molecular Chemistry
"""

import torch
import torch.nn as nn


class MolecularNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        self.atoms = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(8)])
        self.bonds = nn.Linear(embed_dim * 8, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        atoms = [a(x) for a in self.atoms]
        molecule = torch.cat(atoms, -1)
        return {'atoms': atoms, 'molecule': torch.sigmoid(self.bonds(molecule))}


def create_molecular_network(input_dim: int = 128, embed_dim: int = 256):
    return MolecularNetwork(input_dim, embed_dim)
