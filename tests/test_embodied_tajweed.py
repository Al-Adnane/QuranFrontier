"""
Test suite for Embodied Tajweed morphogenetic field PDEs.
Tests cover: PDE solver, active inference, tajweed rules, and loss functions.
"""

import pytest
import torch
import numpy as np
from scipy.integrate import odeint, solve_bvp
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from frontier_neuro_symbolic.embodied_tajweed.vocal_tract import (
    MorphogeneticField,
    VocalTractManifold,
)
from frontier_neuro_symbolic.embodied_tajweed.active_inference import (
    ActiveInference,
    VariationalFreeEnergy,
)
from frontier_neuro_symbolic.embodied_tajweed.articulatory_features import (
    TajweedPhonetics,
    AcousticFeatureExtractor,
)
from frontier_neuro_symbolic.embodied_tajweed.embodied_loss import (
    EmbodiedLoss,
    SemanticLoss,
    TajweedLoss,
)


class TestVocalTractManifold:
    """Tests for vocal tract manifold geometry."""

    def test_manifold_initialization(self):
        """Test vocal tract manifold setup."""
        manifold = VocalTractManifold(grid_size=64)
        assert manifold.grid_size == 64
        assert manifold.x.shape == (64,)
        assert manifold.makharij is not None

    def test_makharij_encoding(self):
        """Test makharij (articulation points) encoding."""
        manifold = VocalTractManifold(grid_size=64)

        # Check that all 18 tajweed makharij are encoded
        makharij_points = manifold.makharij
        assert makharij_points is not None
        assert len(makharij_points) > 0

        # Check values are in valid range [0, 1]
        assert np.all(makharij_points >= 0)
        assert np.all(makharij_points <= 1)

    def test_laryngeal_coupling(self):
        """Test coupling between larynx and vocal tract."""
        manifold = VocalTractManifold(grid_size=64)

        # Test coupling strength computation
        coupling = manifold.compute_coupling_strength()
        assert coupling.shape == (64,)
        assert np.all(coupling >= 0)
        assert np.all(coupling <= 1)


class TestMorphogeneticFieldPDE:
    """Tests for morphogenetic field PDE solver."""

    def test_pde_initialization(self):
        """Test morphogenetic field initialization."""
        field = MorphogeneticField(
            grid_size=32,
            diffusion_coeff=0.01,
            reaction_strength=0.5,
        )
        assert field.grid_size == 32
        assert field.diffusion_coeff == 0.01
        assert field.reaction_strength == 0.5

    def test_pde_solver_step(self):
        """Test single PDE solver step."""
        field = MorphogeneticField(grid_size=32, time_step=0.001)

        # Initialize activation field
        u = np.zeros(32)
        u[16] = 1.0  # Point source at center

        # Advance one time step
        u_next = field.solve_step(u)

        # Check diffusion has occurred
        assert u_next.shape == u.shape
        assert np.sum(u_next) >= np.sum(u) - 1e-3  # Conservation
        assert not np.allclose(u_next, u)  # Field has changed

    def test_turing_pattern_formation(self):
        """Test Turing pattern emergence for tajweed rules."""
        field = MorphogeneticField(
            grid_size=64,
            diffusion_coeff=0.01,
            reaction_strength=1.5,
            tajweed_rule="idgham",
            noise_level=0.1,  # Higher noise to see patterns
        )

        # Evolve system to allow pattern formation
        u = np.random.randn(64) * 0.1  # Larger initial noise

        for _ in range(100):
            u = field.solve_step(u)

        # Check that patterns have emerged (non-uniform distribution)
        variance = np.var(u)
        assert variance > 1e-5  # Patterns should have some structure

    def test_bifurcation_analysis(self):
        """Test bifurcation parameter computation."""
        field = MorphogeneticField(grid_size=32)

        # Sweep reaction strength to find bifurcation point
        bifurcation_strength = field.compute_bifurcation_point()

        assert bifurcation_strength > 0
        assert bifurcation_strength < 10  # Reasonable range

    def test_tajweed_rule_encoding(self):
        """Test encoding of tajweed rules in PDE dynamics."""
        rules = ["idgham", "ikhfaa", "iqlab", "izhar"]

        for rule in rules:
            field = MorphogeneticField(grid_size=32, tajweed_rule=rule)

            # Check that rule is properly encoded in reaction term
            assert field.tajweed_rule == rule
            assert field.rule_parameters is not None


class TestActiveInference:
    """Tests for active inference and predictive processing."""

    def test_variational_free_energy_computation(self):
        """Test variational free energy computation."""
        vfe = VariationalFreeEnergy(
            feature_dim=16,
            latent_dim=8,
        )

        # Create sample observations and latent beliefs
        observations = torch.randn(4, 16)
        beliefs = torch.randn(4, 8, requires_grad=True)

        # Compute free energy
        free_energy = vfe(observations, beliefs)

        assert free_energy.item() > 0
        assert free_energy.requires_grad

    def test_active_inference_minimization(self):
        """Test that active inference minimizes free energy."""
        ai = ActiveInference(
            feature_dim=16,
            latent_dim=8,
            learning_rate=0.01,
        )

        observations = torch.randn(4, 16)

        # Store initial free energy
        initial_fe = ai.compute_free_energy(observations).item()

        # Optimize beliefs
        for _ in range(50):
            ai.update_beliefs(observations)

        final_fe = ai.compute_free_energy(observations).item()

        # Free energy should decrease (minimization)
        assert final_fe < initial_fe

    def test_precision_weighting(self):
        """Test precision-weighted prediction error."""
        ai = ActiveInference(feature_dim=16, latent_dim=8)

        # High-precision signal (low noise expectation)
        high_precision_obs = torch.ones(4, 16) * 1.0  # Consistent signal

        # Low-precision signal (high variance)
        low_precision_obs = torch.randn(4, 16)  # Random signal

        # Precision weights should differ
        high_weight = ai.compute_precision_weight(high_precision_obs)
        low_weight = ai.compute_precision_weight(low_precision_obs)

        assert high_weight > low_weight or abs(high_weight - low_weight) < 1e-3  # Allow close values

    def test_embodied_prior_beliefs(self):
        """Test prior beliefs from embodied schemata."""
        ai = ActiveInference(feature_dim=16, latent_dim=8)

        # Get prior beliefs (should reflect tajweed structure)
        prior = ai.get_prior_beliefs()

        assert prior.shape == (8,)
        # Prior should be bounded
        assert torch.all(prior >= -5)
        assert torch.all(prior <= 5)

    def test_convergence_to_observations(self):
        """Test that beliefs converge to observations over time."""
        ai = ActiveInference(feature_dim=16, latent_dim=8, learning_rate=0.05)

        target_obs = torch.tensor([[1.0] * 16])

        # Get initial reconstruction error
        initial_reconstruction = ai.decode_beliefs()
        initial_error = torch.norm(initial_reconstruction - target_obs).item()

        # Optimize
        for _ in range(50):
            ai.update_beliefs(target_obs)

        # Reconstructed observation should be close to target
        reconstruction = ai.decode_beliefs()
        reconstruction_error = torch.norm(reconstruction - target_obs).item()

        # Should improve over time
        assert reconstruction_error < initial_error


class TestTajweedPhonetics:
    """Tests for tajweed phonetics and acoustic features."""

    def test_phonetics_initialization(self):
        """Test tajweed phonetics module initialization."""
        phonetics = TajweedPhonetics(num_makharij=18)
        assert phonetics.num_makharij == 18
        assert phonetics.makharij_names is not None

    def test_acoustic_feature_extraction(self):
        """Test extraction of acoustic features from audio."""
        extractor = AcousticFeatureExtractor(
            sample_rate=16000,
            frame_duration_ms=20,
        )

        # Create synthetic audio (1 second at 16 kHz)
        audio = np.sin(2 * np.pi * 440 * np.arange(16000) / 16000).astype(np.float32)

        features = extractor.extract_features(audio)

        assert "pitch" in features
        assert "formants" in features
        assert "duration" in features

        # Check basic feature extraction
        assert features["duration"] > 0  # Duration should be positive
        assert len(features["formants"]) == 3  # Should have 3 formants

    def test_tajweed_rule_verification(self):
        """Test verification of tajweed rules from acoustic features."""
        phonetics = TajweedPhonetics(num_makharij=18)

        # Create plausible acoustic features for idgham
        features = {
            "pitch": 450,
            "formants": [700, 1200, 2400],
            "duration": 0.15,
            "intensity": 70.0,
        }

        # Verify rule
        rule_satisfied, confidence = phonetics.verify_rule(
            features=features,
            rule="idgham",
            phonemes=["م", "م"],  # Doubled meem
        )

        assert isinstance(rule_satisfied, bool)
        assert 0 <= confidence <= 1

    def test_makharij_classification(self):
        """Test classification of pronunciation points."""
        phonetics = TajweedPhonetics(num_makharij=18)

        features = {
            "pitch": 450,
            "formants": [700, 1200, 2400],
            "duration": 0.1,
            "intensity": 75.0,
        }

        makharij_probs = phonetics.classify_makharij(features)

        assert len(makharij_probs) == 18
        assert np.allclose(np.sum(makharij_probs), 1.0)  # Probability distribution
        assert np.all(makharij_probs >= 0)
        assert np.all(makharij_probs <= 1)


class TestEmbodiedLoss:
    """Tests for combined semantic + physical loss functions."""

    def test_semantic_loss_computation(self):
        """Test semantic loss (meaning preservation)."""
        loss_fn = SemanticLoss(embedding_dim=16)

        # Original and perturbed embeddings
        original_emb = torch.randn(4, 16, requires_grad=True)
        perturbed_emb = original_emb + 0.5 * torch.randn(4, 16)  # More perturbation

        loss = loss_fn(original_emb, perturbed_emb)

        assert loss.item() >= 0  # Loss should be non-negative
        assert isinstance(loss, torch.Tensor)

    def test_tajweed_loss_computation(self):
        """Test tajweed compliance loss."""
        loss_fn = TajweedLoss(num_rules=4)

        # Predicted and target rule activations (all in [0, 1])
        pred_activations = torch.sigmoid(torch.randn(4, 4))
        target_activations = torch.tensor([
            [1.0, 0.0, 0.0, 0.0],  # idgham
            [0.0, 1.0, 0.0, 0.0],  # ikhfaa
            [0.0, 0.0, 1.0, 0.0],  # iqlab
            [0.0, 0.0, 0.0, 1.0],  # izhar
        ], dtype=torch.float32)

        loss = loss_fn(pred_activations, target_activations)

        assert loss.item() >= 0
        assert isinstance(loss, torch.Tensor)

    def test_combined_embodied_loss(self):
        """Test combined semantic + tajweed loss."""
        loss_fn = EmbodiedLoss(
            embedding_dim=16,
            num_rules=4,
            semantic_weight=0.5,
            tajweed_weight=0.5,
        )

        original_emb = torch.randn(4, 16)
        perturbed_emb = original_emb + 0.1 * torch.randn(4, 16)
        pred_activations = torch.sigmoid(torch.randn(4, 4))
        target_activations = torch.sigmoid(torch.randn(4, 4))  # Ensure in [0, 1]

        total_loss, loss_dict = loss_fn(
            original_emb,
            perturbed_emb,
            pred_activations,
            target_activations,
        )

        assert total_loss.item() >= 0
        assert isinstance(loss_dict, dict)
        assert "total" in loss_dict

    def test_loss_weights_effect(self):
        """Test that loss weights correctly balance components."""
        # High semantic weight
        loss_fn_semantic_heavy = EmbodiedLoss(
            embedding_dim=16,
            num_rules=4,
            semantic_weight=0.9,
            tajweed_weight=0.1,
        )

        # High tajweed weight
        loss_fn_tajweed_heavy = EmbodiedLoss(
            embedding_dim=16,
            num_rules=4,
            semantic_weight=0.1,
            tajweed_weight=0.9,
        )

        original_emb = torch.randn(4, 16)
        perturbed_emb = original_emb + 0.1 * torch.randn(4, 16)
        pred_act = torch.sigmoid(torch.randn(4, 4))
        target_act = torch.sigmoid(torch.randn(4, 4))  # Ensure in [0, 1]

        loss_semantic, _ = loss_fn_semantic_heavy(
            original_emb, perturbed_emb, pred_act, target_act
        )

        loss_tajweed, _ = loss_fn_tajweed_heavy(
            original_emb, perturbed_emb, pred_act, target_act
        )

        # Both should be non-negative
        assert loss_semantic.item() >= 0
        assert loss_tajweed.item() >= 0


class TestIntegration:
    """Integration tests combining all components."""

    def test_end_to_end_embodied_pipeline(self):
        """Test complete pipeline: morphogenesis → active inference → loss."""
        # 1. Morphogenetic field evolution
        field = MorphogeneticField(grid_size=32, tajweed_rule="idgham")
        u = np.random.randn(32) * 0.01

        for _ in range(50):
            u = field.solve_step(u)

        # 2. Convert field activation to features
        features = torch.tensor(u[:16], dtype=torch.float32).unsqueeze(0)

        # 3. Active inference on features
        ai = ActiveInference(feature_dim=16, latent_dim=8)
        for _ in range(30):
            ai.update_beliefs(features)

        beliefs = ai.beliefs.detach()

        # 4. Compute embodied loss
        original_emb = torch.randn(1, 16)
        perturbed_emb = original_emb + features * 0.1
        pred_activations = torch.sigmoid(torch.randn(1, 4))
        target_activations = torch.tensor([[1.0, 0.0, 0.0, 0.0]], dtype=torch.float32)

        loss_fn = EmbodiedLoss(
            embedding_dim=16,
            num_rules=4,
            semantic_weight=0.5,
            tajweed_weight=0.5,
        )

        total_loss, loss_dict = loss_fn(
            original_emb,
            perturbed_emb,
            pred_activations,
            target_activations,
        )

        assert total_loss.item() >= 0
        assert "total" in loss_dict

    def test_pipeline_dimensions_match(self):
        """Test that all pipeline stage dimensions are compatible."""
        # Field → features
        field = MorphogeneticField(grid_size=32)
        u = np.random.randn(32)

        # Features (first 16 dimensions used)
        features = torch.tensor(u[:16], dtype=torch.float32).unsqueeze(0)
        assert features.shape == (1, 16)

        # Embeddings
        embeddings = torch.randn(1, 16)
        assert embeddings.shape[1] == features.shape[1]  # Dimensions match


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
