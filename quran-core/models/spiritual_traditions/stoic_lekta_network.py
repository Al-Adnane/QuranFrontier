"""Stoic Lekta Network - Sayables Logic.

Inspired by: Stoic Logic

Key insights:
- Lekta (sayables) = incorporeal meaning entities
- Complete lekta = propositions (true/false)
- Incomplete lekta = predicates
- Aximata = assertibles
- Katagoreumata = categorical statements

Architecture:
    Lekta Embedding: Meaning representation
    Complete/Incomplete: Proposition vs predicate
    Assertible Logic: Truth-claim processing
    Corporeal/Incorporeal: Body/meaning distinction
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional


class LektaEmbedding(nn.Module):
    """Embed sayables (lekta)."""
    
    def __init__(self, vocab_size: int = 10000, embed_dim: int = 256):
        super().__init__()
        
        self.embed = nn.Embedding(vocab_size, embed_dim)
        
        # Corporeal (body) vs Incorporeal (meaning)
        self.corporeal = nn.Linear(embed_dim, embed_dim)
        self.incorporeal = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Embed with corporeal/incorporeal distinction."""
        embedded = self.embed(x).mean(dim=1)
        
        return {
            'corporeal': self.corporeal(embedded),
            'incorporeal': self.incorporeal(embedded)
        }


class CompleteLekta(nn.Module):
    """Complete lekta (propositions)."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Proposition processor
        self.proposition = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, 1)  # Truth value
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Process as proposition."""
        return torch.sigmoid(self.proposition(x))


class IncompleteLekta(nn.Module):
    """Incomplete lekta (predicates)."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Predicate processor
        self.predicate = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Process as predicate."""
        return self.predicate(x)


class AssertibleLogic(nn.Module):
    """Aximata - assertible logic."""
    
    def __init__(self, embed_dim: int = 256):
        super().__init__()
        
        # Assertible types
        self.affirmative = nn.Linear(embed_dim, embed_dim)
        self.negative = nn.Linear(embed_dim, embed_dim)
        self.negation = nn.Linear(embed_dim, embed_dim)
        
        # Assertibility detector
        self.assertible = nn.Sequential(
            nn.Linear(embed_dim * 3, 128),
            nn.GELU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Process assertibles."""
        affirmative = self.affirmative(x)
        negative = self.negative(x)
        negation = self.negation(x)
        
        combined = torch.cat([affirmative, negative, negation], dim=-1)
        is_assertible = self.assertible(combined)
        
        return {
            'affirmative': affirmative,
            'negative': negative,
            'negation': negation,
            'is_assertible': is_assertible
        }


class StoicLektaNetwork(nn.Module):
    """Complete Stoic Lekta Network."""
    
    def __init__(self, vocab_size: int = 10000, embed_dim: int = 256):
        super().__init__()
        
        self.embedding = LektaEmbedding(vocab_size, embed_dim)
        self.complete = CompleteLekta(embed_dim)
        self.incomplete = IncompleteLekta(embed_dim)
        self.assertible = AssertibleLogic(embed_dim)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Process through Stoic logic."""
        # Embed
        embedded = self.embedding(x)
        
        # Complete lekta (proposition)
        proposition = self.complete(embedded['incorporeal'])
        
        # Incomplete lekta (predicate)
        predicate = self.incomplete(embedded['incorporeal'])
        
        # Assertible logic
        assertible_result = self.assertible(embedded['incorporeal'])
        
        return {
            'embedded': embedded,
            'proposition': proposition,
            'predicate': predicate,
            'assertible': assertible_result
        }


    @classmethod
    def self_test(cls) -> bool:
        """Create model, run forward pass, assert output shapes."""
        model = cls(vocab_size=100, embed_dim=64)
        model.eval()
        x = torch.randint(0, 100, (2, 8))
        with torch.no_grad():
            result = model(x)
        assert result['proposition'].shape == (2, 1), f"prop shape {result['proposition'].shape}"
        assert result['predicate'].shape == (2, 64)
        assert result['assertible']['is_assertible'].shape == (2, 1)
        print("StoicLektaNetwork self_test PASSED")
        return True


def create_stoic_lekta_network(vocab_size: int = 10000, embed_dim: int = 256) -> StoicLektaNetwork:
    return StoicLektaNetwork(vocab_size, embed_dim)
