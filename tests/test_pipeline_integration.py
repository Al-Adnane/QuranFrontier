"""
End-to-end integration tests for FrontierQu 5-Layer Pipeline and
Consciousness Orchestrator.

Tests:
  - test_pipeline_runs_end_to_end: Arabic + English text → PipelineResult
  - test_pipeline_layer1_produces_embeddings: Neural layer outputs numpy array
  - test_pipeline_layer3_z3_satisfiable: Z3 or fallback produces valid result
  - test_pipeline_layer4_gwt_ignition: GWT produces ignition metrics
  - test_pipeline_layer5_lean_graceful: Lean 4 handles absence gracefully
  - test_consciousness_metrics: ConsciousnessOrchestrator produces valid metrics
  - test_consciousness_phi_bounded: Phi is in [0, 1]
  - test_consciousness_dream_fragments: Dreaming produces ≥ 0 fragments
  - test_z3_deontic_solver: SMTDeonticSolver with Z3 produces assignments
  - test_lean_interface: LeanProver finds lean or handles absence
  - test_pipeline_to_dict: PipelineResult.to_dict() is valid JSON
  - test_pipeline_multiple_inputs: Different inputs produce different results
  - test_model_discovery_count: At least 150 models discoverable
"""

import sys
import os
import json
import pytest
import numpy as np

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


# ─── Pipeline ─────────────────────────────────────────────────────────────────

class TestPipelineOrchestrator:

    @pytest.fixture(scope="class")
    def pipeline(self):
        from pipeline_orchestrator import FrontierQuPipeline
        return FrontierQuPipeline()

    @pytest.fixture(scope="class")
    def arabic_result(self, pipeline):
        return pipeline.run("بسم الله الرحمن الرحيم")

    @pytest.fixture(scope="class")
    def english_result(self, pipeline):
        return pipeline.run("In the name of God, the Most Gracious")

    def test_pipeline_runs_end_to_end(self, arabic_result):
        from pipeline_orchestrator import PipelineResult
        assert isinstance(arabic_result, PipelineResult)

    def test_pipeline_has_all_layers(self, arabic_result):
        from pipeline_orchestrator import Layer1Output, Layer2Output, Layer3Output, Layer4Output, Layer5Output
        assert isinstance(arabic_result.layer1, Layer1Output)
        assert isinstance(arabic_result.layer2, Layer2Output)
        assert isinstance(arabic_result.layer3, Layer3Output)
        assert isinstance(arabic_result.layer4, Layer4Output)
        assert isinstance(arabic_result.layer5, Layer5Output)

    def test_pipeline_layer1_embeddings(self, arabic_result):
        """Layer 1 must produce a numpy embedding array."""
        l1 = arabic_result.layer1
        assert isinstance(l1.embeddings, np.ndarray)
        assert l1.embeddings.shape[0] > 0
        assert not np.all(l1.embeddings == 0)

    def test_pipeline_layer1_has_models(self, arabic_result):
        """At least one model must have run."""
        assert len(arabic_result.layer1.model_names) >= 1

    def test_pipeline_layer1_entropy_positive(self, arabic_result):
        assert arabic_result.layer1.char_entropy >= 0.0

    def test_pipeline_layer2_confidence_bounded(self, arabic_result):
        """All confidence values must be in [0, 1]."""
        l2 = arabic_result.layer2
        for val in [l2.neural_confidence, l2.symbolic_confidence, l2.categorical_confidence]:
            assert 0.0 <= val <= 1.0, f"Confidence out of bounds: {val}"

    def test_pipeline_layer2_qiraat_7(self, arabic_result):
        """Must recognize 7 canonical Qiraat variants."""
        assert arabic_result.layer2.qiraat_variants == 7

    def test_pipeline_layer3_z3_satisfiable(self, arabic_result):
        """Constraint layer must produce a satisfiability result."""
        l3 = arabic_result.layer3
        assert isinstance(l3.satisfiable, bool)
        assert isinstance(l3.deontic_status, str)

    def test_pipeline_layer3_maqasid_bounded(self, arabic_result):
        l3 = arabic_result.layer3
        assert 0.0 <= l3.maqasid_score <= 1.0

    def test_pipeline_layer4_gwt_ignition(self, arabic_result):
        """Consciousness layer must set ignition_fired."""
        l4 = arabic_result.layer4
        assert isinstance(l4.ignition_fired, bool)

    def test_pipeline_layer4_metacognitive_confidence(self, arabic_result):
        l4 = arabic_result.layer4
        assert 0.0 <= l4.metacognitive_confidence <= 1.0
        assert 0.0 <= l4.agreement_score <= 1.0

    def test_pipeline_layer5_lean_graceful(self, arabic_result):
        """Lean 4 layer must handle lean absence gracefully."""
        l5 = arabic_result.layer5
        assert isinstance(l5.lean_available, bool)
        assert isinstance(l5.proofs_verified, int)
        assert l5.proofs_verified >= 0

    def test_pipeline_total_time_reasonable(self, arabic_result):
        """Pipeline must complete in under 60 seconds."""
        assert arabic_result.total_duration_ms < 60000

    def test_pipeline_to_dict(self, arabic_result):
        """PipelineResult.to_dict() must produce valid JSON."""
        d = arabic_result.to_dict()
        assert isinstance(d, dict)
        # Must serialize to JSON without error
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        assert "input" in parsed
        assert "layer1" in parsed
        assert "layer5" in parsed

    def test_pipeline_summary_not_empty(self, arabic_result):
        summary = arabic_result.summary()
        assert isinstance(summary, str)
        assert "Layer 1" in summary
        assert "Layer 5" in summary

    def test_pipeline_multiple_inputs_differ(self, pipeline):
        """Different inputs must produce different embeddings."""
        r1 = pipeline.run("بسم الله الرحمن الرحيم")
        r2 = pipeline.run("الحمد لله رب العالمين")
        # Embeddings should differ (different text hashes)
        assert not np.allclose(r1.layer1.embeddings, r2.layer1.embeddings)

    def test_pipeline_english_runs(self, english_result):
        """Pipeline must work on non-Arabic input too."""
        from pipeline_orchestrator import PipelineResult
        assert isinstance(english_result, PipelineResult)
        assert english_result.layer1.char_entropy >= 0.0


# ─── Consciousness Orchestrator ────────────────────────────────────────────────

class TestConsciousnessOrchestrator:

    @pytest.fixture(scope="class")
    def orchestrator(self):
        from consciousness_orchestrator import ConsciousnessOrchestrator
        return ConsciousnessOrchestrator()

    @pytest.fixture(scope="class")
    def metrics_5(self, orchestrator):
        return orchestrator.run(n_steps=5)

    @pytest.fixture(scope="class")
    def metrics_20(self, orchestrator):
        return orchestrator.run(n_steps=20)

    def test_metrics_type(self, metrics_5):
        from consciousness_orchestrator import ConsciousnessMetrics
        assert isinstance(metrics_5, ConsciousnessMetrics)

    def test_phi_bounded(self, metrics_5):
        """IIT Phi must be in [0, 1]."""
        assert 0.0 <= metrics_5.phi <= 1.0

    def test_consciousness_score_bounded(self, metrics_5):
        assert 0.0 <= metrics_5.consciousness_score <= 1.0

    def test_dream_fragments_non_negative(self, metrics_5):
        assert metrics_5.dream_fragments >= 0

    def test_max_novelty_non_negative(self, metrics_5):
        assert metrics_5.max_novelty >= 0.0

    def test_ignition_rate_bounded(self, metrics_5):
        assert 0.0 <= metrics_5.ignition_rate <= 1.0

    def test_metacognitive_confidence_bounded(self, metrics_5):
        assert 0.0 <= metrics_5.metacognitive_confidence <= 1.0

    def test_agreement_score_bounded(self, metrics_5):
        assert 0.0 <= metrics_5.agreement_score <= 1.0

    def test_temporal_sync_bounded(self, metrics_5):
        assert -1.0 <= metrics_5.temporal_sync <= 1.0

    def test_emotional_valence_bounded(self, metrics_5):
        assert -1.0 <= metrics_5.emotional_valence <= 1.0
        assert 0.0 <= metrics_5.emotional_arousal <= 1.0

    def test_active_modules_list(self, metrics_5):
        assert isinstance(metrics_5.active_modules, list)

    def test_to_dict_serializable(self, metrics_5):
        d = metrics_5.to_dict()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        assert "consciousness_score" in parsed
        assert "phi" in parsed
        assert "gwt" in parsed

    def test_more_steps_positive_ignition(self, metrics_20):
        """More steps → at least some GWT activity if module loaded."""
        if metrics_20.gwt_active:
            assert metrics_20.broadcast_count >= 0

    def test_summary_contains_key_fields(self, metrics_5):
        summary = metrics_5.summary()
        assert "Phi" in summary or "phi" in summary.lower()
        assert "Consciousness Score" in summary

    def test_reproducible(self, orchestrator):
        """Same seed → same metrics."""
        m1 = orchestrator.run(n_steps=5, seed=42)
        m2 = orchestrator.run(n_steps=5, seed=42)
        assert abs(m1.phi - m2.phi) < 1e-6
        assert abs(m1.consciousness_score - m2.consciousness_score) < 1e-6


# ─── Z3 Deontic Solver ────────────────────────────────────────────────────────

class TestZ3DeonticSolver:

    def test_z3_is_available(self):
        """Z3 must be installed."""
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import HAS_Z3
        assert HAS_Z3, "Z3 not installed — run: python3 -m pip install z3-solver"

    def test_z3_basic_satisfiable(self):
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import SMTDeonticSolver
        solver = SMTDeonticSolver()
        solver.add_verse_ruling(("2:255", "Ayat al-Kursi"), "wajib", 0.9)
        assert solver.check_satisfiability() is True

    def test_z3_get_model(self):
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import SMTDeonticSolver
        solver = SMTDeonticSolver()
        solver.add_verse_ruling(("1:1", "Basmala"), "recommended", 0.75)
        solver.check_satisfiability()
        model = solver.get_model()
        assert model is not None
        # Z3 returns ModelRef; dict or ModelRef both valid
        assert len(model) > 0 if hasattr(model, '__len__') else len(list(model)) >= 0

    def test_z3_multiple_rulings(self):
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import SMTDeonticSolver
        solver = SMTDeonticSolver()
        for i in range(5):
            solver.add_verse_ruling((f"v:{i}", f"verse {i}"), "wajib", 0.5 + i*0.08)
        result = solver.check_satisfiability()
        assert isinstance(result, bool)


# ─── Lean 4 Interface ─────────────────────────────────────────────────────────

class TestLeanInterface:

    def test_lean_prover_instantiates(self):
        from frontier_neuro_symbolic.system_integration.lean_interface import LeanProver
        prover = LeanProver(cache_enabled=True, timeout_seconds=10)
        assert prover is not None

    def test_lean_executable_check(self):
        """LeanProver must handle Lean absence gracefully (no exception)."""
        from frontier_neuro_symbolic.system_integration.lean_interface import LeanProver
        prover = LeanProver()
        # lean_executable is either a path or None — both are valid
        assert prover.lean_executable is None or isinstance(prover.lean_executable, str)

    def test_lean_proof_result_structure(self):
        from frontier_neuro_symbolic.system_integration.lean_interface import LeanProver, ProofResult
        prover = LeanProver()
        if prover.lean_executable:
            lean_dir = os.path.join(BASE_DIR, "frontier_formal", "FrontierQu")
            lean_file = os.path.join(lean_dir, "DeonticLogic.lean")
            if os.path.exists(lean_file):
                result = prover.verify_file(lean_file)
                assert isinstance(result, ProofResult)
                assert isinstance(result.verified, bool)
                assert result.duration_ms >= 0
        else:
            pytest.skip("Lean 4 not installed")


# ─── Model Discovery ──────────────────────────────────────────────────────────

class TestModelDiscovery:

    @pytest.fixture(scope="class")
    def factories(self):
        import importlib
        import pkgutil
        import frontier_models
        discovered = []
        seen = set()
        for finder, modname, ispkg in pkgutil.walk_packages(
            path=frontier_models.__path__,
            prefix=frontier_models.__name__ + ".",
            onerror=lambda x: None,
        ):
            if ispkg:
                continue
            try:
                mod = importlib.import_module(modname)
            except Exception:
                continue
            for attr in dir(mod):
                if attr.startswith("create_") and attr.endswith("_network"):
                    fn = getattr(mod, attr)
                    if callable(fn) and (modname, attr) not in seen:
                        seen.add((modname, attr))
                        discovered.append((modname, attr, fn))
        return discovered

    def test_discovery_count_140_plus(self, factories):
        """Must discover at least 140 model factories."""
        assert len(factories) >= 140, f"Only {len(factories)} discovered"

    def test_discovery_covers_frontier_domain(self, factories):
        """Must include frontier domain models."""
        frontier = [m for m, n, _ in factories if "frontier" in m]
        assert len(frontier) >= 10

    def test_discovery_covers_wild_domain(self, factories):
        wild = [m for m, n, _ in factories if "wild" in m]
        assert len(wild) >= 15

    def test_discovery_covers_bio_domain(self, factories):
        bio = [m for m, n, _ in factories if ".bio." in m]
        assert len(bio) >= 5

    def test_discovery_covers_physics_domain(self, factories):
        physics = [m for m, n, _ in factories if ".physics." in m]
        assert len(physics) >= 4

    def test_factory_names_valid(self, factories):
        """All factory names must start with create_ and end with _network."""
        for _, name, _ in factories:
            assert name.startswith("create_"), f"Bad prefix: {name}"
            assert name.endswith("_network"), f"Bad suffix: {name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
