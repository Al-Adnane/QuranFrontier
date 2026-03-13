"""Legal Reasoning Network - Case Law and Statutes.

Inspired by: Legal Theory
"""

import torch
import torch.nn as nn


class LegalReasoningNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Legal sources
        self.constitution = nn.Linear(input_dim, embed_dim)
        self.statutes = nn.Linear(input_dim, embed_dim)
        self.case_law = nn.Linear(input_dim, embed_dim)
        self.regulations = nn.Linear(input_dim, embed_dim)
        # Legal reasoning
        self.precedent = nn.Linear(input_dim, embed_dim)
        self.statutory_interpretation = nn.Linear(input_dim, embed_dim)
        # Case outcome
        self.outcome = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        sources = [self.constitution(x), self.statutes(x), self.case_law(x), self.regulations(x)]
        reasoning = [self.precedent(x), self.statutory_interpretation(x)]
        return {
            'legal_sources': {
                'constitution': self.constitution(x),
                'statutes': self.statutes(x),
                'case_law': self.case_law(x),
                'regulations': self.regulations(x)
            },
            'reasoning': {
                'precedent': self.precedent(x),
                'statutory_interpretation': self.statutory_interpretation(x)
            },
            'case_outcome': torch.sigmoid(self.outcome(torch.cat(sources + reasoning, -1)))
        }


def create_legal_reasoning_network(input_dim: int = 128, embed_dim: int = 256):
    return LegalReasoningNetwork(input_dim, embed_dim)
