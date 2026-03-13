"""Three-World Neuro-Symbolic-Categorical Architecture Tests.

Tests for the neural layer, symbolic layer, categorical layer, and fusion mechanism.
"""

import pytest
import torch
import numpy as np
from frontier_neuro_symbolic.three_world.neural_layer import NeuralLayer
from frontier_neuro_symbolic.three_world.symbolic_layer import SymbolicLayer
from frontier_neuro_symbolic.three_world.categorical_layer import CategoricalLayer
from frontier_neuro_symbolic.three_world.fusion import ThreeWorldArchitecture


class TestNeuralLayer:
    """Tests for the neural embedding layer."""

    @pytest.fixture
    def neural_layer(self):
        """Initialize a NeuralLayer with default parameters."""
        return NeuralLayer(
            vocab_size=1000,
            embedding_dim=128,
            num_heads=4,
            num_layers=2,
            max_seq_len=512,
        )

    def test_neural_initialization(self, neural_layer):
        """Test that NeuralLayer initializes with correct dimensions."""
        assert neural_layer.vocab_size == 1000
        assert neural_layer.embedding_dim == 128
        assert neural_layer.num_heads == 4
        assert neural_layer.num_layers == 2

    def test_tokenization_arabic(self, neural_layer):
        """Test Arabic text tokenization with BPE."""
        arabic_text = "بسم الله الرحمن الرحيم"
        tokens = neural_layer.tokenize(arabic_text)
        assert isinstance(tokens, torch.Tensor)
        assert tokens.dim() == 2  # Batch dimension added by tokenize
        assert tokens.shape[0] == 1  # Batch size of 1
        assert tokens.shape[1] > 0
        assert tokens.max().item() < neural_layer.vocab_size

    def test_position_embeddings(self, neural_layer):
        """Test position embedding generation."""
        seq_len = 10
        pos_emb = neural_layer.get_position_embeddings(seq_len)
        assert pos_emb.shape == (1, seq_len, neural_layer.embedding_dim)
        # Check different positions have different embeddings
        assert not torch.allclose(pos_emb[0, 0], pos_emb[0, 1])

    def test_embedding_forward_pass(self, neural_layer):
        """Test embedding layer forward pass."""
        batch_size = 2
        seq_len = 10
        token_ids = torch.randint(0, 1000, (batch_size, seq_len))
        embeddings = neural_layer.embed(token_ids)
        assert embeddings.shape == (batch_size, seq_len, neural_layer.embedding_dim)

    def test_attention_forward_pass(self, neural_layer):
        """Test multi-head self-attention forward pass."""
        batch_size = 2
        seq_len = 10
        hidden = torch.randn(batch_size, seq_len, neural_layer.embedding_dim)
        attended = neural_layer.attention(hidden)
        assert attended.shape == (batch_size, seq_len, neural_layer.embedding_dim)

    def test_full_encoder_forward_pass(self, neural_layer):
        """Test full encoder forward pass."""
        batch_size = 2
        seq_len = 10
        token_ids = torch.randint(0, 1000, (batch_size, seq_len))
        embeddings = neural_layer(token_ids)
        assert embeddings.shape == (batch_size, seq_len, neural_layer.embedding_dim)

    def test_embedding_arabic_verse(self, neural_layer):
        """Test embedding a Quranic verse."""
        verse = "الحمد لله رب العالمين"
        embeddings = neural_layer.encode_verse(verse)
        assert embeddings.dim() == 2
        assert embeddings.shape[1] == neural_layer.embedding_dim
        assert not torch.isnan(embeddings).any()


class TestSymbolicLayer:
    """Tests for the symbolic logic layer."""

    @pytest.fixture
    def symbolic_layer(self):
        """Initialize a SymbolicLayer."""
        return SymbolicLayer(solver="z3")

    def test_symbolic_initialization(self, symbolic_layer):
        """Test SymbolicLayer initializes correctly."""
        assert symbolic_layer.solver_name == "z3"
        assert symbolic_layer.context is not None

    def test_deontic_logic_primitives(self, symbolic_layer):
        """Test deontic logic primitives."""
        # Test obligatory
        obligatory = symbolic_layer.deontic.obligatory("wajib_statement")
        assert obligatory is not None

        # Test forbidden
        forbidden = symbolic_layer.deontic.forbidden("haram_statement")
        assert forbidden is not None

        # Test permissible
        permissible = symbolic_layer.deontic.permissible("mubah_statement")
        assert permissible is not None

    def test_constraint_satisfaction(self, symbolic_layer):
        """Test basic constraint satisfaction with Z3."""
        # Simple constraint: x > 0 and x < 10
        constraint = symbolic_layer.create_constraint("x > 0 and x < 10")
        assert constraint is not None

    def test_temporal_logic_naskh(self, symbolic_layer):
        """Test temporal logic for naskh (abrogation) ordering."""
        # Verse 1 revealed first, verse 2 revealed later
        order = symbolic_layer.temporal_order([
            ("verse_1", 50),  # revealed at time 50
            ("verse_2", 100),  # revealed at time 100
        ])
        assert order is not None
        assert len(order) == 2

    def test_abrogation_logic(self, symbolic_layer):
        """Test abrogation relationships."""
        # Verse 2 abrogates verse 1 if verse 2 is revealed later
        abrogates = symbolic_layer.check_abrogation("verse_1", "verse_2", time_1=50, time_2=100)
        assert isinstance(abrogates, bool)

    def test_symbolic_consistency_check(self, symbolic_layer):
        """Test consistency checking."""
        constraints = [
            "x > 0",
            "x < 10",
            "x > 5",
        ]
        is_consistent = symbolic_layer.is_consistent(constraints)
        assert isinstance(is_consistent, bool)
        assert is_consistent is True

    def test_symbolic_rule_derivation(self, symbolic_layer):
        """Test rule derivation from constraints."""
        premises = ["if (halal) then permitted"]
        conclusion = symbolic_layer.derive_conclusion(premises, "permitted")
        assert conclusion is not None


class TestCategoricalLayer:
    """Tests for the categorical/∞-topos verification layer."""

    @pytest.fixture
    def categorical_layer(self):
        """Initialize a CategoricalLayer."""
        return CategoricalLayer()

    def test_categorical_initialization(self, categorical_layer):
        """Test CategoricalLayer initializes correctly."""
        assert categorical_layer.sheaves is not None
        assert categorical_layer.heyting_algebra is not None

    def test_sheaf_semantics(self, categorical_layer):
        """Test sheaf semantics for interpretation spaces."""
        # Create a simple sheaf over a space
        space = {"point_a", "point_b", "point_c"}
        sheaf = categorical_layer.create_sheaf(space)
        assert sheaf is not None

    def test_heyting_algebra_truth_values(self, categorical_layer):
        """Test Heyting algebra intuitionistic truth values."""
        # In Heyting algebra, truth values are more nuanced than classical
        true_val = categorical_layer.heyting_true()
        false_val = categorical_layer.heyting_false()
        partial_val = categorical_layer.heyting_partial(0.7)

        assert true_val is not None
        assert false_val is not None
        assert partial_val is not None

    def test_heyting_negation(self, categorical_layer):
        """Test intuitionistic negation in Heyting algebra."""
        truth_val = 0.8
        neg_truth = categorical_layer.heyting_negation(truth_val)
        assert 0 <= neg_truth <= 1
        # In intuitionistic logic, ¬¬P ≠ P in general
        double_neg = categorical_layer.heyting_negation(neg_truth)
        assert double_neg != truth_val or truth_val in [0, 1]

    def test_interpretation_space_consistency(self, categorical_layer):
        """Test consistency within interpretation spaces."""
        interpretation = {
            "statement_1": 0.9,
            "statement_2": 0.7,
        }
        is_consistent = categorical_layer.check_interpretation_consistency(interpretation)
        assert isinstance(is_consistent, bool)

    def test_topos_verification(self, categorical_layer):
        """Test ∞-topos verification."""
        # Create a simple categorical statement
        statement = {"type": "obligation", "subject": "believer", "content": "wajib"}
        verification = categorical_layer.verify_topos_statement(statement)
        assert verification is not None

    def test_sheaf_restriction(self, categorical_layer):
        """Test sheaf restriction to open sets."""
        sheaf = categorical_layer.create_sheaf({"a", "b", "c"})
        subset = {"a", "b"}
        restricted = categorical_layer.restrict_sheaf(sheaf, subset)
        assert restricted is not None


class TestFusionArchitecture:
    """Tests for the three-world fusion mechanism."""

    @pytest.fixture
    def three_world(self):
        """Initialize complete three-world architecture."""
        return ThreeWorldArchitecture(
            vocab_size=1000,
            embedding_dim=128,
            num_heads=4,
            num_layers=2,
        )

    def test_three_world_initialization(self, three_world):
        """Test complete initialization."""
        assert three_world.neural_layer is not None
        assert three_world.symbolic_layer is not None
        assert three_world.categorical_layer is not None
        assert three_world.fusion_gate is not None

    def test_neural_to_symbolic_pipeline(self, three_world):
        """Test neural embeddings → symbolic constraints."""
        arabic_text = "الحمد لله رب العالمين"
        neural_output = three_world.neural_layer.encode_verse(arabic_text)
        assert neural_output.shape[1] == 128

    def test_symbolic_to_categorical_pipeline(self, three_world):
        """Test symbolic constraints → categorical verification."""
        constraints = ["x > 0", "x < 10"]
        is_consistent = three_world.symbolic_layer.is_consistent(constraints)
        assert isinstance(is_consistent, bool)

    def test_full_three_world_pipeline(self, three_world):
        """Test complete pipeline: neural → symbolic → categorical."""
        verse = "بسم الله الرحمن الرحيم"
        context = {"topic": "basmala", "interpretation": "opening"}

        # Neural phase: embed the verse
        neural_embedding = three_world.encode_verse(verse)
        assert neural_embedding is not None

        # Symbolic phase: check logical consistency
        symbolic_check = three_world.check_symbolic_consistency(
            verse, context
        )
        assert symbolic_check is not None

        # Categorical phase: verify interpretation
        categorical_verification = three_world.verify_categorical_interpretation(
            neural_embedding, context
        )
        assert categorical_verification is not None

    def test_feedback_loop(self, three_world):
        """Test feedback from symbolic violations to neural layer."""
        verse = "الحمد لله"
        violations = ["inconsistency_type_1"]

        # Apply feedback
        updated_embedding = three_world.apply_feedback(verse, violations)
        assert updated_embedding is not None

    def test_fusion_gate_weights_learning(self, three_world):
        """Test that fusion gate weights can be updated."""
        initial_weights = three_world.get_fusion_weights()
        # Simulate weight update
        three_world.update_fusion_weights(0.99)
        updated_weights = three_world.get_fusion_weights()

        # Weights should be normalized
        assert np.isclose(updated_weights.sum(), 1.0, atol=1e-6)

    def test_three_world_consistency_resolution(self, three_world):
        """Test resolution of consistency issues through three-world coordination."""
        # Create a statement with potential issues
        statement = "الله يأمر بالعدل"  # "Allah commands justice"

        result = three_world.resolve_consistency(statement)
        assert result is not None
        assert "neural_confidence" in result
        assert "symbolic_consistent" in result
        assert "categorical_verified" in result

    def test_batch_processing(self, three_world):
        """Test batch processing of multiple verses."""
        verses = [
            "بسم الله الرحمن الرحيم",
            "الحمد لله رب العالمين",
            "مالك يوم الدين",
        ]
        context = {"batch": True}

        results = three_world.process_batch(verses, context)
        assert len(results) == 3
        for result in results:
            assert "neural_embedding" in result
            assert "symbolic_check" in result
            assert "categorical_verification" in result

    def test_interpretability_report(self, three_world):
        """Test generation of interpretability report."""
        verse = "الحمد لله رب العالمين"
        context = {"topic": "praise"}

        report = three_world.generate_interpretability_report(verse, context)
        assert "neural_analysis" in report
        assert "symbolic_analysis" in report
        assert "categorical_analysis" in report
        assert "fusion_decision" in report
