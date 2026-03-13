"""Immune Network - Antibody Recognition and Response.

Inspired by: Adaptive immune system

Architecture:
    Antigen Detection: Pathogen recognition
    Antibody Production: B-cell response
    T-Cell Activation: Cell-mediated immunity
    Memory Formation: Long-term immunity
    Self/Non-Self: Autoimmune prevention
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple


class ImmuneNetwork(nn.Module):
    """Immune system-inspired network for anomaly detection."""
    
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, num_antibodies: int = 64):
        super().__init__()
        self.num_antibodies = num_antibodies
        
        # Antigen presentation
        self.antigen_presentation = nn.Linear(input_dim, embed_dim)
        
        # Antibody repertoire (diverse receptors)
        self.antibody_receptors = nn.Parameter(torch.randn(num_antibodies, embed_dim) * 0.5)
        
        # B-cell activation
        self.b_cell_activation = nn.Linear(embed_dim, embed_dim)
        
        # T-cell help
        self.t_cell_help = nn.Linear(embed_dim, embed_dim)
        
        # Antibody production (clonal expansion)
        self.clonal_expansion = nn.Linear(embed_dim, num_antibodies)
        
        # Memory B-cells
        self.memory_cells = nn.Parameter(torch.randn(16, embed_dim) * 0.3)
        
        # Self-tolerance (prevent autoimmunity)
        self.self_tolerance = nn.Parameter(torch.ones(num_antibodies) * 0.5)
        
    def present_antigen(self, antigen: torch.Tensor) -> torch.Tensor:
        """Present antigen to immune system."""
        return self.antigen_presentation(antigen)
    
    def recognize_antigen(self, presented: torch.Tensor) -> torch.Tensor:
        """Antibody-antigen recognition."""
        # Affinity calculation (cosine similarity)
        presented_norm = F.normalize(presented.unsqueeze(1), dim=-1)
        receptor_norm = F.normalize(self.antibody_receptors.unsqueeze(0), dim=-1)
        affinity = (presented_norm * receptor_norm).sum(dim=-1)
        return F.softmax(affinity * 10, dim=-1)
    
    def activate_b_cells(self, recognition: torch.Tensor) -> torch.Tensor:
        """Activate B-cells based on recognition."""
        activated = recognition @ self.b_cell_activation.weight.T
        return F.relu(activated)
    
    def clonal_expansion(self, activated: torch.Tensor) -> torch.Tensor:
        """Clonal expansion of activated B-cells."""
        expansion = self.clonal_expansion(activated)
        return F.softmax(expansion, dim=-1)
    
    def check_self_tolerance(self, recognition: torch.Tensor) -> torch.Tensor:
        """Check for autoimmune response."""
        # Suppress self-reactive antibodies
        tolerance = torch.sigmoid(self.self_tolerance.unsqueeze(0))
        return recognition * (1 - tolerance)
    
    def form_memory(self, activated: torch.Tensor) -> None:
        """Form memory B-cells."""
        with torch.no_grad():
            # Select top activated clones for memory
            top_indices = activated.topk(min(4, self.num_antibodies)).indices
            for i, idx in enumerate(top_indices[0]):
                if i < len(self.memory_cells):
                    self.memory_cells[i] = self.antibody_receptors[idx] * 0.9 + self.memory_cells[i] * 0.1
    
    def forward(self, x: torch.Tensor) -> Dict:
        """Immune response to antigen."""
        # Antigen presentation
        presented = self.present_antigen(x)
        
        # Recognition
        recognition = self.recognize_antigen(presented)
        
        # Self-tolerance check
        recognition = self.check_self_tolerance(recognition)
        
        # B-cell activation
        activated = self.activate_b_cells(recognition)
        
        # Clonal expansion
        antibodies = self.clonal_expansion(activated)
        
        # Form memory
        self.form_memory(activated)
        
        # T-cell help
        t_cell = self.t_cell_help(presented)
        
        # Immune response strength
        response_strength = antibodies.max(dim=-1).values
        
        return {
            'presented_antigen': presented,
            'recognition': recognition,
            'b_cell_activation': activated,
            'antibody_production': antibodies,
            't_cell_response': t_cell,
            'response_strength': response_strength,
            'memory_cells': self.memory_cells
        }


def create_immune_network(input_dim: int = 128, embed_dim: int = 256):
    """Create ImmuneNetwork."""
    return ImmuneNetwork(input_dim, embed_dim)
