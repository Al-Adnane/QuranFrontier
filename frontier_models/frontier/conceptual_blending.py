"""Conceptual Blending Network - Computational Creativity.

Inspired by: Fauconnier & Turner's Conceptual Blending Theory

Key insights:
- Creativity emerges from blending mental spaces
- Input spaces → Generic space → Blended space
- Emergent structure not present in inputs
- Composition, completion, elaboration stages

Architecture:
    Mental Space Encoder: Encode input conceptual spaces
    Generic Space: Extract common structure
    Blending Network: Combine spaces with emergent structure
    Elaboration: Develop blended space
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MentalSpace:
    """A conceptual mental space."""
    elements: torch.Tensor  # [batch, num_elements, dim]
    relations: torch.Tensor  # [batch, num_elements, num_elements]
    frame: torch.Tensor  # [batch, frame_dim]


@dataclass
class BlendResult:
    """Result of conceptual blending."""
    blended_space: MentalSpace
    emergent_structure: torch.Tensor
    blend_quality: torch.Tensor
    creativity_score: torch.Tensor


class MentalSpaceEncoder(nn.Module):
    """Encode concepts into mental spaces."""
    
    def __init__(self, vocab_size: int = 10000, element_dim: int = 128, max_elements: int = 10):
        super().__init__()
        
        self.element_dim = element_dim
        self.max_elements = max_elements
        
        # Element embedding
        self.element_embed = nn.Embedding(vocab_size, element_dim)
        
        # Relation embedding (between pairs of elements)
        self.relation_embed = nn.Embedding(20, element_dim)  # 20 relation types
        
        # Frame embedding (context/schema)
        self.frame_embed = nn.Embedding(100, element_dim)  # 100 frame types
        
    def forward(
        self,
        element_ids: torch.Tensor,
        relation_ids: torch.Tensor,
        frame_id: torch.Tensor
    ) -> MentalSpace:
        """Encode concepts into mental space."""
        batch_size, num_elements = element_ids.shape
        
        # Embed elements
        elements = self.element_embed(element_ids)
        
        # Embed relations
        relations = self.relation_embed(relation_ids)
        
        # Embed frame
        frame = self.frame_embed(frame_id).unsqueeze(1).expand(-1, num_elements, -1)
        
        # Combine
        elements = elements + frame
        
        return MentalSpace(
            elements=elements,
            relations=relations,
            frame=self.frame_embed(frame_id)
        )


class GenericSpaceExtractor(nn.Module):
    """Extract common structure from multiple mental spaces."""
    
    def __init__(self, element_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        
        # Cross-space attention
        self.cross_attention = nn.MultiheadAttention(element_dim, num_heads=4, batch_first=True)
        
        # Common structure extractor
        self.common_extractor = nn.Sequential(
            nn.Linear(element_dim * 2, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, element_dim)
        )
        
    def forward(
        self,
        space1: MentalSpace,
        space2: MentalSpace
    ) -> MentalSpace:
        """Extract generic space from two input spaces."""
        # Cross-space attention to find commonalities
        attended1, _ = self.cross_attention(
            space1.elements,
            space2.elements,
            space2.elements
        )
        
        attended2, _ = self.cross_attention(
            space2.elements,
            space1.elements,
            space1.elements
        )
        
        # Combine to find common structure
        combined1 = torch.cat([space1.elements, attended1], dim=-1)
        combined2 = torch.cat([space2.elements, attended2], dim=-1)
        
        common1 = self.common_extractor(combined1)
        common2 = self.common_extractor(combined2)
        
        # Average common structure
        generic_elements = (common1 + common2) / 2
        
        return MentalSpace(
            elements=generic_elements,
            relations=(space1.relations + space2.relations) / 2,
            frame=(space1.frame + space2.frame) / 2
        )


class BlendingNetwork(nn.Module):
    """Blend mental spaces with emergent structure."""
    
    def __init__(self, element_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        
        # Composition: combine elements from input spaces
        self.composition = nn.Sequential(
            nn.Linear(element_dim * 3, hidden_dim),  # space1 + space2 + generic
            nn.GELU(),
            nn.Linear(hidden_dim, element_dim)
        )
        
        # Completion: fill in missing structure from long-term memory
        self.completion = nn.Sequential(
            nn.Linear(element_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, element_dim)
        )
        
        # Emergent structure detector
        self.emergent_detector = nn.Sequential(
            nn.Linear(element_dim * 2, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        space1: MentalSpace,
        space2: MentalSpace,
        generic: MentalSpace
    ) -> BlendResult:
        """Blend two mental spaces."""
        # Composition stage
        combined = torch.cat([
            space1.elements,
            space2.elements,
            generic.elements
        ], dim=-1)
        blended_elements = self.composition(combined)
        
        # Completion stage
        completed_elements = blended_elements + self.completion(blended_elements)
        
        # Create blended space
        blended_space = MentalSpace(
            elements=completed_elements,
            relations=(space1.relations + space2.relations) / 2,
            frame=generic.frame
        )
        
        # Detect emergent structure (new patterns not in inputs)
        emergent_input = torch.cat([
            blended_elements,
            (space1.elements + space2.elements) / 2
        ], dim=-1)
        emergent_structure = self.emergent_detector(emergent_input)
        
        # Compute blend quality
        blend_quality = self._compute_blend_quality(blended_space, space1, space2)
        
        # Creativity score (emergence + quality)
        creativity_score = emergent_structure.mean(dim=1) * blend_quality
        
        return BlendResult(
            blended_space=blended_space,
            emergent_structure=emergent_structure,
            blend_quality=blend_quality,
            creativity_score=creativity_score
        )
    
    def _compute_blend_quality(
        self,
        blended: MentalSpace,
        space1: MentalSpace,
        space2: MentalSpace
    ) -> torch.Tensor:
        """Compute quality of blend (integration, topology, etc.)."""
        # Integration: how well elements fit together
        integration = blended.elements.std(dim=1).mean(dim=-1, keepdim=True)
        
        # Topology preservation: structure from inputs preserved
        topology1 = F.cosine_similarity(blended.elements, space1.elements, dim=-1).mean(dim=1, keepdim=True)
        topology2 = F.cosine_similarity(blended.elements, space2.elements, dim=-1).mean(dim=1, keepdim=True)
        
        # Webbing: connections between elements
        webbing = blended.relations.norm(dim=-1).mean(dim=1, keepdim=True)
        
        # Quality = integration + topology + webbing
        quality = (integration + topology1 + topology2 + webbing) / 4
        
        return quality.sigmoid()


class ElaborationNetwork(nn.Module):
    """Elaborate and develop the blended space."""
    
    def __init__(self, element_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        
        # Elaboration RNN (develop the blend over time)
        self.elaboration_rnn = nn.LSTM(element_dim, hidden_dim, num_layers=2, batch_first=True)
        
        # Output projection
        self.output_proj = nn.Linear(hidden_dim, element_dim)
        
    def forward(
        self,
        blended_space: MentalSpace,
        num_steps: int = 5
    ) -> List[MentalSpace]:
        """Elaborate blended space over multiple steps."""
        batch_size, num_elements, element_dim = blended_space.elements.shape
        
        # Initialize RNN
        h0 = torch.zeros(2, batch_size, self.elaboration_rnn.hidden_size, device=blended_space.elements.device)
        c0 = torch.zeros(2, batch_size, self.elaboration_rnn.hidden_size, device=blended_space.elements.device)
        
        elaborated_spaces = []
        current_elements = blended_space.elements
        
        for step in range(num_steps):
            # Run elaboration step
            output, (h0, c0) = self.elaboration_rnn(current_elements, (h0, c0))
            
            # Project back to element space
            new_elements = self.output_proj(output)
            
            # Create elaborated space
            elaborated_space = MentalSpace(
                elements=new_elements,
                relations=blended_space.relations,
                frame=blended_space.frame
            )
            
            elaborated_spaces.append(elaborated_space)
            current_elements = new_elements
        
        return elaborated_spaces


class ConceptualBlendingNetwork(nn.Module):
    """Complete Conceptual Blending Network for computational creativity.
    
    Applications:
    - Creative idea generation
    - Metaphor understanding
    - Analogical reasoning
    - Conceptual innovation
    """
    
    def __init__(
        self,
        vocab_size: int = 10000,
        element_dim: int = 128,
        max_elements: int = 10
    ):
        super().__init__()
        
        self.encoder = MentalSpaceEncoder(vocab_size, element_dim, max_elements)
        self.generic_extractor = GenericSpaceExtractor(element_dim)
        self.blender = BlendingNetwork(element_dim)
        self.elaboration = ElaborationNetwork(element_dim)
        
    def forward(
        self,
        space1_elements: torch.Tensor,
        space1_relations: torch.Tensor,
        space1_frame: torch.Tensor,
        space2_elements: torch.Tensor,
        space2_relations: torch.Tensor,
        space2_frame: torch.Tensor,
        num_elaboration_steps: int = 5
    ) -> Dict:
        """Perform conceptual blending.
        
        Args:
            space1_elements: [batch, num_elements] element IDs for space 1
            space1_relations: [batch, num_elements, num_elements] relation IDs for space 1
            space1_frame: [batch] frame ID for space 1
            space2_elements: [batch, num_elements] element IDs for space 2
            space2_relations: [batch, num_elements, num_elements] relation IDs for space 2
            space2_frame: [batch] frame ID for space 2
            num_elaboration_steps: Number of elaboration steps
        Returns:
            Dict with blend result and elaborated spaces
        """
        # Encode input spaces
        space1 = self.encoder(space1_elements, space1_relations, space1_frame)
        space2 = self.encoder(space2_elements, space2_relations, space2_frame)
        
        # Extract generic space
        generic = self.generic_extractor(space1, space2)
        
        # Blend spaces
        blend_result = self.blender(space1, space2, generic)
        
        # Elaborate blend
        elaborated_spaces = self.elaboration(blend_result.blended_space, num_elaboration_steps)
        
        return {
            'blend_result': blend_result,
            'elaborated_spaces': elaborated_spaces,
            'input_space1': space1,
            'input_space2': space2,
            'generic_space': generic,
            'creativity_score': blend_result.creativity_score.mean().item()
        }


def create_conceptual_blending_network(
    vocab_size: int = 10000,
    element_dim: int = 128,
    max_elements: int = 10
) -> ConceptualBlendingNetwork:
    """Create ConceptualBlendingNetwork."""
    return ConceptualBlendingNetwork(vocab_size, element_dim, max_elements)
