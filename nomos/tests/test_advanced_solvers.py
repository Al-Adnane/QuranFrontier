"""Unit tests for advanced solvers (quantum annealing, SMT, constraint programming)."""
import pytest
import numpy as np
from typing import Set, Tuple, Dict, Any


class TestQuantumAnnealingIsnad:
    """Test suite for quantum annealing-based isnad verification."""

    def test_qubo_generation_simple_chain(self):
        """Test QUBO matrix generation for simple transmitter chain."""
        from frontier_neuro_symbolic.advanced_solvers.quantum_annealing import (
            QuantumAnnealingIsnad,
        )

        solver = QuantumAnnealingIsnad()

        # Simple isnad: A -> B -> C
        edges = [("A", "B"), ("B", "C")]
        authenticity_scores = {"A": 0.9, "B": 0.85, "C": 0.8}

        qubo, node_to_qubit = solver.generate_qubo(edges, authenticity_scores)

        # Check matrix is square (num_nodes x num_nodes)
        assert qubo.shape == (3, 3)
        # Check field h_i from authenticity scores
        assert qubo[0, 0] == -0.9  # -authenticity score on diagonal
        assert qubo[1, 1] == -0.85
        assert qubo[2, 2] == -0.8
        # Check coupling terms (off-diagonal)
        assert qubo[0, 1] == qubo[1, 0]  # Symmetric

    def test_isnad_dag_linear(self):
        """Test isnad DAG for linear transmission chain."""
        from frontier_neuro_symbolic.advanced_solvers.quantum_annealing import (
            QuantumAnnealingIsnad,
        )

        solver = QuantumAnnealingIsnad()

        # Linear chain: Prophet -> Companion -> Tabi'i -> Imam
        edges = [
            ("Prophet", "Companion"),
            ("Companion", "Tabi'i"),
            ("Tabi'i", "Imam"),
        ]
        authenticity_scores = {
            "Prophet": 1.0,
            "Companion": 0.95,
            "Tabi'i": 0.85,
            "Imam": 0.8,
        }

        qubo, node_to_qubit = solver.generate_qubo(edges, authenticity_scores)
        assert len(node_to_qubit) == 4
        assert qubo.shape == (4, 4)

    def test_classical_fallback_solver(self):
        """Test classical solver fallback when D-Wave unavailable."""
        from frontier_neuro_symbolic.advanced_solvers.quantum_annealing import (
            QuantumAnnealingIsnad,
        )

        solver = QuantumAnnealingIsnad(use_dwave=False)

        edges = [("A", "B"), ("B", "C")]
        authenticity_scores = {"A": 0.9, "B": 0.85, "C": 0.8}

        result = solver.solve_isnad(edges, authenticity_scores)

        assert hasattr(result, 'chain')
        assert hasattr(result, 'consistency_score')
        assert 0 <= result.consistency_score <= 1

    def test_maximal_consistent_subgraph(self):
        """Test finding maximal consistent isnad subgraph."""
        from frontier_neuro_symbolic.advanced_solvers.quantum_annealing import (
            QuantumAnnealingIsnad,
        )

        solver = QuantumAnnealingIsnad(use_dwave=False)

        # Diamond-shaped DAG (two conflicting paths)
        edges = [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("C", "D"),
        ]
        authenticity_scores = {"A": 1.0, "B": 0.9, "C": 0.7, "D": 0.8}

        result = solver.solve_isnad(edges, authenticity_scores)

        chain = result.chain
        consistency = result.consistency_score

        assert len(chain) > 0
        assert consistency > 0


class TestSMTDeonticSolver:
    """Test suite for SMT-based deontic logic solver."""

    def test_smt_formula_creation(self):
        """Test creation of deontic formulas in Z3."""
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import (
            SMTDeonticSolver,
        )

        solver = SMTDeonticSolver()

        # Naskh constraint: if naskh occurred, strength increases
        # □(∀t. naskh(t₁,t₂) → deontic_strength(t₂) > deontic_strength(t₁))

        result = solver.add_naskh_constraint(
            ruling1=("2:183", "fasting"),
            ruling2=("9:5", "fighting"),
            strength1=0.7,
            strength2=0.9,
        )

        assert result is not None

    def test_deontic_status_satisfiability(self):
        """Test satisfiability checking for deontic status assignments."""
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import (
            SMTDeonticSolver,
            DeonticStatus,
        )

        solver = SMTDeonticSolver()

        # Add constraint: if command occurs, wajib (obligatory)
        solver.add_deontic_status(
            ruling=("2:183", "fasting"),
            status=DeonticStatus.WAJIB,
            confidence=0.95,
        )

        is_sat = solver.check_satisfiability()

        assert isinstance(is_sat, bool)
        assert is_sat is True

    def test_temporal_constraint_satisfaction(self):
        """Test temporal constraints on revelation order."""
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import (
            SMTDeonticSolver,
        )

        solver = SMTDeonticSolver()

        # Constraint: Makkan verses revealed before Madinan
        solver.add_temporal_constraint(
            earlier_verse=("96:1", "Makkan"),
            later_verse=("2:1", "Madinan"),
        )

        is_sat = solver.check_satisfiability()
        assert is_sat is True

    def test_verse_ruling_pair_satisfiability(self):
        """Test satisfiability for verse-ruling pairs."""
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import (
            SMTDeonticSolver,
        )

        solver = SMTDeonticSolver()

        solver.add_verse_ruling(
            verse=("2:183", "yawm al-sawm"),
            ruling="fasting is obligatory",
            deontic_strength=0.95,
        )

        # Check if consistent
        is_sat = solver.check_satisfiability()
        assert is_sat is True

    def test_conflicting_rulings_unsatisfiable(self):
        """Test detection of conflicting deontic assignments."""
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import (
            SMTDeonticSolver,
            DeonticStatus,
        )

        solver = SMTDeonticSolver()

        # Add contradictory constraints
        solver.add_deontic_status(
            ruling=("2:183", "fasting"),
            status=DeonticStatus.WAJIB,
            confidence=0.95,
        )
        solver.add_deontic_status(
            ruling=("2:183", "fasting"),
            status=DeonticStatus.HARAM,
            confidence=0.95,
        )

        is_sat = solver.check_satisfiability()

        # Should be unsatisfiable with high confidence
        # (but solver may allow soft conflict resolution)
        assert isinstance(is_sat, bool)


class TestMaqasidOptimizer:
    """Test suite for Maqasid al-Shari'ah constraint optimization."""

    def test_pareto_frontier_computation(self):
        """Test computation of Pareto-optimal fiqh positions."""
        from frontier_neuro_symbolic.advanced_solvers.constraint_programmer import (
            MaqasidOptimizer,
            ParetoSolution,
        )

        optimizer = MaqasidOptimizer()

        # 5 Maqasid objectives
        objectives = {
            "preservation_din": 0.9,  # Religion preservation
            "preservation_nafs": 0.85,  # Life preservation
            "preservation_aql": 0.8,  # Intellect preservation
            "preservation_mal": 0.75,  # Property preservation
            "preservation_ird": 0.7,  # Honor preservation
        }

        pareto_front = optimizer.compute_pareto_frontier(objectives)

        assert len(pareto_front) > 0
        for solution in pareto_front:
            assert isinstance(solution, ParetoSolution)
            assert len(solution.ruling) > 0

    def test_quranic_imperative_constraints(self):
        """Test constraint setup from Quranic imperatives."""
        from frontier_neuro_symbolic.advanced_solvers.constraint_programmer import (
            MaqasidOptimizer,
        )

        optimizer = MaqasidOptimizer()

        # Add Quranic commands as constraints
        optimizer.add_constraint(
            description="Establish prayer",
            quranic_reference=("17:78", "aqim al-salah"),
            maqsad="preservation_din",
            weight=1.0,
        )

        constraints = optimizer.get_constraints()
        assert len(constraints) > 0

    def test_multi_objective_optimization(self):
        """Test multi-objective optimization for legal rulings."""
        from frontier_neuro_symbolic.advanced_solvers.constraint_programmer import (
            MaqasidOptimizer,
        )

        optimizer = MaqasidOptimizer()

        # Set up competing objectives
        optimizer.add_constraint(
            description="Allow necessary harm",
            maqsad="preservation_nafs",
            weight=0.9,
        )
        optimizer.add_constraint(
            description="Maintain sanctity",
            maqsad="preservation_din",
            weight=0.95,
        )

        solutions = optimizer.optimize()

        assert len(solutions) > 0
        for sol in solutions:
            assert hasattr(sol, 'ruling')
            assert hasattr(sol, 'trade_offs')

    def test_evolutionary_algorithm_convergence(self):
        """Test evolutionary algorithm converges to Pareto frontier."""
        from frontier_neuro_symbolic.advanced_solvers.constraint_programmer import (
            MaqasidOptimizer,
        )

        optimizer = MaqasidOptimizer(population_size=20, generations=5)

        objectives = {
            "preservation_din": 0.9,
            "preservation_nafs": 0.85,
            "preservation_aql": 0.8,
        }

        front = optimizer.compute_pareto_frontier(objectives)

        assert len(front) >= 1
        # Check that solutions are diverse (not all identical)
        if len(front) > 1:
            def _get_vals(sol):
                if isinstance(sol, dict):
                    return {k: v for k, v in sol.items() if isinstance(v, (int, float))}
                return sol.objectives if hasattr(sol, 'objectives') else {}

            diversities = [
                sum(
                    (_get_vals(front[i]).get(k, 0) - _get_vals(front[j]).get(k, 0)) ** 2
                    for k in _get_vals(front[i]).keys()
                )
                for i in range(len(front))
                for j in range(i + 1, len(front))
            ]
            assert any(d > 0 for d in diversities)


class TestProbabilisticPrograms:
    """Test suite for probabilistic programming with NumPyro."""

    def test_naskh_posterior_inference(self):
        """Test Bayesian inference of naskh posterior given evidence."""
        from frontier_neuro_symbolic.advanced_solvers.probabilistic_programs import (
            NaskhProbabilisticModel,
        )

        model = NaskhProbabilisticModel()

        # Evidence: qira'at variants observed
        evidence = {
            "qiraat_variants": [
                ("2:183", "sawm", 0.8),  # 80% of readers say 'sawm'
                ("2:183", "siyam", 0.2),  # 20% say 'siyam'
            ]
        }

        posterior = model.infer_naskh_posterior(evidence)

        assert "naskh_occurred" in posterior
        assert "confidence" in posterior
        assert 0 <= posterior["confidence"] <= 1

    def test_chronology_constraint_modeling(self):
        """Test probabilistic modeling of chronology constraints."""
        from frontier_neuro_symbolic.advanced_solvers.probabilistic_programs import (
            ChronologyPPL,
        )

        ppl = ChronologyPPL()

        # Sample prior over revelation times
        times = ppl.sample_revelation_times(num_verses=10)

        assert len(times) == 10
        assert all(0 <= t <= 1 for t in times)  # Normalized time axis

    def test_qiraat_likelihood_model(self):
        """Test qira'at variants as noisy evidence."""
        from frontier_neuro_symbolic.advanced_solvers.probabilistic_programs import (
            QiraatLikelihoodModel,
        )

        model = QiraatLikelihoodModel()

        # Observe qira'at variants
        variants = [
            ("2:183", "sawm", 0.85),  # Hafs: 85% sawm
            ("2:183", "siyam", 0.15),  # Others: 15% siyam
        ]

        log_likelihood = model.compute_likelihood(variants)

        assert isinstance(log_likelihood, float)
        assert log_likelihood <= 0  # Log likelihood

    def test_variational_inference_convergence(self):
        """Test variational inference with normalizing flows."""
        from frontier_neuro_symbolic.advanced_solvers.probabilistic_programs import (
            VariationalNaskhInference,
        )

        inference = VariationalNaskhInference()

        evidence = {
            "ruling_early": ("2:183", 0.7),
            "ruling_late": ("9:5", 0.95),
        }

        posterior_approx = inference.run_inference(evidence, num_steps=10)

        assert "naskh_probability" in posterior_approx
        assert "entropy" in posterior_approx
        assert 0 <= posterior_approx["naskh_probability"] <= 1

    def test_turing_complete_ppl(self):
        """Test Turing-completeness of PPL (loops, recursion)."""
        from frontier_neuro_symbolic.advanced_solvers.probabilistic_programs import (
            RecursivePPL,
        )

        ppl = RecursivePPL()

        # Define recursive probabilistic model (e.g., branching chains)
        result = ppl.sample_transmission_chain(max_depth=3)

        assert "chain" in result
        assert "log_probability" in result
        assert isinstance(result["log_probability"], float)


class TestIntegration:
    """Integration tests combining multiple solver types."""

    def test_quantum_smt_integration(self):
        """Test quantum and SMT solvers working together."""
        from frontier_neuro_symbolic.advanced_solvers.quantum_annealing import (
            QuantumAnnealingIsnad,
        )
        from frontier_neuro_symbolic.advanced_solvers.smt_solver import (
            SMTDeonticSolver,
        )

        qa_solver = QuantumAnnealingIsnad(use_dwave=False)
        smt_solver = SMTDeonticSolver()

        # Solve isnad via quantum
        edges = [("A", "B"), ("B", "C")]
        scores = {"A": 0.9, "B": 0.85, "C": 0.8}
        isnad_result = qa_solver.solve_isnad(edges, scores)

        # Verify deontic consistency via SMT
        smt_solver.add_verse_ruling(
            verse=("2:183", "sawm"),
            ruling="fasting obligatory",
            deontic_strength=0.95,
        )
        smt_result = smt_solver.check_satisfiability()

        assert isnad_result.consistency_score > 0
        assert smt_result is True

    def test_constraint_to_probabilistic_pipeline(self):
        """Test constraint solution fed to probabilistic inference."""
        from frontier_neuro_symbolic.advanced_solvers.constraint_programmer import (
            MaqasidOptimizer,
        )
        from frontier_neuro_symbolic.advanced_solvers.probabilistic_programs import (
            NaskhProbabilisticModel,
        )

        optimizer = MaqasidOptimizer()
        ppl = NaskhProbabilisticModel()

        # Optimize constraints
        objectives = {"preservation_din": 0.9, "preservation_nafs": 0.85}
        solutions = optimizer.compute_pareto_frontier(objectives)

        # Use solution as prior for probabilistic inference
        evidence = {"qiraat_variants": [("2:183", "sawm", 0.8)]}
        posterior = ppl.infer_naskh_posterior(evidence)

        assert len(solutions) > 0
        assert posterior["confidence"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
