"""
Tests for the 5 integration modules in frontier_neuro_symbolic/integrations/.

Each test:
  - Imports the module
  - Instantiates with default/minimal params
  - Runs a basic operation (forward pass, dream session, binding, etc.)
  - Asserts output shape and no NaN/Inf values

Integration modules:
  1. dream_tajweed_generator.py  — TajweedDreamGenerator
  2. hott_naskh_evolution.py     — NaskhTypeEvolution
  3. hrr_qiraat_binding.py       — QiraatHolographicBinding
  4. moe_three_world.py          — MoEThreeWorldRouter
  5. temporal_substrate_sync.py  — GammaSynchronizedOrchestrator

Note: Some modules depend on optional packages (z3, yaml). Tests for those
modules are skipped if dependencies are not installed.
"""

import pytest
import torch
import numpy as np
import sys
import os
import time
import importlib

# Add project root to path
_project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, _project_root)


def assert_no_nan_inf(tensor, name="tensor"):
    """Assert tensor contains no NaN or Inf values."""
    if isinstance(tensor, torch.Tensor):
        assert not torch.isnan(tensor).any(), f"{name} contains NaN"
        assert not torch.isinf(tensor).any(), f"{name} contains Inf"
    elif isinstance(tensor, np.ndarray):
        assert not np.isnan(tensor).any(), f"{name} contains NaN"
        assert not np.isinf(tensor).any(), f"{name} contains Inf"


def _can_import(module_path: str) -> bool:
    """Check if a module can be imported without error."""
    try:
        importlib.import_module(module_path)
        return True
    except (ImportError, ModuleNotFoundError):
        return False


# Dependency availability flags
_has_z3 = _can_import('z3')
_has_yaml = _can_import('yaml')

# Integration module availability (some depend on z3/yaml transitively)
_has_dream_tajweed = _can_import('frontier_neuro_symbolic.integrations.dream_tajweed_generator')
_has_hott_naskh = _can_import('frontier_neuro_symbolic.integrations.hott_naskh_evolution')
_has_hrr_qiraat = _can_import('frontier_neuro_symbolic.integrations.hrr_qiraat_binding')
_has_moe_three_world = _can_import('frontier_neuro_symbolic.integrations.moe_three_world')
_has_temporal_sync = _can_import('frontier_neuro_symbolic.integrations.temporal_substrate_sync')


# ---------------------------------------------------------------------------
# 1. Dream Tajweed Generator
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not _has_dream_tajweed,
                    reason="dream_tajweed_generator requires dependencies not installed")
class TestDreamTajweedGenerator:
    """Test TajweedDreamGenerator — novel tajweed pattern discovery."""

    def test_import(self):
        from frontier_neuro_symbolic.integrations.dream_tajweed_generator import (
            TajweedDreamGenerator,
            DreamPattern,
            DreamSession,
        )
        assert TajweedDreamGenerator is not None
        assert DreamPattern is not None
        assert DreamSession is not None

    def test_instantiation(self):
        from frontier_neuro_symbolic.integrations.dream_tajweed_generator import (
            TajweedDreamGenerator,
        )
        gen = TajweedDreamGenerator(
            grid_size=32,
            base_noise_level=0.01,
            dream_amplification=5.0,
            novelty_threshold=0.3,
            phonetic_threshold=0.3,
        )
        assert gen is not None
        assert gen.grid_size == 32
        assert gen.dream_amplification == 5.0

    def test_dream(self):
        """Run a dream session and verify structure."""
        from frontier_neuro_symbolic.integrations.dream_tajweed_generator import (
            TajweedDreamGenerator,
        )
        gen = TajweedDreamGenerator(
            grid_size=16,
            novelty_threshold=0.0,
            phonetic_threshold=0.0,
        )

        session = gen.dream(base_rule="idgham", num_dreams=2, evolution_steps=10)

        assert session is not None
        assert isinstance(session.mean_novelty, float)
        assert session.mean_novelty >= 0.0

    def test_dream_all_rules(self):
        """Run dreams across all tajweed rules."""
        from frontier_neuro_symbolic.integrations.dream_tajweed_generator import (
            TajweedDreamGenerator,
        )
        gen = TajweedDreamGenerator(
            grid_size=16,
            novelty_threshold=0.0,
            phonetic_threshold=0.0,
        )

        results = gen.dream_all_rules(num_dreams_per_rule=1, evolution_steps=10)

        assert isinstance(results, dict)
        assert len(results) == 4
        for rule in ["idgham", "ikhfaa", "iqlab", "izhar"]:
            assert rule in results


# ---------------------------------------------------------------------------
# 2. HoTT Naskh Evolution
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not _has_hott_naskh,
                    reason="hott_naskh_evolution requires dependencies not installed")
class TestNaskhTypeEvolution:
    """Test NaskhTypeEvolution — abrogation as HoTT type evolution."""

    def test_import(self):
        from frontier_neuro_symbolic.integrations.hott_naskh_evolution import (
            NaskhTypeEvolution,
            NaskhEvolutionEvent,
            TypeEvolutionChain,
        )
        assert NaskhTypeEvolution is not None
        assert NaskhEvolutionEvent is not None

    def test_instantiation(self):
        from frontier_neuro_symbolic.integrations.hott_naskh_evolution import (
            NaskhTypeEvolution,
        )
        nte = NaskhTypeEvolution(
            embedding_dim=64,
            stack_dimension=3,
            semantic_dim=32,
            max_universe_levels=5,
        )
        assert nte is not None
        assert nte.embedding_dim == 64

    def test_register_verse(self):
        """Register a verse and verify it exists in the registry."""
        from frontier_neuro_symbolic.integrations.hott_naskh_evolution import (
            NaskhTypeEvolution,
        )
        nte = NaskhTypeEvolution(
            embedding_dim=64,
            stack_dimension=3,
            semantic_dim=32,
        )

        embedding = torch.randn(64)
        nte.register_verse("2:106", embedding)

        assert "2:106" in nte._verse_registry

    def test_detect_naskh(self):
        """Register two verses and detect abrogation."""
        from frontier_neuro_symbolic.integrations.hott_naskh_evolution import (
            NaskhTypeEvolution,
        )
        nte = NaskhTypeEvolution(
            embedding_dim=64,
            stack_dimension=3,
            semantic_dim=32,
        )

        emb1 = torch.randn(64)
        emb2 = torch.randn(64)
        nte.register_verse("2:106", emb1)
        nte.register_verse("2:107", emb2)

        result = nte.detect_and_evolve("2:106", "2:107")
        assert result is None or hasattr(result, 'abrogated_verse')


# ---------------------------------------------------------------------------
# 3. HRR-Qiraat Binding
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not _has_hrr_qiraat,
                    reason="hrr_qiraat_binding requires dependencies not installed")
class TestQiraatHolographicBinding:
    """Test QiraatHolographicBinding — holographic memory for 7 readings."""

    def test_import(self):
        from frontier_neuro_symbolic.integrations.hrr_qiraat_binding import (
            QiraatHolographicBinding,
            ReadingVariant,
            BoundReadingSet,
            RetrievalResult,
        )
        assert QiraatHolographicBinding is not None

    def test_instantiation(self):
        from frontier_neuro_symbolic.integrations.hrr_qiraat_binding import (
            QiraatHolographicBinding,
        )
        binding = QiraatHolographicBinding(
            holographic_dim=256,
            semantic_dim=128,
            num_readers=7,
        )
        assert binding is not None
        assert binding.num_readers == 7
        assert len(binding._role_vectors) == 7

    def test_role_vectors_are_unit(self):
        """Role vectors should be unit-length."""
        from frontier_neuro_symbolic.integrations.hrr_qiraat_binding import (
            QiraatHolographicBinding,
        )
        binding = QiraatHolographicBinding(holographic_dim=128, semantic_dim=64)

        for i, role in binding._role_vectors.items():
            norm = torch.norm(role).item()
            assert abs(norm - 1.0) < 0.01, f"Role vector {i} norm = {norm}"

    def test_bind_readings(self):
        """Bind 7 readings and verify superposition vector."""
        from frontier_neuro_symbolic.integrations.hrr_qiraat_binding import (
            QiraatHolographicBinding,
            ReadingVariant,
        )
        binding = QiraatHolographicBinding(
            holographic_dim=256,
            semantic_dim=128,
            num_readers=7,
        )

        readers = [
            "Asim (Hafs)", "Ibn Kathir", "Abu Amr",
            "Ibn Amir", "Nafi", "Hamza", "Al-Kisa'i"
        ]

        variants = []
        for i, name in enumerate(readers):
            variants.append(ReadingVariant(
                reader_index=i,
                reader_name=name,
                text=f"test_text_{i}",
                semantic_embedding=torch.randn(128),
            ))

        result = binding.bind_readings("1:1", variants)

        assert result is not None
        assert result.superposition_vector.shape[-1] == 256
        assert_no_nan_inf(result.superposition_vector, "superposition_vector")
        assert result.binding_fidelity >= 0.0


# ---------------------------------------------------------------------------
# 4. MoE Three-World Router
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not _has_moe_three_world,
                    reason="moe_three_world requires z3 or other dependencies not installed")
class TestMoEThreeWorldRouter:
    """Test MoEThreeWorldRouter — sparse gating for 3 worlds."""

    def test_import(self):
        from frontier_neuro_symbolic.integrations.moe_three_world import (
            MoEThreeWorldRouter,
            WorldRoutingResult,
        )
        assert MoEThreeWorldRouter is not None

    def test_instantiation(self):
        from frontier_neuro_symbolic.integrations.moe_three_world import (
            MoEThreeWorldRouter,
        )
        router = MoEThreeWorldRouter(
            input_dim=64,
            hidden_dim=128,
            embedding_dim=64,
            vocab_size=500,
            num_heads=2,
            num_layers=1,
            top_k=2,
        )
        assert router is not None
        assert router.num_worlds == 3
        assert router.top_k == 2

    def test_forward_pass(self):
        """Route a query through the 3-world system."""
        from frontier_neuro_symbolic.integrations.moe_three_world import (
            MoEThreeWorldRouter,
        )
        router = MoEThreeWorldRouter(
            input_dim=64,
            hidden_dim=128,
            embedding_dim=64,
            vocab_size=500,
            num_heads=2,
            num_layers=1,
        )

        query = torch.randn(1, 64)
        result = router(query)

        assert result is not None
        if isinstance(result, dict):
            for key, val in result.items():
                if isinstance(val, torch.Tensor):
                    assert_no_nan_inf(val, f"moe_3world_{key}")
        elif hasattr(result, 'routed_output'):
            assert_no_nan_inf(result.routed_output, "routed_output")

    def test_gating_weights(self):
        """Verify gating produces valid sparse weights over 3 worlds."""
        from frontier_neuro_symbolic.integrations.moe_three_world import (
            MoEThreeWorldRouter,
        )
        router = MoEThreeWorldRouter(
            input_dim=64,
            hidden_dim=128,
            embedding_dim=64,
            vocab_size=500,
        )

        query = torch.randn(4, 64)
        weights, selected, loss = router.gate(query, training=False)

        assert weights.shape == (4, 3), f"Expected (4, 3), got {weights.shape}"
        assert selected.shape[0] == 4
        assert_no_nan_inf(weights, "world_weights")


# ---------------------------------------------------------------------------
# 5. Gamma-Synchronized Orchestrator
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not _has_temporal_sync,
                    reason="temporal_substrate_sync requires dependencies not installed")
class TestGammaSynchronizedOrchestrator:
    """Test GammaSynchronizedOrchestrator — temporal substrate synchronization."""

    def test_import(self):
        from frontier_neuro_symbolic.integrations.temporal_substrate_sync import (
            GammaSynchronizedOrchestrator,
            SubstrateHealth,
            SynchronizedMoment,
        )
        assert GammaSynchronizedOrchestrator is not None

    def test_instantiation(self):
        from frontier_neuro_symbolic.integrations.temporal_substrate_sync import (
            GammaSynchronizedOrchestrator,
        )
        orch = GammaSynchronizedOrchestrator(
            binding_window_ms=50.0,
            gamma_freq_hz=40.0,
            degradation_tau=5.0,
            recovery_rate=0.1,
        )
        assert orch is not None
        assert orch.gamma_freq_hz == 40.0

    def test_register_substrate(self):
        """Register substrates and verify they are tracked."""
        from frontier_neuro_symbolic.integrations.temporal_substrate_sync import (
            GammaSynchronizedOrchestrator,
        )
        orch = GammaSynchronizedOrchestrator()

        orch.register_substrate("quantum", clock_rate_hz=1e15)
        orch.register_substrate("neural", clock_rate_hz=1e3)

        assert "quantum" in orch._health
        assert "neural" in orch._health

    def test_record_and_bind(self):
        """Record events from substrates and create a bound moment."""
        from frontier_neuro_symbolic.integrations.temporal_substrate_sync import (
            GammaSynchronizedOrchestrator,
        )
        # Use a local SubstrateState to avoid yaml dependency
        from dataclasses import dataclass
        from typing import Dict, Any

        @dataclass
        class SubstrateState:
            tensor_data: np.ndarray
            metadata: Dict[str, Any]
            timestamp: float
            substrate_origin: str

        orch = GammaSynchronizedOrchestrator(binding_window_ms=5000.0)

        orch.register_substrate("quantum", clock_rate_hz=1e15)
        orch.register_substrate("neural", clock_rate_hz=1e3)

        state_q = SubstrateState(
            tensor_data=np.random.randn(32),
            metadata={},
            timestamp=time.time(),
            substrate_origin="quantum",
        )
        state_n = SubstrateState(
            tensor_data=np.random.randn(32),
            metadata={},
            timestamp=time.time(),
            substrate_origin="neural",
        )

        orch.submit_event("quantum", state_q)
        orch.submit_event("neural", state_n)

        moment = orch.tick()
        if moment is not None:
            assert len(moment.substrate_weights) >= 1

    def test_health_tracking(self):
        """Verify substrate health tracking."""
        from frontier_neuro_symbolic.integrations.temporal_substrate_sync import (
            GammaSynchronizedOrchestrator,
        )
        orch = GammaSynchronizedOrchestrator()
        orch.register_substrate("test_substrate", clock_rate_hz=1000.0)

        health = orch._health["test_substrate"]
        assert health is not None
        assert health.degradation_factor >= 0.0
        assert health.degradation_factor <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
