"""Yogasutra Network - Systematic Aphoristic Reasoning.

Inspired by: Patanjali's Yogasutras

Key insights:
- 196 aphorisms (sutras) organized in 4 chapters
- Eight limbs (Ashtanga) of yoga
- Kleshas (afflictions) and their removal
- Samadhi states and progression

Architecture:
    Sutra Embedding: Aphoristic compression
    Eight Limbs: Multi-path processing
    Klesha Detector: Affliction identification
    Samadhi Progression: Deepening states
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional
from dataclasses import dataclass


# Eight limbs of yoga
YAMA = 0      # Ethical disciplines
NIYAMA = 1    # Personal observances
ASANA = 2     # Posture
PRANAYAMA = 3 # Breath control
PRATYAHARA = 4 # Sense withdrawal
DHARANA = 5   # Concentration
DHYANA = 6    # Meditation
SAMADHI = 7   # Absorption


# Five Kleshas (afflictions)
AVIDYA = 0    # Ignorance
ASMITA = 1    # Egoism
RAGA = 2      # Attachment
DVESA = 3     # Aversion
ABHINIVESA = 4 # Fear of death


@dataclass
class EightLimbsState:
    """State across eight limbs."""
    limbs: List[torch.Tensor]


class SutraEmbedding(nn.Module):
    """Compress to aphoristic representation."""
    
    def __init__(self, vocab_size: int = 10000, sutra_dim: int = 128):
        super().__init__()
        
        self.sutra_dim = sutra_dim
        
        # Embedding
        self.embed = nn.Embedding(vocab_size, sutra_dim * 2)
        
        # Compression to sutra form (dense, aphoristic)
        self.compress = nn.Sequential(
            nn.Linear(sutra_dim * 2, sutra_dim),
            nn.Tanh()  # Compressed representation
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Embed and compress to sutra form."""
        embedded = self.embed(x)
        pooled = embedded.mean(dim=1)  # Pool over sequence
        sutra_form = self.compress(pooled)
        
        return sutra_form


class EightLimbsProcessor(nn.Module):
    """Process through eight limbs of yoga."""
    
    def __init__(self, sutra_dim: int = 128):
        super().__init__()
        
        # Each limb has specific processing
        self.limb_processors = nn.ModuleList([
            nn.Sequential(
                nn.Linear(sutra_dim, sutra_dim),
                nn.GELU(),
                nn.Linear(sutra_dim, sutra_dim)
            )
            for _ in range(8)
        ])
        
        # Progressive deepening (each limb builds on previous)
        self.progressive = nn.LSTM(sutra_dim, sutra_dim, num_layers=2, batch_first=True)
        
    def forward(self, sutra: torch.Tensor) -> EightLimbsState:
        """Process through eight limbs progressively."""
        batch_size = sutra.size(0)
        
        limbs = []
        current = sutra
        
        for i, processor in enumerate(self.limb_processors):
            current = processor(current)
            limbs.append(current)
        
        # Progressive sequence
        limb_sequence = torch.stack(limbs, dim=1)  # [batch, 8, dim]
        _, (hidden, _) = self.progressive(limb_sequence)
        
        return EightLimbsState(limbs=limbs)


class KleshaDetector(nn.Module):
    """Detect and transform afflictions."""
    
    def __init__(self, sutra_dim: int = 128):
        super().__init__()
        
        # Detection head
        self.detect = nn.Linear(sutra_dim, 5)  # 5 kleshas
        
        # Transformation (vidya - knowledge removes avidya)
        self.transform = nn.Sequential(
            nn.Linear(sutra_dim, sutra_dim),
            nn.GELU(),
            nn.Linear(sutra_dim, sutra_dim)
        )
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Detect and transform kleshas."""
        # Detect afflictions
        klesha_scores = F.softmax(self.detect(x), dim=-1)
        
        # Transform through vidya (knowledge)
        transformed = self.transform(x)
        
        # Reduction in kleshas
        klesha_reduction = 1 - F.softmax(self.detect(transformed), dim=-1)
        
        return {
            'klesha_scores': klesha_scores,
            'klesha_names': ['avidya', 'asmita', 'raga', 'dvesa', 'abhinivesa'],
            'transformed': transformed,
            'klesha_reduction': klesha_reduction
        }


class SamadhiProgression(nn.Module):
    """Model progression through samadhi states."""
    
    def __init__(self, sutra_dim: int = 128):
        super().__init__()
        
        # Samadhi stages
        self.vitarka = nn.Linear(sutra_dim, sutra_dim)  # With gross object
        self.vichara = nn.Linear(sutra_dim, sutra_dim)  # With subtle object
        self.ananda = nn.Linear(sutra_dim, sutra_dim)   # With bliss
        self.asmita = nn.Linear(sutra_dim, sutra_dim)   # With I-am-ness
        self.nirbija = nn.Linear(sutra_dim, sutra_dim)  # Seedless samadhi
        
        # Integration
        self.integrate = nn.Linear(sutra_dim * 5, sutra_dim)
        
        # Samadhi depth estimator
        self.depth_estimator = nn.Sequential(
            nn.Linear(sutra_dim, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Progress through samadhi stages."""
        vitarka = F.relu(self.vitarka(x))
        vichara = F.relu(self.vichara(vitarka))
        ananda = F.relu(self.ananda(vichara))
        asmita_samadhi = F.relu(self.asmita(ananda))
        nirbija = F.relu(self.nirbija(asmita_samadhi))
        
        combined = torch.cat([vitarka, vichara, ananda, asmita_samadhi, nirbija], dim=-1)
        integrated = self.integrate(combined)
        
        # Estimate samadhi depth
        depth = self.depth_estimator(integrated)
        
        return {
            'vitarka': vitarka,
            'vichara': vichara,
            'ananda': ananda,
            'asmita': asmita_samadhi,
            'nirbija': nirbija,
            'integrated': integrated,
            'samadhi_depth': depth
        }


class YogasutraNetwork(nn.Module):
    """Complete Yogasutra Network for systematic aphoristic reasoning.
    
    Applications:
    - Structured philosophical reasoning
    - Progressive deepening of understanding
    - Affliction detection and transformation
    - Meditative state modeling
    """
    
    def __init__(
        self,
        vocab_size: int = 10000,
        sutra_dim: int = 128,
        hidden_dim: int = 256
    ):
        super().__init__()
        
        self.embedding = SutraEmbedding(vocab_size, sutra_dim)
        self.eight_limbs = EightLimbsProcessor(sutra_dim)
        self.klesha_detector = KleshaDetector(sutra_dim)
        self.samadhi = SamadhiProgression(sutra_dim)
        
        # Kaivalya (liberation) head
        self.kaivalya_head = nn.Sequential(
            nn.Linear(sutra_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        x: torch.Tensor,
        num_practice_cycles: int = 3
    ) -> Dict:
        """Process through yogic inquiry.
        
        Args:
            x: [batch, seq_len] token IDs
            num_practice_cycles: Number of abhyasa (practice) cycles
        Returns:
            Dict with eight limbs, kleshas, and samadhi states
        """
        # Embed as sutra
        sutra = self.embedding(x)
        
        # Process through eight limbs
        limbs_state = self.eight_limbs(sutra)
        
        # Detect and transform kleshas
        current = limbs_state.limbs[-1]  # Start from samadhi limb
        for _ in range(num_practice_cycles):
            klesha_result = self.klesha_detector(current)
            current = klesha_result['transformed']
        
        # Progress through samadhi
        samadhi_result = self.samadhi(current)
        
        # Kaivalya (liberation)
        kaivalya = self.kaivalya_head(samadhi_result['integrated'])
        
        return {
            'eight_limbs': limbs_state,
            'klesha_result': klesha_result,
            'samadhi_result': samadhi_result,
            'kaivalya': kaivalya,
            'sutra': sutra
        }


def create_yogasutra_network(
    vocab_size: int = 10000,
    sutra_dim: int = 128,
    hidden_dim: int = 256
) -> YogasutraNetwork:
    """Create YogasutraNetwork."""
    return YogasutraNetwork(vocab_size, sutra_dim, hidden_dim)
