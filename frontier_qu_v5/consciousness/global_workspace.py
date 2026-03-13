"""
Global Workspace Theory Implementation — Baars (1988)

The "theater" metaphor of consciousness:
  - Many unconscious processes run in parallel (audience)
  - They compete for access to a global workspace (stage)
  - Winner gets "broadcast" to all processes (spotlight)
  - This broadcast IS conscious experience

Why this matters for FrontierQu:
  Multiple substrates (quantum, neural, bio, optical) each produce
  outputs. Which one gets to influence the final response? GWT
  provides the mechanism: competition + broadcast.

Key Properties:
  - Bottleneck: Only one content at a time (serial consciousness)
  - Broadcasting: Winner is available to ALL modules
  - Competition: Salience-based winner-take-all
  - Ignition: Threshold crossing triggers global broadcast
"""

import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import sys
import os

try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from main import SubstrateState
except ImportError:
    from dataclasses import dataclass as _dc
    from typing import Dict, Any as _Any

    @_dc
    class SubstrateState:
        """Fallback SubstrateState when main.py is not available."""
        tensor_data: np.ndarray
        metadata: Dict[str, _Any]
        timestamp: float
        substrate_origin: str


@dataclass
class WorkspaceEntry:
    """A content item competing for workspace access."""
    content: np.ndarray
    source: str                     # Which substrate/module produced this
    salience: float                 # How "important" this content is
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BroadcastEvent:
    """Record of a successful broadcast."""
    content: np.ndarray
    source: str
    salience: float
    timestamp: float
    competitors: int                # How many items were competing
    winning_margin: float           # Salience gap over runner-up


class GlobalWorkspace:
    """
    Global Workspace Theory implementation.

    Multiple unconscious processes compete for access to a shared
    workspace. The winner is broadcast globally, making its content
    available to all modules — this broadcast IS consciousness.

    Based on Baars (1988) and Dehaene et al. (2003) "ignition" model.
    """

    def __init__(self, workspace_dim: int = 256,
                 ignition_threshold: float = 0.5,
                 decay_rate: float = 0.95,
                 max_history: int = 500):
        self.workspace_dim = workspace_dim
        self.ignition_threshold = ignition_threshold
        self.decay_rate = decay_rate
        self.max_history = max_history

        # Current workspace state (what is "conscious" right now)
        self.workspace_state: Optional[np.ndarray] = None

        # Competition queue
        self._candidates: List[WorkspaceEntry] = []

        # Broadcast history (recent conscious contents)
        self.access_history: deque = deque(maxlen=max_history)

        # Broadcast listeners (modules that receive broadcasts)
        self._listeners: Dict[str, Any] = {}

        # Metrics
        self._broadcast_count = 0
        self._competition_count = 0
        self._ignition_failures = 0

    def submit_candidate(self, content: np.ndarray, source: str,
                         salience: float, metadata: Optional[Dict] = None):
        """
        Submit content for competition to enter workspace.

        This is what unconscious modules do: they produce outputs
        and submit them for potential conscious access.

        Args:
            content: The content to potentially broadcast
            source: Identifier of the source module/substrate
            salience: How important/urgent this content is [0, 1]
            metadata: Optional additional information
        """
        # Ensure content fits workspace dimension
        flat = content.flatten()
        if len(flat) > self.workspace_dim:
            flat = flat[:self.workspace_dim]
        elif len(flat) < self.workspace_dim:
            flat = np.pad(flat, (0, self.workspace_dim - len(flat)))

        entry = WorkspaceEntry(
            content=flat,
            source=source,
            salience=float(np.clip(salience, 0.0, 1.0)),
            timestamp=time.time(),
            metadata=metadata or {},
        )
        self._candidates.append(entry)

    def compete_for_access(self, candidates: Optional[List[WorkspaceEntry]] = None) -> Optional[np.ndarray]:
        """
        Winner-take-all competition for workspace access.

        All submitted candidates compete based on salience.
        The winner crosses the ignition threshold and gets broadcast.

        Args:
            candidates: Optional explicit candidate list (otherwise uses submitted queue)
        Returns:
            Winning content tensor, or None if no candidate ignites
        """
        if candidates is None:
            candidates = self._candidates

        if not candidates:
            return None

        self._competition_count += 1

        # Sort by salience (highest first)
        sorted_candidates = sorted(candidates, key=lambda c: c.salience, reverse=True)
        winner = sorted_candidates[0]

        # Check ignition threshold
        if winner.salience < self.ignition_threshold:
            self._ignition_failures += 1
            # Decay current workspace state
            if self.workspace_state is not None:
                self.workspace_state *= self.decay_rate
            self._candidates.clear()
            return None

        # Compute winning margin
        if len(sorted_candidates) > 1:
            margin = winner.salience - sorted_candidates[1].salience
        else:
            margin = winner.salience

        # IGNITION: Winner takes the workspace
        self.workspace_state = winner.content.copy()

        # Record broadcast event
        broadcast = BroadcastEvent(
            content=winner.content.copy(),
            source=winner.source,
            salience=winner.salience,
            timestamp=time.time(),
            competitors=len(candidates),
            winning_margin=margin,
        )
        self.access_history.append(broadcast)
        self._broadcast_count += 1

        # Clear competition queue
        self._candidates.clear()

        return self.workspace_state

    def broadcast(self, content: np.ndarray, source: str):
        """
        Directly broadcast content to workspace (forced broadcast).
        Bypasses competition — used for high-priority signals.

        Args:
            content: Content to broadcast
            source: Source identifier
        """
        flat = content.flatten()
        if len(flat) > self.workspace_dim:
            flat = flat[:self.workspace_dim]
        elif len(flat) < self.workspace_dim:
            flat = np.pad(flat, (0, self.workspace_dim - len(flat)))

        self.workspace_state = flat.copy()

        broadcast = BroadcastEvent(
            content=flat.copy(),
            source=source,
            salience=1.0,  # Forced broadcasts have max salience
            timestamp=time.time(),
            competitors=0,
            winning_margin=1.0,
        )
        self.access_history.append(broadcast)
        self._broadcast_count += 1

    def get_workspace_state(self) -> Optional[np.ndarray]:
        """Get current contents of consciousness."""
        return self.workspace_state

    def register_listener(self, module_id: str, callback: Any):
        """Register a module to receive broadcasts."""
        self._listeners[module_id] = callback

    def notify_listeners(self):
        """Notify all listeners of current workspace content."""
        if self.workspace_state is None:
            return
        for module_id, callback in self._listeners.items():
            if callable(callback):
                try:
                    callback(self.workspace_state, module_id)
                except Exception:
                    pass  # Listeners should not crash the workspace

    def get_recent_broadcasts(self, n: int = 10) -> List[BroadcastEvent]:
        """Get N most recent broadcasts."""
        return list(self.access_history)[-n:]

    def compute_workspace_stability(self, window: int = 20) -> float:
        """
        Measure how stable the workspace content is.
        High stability = same source winning repeatedly.
        Low stability = rapid switching between sources.
        """
        if len(self.access_history) < 2:
            return 1.0

        recent = list(self.access_history)[-window:]
        sources = [b.source for b in recent]

        # Compute switching rate
        switches = sum(1 for i in range(1, len(sources)) if sources[i] != sources[i - 1])
        stability = 1.0 - (switches / max(1, len(sources) - 1))

        return float(stability)

    def compute_information_flow(self) -> float:
        """
        Measure information flow through workspace.
        Uses content diversity of recent broadcasts.
        """
        if len(self.access_history) < 5:
            return 0.0

        recent = list(self.access_history)[-20:]
        contents = [b.content for b in recent]

        # Pairwise similarity of broadcast contents
        similarities = []
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                cos_sim = np.dot(contents[i], contents[j]) / (
                    np.linalg.norm(contents[i]) * np.linalg.norm(contents[j]) + 1e-10
                )
                similarities.append(cos_sim)

        # High diversity (low similarity) = high information flow
        mean_sim = float(np.mean(similarities))
        return 1.0 - (mean_sim + 1) / 2  # Map [-1,1] to [1,0]

    def get_metrics(self) -> Dict[str, Any]:
        """Get workspace metrics."""
        return {
            'broadcasts': self._broadcast_count,
            'competitions': self._competition_count,
            'ignition_failures': self._ignition_failures,
            'ignition_rate': self._broadcast_count / max(1, self._competition_count),
            'workspace_active': self.workspace_state is not None,
            'stability': self.compute_workspace_stability(),
            'information_flow': self.compute_information_flow(),
            'history_length': len(self.access_history),
            'pending_candidates': len(self._candidates),
        }
