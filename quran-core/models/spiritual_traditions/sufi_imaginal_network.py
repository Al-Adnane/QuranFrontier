"""Sufi Imaginal Network - Ibn Arabi's Alam al-Mithal.

Inspired by: Sufi Metaphysics of Ibn Arabi

Key insights:
- Alam al-Mithal (imaginal realm) between material and divine
- Creative imagination as epistemic faculty (not fantasy)
- Seven levels of consciousness from material to divine
- Barzakh (isthmus) connecting opposites
- Active imagination mediates senses and intellect

Architecture:
    Imaginal Embedding: Bridge between concrete and abstract
    Seven Levels: Hierarchical consciousness processing
    Barzakh Layer: Connecting opposites
    Creative Synthesis: Imaginal truth discovery
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional
from dataclasses import dataclass


# Seven levels of consciousness (from Ibn Arabi)
MULK = 0          # Material kingdom
MALAKUT = 1       # Angelic kingdom
JABARUT = 2       # Power kingdom
LAHUT = 3         # Divinity realm
HAHUT = 4         # Reality of realities
ANAHU = 5         # "I-ness" realm
HU = 6            # Pure Being


@dataclass
class ImaginalState:
    """State in imaginal realm."""
    material: torch.Tensor
    imaginal: torch.Tensor
    spiritual: torch.Tensor
    level: int


class ImaginalEmbedding(nn.Module):
    """Embed between material and imaginal realms."""
    
    def __init__(self, vocab_size: int = 10000, embed_dim: int = 256):
        super().__init__()
        
        self.embed_dim = embed_dim
        
        # Material embedding (concrete)
        self.material_embed = nn.Embedding(vocab_size, embed_dim)
        
        # Imaginal embedding (bridge)
        self.imaginal_embed = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 2),
            nn.GELU(),
            nn.Linear(embed_dim * 2, embed_dim)
        )
        
        # Spiritual embedding (abstract)
        self.spiritual_embed = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 2),
            nn.GELU(),
            nn.Linear(embed_dim * 2, embed_dim)
        )
        
    def forward(self, x: torch.Tensor) -> ImaginalState:
        """Embed across three realms."""
        # Material level
        material = self.material_embed(x).mean(dim=1)
        
        # Imaginal bridge
        imaginal = self.imaginal_embed(material)
        
        # Spiritual level
        spiritual = self.spiritual_embed(imaginal)
        
        return ImaginalState(
            material=material,
            imaginal=imaginal,
            spiritual=spiritual,
            level=1  # Starting at imaginal level
        )


class SevenLevelsProcessor(nn.Module):
    """Process through seven levels of consciousness."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Seven level processors
        self.levels = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embed_dim, embed_dim),
                nn.GELU(),
                nn.Linear(embed_dim, embed_dim)
            )
            for _ in range(7)
        ])
        
        # Level names
        self.level_names = ['Mulk', 'Malakut', 'Jabarut', 'Lahut', 'Hahut', 'Anahu', 'Hu']
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Process through all seven levels."""
        current = x
        level_outputs = []
        
        for i, level in enumerate(self.levels):
            current = level(current)
            level_outputs.append(current)
        
        return {
            'level_outputs': level_outputs,
            'level_names': self.level_names,
            'final_level': current
        }


class BarzakhLayer(nn.Module):
    """Barzakh - isthmus connecting opposites."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Connect opposites
        self.opposite_connector = nn.Linear(embed_dim * 2, embed_dim)
        
        # Mediation network
        self.mediation = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        
        # Unity detector (recognizing underlying unity)
        self.unity_detector = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.GELU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        opposite1: torch.Tensor,
        opposite2: torch.Tensor
    ) -> Dict:
        """Connect opposites through barzakh."""
        # Combine opposites
        combined = torch.cat([opposite1, opposite2], dim=-1)
        
        # Connect through barzakh
        connected = self.opposite_connector(combined)
        
        # Mediate
        mediated = self.mediation(connected)
        
        # Detect underlying unity
        unity = self.unity_detector(mediated)
        
        return {
            'connected': connected,
            'mediated': mediated,
            'unity': unity
        }


class CreativeImagination(nn.Module):
    """Active imagination as creative faculty."""
    
    def __init__(self, embed_dim: int = 256, hidden_dim: int = 512):
        super().__init__()
        
        # Imagination synthesis
        self.synthesis = nn.Sequential(
            nn.Linear(embed_dim * 3, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, embed_dim)
        )
        
        # Creative transformation
        self.transform = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, embed_dim)
        )
        
        # Truth detector (imaginal truth, not factual)
        self.truth_detector = nn.Sequential(
            nn.Linear(embed_dim, 256),
            nn.GELU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        state: ImaginalState
    ) -> Dict:
        """Creative imagination synthesis."""
        # Combine all three realms
        combined = torch.cat([state.material, state.imaginal, state.spiritual], dim=-1)
        
        # Synthesize
        synthesized = self.synthesis(combined)
        
        # Transform creatively
        transformed = self.transform(synthesized)
        
        # Detect imaginal truth
        truth = self.truth_detector(transformed)
        
        return {
            'synthesized': synthesized,
            'transformed': transformed,
            'imaginal_truth': truth
        }


class SufiImaginalNetwork(nn.Module):
    """Complete Sufi Imaginal Network.
    
    Applications:
    - Creative synthesis
    - Between concrete and abstract reasoning
    - Mystical experience modeling
    - Imagination-based inference
    """
    
    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 256,
        hidden_dim: int = 512
    ):
        super().__init__()
        
        self.embedding = ImaginalEmbedding(vocab_size, embed_dim)
        self.seven_levels = SevenLevelsProcessor(embed_dim)
        self.barzakh = BarzakhLayer(embed_dim)
        self.imagination = CreativeImagination(embed_dim, hidden_dim)
        
        # Haqiqa (truth) head
        self.haqiqa_head = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        x: torch.Tensor,
        num_levels: int = 7
    ) -> Dict:
        """Process through Sufi imaginal framework.
        
        Args:
            x: [batch, seq_len] token IDs
            num_levels: Number of consciousness levels to process
        Returns:
            Dict with imaginal state and truth
        """
        # Embed across realms
        state = self.embedding(x)
        
        # Process through seven levels
        level_result = self.seven_levels(state.spiritual)
        
        # Barzakh between material and spiritual
        barzakh_result = self.barzakh(state.material, state.spiritual)
        
        # Creative imagination
        imagination_result = self.imagination(state)
        
        # Haqiqa (ultimate truth)
        haqiqa = self.haqiqa_head(imagination_result['transformed'])
        
        return {
            'imaginal_state': state,
            'seven_levels': level_result,
            'barzakh': barzakh_result,
            'imagination': imagination_result,
            'haqiqa': haqiqa
        }


    @classmethod
    def self_test(cls) -> bool:
        """Create model, run forward pass, assert output shapes."""
        model = cls(vocab_size=100, embed_dim=64, hidden_dim=128)
        model.eval()
        x = torch.randint(0, 100, (2, 8))
        with torch.no_grad():
            result = model(x)
        assert result['haqiqa'].shape == (2, 1), f"haqiqa shape {result['haqiqa'].shape}"
        assert result['imaginal_state'].material.shape == (2, 64)
        assert result['barzakh']['unity'].shape == (2, 1)
        print("SufiImaginalNetwork self_test PASSED")
        return True


def create_sufi_imaginal_network(
    vocab_size: int = 10000,
    embed_dim: int = 256,
    hidden_dim: int = 512
) -> SufiImaginalNetwork:
    """Create SufiImaginalNetwork."""
    return SufiImaginalNetwork(vocab_size, embed_dim, hidden_dim)
