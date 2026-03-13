"""Kabbalah Sefirot Network - Tree of Life Architecture.

Inspired by: Kabbalistic Tree of Life

Key insights:
- 10 Sefirot as processing nodes
- 22 Paths connecting Sefirot (Hebrew letters)
- Four Worlds (Atziluth, Beriah, Yetzirah, Assiah)
- Tzimtzum (divine contraction) for creation
- Light flowing from Keter to Malkuth

Architecture:
    Sefirot Nodes: 10 hierarchical processing units
    Path Connections: 22 bidirectional pathways
    Four Worlds: Hierarchical depth processing
    Light Flow: Top-down and bottom-up processing
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# 10 Sefirot in order of emanation
SEFIROT_NAMES = [
    'Keter',      # Crown - divine will
    'Chokhmah',   # Wisdom - pure insight
    'Binah',      # Understanding - analytical
    'Chesed',     # Loving-kindness - expansion
    'Gevurah',    # Strength - contraction
    'Tiferet',    # Beauty - harmony
    'Netzach',    # Eternity - endurance
    'Hod',        # Splendor - submission
    'Yesod',      # Foundation - connection
    'Malkuth'     # Kingdom - manifestation
]

# 22 Paths (simplified adjacency)
SEFIROT_PATHS = [
    (0, 1), (0, 2),  # Keter to Chokhmah, Binah
    (1, 2), (1, 3), (1, 6),  # Chokhmah connections
    (2, 4), (2, 5),  # Binah connections
    (3, 4), (3, 6),  # Chesed connections
    (4, 5), (4, 7),  # Gevurah connections
    (5, 6), (5, 7), (5, 8),  # Tiferet connections
    (6, 8), (6, 9),  # Netzach connections
    (7, 8), (7, 9),  # Hod connections
    (8, 9),  # Yesod to Malkuth
]

# Four Worlds
WORLDS = ['Atziluth', 'Beriah', 'Yetzirah', 'Assiah']


@dataclass
class SefirotState:
    """State of all 10 Sefirot."""
    sefirot: List[torch.Tensor]
    light_flow: torch.Tensor


class SefirahNode(nn.Module):
    """Single Sefirah processing node."""
    
    def __init__(self, sefirah_index: int, embed_dim: int = 256):
        super().__init__()
        
        self.sefirah_index = sefirah_index
        self.sefirah_name = SEFIROT_NAMES[sefirah_index]
        
        # Sefirah-specific processing
        self.processor = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        
        # Light receiver
        self.light_receiver = nn.Linear(embed_dim, embed_dim)
        
        # Light emitter
        self.light_emitter = nn.Linear(embed_dim, embed_dim)
        
    def forward(self, x: torch.Tensor, incoming_light: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Process through this Sefirah."""
        # Process input
        processed = self.processor(x)
        
        # Receive light from above
        if incoming_light is not None:
            received = self.light_receiver(incoming_light)
            processed = processed + received
        
        return processed


class PathConnection(nn.Module):
    """Path connecting two Sefirot."""
    
    def __init__(self, from_sefirah: int, to_sefirah: int, embed_dim: int = 256):
        super().__init__()
        
        self.from_sefirah = from_sefirah
        self.to_sefirah = to_sefirah
        
        # Path transformation
        self.path_transform = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        
        # Path weight (learnable)
        self.path_weight = nn.Parameter(torch.ones(1) * 0.5)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Transmit light through path."""
        transformed = self.path_transform(x)
        return transformed * self.path_weight


class FourWorldsProcessor(nn.Module):
    """Process through Four Worlds."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Four world processors
        self.world_processors = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embed_dim, embed_dim),
                nn.GELU(),
                nn.Linear(embed_dim, embed_dim)
            )
            for _ in range(4)
        ])
        
        self.world_names = WORLDS
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Process through all four worlds."""
        current = x
        world_outputs = []
        
        for processor in self.world_processors:
            current = processor(current)
            world_outputs.append(current)
        
        return {
            'world_outputs': world_outputs,
            'world_names': self.world_names,
            'final_world': current
        }


class TzimtzumLayer(nn.Module):
    """Tzimtzum - divine contraction for creation."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Contraction (limitation for manifestation)
        self.contraction = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Linear(embed_dim // 2, embed_dim)
        )
        
        # Void space (potential)
        self.void_space = nn.Parameter(torch.randn(embed_dim) * 0.1)
        
        # Creation from void
        self.creation = nn.Linear(embed_dim, embed_dim)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Apply tzimtzum process."""
        # Contract
        contracted = self.contraction(x)
        
        # Create void space
        void = self.void_space.unsqueeze(0).expand(x.size(0), -1)
        
        # Create from void
        created = self.creation(contracted + void)
        
        return {
            'contracted': contracted,
            'void': void,
            'created': created
        }


class KabbalahSefirotNetwork(nn.Module):
    """Complete Kabbalah Tree of Life Network.
    
    Applications:
    - Hierarchical information processing
    - Light flow modeling
    - Emanation cascades
    - Sacred geometry computation
    """
    
    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 256,
        hidden_dim: int = 512
    ):
        super().__init__()
        
        # Input embedding
        self.embed = nn.Embedding(vocab_size, embed_dim)
        
        # 10 Sefirot nodes
        self.sefirot = nn.ModuleList([
            SefirahNode(i, embed_dim) for i in range(10)
        ])
        
        # 22 Path connections
        self.paths = nn.ModuleList([
            PathConnection(from_s, to_s, embed_dim)
            for from_s, to_s in SEFIROT_PATHS
        ])
        
        # Four Worlds processing
        self.four_worlds = FourWorldsProcessor(embed_dim)
        
        # Tzimtzum
        self.tzimtzum = TzimtzumLayer(embed_dim)
        
        # Shekhinah (divine presence) head
        self.shekhinah_head = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        x: torch.Tensor,
        num_iterations: int = 3
    ) -> Dict:
        """Process through Tree of Life.
        
        Args:
            x: [batch, seq_len] token IDs
            num_iterations: Number of light flow iterations
        Returns:
            Dict with Sefirot states and divine presence
        """
        batch_size = x.size(0)
        
        # Initial embedding
        embedded = self.embed(x).mean(dim=1)
        
        # Initialize Sefirot states
        sefirot_states = [embedded.clone() for _ in range(10)]
        
        # Light flow iterations
        for _ in range(num_iterations):
            # Top-down flow (Keter to Malkuth)
            for i in range(10):
                # Get incoming light from connected Sefirot above
                incoming = None
                for path in self.paths:
                    if path.to_sefirah == i:
                        if incoming is None:
                            incoming = sefirot_states[path.from_sefirah]
                        else:
                            incoming = incoming + sefirot_states[path.from_sefirah]
                
                # Process through this Sefirah
                sefirot_states[i] = self.sefirot[i](sefirot_states[i], incoming)
        
        # Process through Four Worlds
        malkuth_state = sefirot_states[9]  # Malkuth
        world_result = self.four_worlds(malkuth_state)
        
        # Tzimtzum for manifestation
        tzimtzum_result = self.tzimtzum(world_result['final_world'])
        
        # Shekhinah (divine presence in manifestation)
        shekhinah = self.shekhinah_head(tzimtzum_result['created'])
        
        return {
            'sefirot_states': sefirot_states,
            'sefirot_names': SEFIROT_NAMES,
            'four_worlds': world_result,
            'tzimtzum': tzimtzum_result,
            'shekhinah': shekhinah
        }


def create_kabbalah_sefirot_network(
    vocab_size: int = 10000,
    embed_dim: int = 256,
    hidden_dim: int = 512
) -> KabbalahSefirotNetwork:
    """Create KabbalahSefirotNetwork."""
    return KabbalahSefirotNetwork(vocab_size, embed_dim, hidden_dim)
