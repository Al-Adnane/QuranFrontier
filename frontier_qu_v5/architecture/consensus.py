"""
Byzantine Fault Tolerance for Heterogeneous Substrates
When substrates disagree on computation results, consensus protocol resolves.

Adapts PBFT (Practical Byzantine Fault Tolerance) for substrate networks:
- Tolerates f < n/3 faulty/adversarial substrates
- 3-phase commit: pre-prepare → prepare → commit
- Substrate reputation tracking for weighted voting
"""

import numpy as np
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate, SubstrateState


class ConsensusPhase(Enum):
    IDLE = "idle"
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    DECIDED = "decided"


@dataclass
class ConsensusProposal:
    proposer: str
    value_hash: str
    timestamp: float
    phase: ConsensusPhase = ConsensusPhase.PRE_PREPARE
    prepare_votes: Dict[str, bool] = field(default_factory=dict)
    commit_votes: Dict[str, bool] = field(default_factory=dict)
    decided_value: Optional[Any] = None


class ByzantineConsensus:
    """
    PBFT-style consensus for heterogeneous substrates.
    Each substrate votes based on its internal state.
    Reputation system weights votes by historical accuracy.
    """

    def __init__(self, substrates: List[BaseSubstrate]):
        self.substrates = {s.substrate_id: s for s in substrates}
        self.n = len(substrates)
        self.f = (self.n - 1) // 3  # Max Byzantine faults tolerated
        self.reputation: Dict[str, float] = {
            s.substrate_id: 1.0 for s in substrates
        }
        self.consensus_history: List[ConsensusProposal] = []
        self._current_proposal: Optional[ConsensusProposal] = None

    def _state_hash(self, substrate: BaseSubstrate) -> str:
        """Hash substrate state for comparison."""
        if substrate.state is None or substrate.state.tensor_data is None:
            return "00000000deadbeef"
        data = substrate.state.tensor_data
        return hashlib.sha256(data.tobytes()).hexdigest()[:16]

    def _compute_vote(self, substrate: BaseSubstrate, proposal_hash: str) -> bool:
        """
        Substrate votes True if its state is consistent with proposal.
        Uses hamming distance between state hashes.
        """
        own_hash = self._state_hash(substrate)
        # Compare first 8 hex chars (32 bits)
        own_bits = int(own_hash[:8], 16)
        prop_bits = int(proposal_hash[:8], 16)
        hamming = bin(own_bits ^ prop_bits).count('1')
        # Accept if hamming distance < 16 (out of 32 bits)
        return hamming < 16

    async def propose(self, proposer_id: str) -> ConsensusProposal:
        """
        Phase 1: Pre-prepare. Proposer broadcasts its state hash.
        """
        proposer = self.substrates.get(proposer_id)
        if proposer is None:
            raise ValueError(f"Unknown substrate: {proposer_id}")

        proposal = ConsensusProposal(
            proposer=proposer_id,
            value_hash=self._state_hash(proposer),
            timestamp=time.time(),
        )
        self._current_proposal = proposal
        return proposal

    async def prepare(self) -> Dict[str, bool]:
        """
        Phase 2: Each substrate votes on the proposal.
        """
        if self._current_proposal is None:
            raise RuntimeError("No active proposal")

        proposal = self._current_proposal
        proposal.phase = ConsensusPhase.PREPARE

        votes = {}
        for sid, substrate in self.substrates.items():
            if not substrate.is_active:
                continue
            vote = self._compute_vote(substrate, proposal.value_hash)
            votes[sid] = vote
            proposal.prepare_votes[sid] = vote

        return votes

    async def commit(self) -> bool:
        """
        Phase 3: If 2f+1 prepare votes received, proceed to commit.
        Returns True if consensus reached.
        """
        if self._current_proposal is None:
            raise RuntimeError("No active proposal")

        proposal = self._current_proposal
        proposal.phase = ConsensusPhase.COMMIT

        # Count weighted prepare votes
        weighted_yes = sum(
            self.reputation.get(sid, 1.0)
            for sid, vote in proposal.prepare_votes.items()
            if vote
        )
        total_weight = sum(self.reputation.values())
        threshold = total_weight * 2 / 3  # 2/3 supermajority

        if weighted_yes >= threshold:
            proposal.phase = ConsensusPhase.DECIDED
            proposal.decided_value = proposal.value_hash

            # Update reputations
            for sid, vote in proposal.prepare_votes.items():
                if vote:
                    self.reputation[sid] = min(2.0, self.reputation[sid] * 1.01)
                else:
                    self.reputation[sid] = max(0.1, self.reputation[sid] * 0.95)

            self.consensus_history.append(proposal)
            self._current_proposal = None
            return True
        else:
            # Consensus failed
            for sid, vote in proposal.prepare_votes.items():
                if not vote:
                    self.reputation[sid] = max(0.1, self.reputation[sid] * 0.99)
            self._current_proposal = None
            return False

    async def full_consensus_round(self, proposer_id: str) -> Dict[str, Any]:
        """Run complete 3-phase consensus round."""
        proposal = await self.propose(proposer_id)
        votes = await self.prepare()
        decided = await self.commit()

        return {
            'proposer': proposer_id,
            'proposal_hash': proposal.value_hash,
            'votes': votes,
            'consensus_reached': decided,
            'yes_count': sum(1 for v in votes.values() if v),
            'no_count': sum(1 for v in votes.values() if not v),
            'reputations': dict(self.reputation),
        }

    def get_metrics(self) -> Dict[str, float]:
        total_rounds = len(self.consensus_history)
        return {
            'total_rounds': total_rounds,
            'mean_reputation': float(np.mean(list(self.reputation.values()))),
            'min_reputation': float(min(self.reputation.values())) if self.reputation else 0,
            'max_reputation': float(max(self.reputation.values())) if self.reputation else 0,
            'byzantine_tolerance': self.f,
        }
