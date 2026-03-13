"""Zoroastrian Dualism Network - Cosmic Battle.

Inspired by: Zoroastrian Cosmology

Key insights:
- Ahura Mazda vs Angra Mainyu (cosmic dualism)
- Spenta Mainyu (creative force) vs Angra Mainyu (destructive)
- Fravashi (guardian spirits)
- Chinvat Bridge (judgment)

Architecture:
    Dual Forces: Creative vs destructive
    Fravashi Guardians: Protective representations
    Cosmic Battle: Adversarial processing
    Judgment Bridge: Decision boundary
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional


class DualForces(nn.Module):
    """Ahura Mazda vs Angra Mainyu."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Creative force (Spenta Mainyu)
        self.creative = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        
        # Destructive force (Angra Mainyu)
        self.destructive = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.ReLU(),  # More aggressive
            nn.Linear(embed_dim, embed_dim)
        )
        
        # Battle outcome
        self.battle = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Cosmic battle."""
        creative = self.creative(x)
        destructive = self.destructive(x)
        
        # Battle
        combined = torch.cat([creative, destructive], dim=-1)
        outcome = torch.sigmoid(self.battle(combined))
        
        return {
            'creative': creative,
            'destructive': destructive,
            'outcome': outcome
        }


class FravashiGuardian(nn.Module):
    """Fravashi - guardian spirits."""
    
    def __init__(self, embed_dim: int = 256, num_guardians: int = 8):
        super().__init__()
        
        self.num_guardians = num_guardians
        
        # Guardian patterns
        self.guardians = nn.Parameter(torch.randn(num_guardians, embed_dim) * 0.1)
        
        # Guardian activation
        self.activate = nn.Linear(embed_dim, num_guardians)
        
        # Protection score
        self.protection = nn.Linear(embed_dim, 1)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Activate guardians."""
        # Activate guardians
        scores = torch.sigmoid(self.activate(x))
        
        # Weighted guardian presence
        presence = (scores.unsqueeze(-1) * self.guardians.unsqueeze(0)).sum(dim=1)
        
        # Protection score
        protection = torch.sigmoid(self.protection(presence))
        
        return {
            'scores': scores,
            'presence': presence,
            'protection': protection
        }


class ChinvatBridge(nn.Module):
    """Chinvat Bridge - judgment crossing."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Bridge width (varies by soul)
        self.width_estimator = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.GELU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
        
        # Crossing decision
        self.crossing = nn.Linear(embed_dim, 1)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Judge at Chinvat Bridge."""
        # Estimate bridge width
        width = self.width_estimator(x)
        
        # Crossing decision
        can_cross = torch.sigmoid(self.crossing(x))
        
        return {
            'bridge_width': width,
            'can_cross': can_cross
        }


class ZoroastrianDualismNetwork(nn.Module):
    """Complete Zoroastrian Dualism Network."""
    
    def __init__(self, vocab_size: int = 10000, embed_dim: int = 256):
        super().__init__()
        
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.dual_forces = DualForces(embed_dim)
        self.fravashi = FravashiGuardian(embed_dim)
        self.bridge = ChinvatBridge(embed_dim)
        
        # Asha (truth/order) head
        self.asha_head = nn.Sequential(
            nn.Linear(embed_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Process through Zoroastrian framework."""
        # Embed
        embedded = self.embed(x).mean(dim=1)
        
        # Cosmic battle
        battle = self.dual_forces(embedded)
        
        # Guardian protection
        guardians = self.fravashi(battle['creative'])
        
        # Bridge judgment
        judgment = self.bridge(guardians['presence'])
        
        # Asha (truth)
        asha = self.asha_head(judgment['can_cross'])
        
        return {
            'battle': battle,
            'guardians': guardians,
            'judgment': judgment,
            'asha': asha
        }


def create_zoroastrian_dualism_network(vocab_size: int = 10000, embed_dim: int = 256) -> ZoroastrianDualismNetwork:
    return ZoroastrianDualismNetwork(vocab_size, embed_dim)
