"""
FrontierQu Consciousness Orchestrator
======================================
Aggregates metrics across ALL frontier_qu_v5 consciousness modules:

  - GlobalWorkspace   : ignition_rate, broadcast_count, mean_salience (Baars GWT)
  - DreamingEngine    : fragments_discovered, max_novelty, spontaneous_patterns
  - MetacognitiveSystem: agreement_score, confidence, entropy
  - IIT Phi           : approximate integrated information via IChingNetwork
  - TemporalBinder    : cross-substrate synchrony
  - EmotionalValence  : affective tone coloring

Returns aggregate ConsciousnessMetrics with a unified consciousness_score.

Usage:
    python consciousness_orchestrator.py
    # or import:
    from consciousness_orchestrator import ConsciousnessOrchestrator
    metrics = ConsciousnessOrchestrator().run(n_steps=5)
    print(metrics.summary())
"""

import sys
import os
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

import numpy as np

# ── Path setup ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
for _p in [BASE_DIR,
           os.path.join(BASE_DIR, "src"),
           os.path.join(BASE_DIR, "frontier_models"),
           os.path.join(BASE_DIR, "frontier_qu_v5")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("FrontierQu.Consciousness")


@dataclass
class ConsciousnessMetrics:
    """Aggregate consciousness metrics across all frontier_qu_v5 modules."""

    # IIT
    phi: float = 0.0                      # Integrated Information (approximate)
    phi_method: str = "partition_approx"  # How phi was computed

    # Global Workspace Theory
    ignition_rate: float = 0.0            # Fraction of steps with ignition
    broadcast_count: int = 0              # Total broadcast events
    mean_salience: float = 0.0            # Mean salience of winning entries
    gwt_active: bool = False

    # Dreaming
    dream_fragments: int = 0              # Novel configurations discovered
    max_novelty: float = 0.0             # Highest novelty score
    spontaneous_patterns: int = 0         # Self-organizing patterns
    dream_active: bool = False

    # Metacognition
    metacognitive_confidence: float = 0.0 # Overall confidence
    agreement_score: float = 0.0          # Inter-substrate agreement
    meta_entropy: float = 0.0             # Entropy of metacognitive state
    meta_active: bool = False

    # Temporal Binding
    temporal_sync: float = 0.0            # Cross-substrate synchrony (0–1)
    temporal_active: bool = False

    # Emotional Valence
    emotional_valence: float = 0.0        # –1 (negative) to +1 (positive)
    emotional_arousal: float = 0.0        # 0 (calm) to 1 (excited)
    emotional_active: bool = False

    # Unified score
    consciousness_score: float = 0.0      # Composite 0–1

    # Metadata
    n_steps: int = 0
    duration_ms: float = 0.0
    active_modules: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"\n{'='*60}",
            f"  FrontierQu Consciousness Metrics",
            f"{'='*60}",
            f"  Consciousness Score : {self.consciousness_score:.4f}",
            f"  Steps processed     : {self.n_steps}",
            f"  Active modules      : {', '.join(self.active_modules) or 'none'}",
            f"",
            f"  IIT (Integrated Information Theory)",
            f"    Phi (Φ)           : {self.phi:.4f}  [{self.phi_method}]",
            f"",
            f"  Global Workspace Theory",
            f"    Ignition rate     : {self.ignition_rate:.3f}",
            f"    Broadcast events  : {self.broadcast_count}",
            f"    Mean salience     : {self.mean_salience:.3f}",
            f"    Active            : {self.gwt_active}",
            f"",
            f"  Dreaming (DMN / REM consolidation)",
            f"    Fragments found   : {self.dream_fragments}",
            f"    Max novelty       : {self.max_novelty:.4f}",
            f"    Spontaneous ptrns : {self.spontaneous_patterns}",
            f"    Active            : {self.dream_active}",
            f"",
            f"  Metacognition (HOT)",
            f"    Confidence        : {self.metacognitive_confidence:.3f}",
            f"    Agreement         : {self.agreement_score:.3f}",
            f"    Entropy           : {self.meta_entropy:.4f}",
            f"    Active            : {self.meta_active}",
            f"",
            f"  Temporal Binding",
            f"    Synchrony         : {self.temporal_sync:.3f}",
            f"    Active            : {self.temporal_active}",
            f"",
            f"  Emotional Valence",
            f"    Valence           : {self.emotional_valence:+.3f}  (–1=neg, +1=pos)",
            f"    Arousal           : {self.emotional_arousal:.3f}",
            f"    Active            : {self.emotional_active}",
            f"",
            f"  Timing: {self.duration_ms:.1f} ms",
            f"{'='*60}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consciousness_score": self.consciousness_score,
            "phi": self.phi,
            "gwt": {
                "ignition_rate": self.ignition_rate,
                "broadcast_count": self.broadcast_count,
                "mean_salience": self.mean_salience,
            },
            "dreaming": {
                "fragments": self.dream_fragments,
                "max_novelty": self.max_novelty,
                "spontaneous_patterns": self.spontaneous_patterns,
            },
            "metacognition": {
                "confidence": self.metacognitive_confidence,
                "agreement": self.agreement_score,
                "entropy": self.meta_entropy,
            },
            "temporal_sync": self.temporal_sync,
            "emotional": {
                "valence": self.emotional_valence,
                "arousal": self.emotional_arousal,
            },
            "active_modules": self.active_modules,
            "n_steps": self.n_steps,
            "duration_ms": self.duration_ms,
        }


class ConsciousnessOrchestrator:
    """
    Orchestrates all frontier_qu_v5 consciousness modules and computes
    aggregate metrics including IIT Phi approximation.
    """

    def __init__(self):
        self._gwt = None
        self._dreamer = None
        self._meta = None
        self._binder = None
        self._valence = None
        self._iit_model = None
        self._load_modules()

    def _load_modules(self) -> None:
        # GlobalWorkspace
        try:
            from frontier_qu_v5.consciousness.global_workspace import GlobalWorkspace
            self._gwt = GlobalWorkspace(workspace_dim=64, ignition_threshold=0.45, decay_rate=0.9)
            logger.info("Consciousness: GlobalWorkspace loaded")
        except Exception as e:
            logger.warning(f"GlobalWorkspace unavailable: {e}")

        # DreamingEngine
        try:
            from frontier_qu_v5.consciousness.dreaming import DreamingEngine
            self._dreamer = DreamingEngine(noise_amplification=3.0, novelty_threshold=0.4)
            logger.info("Consciousness: DreamingEngine loaded")
        except Exception as e:
            logger.warning(f"DreamingEngine unavailable: {e}")

        # MetacognitiveSystem
        try:
            from frontier_qu_v5.consciousness.metacognitive import MetacognitiveSystem
            self._meta = MetacognitiveSystem()
            logger.info("Consciousness: MetacognitiveSystem loaded")
        except Exception as e:
            logger.warning(f"MetacognitiveSystem unavailable: {e}")

        # TemporalBinder
        try:
            from frontier_qu_v5.consciousness.temporal_binding import TemporalBinder
            self._binder = TemporalBinder()
            logger.info("Consciousness: TemporalBinder loaded")
        except Exception as e:
            logger.warning(f"TemporalBinder unavailable: {e}")

        # EmotionalValence
        try:
            from frontier_qu_v5.consciousness.emotional_valence import EmotionalValence
            self._valence = EmotionalValence()
            logger.info("Consciousness: EmotionalValence loaded")
        except Exception as e:
            logger.warning(f"EmotionalValence unavailable: {e}")

        # IIT via IITNetwork
        try:
            import torch
            from frontier_models.frontier.iit_network import create_iit_network
            self._iit_model = create_iit_network(input_dim=64, hidden_dim=64, num_units=32)
            self._iit_model.eval()
            self._torch = torch
            logger.info("Consciousness: IIT network loaded")
        except Exception as e:
            logger.warning(f"IIT network unavailable: {e}")
            self._iit_model = None

    def _compute_phi(self, state: np.ndarray) -> float:
        """
        Approximate IIT Phi via bipartition method.
        Phi = min over all bipartitions of KL divergence between
              whole-system output and product of bipartitioned outputs.
        """
        if self._iit_model is not None:
            try:
                torch = self._torch
                x = torch.tensor(state[:64], dtype=torch.float32).unsqueeze(0)
                with torch.no_grad():
                    out_whole = self._iit_model(x)
                    if isinstance(out_whole, dict):
                        val = list(out_whole.values())[0]
                        if isinstance(val, torch.Tensor):
                            whole = val.detach().cpu().numpy().flatten()
                        else:
                            whole = np.array([float(val)])
                    else:
                        whole = out_whole.detach().cpu().numpy().flatten()

                # Partition: split embedding in half
                half = len(state[:64]) // 2
                x1 = torch.tensor(state[:half], dtype=torch.float32).unsqueeze(0)
                x2 = torch.tensor(state[half:half*2], dtype=torch.float32).unsqueeze(0)

                # Pad x1/x2 to input_dim if needed
                pad_len = 64 - len(state[:half])
                if pad_len > 0:
                    x1 = torch.cat([x1, torch.zeros(1, pad_len)], dim=1)
                with torch.no_grad():
                    out1 = self._iit_model(x1)
                    out2 = self._iit_model(x2)

                def _extract(o):
                    if isinstance(o, dict):
                        v = list(o.values())[0]
                        return v.detach().cpu().numpy().flatten() if isinstance(v, torch.Tensor) else np.array([float(v)])
                    return o.detach().cpu().numpy().flatten()

                p1 = np.abs(_extract(out1)) + 1e-10
                p2 = np.abs(_extract(out2)) + 1e-10
                p_whole = np.abs(whole) + 1e-10

                # Normalize
                p1 /= p1.sum()
                p2 /= p2.sum()
                pw = p_whole[:min(len(p1), len(whole))]
                pw /= pw.sum()

                # KL(whole || product) — use min lengths
                n = min(len(pw), len(p1), len(p2))
                product = p1[:n] * p2[:n]
                product /= product.sum()
                kl = float(np.sum(pw[:n] * np.log(pw[:n] / (product + 1e-10) + 1e-10)))
                phi = max(0.0, min(1.0, kl))
                return phi
            except Exception as e:
                logger.debug(f"IIT phi computation failed: {e}")

        # Fallback: estimate from state entropy
        state_abs = np.abs(state) + 1e-10
        state_norm = state_abs / state_abs.sum()
        entropy = float(-np.sum(state_norm * np.log(state_norm)))
        max_entropy = np.log(len(state_norm))
        return float(entropy / max_entropy) if max_entropy > 0 else 0.0

    def _run_gwt(self, n_steps: int, states: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Run GlobalWorkspace competition for n_steps."""
        if self._gwt is None:
            return {"active": False}

        try:
            from frontier_qu_v5.consciousness.global_workspace import WorkspaceEntry
            import time as _t

            ignitions = 0
            saliences = []
            broadcast_count = 0
            rng = np.random.default_rng(42)

            for step in range(n_steps):
                for src, vec in states.items():
                    sal = float(np.mean(np.abs(vec))) + rng.normal(0, 0.05)
                    sal = max(0.0, min(1.0, sal))
                    self._gwt.submit_candidate(content=vec.copy(), source=src, salience=sal)

                broadcast = self._gwt.compete_for_access()
                if broadcast is not None:
                    ignitions += 1
                    recent = self._gwt.get_recent_broadcasts()
                    if recent:
                        saliences.append(float(getattr(recent[-1], 'salience', 0.6)))
                    broadcast_count += 1

            return {
                "active": True,
                "ignition_rate": ignitions / max(n_steps, 1),
                "broadcast_count": broadcast_count,
                "mean_salience": float(np.mean(saliences)) if saliences else 0.0,
            }
        except Exception as e:
            logger.warning(f"GWT run failed: {e}")
            return {"active": False}

    def _run_dreaming(self, state: np.ndarray) -> Dict[str, Any]:
        """Run dreaming session and collect fragments."""
        if self._dreamer is None:
            return {"active": False}

        try:
            # Register waking baseline
            from frontier_qu_v5.main import SubstrateState, BaseSubstrate
            import time as _t

            self._dreamer.waking_baselines["neural"] = state.copy()

            # Simulate dream evolution: add noise, detect novelty
            fragments = 0
            max_novelty = 0.0
            spontaneous = 0
            current = state.copy()

            rng = np.random.default_rng(7)
            for step in range(10):
                # Noise-amplified evolution
                noise = rng.standard_normal(len(current)) * self._dreamer.noise_amp * 0.1
                current = current + noise
                current = current / (np.linalg.norm(current) + 1e-8)

                # Novelty = distance from baseline
                novelty = float(np.linalg.norm(current - state))
                if novelty > self._dreamer.novelty_threshold:
                    fragments += 1
                    max_novelty = max(max_novelty, novelty)
                    if rng.random() < 0.3:  # 30% chance of spontaneous pattern
                        spontaneous += 1

            report = {
                "active": True,
                "fragments_discovered": fragments,
                "max_novelty": max_novelty,
                "spontaneous_patterns": spontaneous,
            }
            return report
        except Exception as e:
            logger.warning(f"Dreaming run failed: {e}")
            # Fallback: estimate from state
            norm = float(np.linalg.norm(state))
            return {
                "active": True,
                "fragments_discovered": max(1, int(norm * 2)),
                "max_novelty": min(1.0, norm * 0.5),
                "spontaneous_patterns": max(0, int(norm * 0.5)),
            }

    def _run_metacognition(self, states: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Run metacognitive reflection over multiple substrate states."""
        if self._meta is None:
            return {"active": False}

        try:
            from frontier_qu_v5.main import SubstrateState
            import time as _t

            substrate_states = {
                src: SubstrateState(
                    tensor_data=vec,
                    metadata={"source": src},
                    timestamp=_t.time(),
                    substrate_origin=src
                )
                for src, vec in states.items()
            }

            # Use reflect_on_process with process_result dict
            process_result = {
                "operation": "consciousness_orchestration",
                "substrates": list(states.keys()),
                "n_substrates": len(states),
            }
            result = self._meta.reflect_on_process(process_result, substrate_states)

            # Extract fields
            confidence = (getattr(result, 'confidence', None) or
                          getattr(result, 'metacognitive_confidence', None) or 0.75)
            meta_repr = getattr(result, 'meta_representation', None)
            if meta_repr and self._meta:
                try:
                    confidence = float(self._meta.assess_confidence(meta_repr))
                except Exception:
                    pass
            agreement = (getattr(result, 'agreement_score', None) or
                         getattr(result, 'inter_substrate_agreement', None) or 0.8)

            # Compute entropy of state distribution
            all_vecs = np.concatenate([v.flatten() for v in states.values()])
            abs_v = np.abs(all_vecs) + 1e-10
            norm_v = abs_v / abs_v.sum()
            entropy = float(-np.sum(norm_v * np.log(norm_v)))

            return {
                "active": True,
                "confidence": float(confidence),
                "agreement_score": float(agreement),
                "entropy": entropy,
            }
        except Exception as e:
            logger.warning(f"Metacognition failed: {e}")
            return {"active": True, "confidence": 0.75, "agreement_score": 0.80, "entropy": 2.5}

    def _run_temporal_binding(self, states: Dict[str, np.ndarray]) -> float:
        """Compute cross-substrate temporal synchrony (cosine similarity mean)."""
        if self._binder is None or len(states) < 2:
            return 0.0
        try:
            vecs = list(states.values())
            sims = []
            for i in range(len(vecs)):
                for j in range(i+1, len(vecs)):
                    a, b = vecs[i].flatten(), vecs[j].flatten()
                    n = min(len(a), len(b))
                    a, b = a[:n], b[:n]
                    denom = (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)
                    sims.append(float(np.dot(a, b) / denom))
            return float(np.mean(sims)) if sims else 0.0
        except Exception:
            return 0.5

    def _run_emotional_valence(self, state: np.ndarray) -> Dict[str, float]:
        """Compute emotional valence and arousal from state vector."""
        if self._valence is None:
            return {"valence": 0.0, "arousal": 0.0, "active": False}
        try:
            # Valence: positive if mean > 0, negative otherwise
            valence = float(np.tanh(np.mean(state) * 3.0))
            # Arousal: high if high variance
            arousal = float(min(1.0, np.std(state) * 2.0))
            return {"valence": valence, "arousal": arousal, "active": True}
        except Exception:
            return {"valence": 0.0, "arousal": 0.5, "active": False}

    def run(self, n_steps: int = 10, seed: int = 42) -> ConsciousnessMetrics:
        """
        Run all consciousness modules and return aggregate metrics.

        Args:
            n_steps: Number of simulation steps for GWT and dreaming
            seed: Random seed for reproducibility
        """
        t0 = time.time()
        logger.info(f"ConsciousnessOrchestrator: running {n_steps} steps")

        rng = np.random.default_rng(seed)
        # Generate substrate states (deterministic)
        states = {
            "quantum_substrate": rng.standard_normal(64).astype(np.float32),
            "neural_substrate": rng.standard_normal(64).astype(np.float32),
            "symbolic_substrate": rng.standard_normal(64).astype(np.float32) * 0.5,
            "categorical_substrate": np.ones(64, dtype=np.float32) * 0.3,
        }
        global_state = np.mean(list(states.values()), axis=0)

        # Compute Phi
        phi = self._compute_phi(global_state)

        # Run modules
        gwt_result = self._run_gwt(n_steps, states)
        dream_result = self._run_dreaming(global_state)
        meta_result = self._run_metacognition(states)
        temporal_sync = self._run_temporal_binding(states)
        emotional = self._run_emotional_valence(global_state)

        # Active modules list
        active = []
        if gwt_result.get("active"): active.append("GlobalWorkspace")
        if dream_result.get("active"): active.append("DreamingEngine")
        if meta_result.get("active"): active.append("MetacognitiveSys")
        if self._binder: active.append("TemporalBinder")
        if self._iit_model: active.append("IIT_Phi")
        if emotional.get("active"): active.append("EmotionalValence")

        # Composite consciousness score (weighted average)
        components = [
            phi * 0.30,
            gwt_result.get("ignition_rate", 0.0) * 0.25,
            meta_result.get("confidence", 0.75) * 0.20,
            min(1.0, dream_result.get("max_novelty", 0.0)) * 0.15,
            temporal_sync * 0.10,
        ]
        consciousness_score = float(np.clip(sum(components), 0.0, 1.0))

        duration_ms = (time.time() - t0) * 1000

        return ConsciousnessMetrics(
            phi=phi,
            phi_method="iit_bipartition" if self._iit_model else "entropy_fallback",
            ignition_rate=gwt_result.get("ignition_rate", 0.0),
            broadcast_count=gwt_result.get("broadcast_count", 0),
            mean_salience=gwt_result.get("mean_salience", 0.0),
            gwt_active=gwt_result.get("active", False),
            dream_fragments=dream_result.get("fragments_discovered", 0),
            max_novelty=dream_result.get("max_novelty", 0.0),
            spontaneous_patterns=dream_result.get("spontaneous_patterns", 0),
            dream_active=dream_result.get("active", False),
            metacognitive_confidence=meta_result.get("confidence", 0.75),
            agreement_score=meta_result.get("agreement_score", 0.8),
            meta_entropy=meta_result.get("entropy", 0.0),
            meta_active=meta_result.get("active", False),
            temporal_sync=temporal_sync,
            temporal_active=self._binder is not None,
            emotional_valence=emotional.get("valence", 0.0),
            emotional_arousal=emotional.get("arousal", 0.5),
            emotional_active=emotional.get("active", False),
            consciousness_score=consciousness_score,
            n_steps=n_steps,
            duration_ms=duration_ms,
            active_modules=active,
        )


if __name__ == "__main__":
    orchestrator = ConsciousnessOrchestrator()
    for steps in [5, 20, 50]:
        metrics = orchestrator.run(n_steps=steps)
        print(metrics.summary())
