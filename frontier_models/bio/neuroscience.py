"""Neuroscience Network - Brain Region Processing.

Inspired by: Brain anatomy and neural circuits

Architecture:
    Cortex: Higher-order processing
    Limbic: Emotional processing
    Brainstem: Basic functions
    Neural Pathways: Inter-region communication
    Neurotransmitters: Chemical signaling
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional


class NeuroscienceNetwork(nn.Module):
    """Brain-inspired network with regional specialization."""
    
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        
        # Brain regions
        self.cortex = nn.Sequential(
            nn.Linear(input_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        
        self.limbic = nn.Sequential(
            nn.Linear(input_dim, embed_dim),
            nn.Tanh(),  # Emotional activation
            nn.Linear(embed_dim, embed_dim)
        )
        
        self.brainstem = nn.Sequential(
            nn.Linear(input_dim, embed_dim // 2),
            nn.ReLU(),  # Basic activation
            nn.Linear(embed_dim // 2, embed_dim // 2)
        )
        
        # Neural pathways (inter-region communication)
        self.cortico_limbic = nn.Linear(embed_dim, embed_dim)
        self.limbico_cortical = nn.Linear(embed_dim, embed_dim)
        self.brainstem_modulation = nn.Linear(embed_dim // 2, embed_dim)
        
        # Neurotransmitter systems
        self.dopamine = nn.Parameter(torch.tensor(0.5))  # Reward
        self.serotonin = nn.Parameter(torch.tensor(0.5))  # Mood
        self.norepinephrine = nn.Parameter(torch.tensor(0.5))  # Arousal
        
        # Integration
        self.integration = nn.Linear(embed_dim * 3, embed_dim)
        
    def process_cortex(self, x: torch.Tensor) -> torch.Tensor:
        """Higher-order cognitive processing."""
        return self.cortex(x)
    
    def process_limbic(self, x: torch.Tensor) -> torch.Tensor:
        """Emotional processing."""
        limbic_out = self.limbic(x)
        # Modulate by serotonin
        return limbic_out * torch.sigmoid(self.serotonin)
    
    def process_brainstem(self, x: torch.Tensor) -> torch.Tensor:
        """Basic life functions."""
        brainstem_out = self.brainstem(x)
        # Modulate by norepinephrine
        return brainstem_out * torch.sigmoid(self.norepinephrine)
    
    def integrate_regions(
        self,
        cortex: torch.Tensor,
        limbic: torch.Tensor,
        brainstem: torch.Tensor
    ) -> torch.Tensor:
        """Integrate brain region outputs."""
        # Inter-region communication
        cortico_limbic = self.cortico_limbic(cortex)
        limbico_cortical = self.limbico_cortical(limbic)
        brainstem_mod = self.brainstem_modulation(brainstem)
        
        # Combine with modulation
        integrated = torch.cat([
            cortex + limbico_cortical * self.dopamine,
            limbic + cortico_limbic,
            brainstem + brainstem_mod
        ], dim=-1)
        
        return self.integration(integrated)
    
    def forward(self, x: torch.Tensor) -> Dict:
        """Full brain processing."""
        # Regional processing
        cortex_out = self.process_cortex(x)
        limbic_out = self.process_limbic(x)
        brainstem_out = self.process_brainstem(x)
        
        # Integration
        integrated = self.integrate_regions(cortex_out, limbic_out, brainstem_out)
        
        # Cognitive function
        cognitive = torch.sigmoid(integrated.mean(dim=-1, keepdim=True))
        
        # Emotional valence
        emotional = torch.tanh(limbic_out.mean(dim=-1, keepdim=True))
        
        # Arousal level
        arousal = torch.sigmoid(brainstem_out.mean(dim=-1, keepdim=True))
        
        return {
            'cortex': cortex_out,
            'limbic': limbic_out,
            'brainstem': brainstem_out,
            'integrated': integrated,
            'cognitive_function': cognitive,
            'emotional_valence': emotional,
            'arousal_level': arousal,
            'dopamine': self.dopamine.item(),
            'serotonin': self.serotonin.item(),
            'norepinephrine': self.norepinephrine.item()
        }


def create_neuroscience_network(input_dim: int = 128, embed_dim: int = 256):
    """Create NeuroscienceNetwork."""
    return NeuroscienceNetwork(input_dim, embed_dim)
