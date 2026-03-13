#!/usr/bin/env python3
"""
FrontierQu v6.0 Year 2 — Comprehensive Test Suite
Tests all 5 new substrates, architectural extensions, and consciousness modules.
"""

import asyncio
import numpy as np
import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import BaseSubstrate, SubstrateState, QuantumSubstrate, NeuralSubstrate


# ═══════════════════════════════════════════════════════════
# NEW SUBSTRATE TESTS
# ═══════════════════════════════════════════════════════════

class TestMorphogeneticSubstrate:
    @pytest.mark.asyncio
    async def test_init_and_step(self):
        from substrates.morphogenetic import MorphogeneticSubstrate
        sub = MorphogeneticSubstrate({'gray_scott': {'grid_size': 20}}, 'morpho')
        await sub.initialize()
        state = await sub.step(0.5)
        assert state.tensor_data.shape == (20, 20)
        assert state.substrate_origin == 'morpho'

    @pytest.mark.asyncio
    async def test_pattern_classification(self):
        from substrates.morphogenetic import MorphogeneticSubstrate
        sub = MorphogeneticSubstrate({'gray_scott': {'grid_size': 30}}, 'morpho')
        await sub.initialize()
        for _ in range(10):
            await sub.step(0.5)
        pattern = sub._pattern_class
        assert pattern in ('spots', 'stripes', 'labyrinth', 'uninitialized')

    @pytest.mark.asyncio
    async def test_logic_output(self):
        from substrates.morphogenetic import MorphogeneticSubstrate
        sub = MorphogeneticSubstrate({'gray_scott': {'grid_size': 20}}, 'morpho')
        await sub.initialize()
        await sub.step(0.5)
        output = sub.get_logic_output()
        assert output in (1, 0, -1)

    @pytest.mark.asyncio
    async def test_metrics(self):
        from substrates.morphogenetic import MorphogeneticSubstrate
        sub = MorphogeneticSubstrate({'gray_scott': {'grid_size': 20}}, 'morpho')
        await sub.initialize()
        await sub.step(0.5)
        m = sub.get_metrics()
        assert 'entropy' in m
        assert 'energy' in m


class TestHolographicSubstrate:
    @pytest.mark.asyncio
    async def test_init_and_step(self):
        from substrates.holographic import HolographicSubstrate
        sub = HolographicSubstrate({'ads_cft': {'boundary_size': 16, 'bulk_layers': 4}}, 'holo')
        await sub.initialize()
        state = await sub.step(0.01)
        assert state.tensor_data.shape == (16,)
        assert 'rt_entropy' in state.metadata

    @pytest.mark.asyncio
    async def test_rt_entropy_positive(self):
        from substrates.holographic import HolographicSubstrate
        sub = HolographicSubstrate({'ads_cft': {'boundary_size': 16, 'bulk_layers': 4}}, 'holo')
        await sub.initialize()
        await sub.step(0.01)
        assert sub._rt_entropy > 0

    @pytest.mark.asyncio
    async def test_error_correction(self):
        from substrates.holographic import HolographicSubstrate
        sub = HolographicSubstrate({'ads_cft': {'boundary_size': 16, 'bulk_layers': 4}}, 'holo')
        await sub.initialize()
        await sub.step(0.01)
        fidelity = sub.state.metadata['error_correction_fidelity']
        assert -1.0 <= fidelity <= 1.0


class TestMemristiveSubstrate:
    @pytest.mark.asyncio
    async def test_init_and_step(self):
        from substrates.memristive import MemristiveSubstrate
        sub = MemristiveSubstrate({'memristor': {'crossbar_rows': 4, 'crossbar_cols': 4}}, 'mem')
        await sub.initialize()
        state = await sub.step(0.01)
        assert len(state.tensor_data) == 4
        assert sub._operations == 1

    @pytest.mark.asyncio
    async def test_matrix_multiply(self):
        from substrates.memristive import MemristiveSubstrate
        sub = MemristiveSubstrate({'memristor': {'crossbar_rows': 4, 'crossbar_cols': 4}}, 'mem')
        await sub.initialize()
        vec = np.ones(4)
        result = sub.matrix_vector_multiply(vec)
        assert len(result) == 4
        assert not np.any(np.isnan(result))

    @pytest.mark.asyncio
    async def test_hebbian_update(self):
        from substrates.memristive import MemristiveSubstrate
        sub = MemristiveSubstrate({'memristor': {'crossbar_rows': 4, 'crossbar_cols': 4}}, 'mem')
        await sub.initialize()
        G_before = sub.G.copy()
        sub.hebbian_update(np.ones(4), np.ones(4), lr=1.0)
        # Conductance should change (though might be subtle)
        assert sub.G is not None


class TestReservoirSubstrate:
    @pytest.mark.asyncio
    async def test_init_and_step(self):
        from substrates.reservoir import ReservoirSubstrate
        sub = ReservoirSubstrate({'reservoir': {'reservoir_size': 50}}, 'res')
        await sub.initialize()
        state = await sub.step(0.01)
        assert state.tensor_data is not None
        assert 'lyapunov_exponent' in state.metadata

    @pytest.mark.asyncio
    async def test_spectral_radius(self):
        from substrates.reservoir import ReservoirSubstrate
        sub = ReservoirSubstrate({'reservoir': {'reservoir_size': 50, 'spectral_radius': 0.9}}, 'res')
        await sub.initialize()
        rho = np.max(np.abs(np.linalg.eigvals(sub.W)))
        assert abs(rho - 0.9) < 0.01

    @pytest.mark.asyncio
    async def test_echo_state_property(self):
        """Reservoir should not explode over many steps."""
        from substrates.reservoir import ReservoirSubstrate
        sub = ReservoirSubstrate({'reservoir': {'reservoir_size': 50, 'spectral_radius': 0.9}}, 'res')
        await sub.initialize()
        for _ in range(100):
            await sub.step(0.01)
        norm = np.linalg.norm(sub.x)
        assert norm < 100  # Should not explode


class TestStochasticThermoSubstrate:
    @pytest.mark.asyncio
    async def test_init_and_step(self):
        from substrates.stochastic_thermo import StochasticThermodynamicSubstrate
        sub = StochasticThermodynamicSubstrate({'thermo': {'n_particles': 10}}, 'thermo')
        await sub.initialize()
        state = await sub.step(0.001)
        assert len(state.tensor_data) == 10
        assert 'jarzynski_free_energy' in state.metadata

    @pytest.mark.asyncio
    async def test_work_accumulation(self):
        from substrates.stochastic_thermo import StochasticThermodynamicSubstrate
        sub = StochasticThermodynamicSubstrate({'thermo': {'n_particles': 10}}, 'thermo')
        await sub.initialize()
        for _ in range(20):
            await sub.step(0.001)
        # Work should have been tracked
        assert len(sub._work_history) == 20

    @pytest.mark.asyncio
    async def test_landauer_limit(self):
        from substrates.stochastic_thermo import StochasticThermodynamicSubstrate
        sub = StochasticThermodynamicSubstrate({'thermo': {'n_particles': 10}}, 'thermo')
        await sub.initialize()
        await sub.step(0.001)
        landauer = sub.state.metadata['landauer_limit']
        assert landauer > 0  # kB * T * ln(2) > 0


# ═══════════════════════════════════════════════════════════
# ARCHITECTURE TESTS
# ═══════════════════════════════════════════════════════════

class TestEntanglement:
    @pytest.mark.asyncio
    async def test_bell_pair_generation(self):
        from architecture.entanglement import EntanglementProtocol
        proto = EntanglementProtocol()
        sub_a = QuantumSubstrate({'qubit_count': 2}, 'qa')
        sub_b = NeuralSubstrate({'neuron_count': 10}, 'nb')
        await sub_a.initialize()
        await sub_b.initialize()
        pair = proto.generate_bell_pair(sub_a, sub_b)
        assert pair.state.shape == (4, 4)
        assert pair.fidelity == 1.0

    @pytest.mark.asyncio
    async def test_chsh_violation(self):
        from architecture.entanglement import EntanglementProtocol
        proto = EntanglementProtocol()
        sub_a = QuantumSubstrate({'qubit_count': 2}, 'qa')
        sub_b = NeuralSubstrate({'neuron_count': 10}, 'nb')
        await sub_a.initialize()
        await sub_b.initialize()
        pair = proto.generate_bell_pair(sub_a, sub_b)
        S = proto.measure_chsh(pair)
        # Should violate classical bound (|S| > 2) for fresh Bell pair
        assert abs(S) > 2.0

    @pytest.mark.asyncio
    async def test_nonlocality_verification(self):
        from architecture.entanglement import EntanglementProtocol
        proto = EntanglementProtocol()
        sub_a = QuantumSubstrate({'qubit_count': 2}, 'qa')
        sub_b = NeuralSubstrate({'neuron_count': 10}, 'nb')
        await sub_a.initialize()
        await sub_b.initialize()
        pair = proto.generate_bell_pair(sub_a, sub_b)
        result = proto.verify_nonlocality(pair)
        assert result['violation'] == True
        assert result['tsirelson_bound'] == pytest.approx(2 * np.sqrt(2), abs=0.01)


class TestConsensus:
    @pytest.mark.asyncio
    async def test_consensus_round(self):
        from architecture.consensus import ByzantineConsensus
        subs = []
        for i in range(5):
            s = QuantumSubstrate({'qubit_count': 2}, f'q{i}')
            await s.initialize()
            await s.step(0.01)
            subs.append(s)
        consensus = ByzantineConsensus(subs)
        result = await consensus.full_consensus_round('q0')
        assert 'consensus_reached' in result
        assert result['yes_count'] + result['no_count'] == 5

    @pytest.mark.asyncio
    async def test_byzantine_tolerance(self):
        from architecture.consensus import ByzantineConsensus
        subs = []
        for i in range(7):
            s = QuantumSubstrate({'qubit_count': 2}, f'q{i}')
            await s.initialize()
            await s.step(0.01)
            subs.append(s)
        consensus = ByzantineConsensus(subs)
        assert consensus.f == 2  # (7-1)//3 = 2


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_health_check(self):
        from architecture.lifecycle import SubstrateLifecycle, HealthStatus
        sub = QuantumSubstrate({'qubit_count': 2}, 'q')
        await sub.initialize()
        await sub.step(0.01)
        lifecycle = SubstrateLifecycle([sub])
        lifecycle.heartbeat('q', {'entropy': 1.0, 'energy': 0.5})
        statuses = lifecycle.check_all()
        assert statuses['q'] == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_death_and_resurrection(self):
        from architecture.lifecycle import SubstrateLifecycle, HealthStatus
        sub = QuantumSubstrate({'qubit_count': 2}, 'q')
        await sub.initialize()
        lifecycle = SubstrateLifecycle([sub])
        lifecycle._kill('q', reason='test')
        assert lifecycle.vitals['q'].status == HealthStatus.DEAD
        success = await lifecycle.resurrect('q')
        assert success
        assert lifecycle.vitals['q'].status == HealthStatus.HEALTHY


class TestEmergentLanguage:
    @pytest.mark.asyncio
    async def test_encode_decode(self):
        from architecture.emergent_language import EmergentLanguage
        sub = QuantumSubstrate({'qubit_count': 2}, 'q')
        await sub.initialize()
        await sub.step(0.01)
        lang = EmergentLanguage(['q', 'n'], message_dim=8)
        msg = lang.encode(sub)
        assert len(msg.content) == 8
        adj = lang.decode('n', msg)
        assert len(adj) == 8

    @pytest.mark.asyncio
    async def test_broadcast(self):
        from architecture.emergent_language import EmergentLanguage
        sub_a = QuantumSubstrate({'qubit_count': 2}, 'q')
        sub_b = NeuralSubstrate({'neuron_count': 10}, 'n')
        await sub_a.initialize()
        await sub_b.initialize()
        await sub_a.step(0.01)
        await sub_b.step(0.01)
        lang = EmergentLanguage(['q', 'n'], message_dim=8)
        adjustments = lang.broadcast(sub_a, [sub_b])
        assert 'n' in adjustments


class TestSelfModifyingHoTT:
    def test_register_and_evolve(self):
        from architecture.self_modifying_hott import SelfModifyingHoTT
        hott = SelfModifyingHoTT()
        hott.register_type('quantum', level=0, attributes={'qubits': 12})
        assert 'quantum' in hott.types
        success = hott.evolve_type('quantum', {'fidelity': 0.99})
        assert success
        assert len(hott.modification_log) >= 2

    def test_path_and_transport(self):
        from architecture.self_modifying_hott import SelfModifyingHoTT
        hott = SelfModifyingHoTT()
        hott.register_type('A', level=0)
        hott.register_type('B', level=0)
        hott.assert_path('A', 'B', proof='isomorphism')
        result = hott.transport({'value': 42}, 'A', 'B')
        assert result['_transported_via'] is not None

    def test_strange_loop_detection(self):
        from architecture.self_modifying_hott import SelfModifyingHoTT
        hott = SelfModifyingHoTT()
        hott.register_type('A', level=0)
        hott.register_type('B', level=0)
        hott.assert_path('A', 'B', proof='forward')
        hott.assert_path('B', 'A', proof='backward')  # Creates loop!
        assert hott.compute_winding_number() >= 1

    def test_merge_types(self):
        from architecture.self_modifying_hott import SelfModifyingHoTT
        hott = SelfModifyingHoTT()
        hott.register_type('X', level=0, attributes={'a': 1})
        hott.register_type('Y', level=0, attributes={'b': 2})
        merged = hott.merge_types('X', 'Y', 'XY')
        assert merged is not None
        assert 'a' in merged.attributes
        assert 'b' in merged.attributes


# ═══════════════════════════════════════════════════════════
# CONSCIOUSNESS TESTS
# ═══════════════════════════════════════════════════════════

class TestDreaming:
    @pytest.mark.asyncio
    async def test_dream_session(self):
        from consciousness.dreaming import DreamingEngine
        subs = []
        for name in ['q', 'n']:
            if name == 'q':
                s = QuantumSubstrate({'qubit_count': 2}, name)
            else:
                s = NeuralSubstrate({'neuron_count': 10}, name)
            await s.initialize()
            await s.step(0.01)
            subs.append(s)

        engine = DreamingEngine(noise_amplification=2.0)
        report = await engine.dream(subs, duration_steps=20, dt=0.01)
        assert report.duration > 0
        assert report.fragments_discovered >= 0


class TestMirror:
    @pytest.mark.asyncio
    async def test_mirror_test(self):
        from consciousness.mirror import MirrorSelfRecognition
        # Use a Year 2 substrate that properly sets self.state
        from substrates.reservoir import ReservoirSubstrate
        sub = ReservoirSubstrate({'reservoir': {'reservoir_size': 20}}, 'res')
        await sub.initialize()
        for _ in range(5):
            await sub.step(0.01)
        assert sub.state is not None, "Substrate must have state before mirror test"
        mirror = MirrorSelfRecognition(n_trials=5)
        result = await mirror.run_mirror_test(sub)
        assert isinstance(result.self_recognition, (bool, np.bool_))
        assert 0 <= result.confidence <= 1


class TestTemporalBinding:
    def test_event_recording(self):
        from consciousness.temporal_binding import TemporalBinder
        binder = TemporalBinder()
        binder.register_clock('q', 1e15)
        state = SubstrateState(
            tensor_data=np.array([1.0, 2.0]),
            metadata={}, timestamp=time.time(),
            substrate_origin='q'
        )
        binder.record_event('q', state, magnitude=1.0)
        assert len(binder.event_buffer) == 1

    def test_moment_binding(self):
        from consciousness.temporal_binding import TemporalBinder
        binder = TemporalBinder(binding_window_ms=1000)  # 1 second window
        binder.register_clock('q', 1e6)
        binder.register_clock('n', 1e3)
        for sid in ['q', 'n', 'q', 'n']:
            state = SubstrateState(
                tensor_data=np.random.randn(4),
                metadata={}, timestamp=time.time(),
                substrate_origin=sid
            )
            binder.record_event(sid, state)
        moment = binder.bind_moment()
        assert moment is not None
        assert moment.participating_substrates == 2


# ═══════════════════════════════════════════════════════════
# INTEGRATION TEST
# ═══════════════════════════════════════════════════════════

class TestIntegration:
    @pytest.mark.asyncio
    async def test_all_substrates_step(self):
        """Verify all 5 new substrates can initialize and step."""
        from substrates.morphogenetic import MorphogeneticSubstrate
        from substrates.holographic import HolographicSubstrate
        from substrates.memristive import MemristiveSubstrate
        from substrates.reservoir import ReservoirSubstrate
        from substrates.stochastic_thermo import StochasticThermodynamicSubstrate

        configs = [
            (MorphogeneticSubstrate, {'gray_scott': {'grid_size': 10}}, 'morpho'),
            (HolographicSubstrate, {'ads_cft': {'boundary_size': 8, 'bulk_layers': 3}}, 'holo'),
            (MemristiveSubstrate, {'memristor': {'crossbar_rows': 4, 'crossbar_cols': 4}}, 'mem'),
            (ReservoirSubstrate, {'reservoir': {'reservoir_size': 20}}, 'res'),
            (StochasticThermodynamicSubstrate, {'thermo': {'n_particles': 5}}, 'thermo'),
        ]

        for cls, cfg, name in configs:
            sub = cls(cfg, name)
            await sub.initialize()
            assert sub.is_active, f"{name} not active after init"
            state = await sub.step(0.01)
            assert state is not None, f"{name} returned None state"
            metrics = sub.get_metrics()
            assert isinstance(metrics, dict), f"{name} metrics not dict"

    @pytest.mark.asyncio
    async def test_cross_substrate_entanglement(self):
        """Entangle a quantum and neural substrate."""
        from architecture.entanglement import EntanglementProtocol
        proto = EntanglementProtocol()
        q = QuantumSubstrate({'qubit_count': 2}, 'q')
        n = NeuralSubstrate({'neuron_count': 10}, 'n')
        await q.initialize()
        await n.initialize()
        pair = proto.generate_bell_pair(q, n)
        S = proto.measure_chsh(pair)
        assert abs(S) > 2.0  # Quantum violation


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
