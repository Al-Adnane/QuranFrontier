"""Jain Seven-Valued Logic Network - Syadvada Reasoning.

Inspired by: Jain Syadvada (Seven-Valued Logic)

Key insights:
- Seven truth values (Saptabhangi) beyond true/false
- Syad-asti (maybe is)
- Syad-nasti (maybe is not)
- Syad-asti-nasti (maybe is and is not)
- Syad-asti-avaktavya (maybe is and is indescribable)
- Syad-nasti-avaktavya (maybe is not and is indescribable)
- Syad-asti-nasti-avaktavya (maybe is, is not, and is indescribable)
- Syad-avaktavya (maybe is indescribable)
- Anekantavada (non-absolutism)

Architecture:
    Seven Truth Values: Probability distribution over 7 values
    Perspective Taking: Multiple viewpoint integration
    Conditional Predication: Context-dependent truth
    Non-Absolutism: Avoiding one-sided conclusions
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# Seven truth values (Saptabhangi)
TRUTH_VALUES = [
    'asti',           # Is (exists)
    'nasti',          # Is not (does not exist)
    'asti-nasti',     # Is and is not
    'asti-avaktavya', # Is and is indescribable
    'nasti-avaktavya',# Is not and is indescribable
    'asti-nasti-avaktavya', # Is, is not, and is indescribable
    'avaktavya'       # Is indescribable
]


@dataclass
class SevenValuedState:
    """Seven-valued truth state."""
    probabilities: torch.Tensor  # [batch, 7]
    primary_value: torch.Tensor  # Most likely truth value
    indeterminacy: torch.Tensor  # Degree of indeterminacy


class SevenValuedEmbedding(nn.Module):
    """Embed into seven-valued space."""
    
    def __init__(self, vocab_size: int = 10000, embed_dim: int = 256):
        super().__init__()
        
        self.embed_dim = embed_dim
        
        # Standard embedding
        self.embed = nn.Embedding(vocab_size, embed_dim)
        
        # Project to seven truth values
        self.truth_projection = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, 7)
        )
        
    def forward(self, x: torch.Tensor) -> SevenValuedState:
        """Embed and compute seven truth values."""
        embedded = self.embed(x).mean(dim=1)
        
        # Project to truth values
        truth_logits = self.truth_projection(embedded)
        
        # Softmax for probabilities
        probabilities = F.softmax(truth_logits, dim=-1)
        
        # Primary value
        primary_value = probabilities.argmax(dim=-1)
        
        # Indeterminacy (entropy)
        indeterminacy = -(probabilities * torch.log(probabilities + 1e-9)).sum(dim=-1)
        
        return SevenValuedState(
            probabilities=probabilities,
            primary_value=primary_value,
            indeterminacy=indeterminacy
        )


class PerspectiveTaker(nn.Module):
    """Take multiple perspectives (Anekantavada)."""
    
    def __init__(self, embed_dim: int = 256, num_perspectives: int = 7):
        super().__init__()
        
        self.num_perspectives = num_perspectives
        
        # Perspective-specific processors
        self.perspectives = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embed_dim, embed_dim),
                nn.GELU(),
                nn.Linear(embed_dim, embed_dim)
            )
            for _ in range(num_perspectives)
        ])
        
        # Perspective names
        self.perspective_names = [
            'Substance', 'Quality', 'Activity', 'Universality',
            'Particularity', 'Inherence', 'Indescribable'
        ][:num_perspectives]
        
        # Integration network
        self.integrate = nn.Linear(embed_dim * num_perspectives, embed_dim)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Process from multiple perspectives."""
        perspective_outputs = []
        
        for processor in self.perspectives:
            perspective_outputs.append(processor(x))
        
        # Integrate all perspectives
        combined = torch.cat(perspective_outputs, dim=-1)
        integrated = self.integrate(combined)
        
        # Perspective agreement (how much perspectives agree)
        agreement = self._compute_agreement(perspective_outputs)
        
        return {
            'perspective_outputs': perspective_outputs,
            'perspective_names': self.perspective_names,
            'integrated': integrated,
            'agreement': agreement
        }
    
    def _compute_agreement(self, outputs: List[torch.Tensor]) -> torch.Tensor:
        """Compute agreement between perspectives."""
        # Stack outputs
        stacked = torch.stack(outputs, dim=1)  # [batch, num_perspectives, dim]
        
        # Variance across perspectives (lower = more agreement)
        variance = stacked.var(dim=1).mean(dim=-1, keepdim=True)
        
        # Convert to agreement score
        agreement = torch.exp(-variance)
        
        return agreement


class ConditionalPredicator(nn.Module):
    """Conditional predication based on context."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Context encoder
        self.context_encoder = nn.Linear(embed_dim, embed_dim)
        
        # Conditional truth modifier
        self.conditional_modifier = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, 7)
        )
        
    def forward(
        self,
        truth_state: SevenValuedState,
        context: torch.Tensor
    ) -> SevenValuedState:
        """Modify truth values based on context."""
        # Encode context
        context_emb = self.context_encoder(context)
        
        # Combine with truth probabilities
        combined = torch.cat([
            truth_state.probabilities,
            context_emb
        ], dim=-1)
        
        # Modify truth values conditionally
        modified_logits = self.conditional_modifier(combined)
        modified_probs = F.softmax(modified_logits, dim=-1)
        
        # New primary value
        primary_value = modified_probs.argmax(dim=-1)
        
        # New indeterminacy
        indeterminacy = -(modified_probs * torch.log(modified_probs + 1e-9)).sum(dim=-1)
        
        return SevenValuedState(
            probabilities=modified_probs,
            primary_value=primary_value,
            indeterminacy=indeterminacy
        )


class NonAbsolutismReasoner(nn.Module):
    """Reason without absolutism (avoid ekantavada)."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Absolutism detector
        self.absolutism_detector = nn.Sequential(
            nn.Linear(7, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
        # Non-absolutist reasoning
        self.reasoning = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        
        # Balance checker (ensures no single view dominates)
        self.balance_checker = nn.Linear(7, 1)
        
    def forward(
        self,
        truth_state: SevenValuedState,
        x: torch.Tensor
    ) -> Dict:
        """Apply non-absolutist reasoning."""
        # Detect absolutism (high probability on single value)
        absolutism_score = self.absolutism_detector(truth_state.probabilities)
        
        # Apply non-absolutist reasoning
        reasoned = self.reasoning(x)
        
        # Check balance
        balance_score = self.balance_checker(truth_state.probabilities)
        
        return {
            'reasoned': reasoned,
            'absolutism_score': absolutism_score,
            'balance_score': balance_score,
            'is_non_absolutist': absolutism_score < 0.5
        }


class JainSevenValuedNetwork(nn.Module):
    """Complete Jain Seven-Valued Logic Network.
    
    Applications:
    - Multi-valued reasoning
    - Perspective-taking
    - Uncertainty quantification
    - Non-absolutist inference
    """
    
    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 256,
        hidden_dim: int = 512
    ):
        super().__init__()
        
        self.embedding = SevenValuedEmbedding(vocab_size, embed_dim)
        self.perspective_taker = PerspectiveTaker(embed_dim)
        self.conditional = ConditionalPredicator(embed_dim)
        self.non_absolutism = NonAbsolutismReasoner(embed_dim)
        
        # Syadvada head (conditional assertion)
        self.syadvada_head = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 7),
            nn.Softmax(dim=-1)
        )
        
    def forward(
        self,
        x: torch.Tensor,
        context: Optional[torch.Tensor] = None
    ) -> Dict:
        """Process through Jain seven-valued logic.
        
        Args:
            x: [batch, seq_len] token IDs
            context: Optional [batch, embed_dim] context for conditioning
        Returns:
            Dict with seven-valued truth state
        """
        # Embed into seven-valued space
        truth_state = self.embedding(x)
        
        # Take multiple perspectives
        perspective_result = self.perspective_taker(truth_state.probabilities)
        
        # Apply conditional predication
        if context is not None:
            truth_state = self.conditional(truth_state, context)
        
        # Apply non-absolutist reasoning
        reasoning_result = self.non_absolutism(
            truth_state,
            perspective_result['integrated']
        )
        
        # Syadvada assertion
        syadvada = self.syadvada_head(reasoning_result['reasoned'])
        
        return {
            'truth_state': truth_state,
            'truth_values': TRUTH_VALUES,
            'perspectives': perspective_result,
            'reasoning': reasoning_result,
            'syadvada': syadvada
        }


def create_jain_seven_valued_network(
    vocab_size: int = 10000,
    embed_dim: int = 256,
    hidden_dim: int = 512
) -> JainSevenValuedNetwork:
    """Create JainSevenValuedNetwork."""
    return JainSevenValuedNetwork(vocab_size, embed_dim, hidden_dim)
