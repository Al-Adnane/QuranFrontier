"""Cross-Modal Synesthesia Network - Sensory Blending Architecture.

Implements cross-modal perception inspired by synesthesia:
- Sound → Color associations
- Text → Taste mappings
- Number → Space positioning
- Multi-sensory integration

Architecture:
    Modality Encoders: Separate encoders for each sense
    Cross-Modal Attention: Attend across modalities
    Synesthetic Mapping: Learnable cross-modal projections
    Blended Representation: Unified multi-sensory space

Applications:
- Multi-modal AI (text + image + audio)
- Creative AI (art from music, etc.)
- Accessibility (sensory substitution)
- Enhanced memory (multi-sensory encoding)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SynestheticExperience:
    """Result of cross-modal processing."""
    primary_modality: str
    induced_modalities: Dict[str, torch.Tensor]
    blending_strength: float
    consistency_score: float


class ModalityEncoder(nn.Module):
    """Encoder for a specific sensory modality."""
    
    def __init__(
        self,
        modality_name: str,
        input_dim: int,
        shared_dim: int = 512
    ):
        super().__init__()
        self.modality_name = modality_name
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, shared_dim * 2),
            nn.GELU(),
            nn.Linear(shared_dim * 2, shared_dim),
            nn.LayerNorm(shared_dim)
        )
        
        # Modality-specific embedding
        self.modality_embed = nn.Parameter(torch.randn(shared_dim) * 0.1)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        encoded = self.encoder(x)
        return encoded + self.modality_embed.unsqueeze(0)


class SynestheticMapping(nn.Module):
    """Maps between sensory modalities."""
    
    def __init__(
        self,
        source_modality: str,
        target_modality: str,
        shared_dim: int = 512
    ):
        super().__init__()
        self.source = source_modality
        self.target = target_modality
        
        # Cross-modal projection
        self.projection = nn.Sequential(
            nn.Linear(shared_dim, shared_dim),
            nn.GELU(),
            nn.Linear(shared_dim, shared_dim)
        )
        
        # Consistency regularizer
        self.consistency_head = nn.Linear(shared_dim * 2, 1)
        
    def forward(
        self,
        source_representation: torch.Tensor,
        target_representation: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, float]:
        """Map from source to target modality."""
        mapped = self.projection(source_representation)
        
        # Compute consistency if target is provided
        consistency = 0.0
        if target_representation is not None:
            combined = torch.cat([mapped, target_representation], dim=-1)
            consistency = torch.sigmoid(self.consistency_head(combined)).mean().item()
        
        return mapped, consistency


class CrossModalAttention(nn.Module):
    """Attention mechanism across modalities."""
    
    def __init__(self, shared_dim: int = 512, num_heads: int = 8):
        super().__init__()
        self.attention = nn.MultiheadAttention(shared_dim, num_heads, batch_first=True)
        
    def forward(
        self,
        query: torch.Tensor,
        modalities: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """Attend from query to all modalities."""
        results = {}
        
        for name, modality_repr in modalities.items():
            if modality_repr.dim() == 2:
                modality_repr = modality_repr.unsqueeze(1)
            if query.dim() == 2:
                query_expanded = query.unsqueeze(1)
            else:
                query_expanded = query
            
            attended, weights = self.attention(
                query_expanded,
                modality_repr,
                modality_repr
            )
            results[name] = {
                'attended': attended.squeeze(1),
                'weights': weights
            }
        
        return results


class CrossModalSynesthesiaNetwork(nn.Module):
    """Main cross-modal synesthesia network.
    
    Creates blended multi-sensory representations.
    """
    
    def __init__(
        self,
        modality_dims: Dict[str, int] = None,
        shared_dim: int = 512
    ):
        super().__init__()
        
        if modality_dims is None:
            modality_dims = {
                'visual': 512,
                'auditory': 256,
                'textual': 768,
                'tactile': 128,
                'conceptual': 512
            }
        
        self.modalities = list(modality_dims.keys())
        
        # Encoders for each modality
        self.encoders = nn.ModuleDict({
            name: ModalityEncoder(name, dim, shared_dim)
            for name, dim in modality_dims.items()
        })
        
        # Synesthetic mappings between all pairs
        self.mappings = nn.ModuleDict()
        for source in self.modalities:
            for target in self.modalities:
                if source != target:
                    key = f"{source}_to_{target}"
                    self.mappings[key] = SynestheticMapping(source, target, shared_dim)
        
        # Cross-modal attention
        self.attention = CrossModalAttention(shared_dim)
        
        # Blended representation
        self.blend = nn.Linear(shared_dim * len(self.modalities), shared_dim)
        
        self.shared_dim = shared_dim
        
    def encode_all(
        self,
        inputs: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """Encode all available modalities."""
        representations = {}
        for name, input_tensor in inputs.items():
            if name in self.encoders:
                representations[name] = self.encoders[name](input_tensor)
        return representations
    
    def induce_synesthesia(
        self,
        primary_modality: str,
        primary_input: torch.Tensor,
        target_modalities: Optional[List[str]] = None
    ) -> SynestheticExperience:
        """Induce synesthetic experience from primary modality."""
        
        # Encode primary
        primary_repr = self.encoders[primary_modality](primary_input)
        
        # Map to other modalities
        induced = {}
        consistencies = []
        
        targets = target_modalities or [m for m in self.modalities if m != primary_modality]
        
        for target in targets:
            key = f"{primary_modality}_to_{target}"
            if key in self.mappings:
                mapped, consistency = self.mappings[key](primary_repr)
                induced[target] = mapped
                consistencies.append(consistency)
        
        return SynestheticExperience(
            primary_modality=primary_modality,
            induced_modalities=induced,
            blending_strength=torch.norm(primary_repr, dim=-1).mean().item(),
            consistency_score=sum(consistencies) / len(consistencies) if consistencies else 0.0
        )
    
    def blend_modalities(
        self,
        representations: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Create blended multi-sensory representation."""
        # Concatenate all available modalities
        tensors = []
        for name in self.modalities:
            if name in representations:
                tensors.append(representations[name])
            else:
                # Zero padding for missing modalities
                tensors.append(torch.zeros(
                    representations[list(representations.keys())[0]].size(0),
                    self.shared_dim,
                    device=next(iter(representations.values())).device
                ))
        
        combined = torch.cat(tensors, dim=-1)
        return self.blend(combined)
    
    def forward(
        self,
        inputs: Dict[str, torch.Tensor],
        primary_modality: Optional[str] = None
    ) -> Dict:
        """Forward pass with cross-modal processing."""
        
        # Encode all modalities
        representations = self.encode_all(inputs)
        
        # Cross-modal attention
        if representations:
            first_key = list(representations.keys())[0]
            attention_results = self.attention(
                representations[first_key],
                representations
            )
        else:
            attention_results = {}
        
        # Synesthetic induction
        if primary_modality and primary_modality in inputs:
            synesthesia = self.induce_synesthesia(
                primary_modality,
                inputs[primary_modality]
            )
        else:
            synesthesia = None
        
        # Blend
        blended = self.blend_modalities(representations)
        
        return {
            'representations': representations,
            'attention': attention_results,
            'synesthesia': synesthesia,
            'blended': blended
        }


def create_synesthesia_network(
    modality_dims: Dict[str, int] = None,
    shared_dim: int = 512
) -> CrossModalSynesthesiaNetwork:
    """Create CrossModalSynesthesiaNetwork."""
    return CrossModalSynesthesiaNetwork(modality_dims, shared_dim)
