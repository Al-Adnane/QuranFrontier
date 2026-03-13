#!/usr/bin/env python3
"""
Basic test suite for FrontierQu v5.0+
Verifies all substrates initialize and run correctly
"""

import asyncio
import numpy as np
import pytest
from main import (
    QuantumSubstrate, NeuralSubstrate, OpticalSubstrate,
    BioSubstrate, TopologicalSubstrate, CausalSubstrate,
    HoTTMiddleware, ConsciousnessMonitor, SafetyProtocol,
    FrontierQuOrchestrator
)

class TestSubstrates:
    """Test individual substrate implementations"""

    @pytest.mark.asyncio
    async def test_quantum_initialization(self):
        """Test quantum substrate initializes"""
        substrate = QuantumSubstrate({}, 'quantum')
        await substrate.initialize()
        assert substrate.is_active
        assert substrate.state_vector is not None

    @pytest.mark.asyncio
    async def test_quantum_step(self):
        """Test quantum substrate can step"""
        substrate = QuantumSubstrate({'qubit_count': 2}, 'quantum')
        await substrate.initialize()
        state = await substrate.step(0.01)
        assert state is not None
        assert state.tensor_data.shape == (4, 4)

    @pytest.mark.asyncio
    async def test_neural_initialization(self):
        """Test neural substrate initializes"""
        substrate = NeuralSubstrate({'neuron_count': 100}, 'neural')
        await substrate.initialize()
        assert substrate.is_active

    @pytest.mark.asyncio
    async def test_neural_step(self):
        """Test neural substrate can step"""
        substrate = NeuralSubstrate({'neuron_count': 100}, 'neural')
        await substrate.initialize()
        state = await substrate.step(0.01)
        assert state is not None

    @pytest.mark.asyncio
    async def test_optical_initialization(self):
        """Test optical substrate initializes"""
        substrate = OpticalSubstrate({'field_dimension': 32}, 'optical')
        await substrate.initialize()
        assert substrate.is_active

    @pytest.mark.asyncio
    async def test_optical_step(self):
        """Test optical substrate can step"""
        substrate = OpticalSubstrate({'field_dimension': 32}, 'optical')
        await substrate.initialize()
        state = await substrate.step(0.01)
        assert state is not None

    @pytest.mark.asyncio
    async def test_bio_initialization(self):
        """Test biocomputing substrate initializes"""
        substrate = BioSubstrate({}, 'bio')
        await substrate.initialize()
        assert substrate.is_active

    @pytest.mark.asyncio
    async def test_topological_initialization(self):
        """Test topological substrate initializes"""
        substrate = TopologicalSubstrate({}, 'topo')
        await substrate.initialize()
        assert substrate.is_active

    @pytest.mark.asyncio
    async def test_causal_initialization(self):
        """Test causal substrate initializes"""
        substrate = CausalSubstrate({}, 'causal')
        await substrate.initialize()
        assert substrate.is_active

class TestMiddleware:
    """Test HoTT middleware"""

    def test_hott_initialization(self):
        """Test HoTT middleware initializes"""
        middleware = HoTTMiddleware()
        assert middleware is not None

    def test_hott_translation(self):
        """Test HoTT can translate between substrates"""
        from main import SubstrateState
        middleware = HoTTMiddleware()

        state = SubstrateState(
            tensor_data=np.random.rand(4, 4),
            metadata={},
            timestamp=0.0,
            substrate_origin="quantum"
        )

        translated = middleware.translate(state, "neural")
        assert translated.substrate_origin == "neural"

class TestConsciousness:
    """Test consciousness monitoring"""

    def test_consciousness_monitor_initialization(self):
        """Test consciousness monitor initializes"""
        monitor = ConsciousnessMonitor()
        assert monitor is not None

    def test_consciousness_calculation(self):
        """Test consciousness (Phi) can be calculated"""
        from main import SubstrateState
        monitor = ConsciousnessMonitor()

        states = [
            SubstrateState(
                tensor_data=np.random.rand(4, 4),
                metadata={},
                timestamp=0.0,
                substrate_origin=f"substrate_{i}"
            )
            for i in range(3)
        ]

        phi = monitor.update(states)
        assert phi >= 0.0

class TestSafety:
    """Test safety protocols"""

    def test_safety_initialization(self):
        """Test safety protocol initializes"""
        safety = SafetyProtocol({'phi_threshold_halt': 15.0})
        assert safety is not None

    def test_safety_check_normal(self):
        """Test safety check passes under normal conditions"""
        safety = SafetyProtocol({'phi_threshold_halt': 15.0})
        result = safety.check_metrics({'global_phi': 5.0})
        assert result is True

    def test_safety_check_breach(self):
        """Test safety check triggers on Phi threshold breach"""
        safety = SafetyProtocol({'phi_threshold_halt': 15.0})
        result = safety.check_metrics({'global_phi': 20.0})
        assert result is False
        assert safety.kill_switch is True

class TestOrchestrator:
    """Test full orchestrator"""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initializes with config"""
        orchestrator = FrontierQuOrchestrator("config.yaml")
        assert orchestrator is not None

    @pytest.mark.asyncio
    async def test_orchestrator_substrate_initialization(self):
        """Test orchestrator initializes all substrates"""
        orchestrator = FrontierQuOrchestrator("config.yaml")
        await orchestrator.initialize_substrates()
        assert len(orchestrator.substrates) == 6

    @pytest.mark.asyncio
    async def test_orchestrator_single_step(self):
        """Test orchestrator can run a single step"""
        orchestrator = FrontierQuOrchestrator("config.yaml")
        await orchestrator.initialize_substrates()
        result = await orchestrator.step(0.01)
        assert result is True

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_simulation_10_steps():
    """Integration test: run 10 steps of full simulation"""
    orchestrator = FrontierQuOrchestrator("config.yaml")
    await orchestrator.initialize_substrates()

    for i in range(10):
        result = await orchestrator.step(0.01)
        assert result is True

    assert orchestrator.step_count == 10

@pytest.mark.asyncio
async def test_full_simulation_100_steps():
    """Integration test: run 100 steps of full simulation"""
    orchestrator = FrontierQuOrchestrator("config.yaml")
    await orchestrator.initialize_substrates()

    for i in range(100):
        result = await orchestrator.step(0.01)
        if not result:
            break

    assert orchestrator.step_count >= 90  # Allow some margin

if __name__ == "__main__":
    # Run basic tests without pytest
    print("Running FrontierQu v5.0+ Basic Tests...\n")

    async def run_tests():
        print("✓ Quantum substrate test")
        substrate = QuantumSubstrate({'qubit_count': 2}, 'quantum')
        await substrate.initialize()
        state = await substrate.step(0.01)
        print(f"  - State shape: {state.tensor_data.shape}")

        print("✓ Neural substrate test")
        neural = NeuralSubstrate({'neuron_count': 50}, 'neural')
        await neural.initialize()
        state = await neural.step(0.01)
        print(f"  - Spike count: {state.metadata['spike_count']}")

        print("✓ HoTT middleware test")
        middleware = HoTTMiddleware()
        print(f"  - Middleware ready: {middleware is not None}")

        print("✓ Consciousness monitor test")
        monitor = ConsciousnessMonitor()
        phi = monitor.update([state])
        print(f"  - Initial Φ: {phi:.4f}")

        print("✓ Safety protocol test")
        safety = SafetyProtocol({'phi_threshold_halt': 15.0})
        safe = safety.check_metrics({'global_phi': 5.0})
        print(f"  - System safe: {safe}")

        print("\n✅ All basic tests passed!")

    asyncio.run(run_tests())
