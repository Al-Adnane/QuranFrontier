"""Abhidhamma Network - Phenomenological Decomposition.

Inspired by: Buddhist Abhidhamma Pitaka

Key insights:
- Break experience into ultimate phenomena (dhammas)
- Systematic analysis of mind and reality
- Conditional relations between phenomena (24 patthana)
- Moment-to-moment analysis of consciousness
- No permanent self, only flowing processes

Architecture:
    Dhamma Decomposition: Break experience into ultimate constituents
    Conditional Relations: Model the 24 conditional relations
    Consciousness Moments: Moment-to-moment analysis
    Citta-Vithi: Cognitive process modeling
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field


# Abhidhamma categories (simplified)
ULTIMATE_REALITIES = {
    'citta': 89,  # Types of consciousness
    'cetasika': 52,  # Mental factors
    'rupa': 28,  # Material phenomena
    'nibbana': 1  # Unconditioned
}

CONDITIONAL_RELATIONS = [
    'root', 'object', 'dominance', 'proximity', 'contiguity',
    'conascent', 'mutual', 'support', 'decisive', 'prenascence',
    'postnascence', 'repetition', 'kamma', 'result', 'nutriment',
    'faculty', 'jhana', 'path', 'association', 'dissociation',
    'presence', 'absence', 'disappearance', 'non-disappearance'
]


@dataclass
class Dhamma:
    """An ultimate phenomenon (dhamma)."""
    dhamma_id: int
    category: str  # citta, cetasika, rupa, nibbana
    characteristics: List[str]
    function: str
    manifestation: str
    proximate_cause: str
    conditionality: Dict[str, float]  # Relations to other dhammas


class DhammaDecomposition(nn.Module):
    """Decompose experience into ultimate phenomena."""
    
    def __init__(self, input_dim: int = 512, dhamma_dim: int = 256):
        super().__init__()
        
        self.dhamma_dim = dhamma_dim
        
        # Total dhamma types (simplified)
        total_dhammas = sum(ULTIMATE_REALITIES.values())
        
        # Decomposition heads for each category
        self.citta_head = nn.Linear(input_dim, ULTIMATE_REALITIES['citta'] * dhamma_dim)
        self.cetasika_head = nn.Linear(input_dim, ULTIMATE_REALITIES['cetasika'] * dhamma_dim)
        self.rupa_head = nn.Linear(input_dim, ULTIMATE_REALITIES['rupa'] * dhamma_dim)
        
        # Nibbana is unconditioned - special handling
        self.nibbana_head = nn.Linear(input_dim, dhamma_dim)
        
        # Softmax for categorical distribution
        self.citta_softmax = nn.Softmax(dim=-1)
        self.cetasika_softmax = nn.Softmax(dim=-1)
        self.rupa_softmax = nn.Softmax(dim=-1)
        
    def forward(self, experience: torch.Tensor) -> Dict:
        """Decompose experience into dhammas."""
        batch_size = experience.size(0)
        
        # Decompose into categories
        citta_logits = self.citta_head(experience).view(batch_size, ULTIMATE_REALITIES['citta'], self.dhamma_dim)
        cetasika_logits = self.cetasika_head(experience).view(batch_size, ULTIMATE_REALITIES['cetasika'], self.dhamma_dim)
        rupa_logits = self.rupa_head(experience).view(batch_size, ULTIMATE_REALITIES['rupa'], self.dhamma_dim)
        nibbana_repr = self.nibbana_head(experience)
        
        # Get distributions over dhamma types
        citta_weights = self.citta_softmax(citta_logits.mean(dim=-1))
        cetasika_weights = self.cetasika_softmax(cetasika_logits.mean(dim=-1))
        rupa_weights = self.rupa_softmax(rupa_logits.mean(dim=-1))
        
        # Weighted representations
        citta_repr = (citta_weights.unsqueeze(-1) * citta_logits).sum(dim=1)
        cetasika_repr = (cetasika_weights.unsqueeze(-1) * cetasika_logits).sum(dim=1)
        rupa_repr = (rupa_weights.unsqueeze(-1) * rupa_logits).sum(dim=1)
        
        return {
            'citta': citta_repr,
            'cetasika': cetasika_repr,
            'rupa': rupa_repr,
            'nibbana': nibbana_repr,
            'citta_weights': citta_weights,
            'cetasika_weights': cetasika_weights,
            'rupa_weights': rupa_weights
        }


class ConditionalRelations(nn.Module):
    """Model the 24 conditional relations (patthana)."""
    
    def __init__(self, dhamma_dim: int = 256, num_relations: int = 24):
        super().__init__()
        
        self.num_relations = num_relations
        
        # Relation embeddings
        self.relation_embed = nn.Embedding(num_relations, dhamma_dim)
        
        # Relation strength predictors
        self.relation_strength = nn.Sequential(
            nn.Linear(dhamma_dim * 2, dhamma_dim),
            nn.GELU(),
            nn.Linear(dhamma_dim, 1),
            nn.Sigmoid()
        )
        
        # Conditional dependency graph
        self.conditional_graph = nn.Parameter(torch.randn(num_relations, num_relations) * 0.1)
        
    def forward(
        self,
        dhamma_repr: Dict[str, torch.Tensor],
        relation_mask: Optional[torch.Tensor] = None
    ) -> Dict:
        """Compute conditional relations between dhammas."""
        # Extract representations
        citta = dhamma_repr['citta']
        cetasika = dhamma_repr['cetasika']
        rupa = dhamma_repr['rupa']
        
        # Compute relation strengths between categories
        relations = {}
        
        for i, rel_name in enumerate(CONDITIONAL_RELATIONS):
            rel_embed = self.relation_embed(torch.tensor(i, device=citta.device))
            
            # Check if this relation applies between categories
            citta_cetasika = torch.cat([citta, cetasika], dim=-1)
            citta_rupa = torch.cat([citta, rupa], dim=-1)
            
            relations[f'{rel_name}_cc'] = self.relation_strength(citta_cetasika)
            relations[f'{rel_name}_cr'] = self.relation_strength(citta_rupa)
        
        # Build conditional graph
        conditional_graph = torch.sigmoid(self.conditional_graph)
        
        return {
            'relations': relations,
            'conditional_graph': conditional_graph,
            'relation_embeds': self.relation_embed.weight
        }


class ConsciousnessMoment(nn.Module):
    """Model a single moment of consciousness (citta-khana)."""
    
    def __init__(self, dhamma_dim: int = 256):
        super().__init__()
        
        # Three phases of consciousness moment
        self.arising = nn.Linear(dhamma_dim, dhamma_dim)
        self.presence = nn.Linear(dhamma_dim, dhamma_dim)
        self.dissolution = nn.Linear(dhamma_dim, dhamma_dim)
        
        # Moment integration
        self.moment_integrate = nn.Sequential(
            nn.Linear(dhamma_dim * 3, dhamma_dim),
            nn.GELU(),
            nn.Linear(dhamma_dim, dhamma_dim)
        )
        
    def forward(self, citta_repr: torch.Tensor) -> Dict:
        """Process a moment of consciousness."""
        # Three phases
        arising = self.arising(citta_repr)
        presence = self.presence(citta_repr)
        dissolution = self.dissolution(citta_repr)
        
        # Integrate
        combined = torch.cat([arising, presence, dissolution], dim=-1)
        moment_repr = self.moment_integrate(combined)
        
        return {
            'moment_repr': moment_repr,
            'arising': arising,
            'presence': presence,
            'dissolution': dissolution,
            'impermanence_score': torch.norm(dissolution - arising, dim=-1)
        }


class CittaVithi(nn.Module):
    """Model cognitive process (citta-vithi) - sequence of consciousness moments."""
    
    def __init__(self, dhamma_dim: int = 256, max_moments: int = 17):
        super().__init__()
        
        self.max_moments = max_moments
        
        # Cognitive process phases (simplified)
        # Past bhavanga, bhavanga calana, bhavanga upaccheda, etc.
        self.phase_embed = nn.Embedding(17, dhamma_dim)
        
        # Process sequence
        self.process_rnn = nn.LSTM(dhamma_dim, dhamma_dim, num_layers=2, batch_first=True)
        
        # Process completion detector
        self.completion_detector = nn.Sequential(
            nn.Linear(dhamma_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        moment_sequence: torch.Tensor,  # [batch, num_moments, dhamma_dim]
        phase_indices: Optional[torch.Tensor] = None
    ) -> Dict:
        """Process cognitive process sequence."""
        batch_size, num_moments, dhamma_dim = moment_sequence.shape
        
        # Add phase embeddings if provided
        if phase_indices is not None:
            phase_emb = self.phase_embed(phase_indices)
            moment_sequence = moment_sequence + phase_emb
        
        # Process sequence
        output, (hidden, _) = self.process_rnn(moment_sequence)
        
        # Detect completion
        completion = self.completion_detector(hidden[-1])
        
        return {
            'process_output': output,
            'final_state': hidden[-1],
            'completion': completion,
            'num_moments': num_moments
        }


class AbhidhammaNetwork(nn.Module):
    """Complete Abhidhamma Network for phenomenological analysis.
    
    Inspired by Buddhist Abhidhamma Pitaka.
    
    Applications:
    - Fine-grained experience analysis
    - Consciousness modeling
    - Conditional reasoning
    - Mind-state classification
    """
    
    def __init__(
        self,
        input_dim: int = 512,
        dhamma_dim: int = 256
    ):
        super().__init__()
        
        self.decomposition = DhammaDecomposition(input_dim, dhamma_dim)
        self.conditional = ConditionalRelations(dhamma_dim)
        self.moment = ConsciousnessMoment(dhamma_dim)
        self.vithi = CittaVithi(dhamma_dim)
        
        # Output integration
        self.output_proj = nn.Linear(dhamma_dim, dhamma_dim)
        
    def forward(
        self,
        experience: torch.Tensor,
        moment_sequence: Optional[torch.Tensor] = None
    ) -> Dict:
        """Analyze experience through Abhidhamma framework.
        
        Args:
            experience: [batch, input_dim] experience to analyze
            moment_sequence: Optional [batch, num_moments, dhamma_dim] for cognitive process
        Returns:
            Dict with phenomenological analysis
        """
        # Decompose into dhammas
        dhamma_repr = self.decomposition(experience)
        
        # Compute conditional relations
        relations = self.conditional(dhamma_repr)
        
        # Analyze consciousness moment
        moment_analysis = self.moment(dhamma_repr['citta'])
        
        # Process cognitive sequence if provided
        vithi_analysis = None
        if moment_sequence is not None:
            vithi_analysis = self.vithi(moment_sequence)
        
        # Integrate
        integrated = (
            dhamma_repr['citta'] +
            dhamma_repr['cetasika'] +
            dhamma_repr['rupa']
        ) / 3
        
        output = self.output_proj(integrated)
        
        return {
            'output': output,
            'dhamma_decomposition': dhamma_repr,
            'conditional_relations': relations,
            'moment_analysis': moment_analysis,
            'vithi_analysis': vithi_analysis,
            'impermanence': moment_analysis['impermanence_score']
        }


def create_abhidhamma_network(
    input_dim: int = 512,
    dhamma_dim: int = 256
) -> AbhidhammaNetwork:
    """Create AbhidhammaNetwork."""
    return AbhidhammaNetwork(input_dim, dhamma_dim)
