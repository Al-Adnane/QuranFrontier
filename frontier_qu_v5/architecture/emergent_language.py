"""
Emergent Inter-Substrate Language
Instead of imposing HoTT translation top-down, let substrates develop
their own communication protocol via information-theoretic pressure.

Inspired by emergent communication in multi-agent RL:
- Substrates emit "messages" (fixed-length vectors)
- Receiver substrates decode messages to adjust behavior
- Communication channel optimized by mutual information maximization
"""

import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate


@dataclass
class Message:
    sender: str
    content: np.ndarray   # Fixed-length message vector
    timestamp: float
    channel: int = 0      # Communication channel ID


@dataclass
class LanguageStats:
    vocabulary_size: int = 0
    mutual_information: float = 0.0
    compositionality: float = 0.0  # Topographic similarity
    convergence: float = 0.0       # How stable the protocol is


class EmergentLanguage:
    """
    Emergent communication protocol between substrates.
    Each substrate has an encoder (state → message) and decoder (message → adjustment).
    The protocol evolves via information-theoretic pressure:
    maximize I(message; receiver_state | sender_state).
    """

    def __init__(self, substrate_ids: List[str], message_dim: int = 16,
                 vocab_size: int = 32):
        self.substrate_ids = substrate_ids
        self.message_dim = message_dim
        self.vocab_size = vocab_size

        # Encoder: maps substrate state hash to message vector
        # (Random projection initially; evolves via feedback)
        self.encoders: Dict[str, np.ndarray] = {
            sid: np.random.randn(message_dim, message_dim) * 0.1
            for sid in substrate_ids
        }

        # Decoder: maps received message to state adjustment
        self.decoders: Dict[str, np.ndarray] = {
            sid: np.random.randn(message_dim, message_dim) * 0.1
            for sid in substrate_ids
        }

        self.message_history: List[Message] = []
        self._mutual_info_history: List[float] = []

    def encode(self, substrate: BaseSubstrate) -> Message:
        """Substrate encodes its state into a message."""
        sid = substrate.substrate_id
        encoder = self.encoders.get(sid)
        if encoder is None or substrate.state is None:
            return Message(sender=sid, content=np.zeros(self.message_dim),
                          timestamp=time.time())

        # Extract features from state
        data = substrate.state.tensor_data.flatten()
        # Compress to message_dim via random projection
        if len(data) < self.message_dim:
            data = np.pad(data, (0, self.message_dim - len(data)))
        else:
            data = data[:self.message_dim]

        # Apply learned encoder
        content = np.tanh(encoder @ data)

        msg = Message(sender=sid, content=content, timestamp=time.time())
        self.message_history.append(msg)
        return msg

    def decode(self, receiver_id: str, message: Message) -> np.ndarray:
        """Receiver decodes message into state adjustment vector."""
        decoder = self.decoders.get(receiver_id)
        if decoder is None:
            return np.zeros(self.message_dim)
        return np.tanh(decoder @ message.content)

    def broadcast(self, sender: BaseSubstrate,
                  receivers: List[BaseSubstrate]) -> Dict[str, np.ndarray]:
        """Sender broadcasts message to all receivers."""
        msg = self.encode(sender)
        adjustments = {}
        for receiver in receivers:
            if receiver.substrate_id == sender.substrate_id:
                continue
            adj = self.decode(receiver.substrate_id, msg)
            adjustments[receiver.substrate_id] = adj
        return adjustments

    def _estimate_mutual_information(self, n_samples: int = 50) -> float:
        """
        Estimate I(Message; Sender) from recent message history.
        Uses binning estimator.
        """
        if len(self.message_history) < n_samples:
            return 0.0

        recent = self.message_history[-n_samples:]

        # Bin messages by sender
        sender_messages: Dict[str, List[np.ndarray]] = {}
        for msg in recent:
            sender_messages.setdefault(msg.sender, []).append(msg.content)

        # Compute entropy of messages H(M)
        all_contents = np.array([msg.content for msg in recent])
        H_M = self._entropy(all_contents)

        # Compute conditional entropy H(M|S)
        H_M_given_S = 0.0
        for sid, contents in sender_messages.items():
            p_s = len(contents) / n_samples
            H_M_given_S += p_s * self._entropy(np.array(contents))

        mi = max(0.0, H_M - H_M_given_S)
        self._mutual_info_history.append(mi)
        return mi

    def _entropy(self, vectors: np.ndarray, bins: int = 10) -> float:
        """Estimate entropy of vector distribution via histogram binning."""
        if len(vectors) < 2:
            return 0.0
        # Use first component for simplicity
        vals = vectors[:, 0] if vectors.ndim > 1 else vectors
        hist, _ = np.histogram(vals, bins=bins, range=(-1, 1))
        prob = hist / hist.sum()
        prob = prob[prob > 0]
        return float(-np.sum(prob * np.log2(prob)))

    def update_protocol(self, feedback: Dict[str, float], lr: float = 0.01):
        """
        Update encoder/decoder weights based on communication effectiveness.
        feedback: {substrate_id: reward_signal}
        Positive reward → strengthen current encoding.
        """
        for sid, reward in feedback.items():
            if sid in self.encoders:
                # Simple gradient-free update: perturb in direction of reward
                noise = np.random.randn(*self.encoders[sid].shape) * lr
                self.encoders[sid] += reward * noise
            if sid in self.decoders:
                noise = np.random.randn(*self.decoders[sid].shape) * lr
                self.decoders[sid] += reward * noise

    def measure_compositionality(self) -> float:
        """
        Topographic similarity: correlation between message distance
        and state distance. High = compositional language.
        """
        if len(self.message_history) < 10:
            return 0.0

        recent = self.message_history[-20:]
        contents = np.array([m.content for m in recent])
        senders = [m.sender for m in recent]

        # Message distances
        msg_dists = []
        sender_dists = []
        for i in range(len(recent)):
            for j in range(i + 1, len(recent)):
                msg_dists.append(np.linalg.norm(contents[i] - contents[j]))
                sender_dists.append(0.0 if senders[i] == senders[j] else 1.0)

        if len(msg_dists) < 3:
            return 0.0

        msg_dists = np.array(msg_dists)
        sender_dists = np.array(sender_dists)

        if np.std(msg_dists) < 1e-10 or np.std(sender_dists) < 1e-10:
            return 0.0

        corr = np.corrcoef(msg_dists, sender_dists)[0, 1]
        return float(corr) if not np.isnan(corr) else 0.0

    def get_stats(self) -> LanguageStats:
        mi = self._estimate_mutual_information()
        comp = self.measure_compositionality()
        # Convergence: how stable MI is over time
        if len(self._mutual_info_history) > 10:
            recent_mi = self._mutual_info_history[-10:]
            convergence = 1.0 / (np.std(recent_mi) + 0.01)
        else:
            convergence = 0.0

        return LanguageStats(
            vocabulary_size=self.vocab_size,
            mutual_information=mi,
            compositionality=comp,
            convergence=convergence,
        )
