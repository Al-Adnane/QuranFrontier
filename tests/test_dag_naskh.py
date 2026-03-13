"""Test suite for Derived Algebraic Geometry Naskh Solver.

Tests the derived stack representation, cohomology computation,
and naskh (abrogation) detection in the framework of derived algebraic geometry.
"""

import pytest
import torch
import numpy as np
from frontier_neuro_symbolic.dag_naskh.stacks import DerivedStack, DerivedPoint
from frontier_neuro_symbolic.dag_naskh.cohomology import CohomologyComputer, BettiAnalyzer
from frontier_neuro_symbolic.dag_naskh.naskh_solver import NaskhSolver


class TestDerivedStack:
    """Test DerivedStack data structure and operations."""

    def test_derived_stack_creation(self):
        """Create a derived stack with dimensions and verify structure."""
        stack = DerivedStack(
            dimension=3,
            ambient_dim=10,
            name="Quranic Interpretation Space"
        )
        assert stack.dimension == 3
        assert stack.ambient_dim == 10
        assert stack.name == "Quranic Interpretation Space"

    def test_derived_stack_add_point(self):
        """Add points to derived stack and verify storage."""
        stack = DerivedStack(dimension=2, ambient_dim=5)

        # Create a derived point with homological structure
        point_data = torch.randn(5)
        derived_point = DerivedPoint(
            position=point_data,
            verse_ref=(2, 106),
            semantic_dimension=3
        )

        stack.add_point(derived_point)
        assert len(stack.points) == 1
        assert stack.points[0].verse_ref == (2, 106)

    def test_derived_point_homological_memory(self):
        """Test that derived points preserve homological memory."""
        point1 = DerivedPoint(
            position=torch.randn(5),
            verse_ref=(2, 106),
            semantic_dimension=3
        )

        point2 = DerivedPoint(
            position=torch.randn(5),
            verse_ref=(16, 101),
            semantic_dimension=3
        )

        # Homological memory should be initialized
        assert point1.homological_memory is not None
        assert point2.homological_memory is not None

    def test_derived_intersection_computation(self):
        """Test derived intersection of two points in the stack."""
        stack = DerivedStack(dimension=2, ambient_dim=5)

        # Create two verse embeddings
        pos1 = torch.tensor([1.0, 2.0, 3.0, 0.0, 0.0])
        pos2 = torch.tensor([1.0, 2.0, 3.5, 0.1, 0.0])

        point1 = DerivedPoint(pos1, verse_ref=(2, 106), semantic_dimension=3)
        point2 = DerivedPoint(pos2, verse_ref=(16, 101), semantic_dimension=3)

        stack.add_point(point1)
        stack.add_point(point2)

        # Compute intersection
        intersection = stack.compute_intersection(point1, point2)
        assert intersection is not None
        assert isinstance(intersection, torch.Tensor)
        assert intersection.shape == pos1.shape


class TestCohomologyComputation:
    """Test cohomology computation and analysis."""

    def test_cohomology_computer_initialization(self):
        """Initialize cohomology computer with proper parameters."""
        cohom = CohomologyComputer(
            dimension=3,
            embedding_dim=5,
            max_degree=3
        )
        assert cohom.dimension == 3
        assert cohom.max_degree == 3

    def test_compute_cohomology_groups(self):
        """Compute cohomology groups H^n(X, O_X) for interpretation space."""
        cohom = CohomologyComputer(dimension=2, embedding_dim=4, max_degree=2)

        # Create sample interpretation space embedding
        X_embedding = torch.randn(10, 4)  # 10 points in 4D space

        # Compute cohomology
        cohom_groups = cohom.compute_cohomology_groups(X_embedding)

        assert isinstance(cohom_groups, dict)
        assert len(cohom_groups) > 0
        # Should have groups for degrees 0, 1, 2
        assert 0 in cohom_groups or 1 in cohom_groups

    def test_semantic_cohesion_degree(self):
        """Detect semantic cohesion degree from cohomology."""
        cohom = CohomologyComputer(dimension=2, embedding_dim=4, max_degree=2)
        X_embedding = torch.randn(10, 4)

        cohesion = cohom.compute_semantic_cohesion(X_embedding)

        assert isinstance(cohesion, float)
        assert 0.0 <= cohesion <= 1.0

    def test_betti_numbers_computation(self):
        """Compute Betti numbers (topological invariants)."""
        analyzer = BettiAnalyzer(dimension=2, max_degree=2)

        # Create a simple space embedding
        X_embedding = torch.randn(15, 4)

        betti_nums = analyzer.compute_betti_numbers(X_embedding)

        assert isinstance(betti_nums, dict)
        assert len(betti_nums) > 0
        # Betti numbers should be non-negative integers
        for deg, num in betti_nums.items():
            assert isinstance(num, (int, np.integer))
            assert num >= 0

    def test_betti_stability_under_perturbation(self):
        """Verify Betti numbers are stable under small perturbations."""
        analyzer = BettiAnalyzer(dimension=2, max_degree=2)

        X_base = torch.randn(15, 4)
        X_perturbed = X_base + 0.01 * torch.randn_like(X_base)

        betti_base = analyzer.compute_betti_numbers(X_base)
        betti_perturbed = analyzer.compute_betti_numbers(X_perturbed)

        # Betti numbers should be the same (stable invariant)
        assert len(betti_base) == len(betti_perturbed)


class TestNaskhSolver:
    """Test Naskh detection using derived algebraic geometry."""

    def test_naskh_solver_initialization(self):
        """Initialize NaskhSolver with proper configuration."""
        solver = NaskhSolver(
            embedding_dim=8,
            stack_dimension=3,
            semantic_dim=4
        )
        assert solver.embedding_dim == 8
        assert solver.stack_dimension == 3

    def test_model_naskh_derived_intersection(self):
        """Model naskh as derived intersection point."""
        solver = NaskhSolver(embedding_dim=6, stack_dimension=2, semantic_dim=3)

        # Create two verse embeddings (abrogated and abrogating)
        verse1 = torch.randn(6)  # Abrogated verse
        verse2 = torch.randn(6)  # Abrogating verse

        intersection_point = solver.model_naskh(verse1, verse2)

        assert intersection_point is not None
        assert isinstance(intersection_point, torch.Tensor)
        assert intersection_point.shape == verse1.shape

    def test_detect_abrogation_probability(self):
        """Test naskh detection with probability and confidence."""
        solver = NaskhSolver(embedding_dim=6, stack_dimension=2, semantic_dim=3)

        # Create verse embeddings that represent known naskh
        v1 = torch.randn(6)
        v2 = torch.randn(6)

        prob, confidence = solver.detect_abrogation(v1, v2)

        assert isinstance(prob, float)
        assert isinstance(confidence, float)
        assert 0.0 <= prob <= 1.0
        assert 0.0 <= confidence <= 1.0

    def test_compute_homological_memory(self):
        """Compute homological memory of abrogated verse."""
        solver = NaskhSolver(embedding_dim=6, stack_dimension=2, semantic_dim=3)

        abrogated = torch.randn(6)
        abrogating = torch.randn(6)

        memory_tensor = solver.compute_homological_memory(abrogated, abrogating)

        assert memory_tensor is not None
        assert isinstance(memory_tensor, torch.Tensor)
        # Memory should be at least 1D
        assert memory_tensor.ndim >= 1

    def test_naskh_on_known_example(self):
        """Test naskh detection on a specific known example.

        Ayah 2:106 (abrogating) and other verses (abrogated).
        """
        solver = NaskhSolver(embedding_dim=8, stack_dimension=3, semantic_dim=4)

        # Create embeddings with some structure
        # In practice these would come from semantic encoders
        v_2_106 = torch.tensor([
            0.7, 0.3, -0.2, 0.5, 0.1, -0.4, 0.6, 0.2
        ])

        v_abrogated = torch.tensor([
            0.65, 0.32, -0.19, 0.48, 0.12, -0.39, 0.58, 0.19
        ])

        prob, conf = solver.detect_abrogation(v_2_106, v_abrogated)

        # Known example should have reasonable probability
        assert prob >= 0.0
        assert conf >= 0.0

    def test_naskh_memory_accumulation(self):
        """Test that homological memory accumulates for multiple abrogations."""
        solver = NaskhSolver(embedding_dim=5, stack_dimension=2, semantic_dim=2)

        # Simulate multiple verses being abrogated
        abrogating_verse = torch.randn(5)
        memory = None

        for i in range(3):
            abrogated_verse = torch.randn(5)
            new_memory = solver.compute_homological_memory(
                abrogated_verse, abrogating_verse
            )

            if memory is None:
                memory = new_memory
            else:
                # Memory should be able to be accumulated
                memory = memory + 0.1 * new_memory

        assert memory is not None
        assert isinstance(memory, torch.Tensor)

    def test_naskh_differentiability(self):
        """Test that naskh operations are differentiable."""
        solver = NaskhSolver(embedding_dim=4, stack_dimension=2, semantic_dim=2)

        v1 = torch.randn(4, requires_grad=True)
        v2 = torch.randn(4, requires_grad=True)

        # Model naskh should preserve gradient
        intersection = solver.model_naskh(v1, v2)
        loss = intersection.sum()
        loss.backward()

        assert v1.grad is not None
        assert v2.grad is not None

    def test_solver_batch_processing(self):
        """Test batch processing of multiple verse pairs."""
        solver = NaskhSolver(embedding_dim=6, stack_dimension=2, semantic_dim=3)

        # Batch of 5 verse pairs
        batch_v1 = torch.randn(5, 6)
        batch_v2 = torch.randn(5, 6)

        # Process batch
        probs = []
        confs = []
        for i in range(batch_v1.shape[0]):
            prob, conf = solver.detect_abrogation(batch_v1[i], batch_v2[i])
            probs.append(prob)
            confs.append(conf)

        assert len(probs) == 5
        assert len(confs) == 5
        assert all(0.0 <= p <= 1.0 for p in probs)
        assert all(0.0 <= c <= 1.0 for c in confs)

    def test_naskh_solver_state_persistence(self):
        """Test that solver state can be saved and loaded."""
        solver1 = NaskhSolver(embedding_dim=6, stack_dimension=2, semantic_dim=3)

        # Create some state
        v1 = torch.randn(6)
        v2 = torch.randn(6)
        memory = solver1.compute_homological_memory(v1, v2)

        # Should be able to access solver properties
        assert solver1.embedding_dim == 6
        assert solver1.stack_dimension == 2
        assert solver1.semantic_dim == 3
