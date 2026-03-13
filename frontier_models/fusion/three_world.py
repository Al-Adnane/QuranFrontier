"""Three-World Fusion - Neural + Symbolic + Categorical Integration.

Unifies three reasoning paradigms:
1. Neural: Pattern recognition, embeddings
2. Symbolic: Logic, rules, constraints  
3. Categorical: Structure, relationships, topology
"""

import torch
import torch.nn as nn
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ThreeWorldOutput:
    neural_output: torch.Tensor
    symbolic_confidence: float
    categorical_confidence: float
    fused_output: torch.Tensor
    world_weights: Tuple[float, float, float]


class NeuralWorld(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)


class SymbolicWorld(nn.Module):
    def __init__(self, num_rules: int = 100, hidden_dim: int = 512):
        super().__init__()
        self.rule_embeddings = nn.Embedding(num_rules, hidden_dim)
        self.confidence_head = nn.Linear(hidden_dim, 1)
        
    def forward(self, x: torch.Tensor, rule_ids: torch.Tensor) -> Tuple[torch.Tensor, float]:
        rule_emb = self.rule_embeddings(rule_ids).mean(dim=1)
        combined = x + rule_emb
        confidence = torch.sigmoid(self.confidence_head(combined)).item()
        return combined, confidence


class CategoricalWorld(nn.Module):
    def __init__(self, num_objects: int, hidden_dim: int = 512):
        super().__init__()
        self.object_embed = nn.Embedding(num_objects, hidden_dim)
        self.morphism_head = nn.Linear(hidden_dim * 2, hidden_dim)
        self.confidence_head = nn.Linear(hidden_dim, 1)
        
    def forward(self, x: torch.Tensor, obj_ids: torch.Tensor) -> Tuple[torch.Tensor, float]:
        obj_emb = self.object_embed(obj_ids).mean(dim=1)
        combined = torch.cat([x, obj_emb], dim=-1)
        morphism = self.morphism_head(combined)
        confidence = torch.sigmoid(self.confidence_head(morphism)).item()
        return morphism, confidence


class ThreeWorldFusion(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512):
        super().__init__()
        self.neural = NeuralWorld(input_dim, hidden_dim)
        self.symbolic = SymbolicWorld(hidden_dim=hidden_dim)
        self.categorical = CategoricalWorld(num_objects=1000, hidden_dim=hidden_dim)
        
        self.fusion_gate = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.Sigmoid()
        )
        self.output_proj = nn.Linear(hidden_dim, hidden_dim)
        
    def forward(self, x: torch.Tensor, rule_ids: torch.Tensor, obj_ids: torch.Tensor) -> ThreeWorldOutput:
        neural_out = self.neural(x)
        symbolic_out, sym_conf = self.symbolic(neural_out, rule_ids)
        cat_out, cat_conf = self.categorical(symbolic_out, obj_ids)
        
        combined = torch.cat([neural_out, symbolic_out, cat_out], dim=-1)
        weights = self.fusion_gate(combined)
        
        fused = weights * torch.cat([neural_out, symbolic_out, cat_out], dim=-1)
        fused = fused.mean(dim=-1, keepdim=True) if fused.dim() > 2 else fused
        output = self.output_proj(fused)
        
        return ThreeWorldOutput(
            neural_output=neural_out,
            symbolic_confidence=sym_conf,
            categorical_confidence=cat_conf,
            fused_output=output,
            world_weights=(0.33, 0.33, 0.33)
        )


def create_three_world_fusion(input_dim: int, hidden_dim: int = 512) -> ThreeWorldFusion:
    return ThreeWorldFusion(input_dim, hidden_dim)
