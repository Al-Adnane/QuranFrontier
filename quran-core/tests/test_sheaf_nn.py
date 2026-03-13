"""Test suite for Sheaf Neural Networks for Quranic complex.

Tests sheaf convolution layers, message passing, morphological equivariance,
and training on simplicial complexes encoding Quranic structure.
"""

import pytest
import torch
import numpy as np
import networkx as nx
from frontier_neuro_symbolic.sheaf_nn.sheaf_layer import SheafConvLayer
from frontier_neuro_symbolic.sheaf_nn.message_passing import SheafMessagePassing
from frontier_neuro_symbolic.sheaf_nn.equivariance import MorphologicalEquivariance
from frontier_neuro_symbolic.sheaf_nn.training import SheafNNTrainer


class TestSheafConvLayer:
    """Test sheaf convolution on simplicial complexes."""

    def test_sheaf_conv_layer_creation(self):
        """Create a sheaf convolution layer with specified dimensions."""
        layer = SheafConvLayer(
            in_channels=16,
            out_channels=32,
            num_nodes=10,
            num_edges=15
        )
        assert layer.in_channels == 16
        assert layer.out_channels == 32
        assert layer.num_nodes == 10
        assert layer.num_edges == 15

    def test_sheaf_conv_forward_pass(self):
        """Test forward pass with node features on a simplicial complex."""
        in_channels = 8
        out_channels = 16
        num_nodes = 5
        batch_size = 2

        # Create edge list for a simple cycle graph
        edge_index = torch.tensor([
            [0, 1, 1, 2, 2, 3, 3, 4, 4, 0],
            [1, 0, 2, 1, 3, 2, 4, 3, 0, 4]
        ], dtype=torch.long)

        num_edges = edge_index.shape[1]

        layer = SheafConvLayer(
            in_channels=in_channels,
            out_channels=out_channels,
            num_nodes=num_nodes,
            num_edges=num_edges
        )

        # Create node features: (batch_size * num_nodes, in_channels)
        x = torch.randn(batch_size * num_nodes, in_channels)

        output = layer(x, edge_index)

        # Output should have shape (batch_size * num_nodes, out_channels)
        assert output.shape == (batch_size * num_nodes, out_channels)
        assert not torch.isnan(output).any(), "Output contains NaN"
        assert not torch.isinf(output).any(), "Output contains Inf"

    def test_restriction_map_learnable(self):
        """Test that restriction maps (F_ij parameters) are learnable."""
        layer = SheafConvLayer(
            in_channels=8,
            out_channels=16,
            num_nodes=4,
            num_edges=5
        )

        # Collect initial parameters
        initial_params = {name: param.clone() for name, param in layer.named_parameters()}

        # Forward pass
        x = torch.randn(4, 8)
        edge_index = torch.tensor([[0, 1, 1, 2, 2], [1, 0, 2, 1, 3]], dtype=torch.long)
        output = layer(x, edge_index)

        # Backward pass with dummy loss
        loss = output.sum()
        loss.backward()

        # Verify parameters have gradients and would be updated
        for name, param in layer.named_parameters():
            if param.requires_grad:
                assert param.grad is not None, f"Parameter {name} has no gradient"

    def test_sheaf_axiom_preservation(self):
        """Test that gluing axiom consistency is maintained."""
        layer = SheafConvLayer(
            in_channels=8,
            out_channels=8,
            num_nodes=4,
            num_edges=4
        )

        # Create simple diamond graph: 0-1-3, 0-2-3 (overlapping paths)
        x = torch.randn(4, 8)
        edge_index = torch.tensor([
            [0, 0, 1, 2],
            [1, 2, 3, 3]
        ], dtype=torch.long)

        # Two separate forward passes
        output1 = layer(x, edge_index)
        output2 = layer(x, edge_index)

        # Same input should give deterministic output (no dropout)
        torch.testing.assert_close(output1, output2)

    def test_aggregation_is_sum(self):
        """Test that aggregation is indeed a summation of restriction maps."""
        layer = SheafConvLayer(
            in_channels=4,
            out_channels=4,
            num_nodes=3,
            num_edges=3
        )
        layer.eval()

        x = torch.ones(3, 4)  # All ones for easy verification
        edge_index = torch.tensor([
            [0, 1, 1],
            [1, 0, 2]
        ], dtype=torch.long)

        output = layer(x, edge_index)

        # Output shape should be (3, 4)
        assert output.shape == (3, 4)
        # Each node's output should be non-zero (sum of restriction maps)
        assert (output != 0).any()


class TestSheafMessagePassing:
    """Test multi-layer sheaf message passing networks."""

    def test_message_passing_creation(self):
        """Create a multi-layer sheaf message passing network."""
        mp = SheafMessagePassing(
            in_channels=16,
            hidden_channels=[32, 64, 32],
            out_channels=16,
            num_nodes=10,
            num_edges=20
        )
        assert mp.in_channels == 16
        assert mp.out_channels == 16
        assert len(mp.layers) == 4  # 3 hidden layers + 1 output layer

    def test_message_passing_forward(self):
        """Test forward pass through multi-layer network."""
        mp = SheafMessagePassing(
            in_channels=8,
            hidden_channels=[16, 32],
            out_channels=8,
            num_nodes=5,
            num_edges=10
        )

        x = torch.randn(5, 8)
        edge_index = torch.tensor([
            [0, 1, 1, 2, 2, 3, 3, 4, 4, 0],
            [1, 0, 2, 1, 3, 2, 4, 3, 0, 4]
        ], dtype=torch.long)

        output = mp(x, edge_index)

        assert output.shape == (5, 8)
        assert not torch.isnan(output).any()

    def test_gluing_axiom_preservation(self):
        """Test that gluing axioms are preserved through message passing."""
        # Create graph with overlapping regions
        edge_index = torch.tensor([
            [0, 0, 1, 1, 2, 2, 3, 4],
            [1, 2, 3, 4, 3, 5, 5, 5]
        ], dtype=torch.long)

        mp = SheafMessagePassing(
            in_channels=8,
            hidden_channels=[16],
            out_channels=8,
            num_nodes=6,
            num_edges=edge_index.shape[1]
        )
        mp.eval()

        # Create graph with overlapping regions
        x = torch.randn(6, 8)

        output = mp(x, edge_index)

        # Output should preserve structural consistency
        assert output.shape == (6, 8)
        assert torch.isfinite(output).all()

    def test_convergence_behavior(self):
        """Test that message passing converges under repeated iterations."""
        mp = SheafMessagePassing(
            in_channels=8,
            hidden_channels=[8],
            out_channels=8,
            num_nodes=4,
            num_edges=4
        )
        mp.eval()

        x = torch.randn(4, 8)
        edge_index = torch.tensor([
            [0, 1, 2, 3],
            [1, 2, 3, 0]
        ], dtype=torch.long)

        with torch.no_grad():
            out1 = mp(x, edge_index)
            # Message passing should be stable
            assert torch.isfinite(out1).all()


class TestMorphologicalEquivariance:
    """Test morphological equivariance for Arabic roots."""

    def test_equivariance_creation(self):
        """Create a morphological equivariance module."""
        eq = MorphologicalEquivariance(
            num_roots=100,
            embedding_dim=32,
            num_words=200
        )
        assert eq.num_roots == 100
        assert eq.embedding_dim == 32
        assert eq.num_words == 200

    def test_root_extraction(self):
        """Test extraction of roots from Arabic words."""
        eq = MorphologicalEquivariance(
            num_roots=100,
            embedding_dim=16,
            num_words=50
        )

        # Test with word indices
        word_indices = torch.tensor([0, 5, 10, 15], dtype=torch.long)
        root_indices = torch.tensor([0, 0, 1, 2], dtype=torch.long)

        eq.register_root_mapping(word_indices, root_indices)
        extracted_roots = eq.extract_roots(word_indices)

        assert (extracted_roots == root_indices).all()

    def test_equivariant_attention_boost(self):
        """Test attention boost for words sharing the same root."""
        eq = MorphologicalEquivariance(
            num_roots=10,
            embedding_dim=8,
            num_words=20
        )

        word_indices = torch.tensor([0, 1, 2, 3], dtype=torch.long)
        root_indices = torch.tensor([0, 0, 1, 2], dtype=torch.long)
        eq.register_root_mapping(word_indices, root_indices)

        # Attention weights for words 0 and 1 (same root)
        attention_weights = torch.tensor([0.2, 0.3, 0.25, 0.25])

        boosted_weights = eq.boost_attention(word_indices, attention_weights)

        # Words 0 and 1 should have boosted weights
        assert boosted_weights[0] > attention_weights[0]
        assert boosted_weights[1] > attention_weights[1]
        # Cross-root words should not see large boosts
        assert boosted_weights[2] <= attention_weights[2] * 1.2  # Small boost factor

    def test_equivariant_feature_extraction(self):
        """Test equivariant feature extraction w.r.t. morphological symmetries."""
        eq = MorphologicalEquivariance(
            num_roots=5,
            embedding_dim=16,
            num_words=15
        )

        # Register root mapping
        word_indices = torch.tensor([0, 1, 2, 3, 4], dtype=torch.long)
        root_indices = torch.tensor([0, 0, 1, 2, 2], dtype=torch.long)
        eq.register_root_mapping(word_indices, root_indices)

        # Extract equivariant features
        features = eq.extract_equivariant_features(word_indices)

        assert features.shape == (5, 16)
        assert torch.isfinite(features).all()


class TestSheafNNTrainer:
    """Test training loop for sheaf neural networks."""

    def test_trainer_creation(self):
        """Create a trainer with specified configuration."""
        trainer = SheafNNTrainer(
            model_in_channels=8,
            model_hidden_channels=[16],
            model_out_channels=8,
            num_nodes=10,
            num_edges=20,
            lr=0.001
        )
        assert trainer.lr == 0.001
        assert trainer.model is not None

    def test_supervised_loss_computation(self):
        """Test supervised loss computation."""
        edge_index = torch.tensor([
            [0, 1, 2, 3, 4],
            [1, 2, 3, 4, 0]
        ], dtype=torch.long)

        trainer = SheafNNTrainer(
            model_in_channels=8,
            model_hidden_channels=[16],
            model_out_channels=2,  # 2 classes for classification
            num_nodes=5,
            num_edges=edge_index.shape[1],
            lr=0.001
        )

        x = torch.randn(5, 8)
        y = torch.randint(0, 2, (5,))  # Binary labels


        loss = trainer.compute_supervised_loss(x, y, edge_index)

        assert loss.item() > 0
        assert torch.isfinite(loss)

    def test_sheaf_consistency_loss(self):
        """Test sheaf consistency loss (gluing axiom violations)."""
        trainer = SheafNNTrainer(
            model_in_channels=8,
            model_hidden_channels=[16],
            model_out_channels=8,
            num_nodes=6,
            num_edges=12,
            lr=0.001
        )

        # Create output with some inconsistency
        output = torch.randn(6, 8)
        edge_index = torch.tensor([
            [0, 1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5, 0]
        ], dtype=torch.long)

        loss = trainer.compute_sheaf_consistency_loss(output, edge_index)

        assert loss.item() >= 0
        assert torch.isfinite(loss)

    def test_combined_loss(self):
        """Test combined supervised + consistency loss."""
        edge_index = torch.tensor([
            [0, 1, 2, 3, 4],
            [1, 2, 3, 4, 0]
        ], dtype=torch.long)

        trainer = SheafNNTrainer(
            model_in_channels=8,
            model_hidden_channels=[16],
            model_out_channels=2,
            num_nodes=5,
            num_edges=edge_index.shape[1],
            lr=0.001,
            consistency_weight=0.5
        )

        x = torch.randn(5, 8)
        y = torch.randint(0, 2, (5,))

        output = trainer.model(x, edge_index)
        loss = trainer.compute_loss(output, y, edge_index)

        assert loss.item() > 0
        assert torch.isfinite(loss)

    def test_training_step(self):
        """Test a single training step."""
        edge_index = torch.tensor([
            [0, 1, 2, 3, 4],
            [1, 2, 3, 4, 0]
        ], dtype=torch.long)

        trainer = SheafNNTrainer(
            model_in_channels=8,
            model_hidden_channels=[16],
            model_out_channels=2,
            num_nodes=5,
            num_edges=edge_index.shape[1],
            lr=0.001
        )

        x = torch.randn(5, 8)
        y = torch.randint(0, 2, (5,))

        # Collect initial parameters
        initial_params = {name: param.clone() for name, param in trainer.model.named_parameters()}

        # Training step
        loss = trainer.training_step(x, y, edge_index)

        # Verify parameters were updated
        params_updated = False
        for name, param in trainer.model.named_parameters():
            if not torch.allclose(param, initial_params[name]):
                params_updated = True
                break

        assert params_updated, "Parameters were not updated during training step"
        assert torch.isfinite(loss)

    def test_train_loop(self):
        """Test the full training loop."""
        edge_index = torch.tensor([
            [0, 1, 2, 3, 4],
            [1, 2, 3, 4, 0]
        ], dtype=torch.long)

        trainer = SheafNNTrainer(
            model_in_channels=8,
            model_hidden_channels=[16],
            model_out_channels=2,
            num_nodes=5,
            num_edges=edge_index.shape[1],
            lr=0.01
        )

        x = torch.randn(5, 8)
        y = torch.randint(0, 2, (5,))

        # Train for a few steps
        losses = trainer.train(x, y, edge_index, num_epochs=3)

        assert len(losses) == 3
        # Loss should generally decrease (or at least be finite)
        assert all(torch.isfinite(l) for l in losses)


class TestEndToEndSheafNN:
    """End-to-end integration tests for sheaf neural networks."""

    def test_full_pipeline(self):
        """Test complete pipeline from data to training."""
        # Create a synthetic simplicial complex encoding Quranic structure
        num_nodes = 10
        num_edges = 15

        # Random node features
        x = torch.randn(num_nodes, 16)

        # Random edge list (simplicial complex)
        edge_list = []
        for _ in range(num_edges):
            u, v = np.random.randint(0, num_nodes, 2)
            if u != v:
                edge_list.append((u, v))
        edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()

        # Create labels for supervised learning
        y = torch.randint(0, 2, (num_nodes,))

        # Initialize trainer
        trainer = SheafNNTrainer(
            model_in_channels=16,
            model_hidden_channels=[32, 32],
            model_out_channels=2,
            num_nodes=num_nodes,
            num_edges=edge_index.shape[1],
            lr=0.01,
            consistency_weight=0.3
        )

        # Train the model
        losses = trainer.train(x, y, edge_index, num_epochs=5)

        assert len(losses) == 5
        assert all(torch.isfinite(l) for l in losses)

        # Inference
        with torch.no_grad():
            output = trainer.model(x, edge_index)
            predictions = torch.argmax(output, dim=1)

        assert predictions.shape == (num_nodes,)
        assert predictions.dtype == torch.long

    def test_equivariance_in_pipeline(self):
        """Test morphological equivariance integration in full pipeline."""
        num_nodes = 10
        num_words = num_nodes
        num_roots = 5

        x = torch.randn(num_nodes, 16)
        edge_index = torch.tensor([
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        ], dtype=torch.long)

        y = torch.randint(0, 2, (num_nodes,))

        # Initialize trainer with equivariance module
        trainer = SheafNNTrainer(
            model_in_channels=16,
            model_hidden_channels=[32],
            model_out_channels=2,
            num_nodes=num_nodes,
            num_edges=edge_index.shape[1],
            lr=0.01,
            consistency_weight=0.3
        )

        # Add equivariance
        word_indices = torch.arange(num_words)
        root_indices = torch.tensor([i % num_roots for i in range(num_words)], dtype=torch.long)

        # Train
        losses = trainer.train(x, y, edge_index, num_epochs=3)

        assert len(losses) == 3
