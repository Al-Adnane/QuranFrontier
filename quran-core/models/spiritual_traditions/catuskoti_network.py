"""Catuskoti Network - Four-Valued Paraconsistent Logic.

Inspired by: Buddhist Catuskoti (four corners of logic)

Key insights:
- Four truth values: True, False, Both, Neither
- Paraconsistent: contradictions don't explode
- Natural for ambiguous/uncertain information
- Beyond binary true/false

Architecture:
    Four-Valued Embedding: Represent all four truth values
    Catuskoti Logic: Operations on four values
    Paraconsistent Reasoning: Handle contradictions gracefully
    Truth Value Dynamics: Evolve truth values over reasoning steps
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# Truth value indices
TRUE = 0
FALSE = 1
BOTH = 2    # True AND False (contradiction)
NEITHER = 3 # NOT True AND NOT False (indeterminate)


@dataclass
class FourValuedTensor:
    """Tensor with four-valued logic representation."""
    values: torch.Tensor  # [batch, ..., 4] truth value distribution
    
    def true_prob(self) -> torch.Tensor:
        return self.values[..., TRUE]
    
    def false_prob(self) -> torch.Tensor:
        return self.values[..., FALSE]
    
    def both_prob(self) -> torch.Tensor:
        return self.values[..., BOTH]
    
    def neither_prob(self) -> torch.Tensor:
        return self.values[..., NEITHER]
    
    def is_contradictory(self, threshold: float = 0.5) -> torch.Tensor:
        """Check if contradictory (both true and false)."""
        return (self.true_prob() > threshold) & (self.false_prob() > threshold)
    
    def is_indeterminate(self, threshold: float = 0.5) -> torch.Tensor:
        """Check if indeterminate (neither true nor false)."""
        return (self.true_prob() < threshold) & (self.false_prob() < threshold)


class FourValuedEmbedding(nn.Module):
    """Embed into four-valued space."""
    
    def __init__(self, vocab_size: int, embed_dim: int):
        super().__init__()
        
        self.embed_dim = embed_dim
        
        # Standard embedding
        self.embed = nn.Embedding(vocab_size, embed_dim)
        
        # Project to four truth values
        self.truth_projection = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, 4),
            nn.Softmax(dim=-1)
        )
        
    def forward(self, x: torch.Tensor) -> FourValuedTensor:
        """Embed to four-valued representation."""
        embedded = self.embed(x)
        truth_values = self.truth_projection(embedded)
        
        return FourValuedTensor(values=truth_values)


class CatuskotiLogic(nn.Module):
    """Implement catuskoti logical operations."""
    
    def __init__(self):
        super().__init__()
        
        # Learnable truth tables (soft)
        self.negation_table = nn.Parameter(torch.randn(4, 4))
        self.conjunction_table = nn.Parameter(torch.randn(4, 4, 4))
        self.disjunction_table = nn.Parameter(torch.randn(4, 4, 4))
        
    def negation(self, x: FourValuedTensor) -> FourValuedTensor:
        """Logical negation in catuskoti.
        
        NOT True = False
        NOT False = True
        NOT Both = Both (still contradictory)
        NOT Neither = Neither (still indeterminate)
        """
        # Apply soft truth table
        negated = F.linear(x.values, self.negation_table)
        negated = F.softmax(negated, dim=-1)
        
        return FourValuedTensor(values=negated)
    
    def conjunction(self, x: FourValuedTensor, y: FourValuedTensor) -> FourValuedTensor:
        """Logical AND in catuskoti."""
        batch_size = x.values.size(0)
        
        # Outer product for combination
        x_expanded = x.values.unsqueeze(-1)  # [batch, 4, 1]
        y_expanded = y.values.unsqueeze(-2)  # [batch, 1, 4]
        
        # Combine with truth table
        combined = x_expanded * y_expanded  # [batch, 4, 4]
        
        # Apply truth table
        result = torch.einsum('bij,ijk->bk', combined, self.conjunction_table)
        result = F.softmax(result, dim=-1)
        
        return FourValuedTensor(values=result)
    
    def disjunction(self, x: FourValuedTensor, y: FourValuedTensor) -> FourValuedTensor:
        """Logical OR in catuskoti."""
        batch_size = x.values.size(0)
        
        # Outer product
        x_expanded = x.values.unsqueeze(-1)
        y_expanded = y.values.unsqueeze(-2)
        
        combined = x_expanded * y_expanded
        
        # Apply truth table
        result = torch.einsum('bij,ijk->bk', combined, self.disjunction_table)
        result = F.softmax(result, dim=-1)
        
        return FourValuedTensor(values=result)
    
    def implication(self, x: FourValuedTensor, y: FourValuedTensor) -> FourValuedTensor:
        """Logical implication (A → B = NOT A OR B)."""
        not_x = self.negation(x)
        return self.disjunction(not_x, y)


class ParaconsistentReasoner(nn.Module):
    """Reason with contradictions without explosion."""
    
    def __init__(self, embed_dim: int, hidden_dim: int = 128):
        super().__init__()
        
        # Contradiction handler
        self.contradiction_handler = nn.Sequential(
            nn.Linear(4, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 4)
        )
        
        # Consistency regularizer
        self.consistency_head = nn.Sequential(
            nn.Linear(4, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        x: FourValuedTensor,
        resolve_contradictions: bool = True
    ) -> Tuple[FourValuedTensor, torch.Tensor]:
        """Reason paraconsistently.
        
        Args:
            x: Four-valued input
            resolve_contradictions: Whether to resolve contradictions
        Returns:
            (reasoned output, consistency score)
        """
        # Check consistency
        consistency_score = self.consistency_head(x.values).squeeze(-1)
        
        # Handle contradictions
        if resolve_contradictions:
            resolved_values = self.contradiction_handler(x.values)
            resolved_values = F.softmax(resolved_values, dim=-1)
            output = FourValuedTensor(values=resolved_values)
        else:
            output = x
        
        return output, consistency_score


class TruthValueDynamics(nn.Module):
    """Evolve truth values over reasoning steps."""
    
    def __init__(self, embed_dim: int, hidden_dim: int = 128):
        super().__init__()
        
        # Truth value evolution
        self.evolution_rnn = nn.GRU(4, hidden_dim, num_layers=2, batch_first=True)
        
        # Output projection
        self.output_proj = nn.Sequential(
            nn.Linear(hidden_dim, 4),
            nn.Softmax(dim=-1)
        )
        
    def forward(
        self,
        initial_values: torch.Tensor,
        num_steps: int = 5
    ) -> List[FourValuedTensor]:
        """Evolve truth values over reasoning steps."""
        batch_size = initial_values.size(0)
        
        # Initialize sequence
        sequence = initial_values.unsqueeze(1).repeat(1, num_steps, 1)
        
        # Evolve through RNN
        output, _ = self.evolution_rnn(sequence)
        
        # Project to truth values
        evolved_values = self.output_proj(output)
        
        # Convert to list of FourValuedTensor
        results = []
        for step in range(num_steps):
            results.append(FourValuedTensor(values=evolved_values[:, step, :]))
        
        return results


class CatuskotiNetwork(nn.Module):
    """Complete Catuskoti Network for paraconsistent reasoning.
    
    Applications:
    - Reasoning with contradictions
    - Ambiguous information processing
    - Multi-valued logic inference
    - Dialetheic reasoning (true contradictions)
    """
    
    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 128,
        hidden_dim: int = 256
    ):
        super().__init__()
        
        self.embed_dim = embed_dim
        
        # Four-valued embedding
        self.embedding = FourValuedEmbedding(vocab_size, embed_dim)
        
        # Catuskoti logic operations
        self.logic = CatuskotiLogic()
        
        # Paraconsistent reasoning
        self.reasoner = ParaconsistentReasoner(embed_dim, hidden_dim)
        
        # Truth value dynamics
        self.dynamics = TruthValueDynamics(embed_dim, hidden_dim)
        
        # Output projection
        self.output_proj = nn.Linear(4, 1)  # Single output (e.g., probability of true)
        
    def forward(
        self,
        x: torch.Tensor,
        num_reasoning_steps: int = 5,
        resolve_contradictions: bool = True
    ) -> Dict:
        """Process through catuskoti network.
        
        Args:
            x: [batch, seq_len] token IDs
            num_reasoning_steps: Number of reasoning iterations
            resolve_contradictions: Whether to resolve contradictions
        Returns:
            Dict with four-valued reasoning results
        """
        batch_size, seq_len = x.shape
        
        # Embed to four-valued representation
        embedded = self.embedding(x)
        
        # Aggregate over sequence (mean pooling)
        aggregated = embedded.values.mean(dim=1)
        aggregated_tensor = FourValuedTensor(values=aggregated)
        
        # Paraconsistent reasoning
        reasoned, consistency = self.reasoner(aggregated_tensor, resolve_contradictions)
        
        # Truth value dynamics
        evolved = self.dynamics(reasoned.values, num_reasoning_steps)
        
        # Final output
        final_output = self.output_proj(evolved[-1].values)
        
        # Compute logic metrics
        contradiction_rate = evolved[-1].is_contradictory().float().mean()
        indeterminate_rate = evolved[-1].is_indeterminate().float().mean()
        
        return {
            'output': final_output,
            'initial_values': embedded,
            'reasoned_values': reasoned,
            'evolved_values': evolved,
            'consistency_score': consistency,
            'contradiction_rate': contradiction_rate,
            'indeterminate_rate': indeterminate_rate,
            'final_truth_values': evolved[-1].values
        }
    
    def evaluate_proposition(
        self,
        proposition_ids: torch.Tensor
    ) -> Dict:
        """Evaluate a proposition's truth value."""
        result = self.forward(proposition_ids)
        
        final_truth = result['final_truth_values']
        
        return {
            'true_probability': final_truth[:, TRUE].item(),
            'false_probability': final_truth[:, FALSE].item(),
            'both_probability': final_truth[:, BOTH].item(),
            'neither_probability': final_truth[:, NEITHER].item(),
            'is_contradictory': result['contradiction_rate'].item() > 0.5,
            'is_indeterminate': result['indeterminate_rate'].item() > 0.5
        }


def create_catuskoti_network(
    vocab_size: int = 10000,
    embed_dim: int = 128,
    hidden_dim: int = 256
) -> CatuskotiNetwork:
    """Create CatuskotiNetwork."""
    return CatuskotiNetwork(vocab_size, embed_dim, hidden_dim)
