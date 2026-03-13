"""Multi-Agent Scholar Debate System.

Implements a formal argumentation framework for Islamic jurisprudence
using three specialized agents:
- ProposerAgent: Generates interpretations using RAG
- CriticAgent: Validates against sources (hadith, madhabs)
- VerifierAgent: Checks logical consistency with deontic logic
- DebateEngine: Orchestrates agents using LangGraph + Dung semantics
- ScholarMemory: Maintains context and learns from feedback
"""

from .proposer_agent import ProposerAgent, Interpretation, SourceType
from .critic_agent import CriticAgent, CritiqueResult, HadithGrade
from .verifier_agent import VerifierAgent, DeonticModality, DeonticStatement
from .debate_engine import DebateEngine, Argument, ArgumentStatus, RoundResult
from .scholar_memory import ScholarMemory, MemoryEntry, CausalChain

__all__ = [
    # Proposer
    "ProposerAgent",
    "Interpretation",
    "SourceType",
    # Critic
    "CriticAgent",
    "CritiqueResult",
    "HadithGrade",
    # Verifier
    "VerifierAgent",
    "DeonticModality",
    "DeonticStatement",
    # Debate
    "DebateEngine",
    "Argument",
    "ArgumentStatus",
    "RoundResult",
    # Memory
    "ScholarMemory",
    "MemoryEntry",
    "CausalChain",
]
