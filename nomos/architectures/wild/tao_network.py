"""Tao Network - Paradox-Tolerant Reasoning.

Inspired by: Tao Te Ching, Zhuangzi

Simplified working version.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict


class TaoNetwork(nn.Module):
    """Tao Network for paradox-tolerant reasoning."""
    
    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 128,
        action_dim: int = 64
    ):
        super().__init__()
        
        self.embed_dim = embed_dim
        
        # Concept and complement embeddings
        self.concept_embed = nn.Embedding(vocab_size, embed_dim)
        self.complement_embed = nn.Embedding(vocab_size, embed_dim)
        
        # Paradox tension
        self.tension_proj = nn.Linear(embed_dim * 2, 1)
        
        # Synthesis
        self.synthesis_proj = nn.Linear(embed_dim * 2, embed_dim)
        
        # Yin-yang balance
        self.yin_proj = nn.Linear(embed_dim, embed_dim)
        self.yang_proj = nn.Linear(embed_dim, embed_dim)
        self.balance_param = nn.Parameter(torch.tensor(0.5))
        
        # Ambiguity preservation
        self.ambiguity_heads = nn.ModuleList([
            nn.Linear(embed_dim, embed_dim) for _ in range(5)
        ])
        
        # Wu-wei policy
        self.wu_wei_policy = nn.Linear(embed_dim, action_dim)
        self.effort_detector = nn.Linear(embed_dim, 1)
        
        # Output
        self.output_proj = nn.Linear(embed_dim, embed_dim)
        
    def forward(
        self,
        concept_ids: torch.Tensor,
        complement_ids: torch.Tensor,
    ) -> Dict:
        """Process through Tao framework."""
        batch_size, seq_len = concept_ids.shape
        
        # Embed concepts with complements
        concept_emb = self.concept_embed(concept_ids)
        complement_emb = self.complement_embed(complement_ids)
        combined = torch.cat([concept_emb, complement_emb], dim=-1)
        
        # Paradox tension
        tension = torch.sigmoid(self.tension_proj(combined))
        
        # Synthesis
        synthesis = self.synthesis_proj(combined)
        synthesis = F.normalize(synthesis, dim=-1)
        
        # Yin-yang balance
        yin = self.yin_proj(synthesis)
        yang = self.yang_proj(synthesis)
        balanced = self.balance_param * yin + (1 - self.balance_param) * yang
        
        # Balance metric
        yin_energy = yin.norm(dim=-1).mean()
        yang_energy = yang.norm(dim=-1).mean()
        balance_metric = 2 * (yin_energy * yang_energy) / (yin_energy ** 2 + yang_energy ** 2 + 1e-9)
        
        # Ambiguity preservation
        interpretations = torch.stack([head(synthesis) for head in self.ambiguity_heads], dim=1)
        combined_interp = interpretations.mean(dim=1)
        
        # Wu-wei policy
        effort = torch.sigmoid(self.effort_detector(combined_interp))
        wu_wei_action = self.wu_wei_policy(combined_interp)
        wu_wei_score = (1 - effort) * wu_wei_action.norm(dim=-1, keepdim=True)
        
        # Output
        output = self.output_proj(combined_interp)
        
        return {
            'output': output,
            'tension': tension,
            'synthesis': synthesis,
            'yin': yin,
            'yang': yang,
            'balance_metric': balance_metric,
            'interpretations': interpretations,
            'wu_wei_action': wu_wei_action,
            'effort': effort,
            'wu_wei_score': wu_wei_score
        }


def create_tao_network(vocab_size: int = 10000, embed_dim: int = 128, action_dim: int = 64) -> TaoNetwork:
    """Create TaoNetwork."""
    return TaoNetwork(vocab_size, embed_dim, action_dim)
