"""Temporal Substrate Synchronization — Gamma-Synchronized Orchestration.

Enforces 50ms binding windows on inter-substrate communication using the
TemporalBinder from the consciousness subsystem. Substrates that exceed
the binding window latency get degraded (their weight in the unified
"present moment" is reduced).

This integration bridges:
  frontier_qu_v5/consciousness/temporal_binding.py  (TemporalBinder, BoundMoment)
  The Three-World subsystem substrates (neural, symbolic, categorical)

The orchestrator maintains a gamma oscillation (40 Hz) that gates when
substrates may contribute to the unified moment. Substrates that miss
their window get exponentially degraded.
"""

import sys
import os
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _project_root)
sys.path.insert(0, os.path.join(_project_root, "frontier_qu_v5"))

try:
    from frontier_qu_v5.main import SubstrateState
    from frontier_qu_v5.consciousness.temporal_binding import (
        TemporalBinder,
        TemporalEvent,
        BoundMoment,
    )
    _HAS_QU_V5 = True
except ImportError:
    _HAS_QU_V5 = False
    SubstrateState = None
    TemporalBinder = None
    TemporalEvent = None
    BoundMoment = None


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SubstrateHealth:
    """Health and latency tracking for a single substrate."""
    substrate_id: str
    total_events: int = 0
    on_time_events: int = 0
    late_events: int = 0
    degradation_factor: float = 1.0     # 1.0 = healthy, 0.0 = fully degraded
    mean_latency_ms: float = 0.0
    last_event_time: float = 0.0
    latency_history: List[float] = field(default_factory=list)


@dataclass
class SynchronizedMoment:
    """An extended BoundMoment with degradation-aware weighting."""
    bound_moment: BoundMoment
    substrate_weights: Dict[str, float]   # Degradation-adjusted weights
    effective_integration: float           # Integration score * weight product
    degraded_substrates: List[str]         # Substrates currently degraded
    gamma_phase: float                     # Current gamma oscillation phase [0, 2pi)


# ---------------------------------------------------------------------------
# Main integration class
# ---------------------------------------------------------------------------

class GammaSynchronizedOrchestrator:
    """Enforce gamma-synchronized binding windows on substrate communication.

    Architecture:
        1. Each substrate registers its clock rate with the TemporalBinder.
        2. On every substrate event, the orchestrator checks whether the event
           arrived within the current 50ms binding window.
        3. Late events cause the substrate's degradation factor to decay
           exponentially (tau = 5 windows).
        4. On-time events allow the degradation factor to recover.
        5. Bound moments are created only at gamma cycle boundaries (40 Hz).
        6. The effective contribution of each substrate to the unified moment
           is weighted by its degradation factor.

    Parameters:
        binding_window_ms: Width of the binding window (default 50ms).
        gamma_freq_hz: Gamma oscillation frequency (default 40 Hz).
        degradation_tau: Exponential decay time constant for late substrates,
                         measured in number of windows.
        recovery_rate: How fast degradation recovers on on-time events.
    """

    def __init__(
        self,
        binding_window_ms: float = 50.0,
        gamma_freq_hz: float = 40.0,
        degradation_tau: float = 5.0,
        recovery_rate: float = 0.1,
        max_history: int = 500,
    ):
        self.binding_window_ms = binding_window_ms
        self.gamma_freq_hz = gamma_freq_hz
        self.degradation_tau = degradation_tau
        self.recovery_rate = recovery_rate

        # Core temporal binder from consciousness subsystem
        self.binder = TemporalBinder(
            binding_window_ms=binding_window_ms,
            gamma_freq_hz=gamma_freq_hz,
            max_history=max_history,
        )

        # Per-substrate health tracking
        self._health: Dict[str, SubstrateHealth] = {}

        # Gamma phase tracking
        self._gamma_phase: float = 0.0
        self._last_cycle_time: float = time.time()
        self._gamma_period: float = 1.0 / gamma_freq_hz

        # Synchronized moments history
        self.moments: List[SynchronizedMoment] = []

        # Window boundary tracking
        self._window_start: float = time.time()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_substrate(
        self,
        substrate_id: str,
        clock_rate_hz: float = 1000.0,
    ):
        """Register a substrate with its clock rate.

        Args:
            substrate_id: Unique identifier (e.g., "neural", "symbolic", "quantum").
            clock_rate_hz: Substrate's internal clock ticks per second.
        """
        self.binder.register_clock(substrate_id, clock_rate_hz)
        self._health[substrate_id] = SubstrateHealth(substrate_id=substrate_id)

    def submit_event(
        self,
        substrate_id: str,
        state: SubstrateState,
        magnitude: float = 1.0,
    ) -> Tuple[bool, float]:
        """Submit a substrate event to the synchronization system.

        Checks whether the event is within the binding window. If late,
        the substrate's degradation factor decays. If on-time, it recovers.

        Args:
            substrate_id: Which substrate sent this event.
            state: The substrate's current state.
            magnitude: Event significance.

        Returns:
            Tuple of (on_time: bool, degradation_factor: float).
        """
        now = time.time()
        health = self._health.get(substrate_id)
        if health is None:
            # Auto-register if not yet registered
            self.register_substrate(substrate_id)
            health = self._health[substrate_id]

        # Record event in temporal binder
        self.binder.record_event(substrate_id, state, magnitude)

        # Compute latency relative to current window start
        latency_ms = (now - self._window_start) * 1000.0
        on_time = latency_ms <= self.binding_window_ms

        # Update health
        health.total_events += 1
        health.last_event_time = now
        health.latency_history.append(latency_ms)
        if len(health.latency_history) > 100:
            health.latency_history = health.latency_history[-100:]
        health.mean_latency_ms = float(np.mean(health.latency_history))

        if on_time:
            health.on_time_events += 1
            # Recovery: move degradation toward 1.0
            health.degradation_factor = min(
                1.0,
                health.degradation_factor + self.recovery_rate * (1.0 - health.degradation_factor),
            )
        else:
            health.late_events += 1
            # Exponential decay
            decay = np.exp(-1.0 / self.degradation_tau)
            health.degradation_factor *= decay

        return on_time, health.degradation_factor

    def tick(self) -> Optional[SynchronizedMoment]:
        """Advance the gamma clock by one cycle and create a synchronized moment.

        Should be called at approximately gamma_freq_hz (40 Hz). Creates a
        BoundMoment from the temporal binder and wraps it with degradation-
        aware substrate weighting.

        Returns:
            SynchronizedMoment if events exist in the window, else None.
        """
        now = time.time()

        # Advance gamma phase
        elapsed = now - self._last_cycle_time
        self._gamma_phase = (self._gamma_phase + 2 * np.pi * elapsed * self.gamma_freq_hz) % (2 * np.pi)
        self._last_cycle_time = now

        # Reset window boundary
        self._window_start = now

        # Bind moment via temporal binder
        bound_moment = self.binder.bind_moment()
        if bound_moment is None:
            return None

        # Compute degradation-weighted substrate contributions
        substrate_weights: Dict[str, float] = {}
        degraded: List[str] = []

        for sid, health in self._health.items():
            substrate_weights[sid] = health.degradation_factor
            if health.degradation_factor < 0.5:
                degraded.append(sid)

        # Effective integration = raw integration * product of participating weights
        participating_ids = set(e.substrate_id for e in bound_moment.events)
        weight_product = 1.0
        for sid in participating_ids:
            weight_product *= substrate_weights.get(sid, 1.0)

        effective_integration = bound_moment.integration_score * weight_product

        sync_moment = SynchronizedMoment(
            bound_moment=bound_moment,
            substrate_weights=substrate_weights,
            effective_integration=effective_integration,
            degraded_substrates=degraded,
            gamma_phase=self._gamma_phase,
        )

        self.moments.append(sync_moment)
        if len(self.moments) > 500:
            self.moments = self.moments[-500:]

        return sync_moment

    def get_substrate_health(self, substrate_id: str) -> Optional[SubstrateHealth]:
        """Get health report for a substrate."""
        return self._health.get(substrate_id)

    def get_all_health(self) -> Dict[str, SubstrateHealth]:
        """Get health for all substrates."""
        return dict(self._health)

    def is_degraded(self, substrate_id: str, threshold: float = 0.5) -> bool:
        """Check if a substrate is currently degraded.

        Args:
            substrate_id: Substrate to check.
            threshold: Degradation factor below which substrate is considered degraded.

        Returns:
            True if substrate degradation factor < threshold.
        """
        health = self._health.get(substrate_id)
        if health is None:
            return False
        return health.degradation_factor < threshold

    def reset_degradation(self, substrate_id: str):
        """Manually reset a substrate's degradation factor to 1.0."""
        health = self._health.get(substrate_id)
        if health is not None:
            health.degradation_factor = 1.0

    def get_metrics(self) -> Dict[str, Any]:
        """Return orchestration metrics."""
        binder_metrics = self.binder.get_metrics()

        health_summary = {}
        for sid, h in self._health.items():
            health_summary[sid] = {
                "degradation": h.degradation_factor,
                "on_time_pct": (h.on_time_events / max(1, h.total_events)) * 100,
                "mean_latency_ms": h.mean_latency_ms,
                "total_events": h.total_events,
            }

        recent_moments = self.moments[-20:] if self.moments else []
        mean_effective = float(np.mean([m.effective_integration for m in recent_moments])) if recent_moments else 0.0

        return {
            "binder": binder_metrics,
            "substrate_health": health_summary,
            "gamma_phase": self._gamma_phase,
            "binding_window_ms": self.binding_window_ms,
            "total_sync_moments": len(self.moments),
            "mean_effective_integration": mean_effective,
            "num_degraded": sum(1 for h in self._health.values() if h.degradation_factor < 0.5),
        }
