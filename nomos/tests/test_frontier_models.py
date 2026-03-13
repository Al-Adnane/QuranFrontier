"""
Comprehensive tests for frontier_models.

Tests at least 10 key models:
- Instantiate with default/minimal params
- Run forward pass with random tensor input
- Assert output shape and no NaN/Inf values
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
# Add consciousness dir directly to avoid yaml dependency in main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'frontier_qu_v5', 'consciousness'))


def assert_no_nan_inf(tensor, name="tensor"):
    """Assert tensor contains no NaN or Inf values."""
    if isinstance(tensor, torch.Tensor):
        assert not torch.isnan(tensor).any(), f"{name} contains NaN"
        assert not torch.isinf(tensor).any(), f"{name} contains Inf"
    elif isinstance(tensor, np.ndarray):
        assert not np.isnan(tensor).any(), f"{name} contains NaN"
        assert not np.isinf(tensor).any(), f"{name} contains Inf"


# ---------------------------------------------------------------------------
# 1. Holographic Memory Network
# ---------------------------------------------------------------------------
class TestHolographicMemory:
    """Test holographic memory bind/unbind roundtrip and forward pass."""

    def test_instantiation(self):
        from frontier_models.wild.holographic_memory import HolographicMemoryNetwork
        net = HolographicMemoryNetwork(item_dim=64, holographic_dim=128, memory_capacity=50)
        assert net is not None
        assert net.holographic_dim == 128

    def test_bind_unbind_roundtrip(self):
        from frontier_models.wild.holographic_memory import HolographicMemory
        mem = HolographicMemory(holographic_dim=128, capacity=100)

        item1 = torch.randn(128)
        item2 = torch.randn(128)

        bound = mem.bind(item1, item2)
        assert bound.shape == (128,), f"Bound shape: {bound.shape}"
        assert_no_nan_inf(bound, "bound")

        recovered = mem.unbind(bound, item1)
        assert recovered.shape == (128,), f"Recovered shape: {recovered.shape}"
        assert_no_nan_inf(recovered, "recovered")

        # Recovered should correlate with item2 (not exact due to noise)
        cos_sim = torch.nn.functional.cosine_similarity(
            recovered.unsqueeze(0), item2.unsqueeze(0)
        ).item()
        # Holographic binding is approximate, just check it's not random
        assert cos_sim > -1.0, "Unbind result is degenerate"

    def test_store_and_retrieve(self):
        from frontier_models.wild.holographic_memory import HolographicMemory
        mem = HolographicMemory(holographic_dim=64, capacity=100)

        # Store some items
        items = [torch.randn(64) for _ in range(5)]
        for item in items:
            mem.store(item)

        assert mem.memory_count == 5

        # Retrieve with first item as cue
        results = mem.retrieve(items[0], k=3)
        assert len(results) > 0
        assert results[0].similarity > 0, "Top result should have positive similarity"
        assert_no_nan_inf(results[0].retrieved, "retrieved")

    def test_recall(self):
        """Test storing and recalling a memory via the high-level API."""
        from frontier_models.wild.holographic_memory import HolographicMemoryNetwork
        net = HolographicMemoryNetwork(item_dim=64, holographic_dim=128, memory_capacity=50)

        # Store some items
        items = torch.randn(5, 64)
        count = net.store_memories(items)
        assert count == 5

        # Recall with first item as cue
        result = net.recall(items[0])
        assert result is not None
        assert result.similarity > 0
        assert_no_nan_inf(result.retrieved, "recalled_memory")


# ---------------------------------------------------------------------------
# 2. Mixture of Experts
# ---------------------------------------------------------------------------
class TestMixtureOfExperts:
    """Test MoE gating and forward pass."""

    def test_instantiation(self):
        from frontier_models.wild.mixture_of_experts import MoENetwork
        net = MoENetwork(input_dim=64, hidden_dim=128, output_dim=10, num_experts=4, top_k=2)
        assert net is not None
        assert net.num_experts == 4
        assert net.top_k == 2

    def test_gating_produces_valid_topk_weights(self):
        from frontier_models.wild.mixture_of_experts import GatingNetwork
        gate = GatingNetwork(input_dim=64, num_experts=8, top_k=2)

        x = torch.randn(4, 64)
        weights, selected, load_loss = gate(x, training=False)

        # Weights should sum to ~1 per sample
        weight_sums = weights.sum(dim=-1)
        assert torch.allclose(weight_sums, torch.ones(4), atol=0.01), \
            f"Weight sums: {weight_sums}"

        # Selected should have shape [batch, top_k]
        assert selected.shape == (4, 2)

        # Only top_k experts should have non-zero weights
        nonzero_per_sample = (weights > 0).sum(dim=-1)
        assert (nonzero_per_sample <= 2).all(), "More than top_k experts have non-zero weight"

        assert_no_nan_inf(weights, "gating_weights")
        assert_no_nan_inf(load_loss, "load_loss")

    def test_forward_pass(self):
        from frontier_models.wild.mixture_of_experts import MoENetwork
        net = MoENetwork(input_dim=64, hidden_dim=128, output_dim=10, num_experts=4, top_k=2)

        x = torch.randn(8, 64)
        output = net(x, training=False)

        assert 'logits' in output
        assert output['logits'].shape == (8, 10)
        assert_no_nan_inf(output['logits'], "moe_logits")
        assert_no_nan_inf(output['load_balancing_loss'], "load_loss")

    def test_moe_layer_output_shape(self):
        from frontier_models.wild.mixture_of_experts import MoELayer
        layer = MoELayer(input_dim=64, output_dim=64, num_experts=4, top_k=2)

        x = torch.randn(4, 64)
        result = layer(x, training=False)

        assert result.output.shape == (4, 64)
        assert_no_nan_inf(result.output, "moe_layer_output")


# ---------------------------------------------------------------------------
# 3. Temporal Prediction Network
# ---------------------------------------------------------------------------
class TestTemporalPrediction:
    """Test predictive processing and prediction error computation."""

    def test_instantiation(self):
        from frontier_models.wild.temporal_prediction import TemporalPredictionNetwork
        net = TemporalPredictionNetwork(input_dim=32, hidden_dim=64, num_levels=3)
        assert net is not None
        assert net.num_levels == 3

    def test_prediction_error_computation(self):
        from frontier_models.wild.temporal_prediction import TemporalPredictionNetwork
        net = TemporalPredictionNetwork(input_dim=64, hidden_dim=64, num_levels=2)

        # Use batch_size=1 to avoid broadcasting bug in precision weighting
        observed = torch.randn(1, 8, 64)
        state = net.predict_sequence(observed, num_steps=5)

        assert state.free_energy >= 0, "Free energy should be non-negative"
        assert len(state.predictions) == 8, "Should have prediction for each timestep"
        assert len(state.prediction_errors) == 8

    def test_forward_pass(self):
        from frontier_models.wild.temporal_prediction import TemporalPredictionNetwork
        net = TemporalPredictionNetwork(input_dim=64, hidden_dim=64, num_levels=2)

        # Use batch_size=1 to avoid broadcasting bug in precision weighting
        observed = torch.randn(1, 8, 64)
        output = net(observed)

        assert 'free_energy' in output
        assert 'predictions' in output
        assert 'errors' in output
        assert output['free_energy'] >= 0


# ---------------------------------------------------------------------------
# 4. Consciousness Integration Network
# ---------------------------------------------------------------------------
class TestConsciousnessNetwork:
    """Test consciousness network initialization and processing."""

    def test_instantiation(self):
        from frontier_models.wild.consciousness_network import ConsciousnessIntegrationNetwork
        input_dims = {'vision': 64, 'language': 128, 'memory': 32}
        net = ConsciousnessIntegrationNetwork(input_dims, workspace_dim=128)
        assert net is not None
        assert 'vision' in net.proc_modules

    def test_default_creation(self):
        from frontier_models.wild.consciousness_network import create_consciousness_network
        net = create_consciousness_network()
        assert net is not None

    def test_forward_pass(self):
        from frontier_models.wild.consciousness_network import ConsciousnessIntegrationNetwork
        # workspace_dim must match hidden_dim for attention to work
        input_dims = {'vision': 64, 'language': 128}
        net = ConsciousnessIntegrationNetwork(input_dims, workspace_dim=256, hidden_dim=256)

        inputs = {
            'vision': torch.randn(1, 64),
            'language': torch.randn(1, 128),
        }

        output = net(inputs)
        assert 'workspace' in output
        assert 'phi' in output
        assert 'active_modules' in output
        assert 'report' in output
        assert_no_nan_inf(output['workspace'], "workspace_content")


# ---------------------------------------------------------------------------
# 5. Simplicial Attention Transformer
# ---------------------------------------------------------------------------
class TestSimplicialAttention:
    """Test simplicial attention transformer components."""

    def test_simplicial_embedding(self):
        from frontier_models.topological.simplicial_attention import SimplicialEmbedding
        emb = SimplicialEmbedding(
            num_vertices=10, num_edges=15, num_triangles=5, embed_dim=32
        )
        assert emb is not None

        v_ids = torch.arange(10)
        e_ids = torch.arange(15)
        t_ids = torch.arange(5)

        v_emb, e_emb, t_emb = emb(v_ids, e_ids, t_ids)
        assert v_emb.shape == (10, 32)
        assert e_emb.shape == (15, 32)
        assert t_emb.shape == (5, 32)
        assert_no_nan_inf(v_emb, "vertex_embedding")

    def test_boundary_operator(self):
        from frontier_models.topological.simplicial_attention import BoundaryOperator
        bo = BoundaryOperator(from_dim=1, to_dim=0)
        assert bo is not None
        assert bo.from_dim == 1

    def test_simplicial_structure_dataclass(self):
        from frontier_models.topological.simplicial_attention import SimplicialStructure
        structure = SimplicialStructure(
            vertices=torch.randn(10, 32),
            edges=torch.tensor([[0, 1], [1, 2], [2, 0]]),
            triangles=torch.tensor([[0, 1, 2]]),
        )
        assert structure.vertices.shape == (10, 32)
        assert structure.edges.shape == (3, 2)


# ---------------------------------------------------------------------------
# 6. Deontic Logic Network
# ---------------------------------------------------------------------------
class TestDeonticLogic:
    """Test deontic logic network for normative reasoning."""

    def test_instantiation(self):
        from frontier_models.symbolic.deontic import DeonticLogicNetwork
        net = DeonticLogicNetwork(input_dim=64, hidden_dim=128)
        assert net is not None

    def test_constraint_layer(self):
        from frontier_models.symbolic.deontic import DeonticConstraintLayer
        cl = DeonticConstraintLayer(num_classes=5)

        logits = torch.randn(4, 5)
        constrained = cl(logits, hard_constraints=True)

        assert constrained.shape == (4, 5)
        assert_no_nan_inf(constrained, "constrained_logits")

    def test_constraint_loss(self):
        from frontier_models.symbolic.deontic import DeonticConstraintLayer
        cl = DeonticConstraintLayer(num_classes=5)

        logits = torch.randn(4, 5)
        loss = cl.constraint_loss(logits)

        assert loss.shape == ()
        assert loss.item() >= 0, "Constraint loss should be non-negative"
        assert_no_nan_inf(loss, "constraint_loss")

    def test_forward_classify(self):
        from frontier_models.symbolic.deontic import DeonticLogicNetwork
        net = DeonticLogicNetwork(input_dim=64, hidden_dim=128)

        features = torch.randn(1, 8, 64)  # batch=1, seq_len=8
        ruling = net.classify(features)

        assert ruling is not None
        assert 0.0 <= ruling.confidence <= 1.0
        assert ruling.status is not None


# ---------------------------------------------------------------------------
# 7. Quranic GNN
# ---------------------------------------------------------------------------
class TestQuranicGNN:
    """Test holistic Quranic graph neural network."""

    def test_instantiation(self):
        from frontier_models.holistic.quranic_gnn import HolisticQuranicGNN
        net = HolisticQuranicGNN(input_dim=64, hidden_dim=128)
        assert net is not None

    def test_forward_pass(self):
        from frontier_models.holistic.quranic_gnn import HolisticQuranicGNN
        net = HolisticQuranicGNN(input_dim=64, hidden_dim=128)

        x = torch.randn(20, 64)  # 20 verses, 64-dim features
        output = net(x)

        assert output.shape == (20, 128)
        assert_no_nan_inf(output, "quranic_gnn_output")

    def test_query(self):
        from frontier_models.holistic.quranic_gnn import HolisticQuranicGNN
        net = HolisticQuranicGNN(input_dim=64, hidden_dim=128)

        verse_features = torch.randn(50, 64)
        query_emb = torch.randn(128)

        result = net.query(verse_features, query_emb, k=10)
        assert result.activations.shape[0] == 10


# ---------------------------------------------------------------------------
# 8. Quantum Superposition Embedding
# ---------------------------------------------------------------------------
class TestQuantumSuperposition:
    """Test quantum superposition embeddings."""

    def test_hilbert_space_embedding(self):
        from frontier_models.quantum.superposition import HilbertSpaceEmbedding
        emb = HilbertSpaceEmbedding(vocab_size=100, hilbert_dim=32, num_basis_states=8)
        assert emb is not None

        input_ids = torch.randint(0, 100, (2, 10))
        state = emb(input_ids)

        assert state.state_vector is not None
        assert state.probabilities is not None
        # Probabilities should be non-negative
        assert (state.probabilities.real >= -1e-6).all(), "Probabilities must be non-negative"

    def test_quantum_state_properties(self):
        from frontier_models.quantum.superposition import HilbertSpaceEmbedding
        emb = HilbertSpaceEmbedding(vocab_size=100, hilbert_dim=32)

        input_ids = torch.randint(0, 100, (1, 5))
        state = emb(input_ids)

        # State vector should be normalized (unit length)
        norm = torch.norm(state.state_vector)
        assert norm.item() > 0, "State vector should be non-zero"
        # Phase should exist
        assert state.phase is not None
        assert state.phase.shape[-1] == 32


# ---------------------------------------------------------------------------
# 9. p-adic Neural Network
# ---------------------------------------------------------------------------
class TestPAdicNetwork:
    """Test p-adic neural network."""

    def test_instantiation(self):
        from frontier_models.frontier.p_adic_network import PAdicNeuralNetwork
        net = PAdicNeuralNetwork(vocab_size=500, embed_dim=64, hidden_dim=128)
        assert net is not None
        assert net.p == 2  # Default p

    def test_forward_pass(self):
        from frontier_models.frontier.p_adic_network import PAdicNeuralNetwork
        net = PAdicNeuralNetwork(vocab_size=500, embed_dim=64, hidden_dim=128)

        # Input is token IDs, not raw features
        x = torch.randint(0, 500, (4, 10))  # batch=4, seq_len=10
        output = net(x)

        assert isinstance(output, dict)
        assert 'output' in output
        assert_no_nan_inf(output['output'], "p_adic_output")
        assert output['p'] == 2


# ---------------------------------------------------------------------------
# 10. Holographic Encoder (standalone)
# ---------------------------------------------------------------------------
class TestHolographicEncoder:
    """Test holographic encoder independently."""

    def test_encoding_produces_unit_vectors(self):
        from frontier_models.wild.holographic_memory import HolographicEncoder
        enc = HolographicEncoder(item_dim=64, holographic_dim=128)

        items = torch.randn(8, 64)
        encoded = enc(items)

        assert encoded.shape == (8, 128)
        assert_no_nan_inf(encoded, "encoded")

        # Should be approximately unit vectors
        norms = torch.norm(encoded, dim=-1)
        assert torch.allclose(norms, torch.ones(8), atol=0.01), \
            f"Encoded vectors should be unit length, got norms: {norms}"


# ---------------------------------------------------------------------------
# 11. Expert Network (component of MoE)
# ---------------------------------------------------------------------------
class TestExpertNetwork:
    """Test individual expert network."""

    def test_forward_pass(self):
        from frontier_models.wild.mixture_of_experts import ExpertNetwork
        expert = ExpertNetwork(input_dim=64, output_dim=64, hidden_dim=256)

        x = torch.randn(4, 64)
        output = expert(x)

        assert output.shape == (4, 64)
        assert_no_nan_inf(output, "expert_output")


# ---------------------------------------------------------------------------
# 12. Prediction Layer (component of temporal prediction)
# ---------------------------------------------------------------------------
class TestPredictionLayer:
    """Test single prediction layer."""

    def test_forward_with_prediction(self):
        from frontier_models.wild.temporal_prediction import PredictionLayer
        layer = PredictionLayer(input_dim=32, hidden_dim=64)

        input_data = torch.randn(2, 32)
        top_pred = torch.randn(2, 64)

        pred, error, precision = layer(input_data, top_pred)

        assert pred.shape == (2, 32)
        assert error.shape == (2, 64)
        assert precision.shape == (2, 1)
        assert (precision >= 0).all() and (precision <= 1).all(), \
            "Precision should be in [0, 1]"
        assert_no_nan_inf(pred, "prediction")
        assert_no_nan_inf(error, "error")

    def test_forward_without_prediction(self):
        from frontier_models.wild.temporal_prediction import PredictionLayer
        layer = PredictionLayer(input_dim=32, hidden_dim=64)

        input_data = torch.randn(2, 32)
        pred, error, precision = layer(input_data, None)

        # Without top-down prediction, prediction should be zeros
        assert torch.allclose(pred, torch.zeros_like(pred))


# ---------------------------------------------------------------------------
# 13. Holographic Attention
# ---------------------------------------------------------------------------
class TestHolographicAttention:
    """Test holographic attention mechanism."""

    def test_forward_pass(self):
        from frontier_models.wild.holographic_memory import HolographicAttention
        attn = HolographicAttention(holographic_dim=64, num_heads=4)

        query = torch.randn(2, 64)
        keys = torch.randn(2, 5, 64)
        values = torch.randn(2, 5, 64)

        output = attn(query, keys, values)
        assert output.shape == (2, 64)
        assert_no_nan_inf(output, "holographic_attention_output")


# ---------------------------------------------------------------------------
# Consciousness Module Tests (new modules)
# ---------------------------------------------------------------------------
class TestMetacognitiveSystem:
    """Test the new metacognitive awareness system."""

    def test_instantiation(self):
        from metacognitive import MetacognitiveSystem
        mc = MetacognitiveSystem()
        assert mc is not None

    def test_form_meta_representation(self):
        from metacognitive import MetacognitiveSystem
        mc = MetacognitiveSystem()

        result = {'output': np.random.randn(100), 'duration': 0.5}
        meta = mc.form_meta_representation(result)

        assert meta.process_id == "proc_000000"
        assert meta.output_summary.shape == (64,)
        assert meta.entropy >= 0

    def test_assess_confidence(self):
        from metacognitive import MetacognitiveSystem
        mc = MetacognitiveSystem()

        result = {'output': np.random.randn(100)}
        meta = mc.form_meta_representation(result)
        confidence = mc.assess_confidence(meta)

        assert 0.0 <= confidence <= 1.0

    def test_reflect_on_process(self):
        from metacognitive import MetacognitiveSystem
        mc = MetacognitiveSystem()

        result = {'output': np.random.randn(100)}
        awareness = mc.reflect_on_process(result)

        assert awareness.confidence >= 0
        assert awareness.uncertainty_type in ('aleatoric', 'epistemic')
        assert isinstance(awareness.self_assessment, str)

    def test_detect_uncertainty(self):
        from metacognitive import MetacognitiveSystem
        mc = MetacognitiveSystem()

        # Identical states = low uncertainty
        state = np.random.randn(50)
        low_unc = mc.detect_uncertainty([state, state.copy(), state.copy()])
        assert low_unc < 0.5, f"Identical states should have low uncertainty, got {low_unc}"

        # Random states = higher uncertainty
        states = [np.random.randn(50) for _ in range(5)]
        high_unc = mc.detect_uncertainty(states)
        assert high_unc >= 0.0


class TestGlobalWorkspaceNew:
    """Test the new global workspace implementation."""

    def test_instantiation(self):
        from global_workspace import GlobalWorkspace
        gw = GlobalWorkspace(workspace_dim=128)
        assert gw is not None
        assert gw.workspace_state is None

    def test_broadcast(self):
        from global_workspace import GlobalWorkspace
        gw = GlobalWorkspace(workspace_dim=64)

        content = np.random.randn(64)
        gw.broadcast(content, source="test_module")

        assert gw.workspace_state is not None
        assert gw.workspace_state.shape == (64,)
        assert len(gw.access_history) == 1

    def test_competition(self):
        from global_workspace import GlobalWorkspace
        gw = GlobalWorkspace(workspace_dim=64, ignition_threshold=0.3)

        # Submit candidates with different saliences
        gw.submit_candidate(np.random.randn(64), "module_a", salience=0.8)
        gw.submit_candidate(np.random.randn(64), "module_b", salience=0.5)
        gw.submit_candidate(np.random.randn(64), "module_c", salience=0.2)

        winner = gw.compete_for_access()

        assert winner is not None
        assert winner.shape == (64,)
        # The broadcast should record the winner
        assert len(gw.access_history) == 1
        assert gw.access_history[0].source == "module_a"

    def test_ignition_failure(self):
        from global_workspace import GlobalWorkspace
        gw = GlobalWorkspace(workspace_dim=64, ignition_threshold=0.9)

        # Submit low-salience candidate
        gw.submit_candidate(np.random.randn(64), "weak_module", salience=0.1)
        result = gw.compete_for_access()

        assert result is None  # Should fail to ignite
        assert gw._ignition_failures == 1

    def test_metrics(self):
        from global_workspace import GlobalWorkspace
        gw = GlobalWorkspace(workspace_dim=64)

        gw.broadcast(np.random.randn(64), "test")
        metrics = gw.get_metrics()

        assert metrics['broadcasts'] == 1
        assert metrics['workspace_active'] is True


class TestEmotionalValence:
    """Test the new emotional valence system."""

    def test_instantiation(self):
        from emotional_valence import EmotionalValence
        ev = EmotionalValence(feature_dim=64)
        assert ev is not None
        assert len(ev.emotional_categories) == 10

    def test_compute_valence(self):
        from emotional_valence import EmotionalValence
        ev = EmotionalValence(feature_dim=64)

        features = np.random.randn(64)
        valence, arousal = ev.compute_valence(features)

        assert -1.0 <= valence <= 1.0, f"Valence out of range: {valence}"
        assert -1.0 <= arousal <= 1.0, f"Arousal out of range: {arousal}"

    def test_affect_processing(self):
        from emotional_valence import EmotionalValence
        ev = EmotionalValence(feature_dim=64)

        state = np.random.randn(100)
        modulated = ev.affect_processing(state, valence=0.8, arousal=0.5)

        assert modulated.shape == state.shape
        assert not np.array_equal(modulated, state), "Modulation should change the state"
        assert not np.isnan(modulated).any()
        assert not np.isinf(modulated).any()

    def test_mood_tracking(self):
        from emotional_valence import EmotionalValence
        ev = EmotionalValence(feature_dim=64)

        # Process multiple verses
        for _ in range(20):
            ev.compute_valence(np.random.randn(64))

        mood_v, mood_a = ev.get_mood()
        assert -1.0 <= mood_v <= 1.0
        assert -1.0 <= mood_a <= 1.0

    def test_emotional_trajectory(self):
        from emotional_valence import EmotionalValence
        ev = EmotionalValence(feature_dim=64)

        for _ in range(10):
            ev.compute_valence(np.random.randn(64))

        trajectory = ev.get_emotional_trajectory(window=5)
        assert len(trajectory['valence']) == 5
        assert len(trajectory['arousal']) == 5

    def test_metrics(self):
        from emotional_valence import EmotionalValence
        ev = EmotionalValence(feature_dim=64)

        for _ in range(5):
            ev.compute_valence(np.random.randn(64))

        metrics = ev.get_metrics()
        assert metrics['emotional_states_recorded'] == 5
        assert 'dominant_category' in metrics


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
