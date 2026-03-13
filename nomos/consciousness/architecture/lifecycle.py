"""
Substrate Death & Resurrection Protocol
Graceful degradation when a substrate fails mid-computation.
Automatic state rerouting through surviving substrates.

Detection → Quarantine → Reroute → Resurrect → Reintegrate
"""

import numpy as np
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import BaseSubstrate, SubstrateState


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    QUARANTINED = "quarantined"
    DEAD = "dead"
    RESURRECTING = "resurrecting"


@dataclass
class SubstrateVitals:
    substrate_id: str
    status: HealthStatus
    entropy: float
    energy: float
    responsiveness: float   # Time since last successful step
    error_count: int
    last_heartbeat: float


class SubstrateLifecycle:
    """
    Monitors substrate health and manages death/resurrection.
    - Entropy too low → frozen (dead)
    - Entropy too high → chaotic (dead)
    - No heartbeat → unresponsive (dead)
    - State NaN/Inf → corrupted (dead)
    """

    def __init__(self, substrates: List[BaseSubstrate]):
        self.substrates = {s.substrate_id: s for s in substrates}
        self.vitals: Dict[str, SubstrateVitals] = {}
        self.death_log: List[Dict[str, Any]] = []
        self.resurrection_log: List[Dict[str, Any]] = []

        # Thresholds
        self.entropy_min = 0.01
        self.entropy_max = 15.0
        self.heartbeat_timeout = 5.0  # seconds
        self.max_errors = 10

        for s in substrates:
            self.vitals[s.substrate_id] = SubstrateVitals(
                substrate_id=s.substrate_id,
                status=HealthStatus.HEALTHY,
                entropy=0.0,
                energy=0.0,
                responsiveness=0.0,
                error_count=0,
                last_heartbeat=time.time(),
            )

    def heartbeat(self, substrate_id: str, metrics: Dict[str, float]):
        """Record a heartbeat from a substrate."""
        v = self.vitals.get(substrate_id)
        if v is None:
            return
        v.last_heartbeat = time.time()
        v.entropy = metrics.get('entropy', v.entropy)
        v.energy = metrics.get('energy', v.energy)
        v.error_count = 0  # Reset on successful heartbeat

    def report_error(self, substrate_id: str, error: str):
        """Substrate reports an error."""
        v = self.vitals.get(substrate_id)
        if v is None:
            return
        v.error_count += 1
        if v.error_count >= self.max_errors:
            self._kill(substrate_id, reason=f"error_threshold: {error}")

    def check_all(self) -> Dict[str, HealthStatus]:
        """Check vitals for all substrates. Returns status map."""
        now = time.time()
        statuses = {}

        for sid, v in self.vitals.items():
            if v.status in (HealthStatus.DEAD, HealthStatus.RESURRECTING):
                statuses[sid] = v.status
                continue

            # Check heartbeat timeout
            if now - v.last_heartbeat > self.heartbeat_timeout:
                self._kill(sid, reason="heartbeat_timeout")
                statuses[sid] = HealthStatus.DEAD
                continue

            # Check entropy bounds
            if v.entropy < self.entropy_min:
                v.status = HealthStatus.DEGRADED
                if v.entropy < self.entropy_min * 0.1:
                    self._kill(sid, reason=f"entropy_frozen: {v.entropy}")
            elif v.entropy > self.entropy_max:
                self._kill(sid, reason=f"entropy_chaotic: {v.entropy}")
            else:
                v.status = HealthStatus.HEALTHY

            # Check for NaN/Inf in state
            substrate = self.substrates.get(sid)
            if substrate and substrate.state is not None:
                data = substrate.state.tensor_data
                if np.any(np.isnan(data)) or np.any(np.isinf(data)):
                    self._kill(sid, reason="state_corrupted_nan_inf")

            statuses[sid] = v.status

        return statuses

    def _kill(self, substrate_id: str, reason: str):
        """Mark substrate as dead."""
        v = self.vitals.get(substrate_id)
        if v is None:
            return
        v.status = HealthStatus.DEAD

        substrate = self.substrates.get(substrate_id)
        if substrate:
            substrate.is_active = False

        self.death_log.append({
            'substrate_id': substrate_id,
            'reason': reason,
            'timestamp': time.time(),
            'last_entropy': v.entropy,
            'last_energy': v.energy,
        })

    async def resurrect(self, substrate_id: str,
                        donor_id: Optional[str] = None) -> bool:
        """
        Resurrect a dead substrate.
        If donor_id provided, clone state from donor.
        Otherwise, reinitialize from scratch.
        """
        v = self.vitals.get(substrate_id)
        substrate = self.substrates.get(substrate_id)
        if v is None or substrate is None:
            return False

        v.status = HealthStatus.RESURRECTING

        try:
            if donor_id and donor_id in self.substrates:
                donor = self.substrates[donor_id]
                if donor.state is not None:
                    # Clone donor state (with substrate_origin updated)
                    substrate.state = SubstrateState(
                        tensor_data=donor.state.tensor_data.copy(),
                        metadata=dict(donor.state.metadata),
                        timestamp=time.time(),
                        substrate_origin=substrate_id,
                    )

            # Reinitialize
            await substrate.initialize()
            substrate.is_active = True
            v.status = HealthStatus.HEALTHY
            v.error_count = 0
            v.last_heartbeat = time.time()

            self.resurrection_log.append({
                'substrate_id': substrate_id,
                'donor': donor_id,
                'timestamp': time.time(),
            })
            return True

        except Exception as e:
            v.status = HealthStatus.DEAD
            return False

    def find_best_donor(self, dead_id: str) -> Optional[str]:
        """Find healthiest substrate to donate state."""
        best_id = None
        best_score = -1
        for sid, v in self.vitals.items():
            if sid == dead_id:
                continue
            if v.status != HealthStatus.HEALTHY:
                continue
            # Score by low error count and moderate entropy
            score = 1.0 / (v.error_count + 1) * min(v.entropy, 5.0)
            if score > best_score:
                best_score = score
                best_id = sid
        return best_id

    def get_alive_substrates(self) -> List[str]:
        """Return IDs of all alive substrates."""
        return [
            sid for sid, v in self.vitals.items()
            if v.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)
        ]

    def get_metrics(self) -> Dict[str, Any]:
        alive = len(self.get_alive_substrates())
        total = len(self.substrates)
        return {
            'alive_count': alive,
            'dead_count': total - alive,
            'total_deaths': len(self.death_log),
            'total_resurrections': len(self.resurrection_log),
            'health_ratio': alive / max(1, total),
        }
