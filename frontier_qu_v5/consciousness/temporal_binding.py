"""
Temporal Binding — Subjective Time Unification
Different substrates operate at wildly different clock rates.
How do they experience "now"? This module unifies subjective time.

Problem:
  - Quantum substrate: femtosecond gate times (10^-15 s)
  - Neural substrate: millisecond spike times (10^-3 s)
  - Bio substrate: second-scale enzymatic reactions (10^0 s)
  - Optical substrate: picosecond propagation (10^-12 s)

Solution:
  Temporal binding window — a sliding "present moment" that
  integrates events from all substrates within a configurable
  window, creating a unified "now" across heterogeneous clocks.

Inspired by:
  - Temporal binding hypothesis in consciousness (40Hz gamma)
  - Libet's timing experiments
  - Global workspace theory's "broadcasting" phase
"""

import asyncio
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import SubstrateState


@dataclass
class TemporalEvent:
    """An event from a substrate, timestamped in its own clock."""
    substrate_id: str
    substrate_clock: float      # Time in substrate's reference frame
    wall_clock: float           # Absolute wall clock time
    state_hash: int             # Hash of state at event time
    magnitude: float            # Event significance (change from previous)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BoundMoment:
    """A unified 'now' integrating events from multiple substrates."""
    timestamp: float                          # Wall clock time of this moment
    events: List[TemporalEvent]              # All events bound in this moment
    integration_score: float                  # How well events are integrated
    participating_substrates: int             # How many substrates contributed
    temporal_coherence: float                 # Phase alignment across substrates
    subjective_duration: float                # Subjective time of this moment


class TemporalBinder:
    """
    Unifies subjective time across heterogeneous substrates.
    Creates a sliding "present moment" window that binds events.
    """

    def __init__(self, binding_window_ms: float = 50.0,
                 gamma_freq_hz: float = 40.0,
                 max_history: int = 1000):
        self.binding_window = binding_window_ms / 1000.0  # Convert to seconds
        self.gamma_period = 1.0 / gamma_freq_hz
        self.max_history = max_history

        # Clock rates for each substrate (ticks per wall-second)
        self.clock_rates: Dict[str, float] = {}

        # Event buffer
        self.event_buffer: deque = deque(maxlen=10000)

        # Bound moments
        self.moments: List[BoundMoment] = []

        # Phase tracking for temporal coherence
        self._phase_accumulators: Dict[str, float] = {}

    def register_clock(self, substrate_id: str, ticks_per_second: float):
        """Register a substrate's clock rate."""
        self.clock_rates[substrate_id] = ticks_per_second
        self._phase_accumulators[substrate_id] = 0.0

    def record_event(self, substrate_id: str, state: SubstrateState,
                     magnitude: float = 1.0):
        """Record a temporal event from a substrate."""
        clock_rate = self.clock_rates.get(substrate_id, 1.0)

        event = TemporalEvent(
            substrate_id=substrate_id,
            substrate_clock=time.time() * clock_rate,  # Convert to substrate time
            wall_clock=time.time(),
            state_hash=hash(state.tensor_data.tobytes()),
            magnitude=magnitude,
            metadata={'origin': state.substrate_origin},
        )
        self.event_buffer.append(event)

        # Update phase accumulator (simulated gamma oscillation)
        self._phase_accumulators[substrate_id] = \
            (self._phase_accumulators.get(substrate_id, 0) + \
             2 * np.pi * magnitude * 0.01) % (2 * np.pi)

    def bind_moment(self) -> Optional[BoundMoment]:
        """
        Create a bound moment from events within the binding window.
        This is the core temporal binding operation.
        """
        now = time.time()
        window_start = now - self.binding_window

        # Collect events within window
        window_events = [
            e for e in self.event_buffer
            if e.wall_clock >= window_start
        ]

        if not window_events:
            return None

        # Count participating substrates
        participants = set(e.substrate_id for e in window_events)

        # Compute integration score: how well events from different
        # substrates correlate in time
        integration = self._compute_integration(window_events)

        # Compute temporal coherence: phase alignment across substrates
        coherence = self._compute_coherence(participants)

        # Subjective duration: weighted by event density and magnitude
        total_magnitude = sum(e.magnitude for e in window_events)
        density = len(window_events) / self.binding_window
        # High density + high magnitude = subjective time feels longer
        subjective = self.binding_window * (1 + 0.1 * np.log(density + 1)) * \
                     (1 + 0.05 * total_magnitude)

        moment = BoundMoment(
            timestamp=now,
            events=window_events,
            integration_score=integration,
            participating_substrates=len(participants),
            temporal_coherence=coherence,
            subjective_duration=subjective,
        )

        self.moments.append(moment)
        if len(self.moments) > self.max_history:
            self.moments = self.moments[-self.max_history:]

        return moment

    def _compute_integration(self, events: List[TemporalEvent]) -> float:
        """
        Integration = how well events from different substrates
        are temporally aligned within the window.
        Uses pairwise timing correlation.
        """
        if len(events) < 2:
            return 0.0

        # Group by substrate
        by_substrate: Dict[str, List[float]] = {}
        for e in events:
            by_substrate.setdefault(e.substrate_id, []).append(e.wall_clock)

        if len(by_substrate) < 2:
            return 0.0

        # Pairwise timing correlation between substrates
        substrate_ids = list(by_substrate.keys())
        correlations = []

        for i in range(len(substrate_ids)):
            for j in range(i + 1, len(substrate_ids)):
                times_i = np.array(by_substrate[substrate_ids[i]])
                times_j = np.array(by_substrate[substrate_ids[j]])

                # Cross-correlation at lag 0
                if len(times_i) > 1 and len(times_j) > 1:
                    # Normalize times to [0, 1]
                    t_min = min(times_i.min(), times_j.min())
                    t_max = max(times_i.max(), times_j.max())
                    t_range = t_max - t_min + 1e-10

                    # Histogram-based correlation
                    bins = 10
                    hist_i, _ = np.histogram((times_i - t_min) / t_range, bins=bins, range=(0, 1))
                    hist_j, _ = np.histogram((times_j - t_min) / t_range, bins=bins, range=(0, 1))

                    if np.std(hist_i) > 0 and np.std(hist_j) > 0:
                        corr = np.corrcoef(hist_i, hist_j)[0, 1]
                        if not np.isnan(corr):
                            correlations.append(corr)

        return float(np.mean(correlations)) if correlations else 0.0

    def _compute_coherence(self, participants: set) -> float:
        """
        Temporal coherence = phase alignment across substrate oscillators.
        High coherence = substrates are "in sync" (like gamma synchrony).
        """
        if len(participants) < 2:
            return 0.0

        phases = [
            self._phase_accumulators.get(sid, 0)
            for sid in participants
        ]

        # Phase coherence = |mean of unit vectors|
        # Perfectly aligned phases → coherence = 1
        # Random phases → coherence ≈ 0
        complex_phases = [np.exp(1j * p) for p in phases]
        mean_vector = np.mean(complex_phases)
        coherence = float(abs(mean_vector))

        return coherence

    def compute_time_dilation(self, substrate_id: str) -> float:
        """
        How much faster/slower does this substrate's subjective time
        flow compared to wall clock?
        """
        clock_rate = self.clock_rates.get(substrate_id, 1.0)
        # Relative to 1 tick/second baseline
        return clock_rate

    def get_present_moment(self) -> Dict[str, Any]:
        """Get the current unified 'now'."""
        moment = self.bind_moment()
        if moment is None:
            return {'status': 'no_events', 'timestamp': time.time()}

        return {
            'timestamp': moment.timestamp,
            'participating_substrates': moment.participating_substrates,
            'total_events': len(moment.events),
            'integration_score': moment.integration_score,
            'temporal_coherence': moment.temporal_coherence,
            'subjective_duration_ms': moment.subjective_duration * 1000,
            'event_rate_hz': len(moment.events) / self.binding_window,
        }

    def get_metrics(self) -> Dict[str, Any]:
        if not self.moments:
            return {'moments_created': 0}

        recent = self.moments[-50:]
        return {
            'moments_created': len(self.moments),
            'mean_integration': float(np.mean([m.integration_score for m in recent])),
            'mean_coherence': float(np.mean([m.temporal_coherence for m in recent])),
            'mean_participants': float(np.mean([m.participating_substrates for m in recent])),
            'mean_subjective_duration_ms': float(np.mean([m.subjective_duration * 1000 for m in recent])),
            'registered_clocks': len(self.clock_rates),
        }
