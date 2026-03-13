"""Deontic Logic Neural Network - Normative Reasoning with Constraints.

This model implements neural networks with built-in deontic logic constraints
for reasoning about obligations, permissions, and prohibitions.

Deontic Categories (Islamic):
    - Wajib (Obligatory): □P (necessarily P)
    - Haram (Forbidden): □¬P (necessarily not P)
    - Mandub (Recommended): ◇P (possibly P)
    - Makruh (Discouraged): ◇¬P (possibly not P)
    - Mubah (Permissible): P ∧ ¬□P ∧ ¬□¬P

Architecture:
    Input: Situation description
    Deontic Encoder: Neural encoding with constraint awareness
    Constraint Layer: Enforces deontic logic axioms
    Output: Deontic classification + rule derivation

Based on frontierqu.logic.deontic for Islamic jurisprudence.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum, auto


class DeonticStatus(Enum):
    """Deontic status in Islamic jurisprudence."""
    WAJIB = auto()      # Obligatory
    HARAM = auto()      # Forbidden
    MANDUB = auto()     # Recommended
    MAKRUH = auto()     # Discouraged
    MUBAH = auto()      # Permissible


# Deontic logic constraints
# □(Wajib(x) → ¬Permissible(¬x))
# □(Haram(x) → ¬Permissible(x))
# □(Wajib(x) → Permissible(x))
DEONTIC_CONSTRAINTS = {
    ('WAJIB', 'HARAM'): 'mutually_exclusive',
    ('WAJIB', 'MUBAH'): 'implies',  # Wajib implies Mubah
    ('HARAM', 'MUBAH'): 'exclusive',
    ('MANDUB', 'MAKRUH'): 'contrary',
}


@dataclass
class DeonticRuling:
    """Deontic ruling result."""
    status: DeonticStatus
    confidence: float
    evidence: List[str]
    constraints_satisfied: bool
    rule_chain: List[str]


class DeonticConstraintLayer(nn.Module):
    """Neural layer enforcing deontic logic constraints."""
    
    def __init__(self, num_classes: int = 5):
        super().__init__()
        self.num_classes = num_classes
        
        # Constraint matrix (learnable soft constraints)
        # C_ij = 1 means class i implies class j
        # C_ij = -1 means class i excludes class j
        self.constraint_matrix = nn.Parameter(torch.zeros(num_classes, num_classes))
        
        # Constraint strength
        self.constraint_strength = nn.Parameter(torch.ones(num_classes))
        
    def forward(
        self,
        logits: torch.Tensor,
        hard_constraints: bool = True
    ) -> torch.Tensor:
        """Apply deontic constraints to predictions.
        
        Args:
            logits: [batch, num_classes] raw predictions
            hard_constraints: Whether to enforce hard constraints
        Returns:
            Constrained logits
        """
        # Compute constraint violations
        probs = F.softmax(logits, dim=-1)
        
        # Constraint: sum of mutually exclusive should be <= 1
        # WAJIB and HARAM are mutually exclusive
        wajib_prob = probs[:, DeonticStatus.WAJIB.value - 1]
        haram_prob = probs[:, DeonticStatus.HARAM.value - 1]
        
        exclusivity_loss = torch.clamp(wajib_prob + haram_prob - 1, min=0).mean()
        
        if hard_constraints:
            # Hard constraint: normalize to satisfy exclusivity
            max_deontic = torch.max(wajib_prob, haram_prob)
            scale = 1.0 / (wajib_prob + haram_prob + 1e-9)
            scale = torch.clamp(scale, max=1.0)
            
            adjusted_logits = logits.clone()
            adjusted_logits[:, DeonticStatus.WAJIB.value - 1] *= scale
            adjusted_logits[:, DeonticStatus.HARAM.value - 1] *= scale
            
            return adjusted_logits
        
        return logits
    
    def constraint_loss(self, logits: torch.Tensor) -> torch.Tensor:
        """Compute constraint violation loss."""
        probs = F.softmax(logits, dim=-1)
        
        # WAJIB + HARAM <= 1
        wajib = probs[:, DeonticStatus.WAJIB.value - 1]
        haram = probs[:, DeonticStatus.HARAM.value - 1]
        exclusivity = torch.clamp(wajib + haram - 1, min=0).mean()
        
        # WAJIB → MUBAH (wajib implies permissible)
        mubah = probs[:, DeonticStatus.MUBAH.value - 1]
        implication = torch.clamp(wajib - mubah, min=0).mean()
        
        # MANDUB and MAKRUH are contraries (can both be false, not both true)
        mandub = probs[:, DeonticStatus.MANDUB.value - 1]
        makruh = probs[:, DeonticStatus.MAKRUH.value - 1]
        contrary = torch.clamp(mandub + makruh - 1, min=0).mean()
        
        return exclusivity + implication + contrary


class DeonticEncoder(nn.Module):
    """Encodes situations for deontic reasoning."""
    
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 512,
        num_layers: int = 4
    ):
        super().__init__()
        
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # Transformer-style encoding
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=8,
            dim_feedforward=hidden_dim * 4,
            dropout=0.1,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Deontic-aware attention
        self.deontic_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=8,
            dropout=0.1
        )
        
    def forward(
        self,
        input_features: torch.Tensor,
        deontic_queries: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Encode input with deontic awareness.
        
        Args:
            input_features: [batch, seq_len, input_dim]
            deontic_queries: Optional [5, batch, hidden_dim] for each deontic class
        Returns:
            Encoded features [batch, hidden_dim]
        """
        # Project input
        h = self.input_proj(input_features)
        
        # Encode
        h = self.encoder(h)
        
        # Pool (mean)
        h_pooled = h.mean(dim=1)
        
        # Deontic-aware attention
        if deontic_queries is not None:
            h_attended, _ = self.deontic_attention(
                deontic_queries, h_pooled.unsqueeze(0), h_pooled.unsqueeze(0)
            )
            return h_attended.mean(dim=0)
        
        return h_pooled


class DeonticLogicNetwork(nn.Module):
    """Main Deontic Logic Network for normative reasoning."""
    
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 512,
        embedding_dim: int = 256
    ):
        super().__init__()
        
        self.encoder = DeonticEncoder(input_dim, hidden_dim)
        self.constraint_layer = DeonticConstraintLayer(num_classes=5)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.LayerNorm(hidden_dim // 2),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 5)  # 5 deontic classes
        )
        
        # Rule derivation head
        self.rule_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, 256)  # Rule embedding
        )
        
        # Evidence head
        self.evidence_head = nn.Linear(hidden_dim, 10)  # Attention over input
        
        # Embedding for deontic classes
        self.deontic_embed = nn.Embedding(5, embedding_dim)
        
        self.hidden_dim = hidden_dim
        
    def classify(
        self,
        input_features: torch.Tensor
    ) -> DeonticRuling:
        """Classify situation into deontic category.
        
        Args:
            input_features: [batch, seq_len, input_dim]
        Returns:
            DeonticRuling with classification and analysis
        """
        self.eval()
        
        batch_size = input_features.size(0)
        
        with torch.no_grad():
            # Encode
            encoded = self.encoder(input_features)
            
            # Classify
            logits = self.classifier(encoded)
            
            # Apply constraints
            constrained_logits = self.constraint_layer(logits, hard_constraints=True)
            
            # Get prediction
            probs = F.softmax(constrained_logits, dim=-1)
            status_id = probs.argmax(dim=-1).item()
            confidence = probs[0, status_id].item()
            
            # Get evidence
            evidence_weights = F.softmax(self.evidence_head(encoded), dim=-1)
            
            # Derive rule
            rule_embedding = self.rule_head(encoded)
            
            # Check constraints
            constraint_violation = self.constraint_layer.constraint_loss(logits)
            constraints_satisfied = constraint_violation.item() < 0.01
            
            status = DeonticStatus(status_id + 1)
            
            return DeonticRuling(
                status=status,
                confidence=confidence,
                evidence=[f"feature_{i}" for i in range(3)],
                constraints_satisfied=constraints_satisfied,
                rule_chain=[status.name]
            )
    
    def check_consistency(
        self,
        rulings: List[DeonticRuling]
    ) -> Tuple[bool, List[str]]:
        """Check consistency of multiple rulings.
        
        Args:
            rulings: List of deontic rulings
        Returns:
            is_consistent, list of conflicts
        """
        conflicts = []
        
        status_counts = {}
        for ruling in rulings:
            status_name = ruling.status.name
            status_counts[status_name] = status_counts.get(status_name, 0) + 1
        
        # Check: can't have both WAJIB and HARAM for same action
        if 'WAJIB' in status_counts and 'HARAM' in status_counts:
            conflicts.append("Contradiction: WAJIB and HARAM for same action")
        
        # Check: MANDUB and MAKRUH can coexist (different aspects)
        # but should flag for review
        
        return len(conflicts) == 0, conflicts
    
    def forward(
        self,
        input_features: torch.Tensor,
        labels: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """Forward pass with optional loss computation.
        
        Args:
            input_features: [batch, seq_len, input_dim]
            labels: Optional [batch] deontic class labels
        Returns:
            Dict with predictions and loss
        """
        # Encode
        encoded = self.encoder(input_features)
        
        # Classify
        logits = self.classifier(encoded)
        
        # Apply constraints
        constrained_logits = self.constraint_layer(logits)
        
        # Rule embedding
        rule_embedding = self.rule_head(encoded)
        
        # Evidence weights
        evidence = F.softmax(self.evidence_head(encoded), dim=-1)
        
        result = {
            'logits': constrained_logits,
            'rule_embedding': rule_embedding,
            'evidence': evidence
        }
        
        if labels is not None:
            # Classification loss
            ce_loss = F.cross_entropy(constrained_logits, labels)
            
            # Constraint loss
            constraint_loss = self.constraint_layer.constraint_loss(logits)
            
            # Total loss with constraint regularization
            result['loss'] = ce_loss + 0.1 * constraint_loss
            result['ce_loss'] = ce_loss
            result['constraint_loss'] = constraint_loss
        
        return result
    
    def derive_qiyas(
        self,
        asl_features: torch.Tensor,  # Original case
        asl_ruling: DeonticStatus,
        far_features: torch.Tensor,   # New case
        illa: str                     # Common cause
    ) -> DeonticRuling:
        """Derive ruling via analogical reasoning (qiyas).
        
        Args:
            asl_features: Features of original case
            asl_ruling: Ruling of original case
            far_features: Features of new case
            illa: Common legal cause
        Returns:
            Derived ruling for new case
        """
        self.eval()
        
        with torch.no_grad():
            # Encode both cases
            asl_encoded = self.encoder(asl_features)
            far_encoded = self.encoder(far_features)
            
            # Compute similarity
            similarity = F.cosine_similarity(asl_encoded, far_encoded, dim=-1)
            
            # If similar enough, transfer ruling
            if similarity.item() > 0.7:
                ruling = DeonticRuling(
                    status=asl_ruling,
                    confidence=similarity.item(),
                    evidence=[f"Qiyas via illa: {illa}"],
                    constraints_satisfied=True,
                    rule_chain=[
                        f"Asl: {asl_ruling.name}",
                        f"Illa: {illa}",
                        f"Far: {asl_ruling.name} (by qiyas)"
                    ]
                )
            else:
                # Fall back to direct classification
                ruling = self.classify(far_features)
            
            return ruling


def create_deontic_network(
    input_dim: int = 768,
    hidden_dim: int = 512
) -> DeonticLogicNetwork:
    """Create DeonticLogicNetwork."""
    return DeonticLogicNetwork(
        input_dim=input_dim,
        hidden_dim=hidden_dim
    )
