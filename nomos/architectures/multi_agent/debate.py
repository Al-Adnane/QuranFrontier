"""Multi-Agent Debate System - Argumentation via Agent Debate.

Implements multi-agent debate with:
- Proposer: Generates interpretations/arguments
- Critic: Challenges and finds flaws
- Verifier: Checks consistency and evidence
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Argument:
    id: str
    text: str
    agent: str
    confidence: float
    supports: List[str] = field(default_factory=list)
    attacks: List[str] = field(default_factory=list)


@dataclass
class DebateResult:
    winner: str
    arguments: List[Argument]
    consensus: float
    unresolved_issues: List[str]


class ProposerAgent(nn.Module):
    def __init__(self, hidden_dim: int = 512):
        super().__init__()
        self.generator = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.confidence_head = nn.Linear(hidden_dim, 1)
        
    def forward(self, context: torch.Tensor) -> tuple:
        out = self.generator(context)
        conf = torch.sigmoid(self.confidence_head(out))
        return out, conf


class CriticAgent(nn.Module):
    def __init__(self, hidden_dim: int = 512):
        super().__init__()
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.weakness_head = nn.Linear(hidden_dim, 1)
        
    def forward(self, proposal: torch.Tensor, context: torch.Tensor) -> tuple:
        combined = torch.cat([proposal, context], dim=-1)
        out = self.critic(combined)
        weakness = torch.sigmoid(self.weakness_head(out))
        return out, weakness


class VerifierAgent(nn.Module):
    def __init__(self, hidden_dim: int = 512):
        super().__init__()
        self.verifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.consistency_head = nn.Linear(hidden_dim, 1)
        
    def forward(self, proposal: torch.Tensor, evidence: torch.Tensor) -> tuple:
        combined = torch.cat([proposal, evidence], dim=-1)
        out = self.verifier(combined)
        consistency = torch.sigmoid(self.consistency_head(out))
        return out, consistency


class MultiAgentDebateSystem(nn.Module):
    def __init__(self, hidden_dim: int = 512, max_rounds: int = 5):
        super().__init__()
        self.proposer = ProposerAgent(hidden_dim)
        self.critic = CriticAgent(hidden_dim)
        self.verifier = VerifierAgent(hidden_dim)
        self.max_rounds = max_rounds
        self.hidden_dim = hidden_dim
        
        self.synthesis = nn.Linear(hidden_dim * 3, hidden_dim)
        
    def debate(self, context: torch.Tensor, evidence: torch.Tensor) -> DebateResult:
        arguments = []
        
        # Round 1: Propose
        proposal, prop_conf = self.proposer(context)
        arguments.append(Argument("1", "proposal", "proposer", prop_conf.item()))
        
        # Round 2: Criticize
        critique, crit_weak = self.critic(proposal, context)
        arguments.append(Argument("2", "critique", "critic", crit_weak.item(), attacks=["1"]))
        
        # Round 3: Verify
        verification, ver_cons = self.verifier(proposal, evidence)
        arguments.append(Argument("3", "verification", "verifier", ver_cons.item(), supports=["1"]))
        
        # Synthesis
        combined = torch.cat([proposal, critique, verification], dim=-1)
        synthesis = self.synthesis(combined)
        
        # Determine winner based on confidence
        scores = [prop_conf.item(), 1 - crit_weak.item(), ver_cons.item()]
        winner = ["proposer", "critic", "verifier"][scores.index(max(scores))]
        consensus = sum(scores) / len(scores)
        
        return DebateResult(
            winner=winner,
            arguments=arguments,
            consensus=consensus,
            unresolved_issues=[]
        )
    
    def forward(self, context: torch.Tensor, evidence: torch.Tensor) -> Dict:
        result = self.debate(context, evidence)
        return {
            'winner': result.winner,
            'consensus': result.consensus,
            'num_arguments': len(result.arguments)
        }


def create_multi_agent_debate(hidden_dim: int = 512, max_rounds: int = 5) -> MultiAgentDebateSystem:
    return MultiAgentDebateSystem(hidden_dim, max_rounds)
