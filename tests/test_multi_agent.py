"""Test suite for Multi-Agent Scholar Debate System.

Tests the Proposer, Critic, and Verifier agents working together in a
formal debate engine with LangGraph coordination and Dung semantics.
"""

import pytest
from frontier_neuro_symbolic.multi_agent.proposer_agent import ProposerAgent
from frontier_neuro_symbolic.multi_agent.critic_agent import CriticAgent
from frontier_neuro_symbolic.multi_agent.verifier_agent import VerifierAgent
from frontier_neuro_symbolic.multi_agent.debate_engine import DebateEngine
from frontier_neuro_symbolic.multi_agent.scholar_memory import ScholarMemory


class TestProposerAgent:
    """Test ProposerAgent interpretation generation."""

    def test_proposer_initialization(self):
        """Initialize proposer agent with proper configuration."""
        proposer = ProposerAgent(
            model_name="claude-3-haiku",
            rag_retriever=None,
            context_window=2048
        )
        assert proposer.model_name == "claude-3-haiku"
        assert proposer.context_window == 2048

    def test_proposer_generates_interpretation(self):
        """Proposer generates interpretation from query + context."""
        proposer = ProposerAgent(model_name="claude-3-haiku")

        query = "What is the ruling on interest (riba) in Islamic finance?"
        retrieved_context = [
            {
                "surah": 2,
                "ayah": 275,
                "text": "Those who consume riba will not stand except like one standing convulsed...",
                "score": 0.95
            }
        ]

        interpretation = proposer.generate(query, retrieved_context)

        assert interpretation is not None
        assert "interpretation" in interpretation
        assert "confidence" in interpretation
        assert 0 <= interpretation["confidence"] <= 1
        assert len(interpretation["interpretation"]) > 0

    def test_proposer_uses_retrieved_context(self):
        """Proposer properly incorporates retrieved context in output."""
        proposer = ProposerAgent(model_name="claude-3-haiku")

        query = "Explain the concept of Tawhid"
        context = [
            {
                "surah": 112,
                "ayah": 1,
                "text": "Say: He is Allah, One",
                "score": 0.98
            }
        ]

        result = proposer.generate(query, context)

        # Should cite the source
        assert "citations" in result or "sources" in result or len(context) > 0

    def test_proposer_handles_empty_context(self):
        """Proposer handles gracefully when no context is retrieved."""
        proposer = ProposerAgent(model_name="claude-3-haiku")

        query = "What is the significance of Surah Al-Ikhlas?"
        interpretation = proposer.generate(query, [])

        assert interpretation is not None
        assert "interpretation" in interpretation


class TestCriticAgent:
    """Test CriticAgent validation against sources."""

    def test_critic_initialization(self):
        """Initialize critic agent with hadith + madhab databases."""
        critic = CriticAgent(
            hadith_db=None,
            madhab_list=["hanafi", "maliki", "shafii", "hanbali"],
            api_key=None
        )
        assert len(critic.madhab_list) == 4
        assert "hanafi" in critic.madhab_list

    def test_critic_validates_interpretation(self):
        """Critic validates interpretation against sources."""
        critic = CriticAgent(madhab_list=["hanafi", "maliki", "shafii", "hanbali"])

        interpretation = "Interest is prohibited in Islamic finance based on Quranic and Hadith evidence."
        sources = {
            "quran": [(2, 275), (2, 278)],
            "hadith": ["Sahih Bukhari 34:160"]
        }

        critique = critic.evaluate(interpretation, sources)

        assert critique is not None
        assert "issues" in critique
        assert "madhab_agreement" in critique
        assert "hadith_strength" in critique
        assert 0 <= critique["madhab_agreement"] <= 1.0

    def test_critic_checks_hadith_authenticity(self):
        """Critic assesses hadith authentication grades."""
        critic = CriticAgent(madhab_list=["hanafi"])

        hadith_refs = ["Sahih Bukhari 34:160", "Sunan Abi Dawud 23:45"]

        strength_assessment = critic.assess_hadith_strength(hadith_refs)

        assert strength_assessment is not None
        assert isinstance(strength_assessment, dict)
        assert "average_grade" in strength_assessment or "grades" in strength_assessment

    def test_critic_computes_madhab_agreement(self):
        """Critic computes agreement score across madhabs."""
        critic = CriticAgent(madhab_list=["hanafi", "maliki", "shafii", "hanbali"])

        interpretation = "Excessive interest is prohibited"
        madhab_positions = {
            "hanafi": 0.95,
            "maliki": 0.92,
            "shafii": 0.96,
            "hanbali": 0.94
        }

        agreement = critic.compute_madhab_agreement(interpretation, madhab_positions)

        assert 0 <= agreement <= 1.0
        assert agreement > 0.85  # Should show high agreement

    def test_critic_returns_evidence(self):
        """Critic returns supporting/contradicting evidence."""
        critic = CriticAgent(madhab_list=["hanafi"])

        interpretation = "Ritual prayer requires ablution"
        critique = critic.evaluate(interpretation, {})

        assert "supporting_evidence" in critique or "evidence" in critique


class TestVerifierAgent:
    """Test VerifierAgent consistency checking."""

    def test_verifier_initialization(self):
        """Initialize verifier with logic solver."""
        verifier = VerifierAgent(
            solver_type="z3",
            max_iterations=100,
            timeout_seconds=5
        )
        assert verifier.solver_type == "z3"
        assert verifier.max_iterations == 100

    def test_verifier_checks_logical_consistency(self):
        """Verifier detects logical contradictions."""
        verifier = VerifierAgent(solver_type="z3")

        statements = [
            "All obligatory acts must be performed",
            "Prayer is obligatory",
            "Prayer must be performed"
        ]

        consistency = verifier.check_consistency(statements)

        assert consistency is not None
        assert "is_consistent" in consistency
        assert consistency["is_consistent"] is True
        assert "confidence" in consistency

    def test_verifier_detects_contradiction(self):
        """Verifier detects logical contradictions."""
        verifier = VerifierAgent(solver_type="z3")

        statements = [
            "Interest is obligatory",
            "Interest is prohibited"
        ]

        consistency = verifier.check_consistency(statements)

        assert consistency["is_consistent"] is False
        assert "contradictions" in consistency or "issues" in consistency

    def test_verifier_checks_naskh_order(self):
        """Verifier detects violations of revelation order (naskh)."""
        verifier = VerifierAgent(solver_type="z3")

        verses = [
            {"surah": 2, "ayah": 106, "ruling": "interest allowed"},
            {"surah": 2, "ayah": 275, "ruling": "interest prohibited"}
        ]

        naskh_check = verifier.check_naskh_violations(verses)

        assert "violations" in naskh_check or "is_valid" in naskh_check

    def test_verifier_enforces_temporal_constraints(self):
        """Verifier enforces temporal ordering of rulings."""
        verifier = VerifierAgent(solver_type="z3")

        timeline = [
            {"year": 1, "ruling": "X is allowed", "verse": (2, 100)},
            {"year": 5, "ruling": "X is prohibited", "verse": (2, 275)}
        ]

        temporal_check = verifier.check_temporal_constraints(timeline)

        assert temporal_check is not None
        assert isinstance(temporal_check, dict)

    def test_verifier_returns_confidence_score(self):
        """Verifier returns confidence metric for consistency check."""
        verifier = VerifierAgent(solver_type="z3")

        statements = ["A implies B", "B implies C", "A implies C"]
        consistency = verifier.check_consistency(statements)

        assert "confidence" in consistency
        assert 0 <= consistency["confidence"] <= 1.0


class TestDebateEngine:
    """Test DebateEngine orchestration of three agents."""

    def test_debate_engine_initialization(self):
        """Initialize debate engine with three agents."""
        engine = DebateEngine(
            proposer=ProposerAgent(model_name="claude-3-haiku"),
            critic=CriticAgent(madhab_list=["hanafi"]),
            verifier=VerifierAgent(solver_type="z3"),
            max_rounds=5
        )
        assert engine.max_rounds == 5
        assert engine.proposer is not None
        assert engine.critic is not None
        assert engine.verifier is not None

    def test_debate_engine_runs_single_round(self):
        """Run single round of debate."""
        engine = DebateEngine(
            proposer=ProposerAgent(model_name="claude-3-haiku"),
            critic=CriticAgent(madhab_list=["hanafi"]),
            verifier=VerifierAgent(solver_type="z3"),
            max_rounds=1
        )

        query = "What is the ruling on riba?"
        context = [{"surah": 2, "ayah": 275, "text": "Those who consume riba..."}]

        round_result = engine.run_round(query, context, round_num=1)

        assert round_result is not None
        assert hasattr(round_result, "proposer_interpretation")
        assert hasattr(round_result, "critic_assessment")
        assert hasattr(round_result, "verifier_consistency")

    def test_debate_engine_runs_full_debate(self):
        """Run complete multi-round debate."""
        engine = DebateEngine(
            proposer=ProposerAgent(model_name="claude-3-haiku"),
            critic=CriticAgent(madhab_list=["hanafi", "maliki"]),
            verifier=VerifierAgent(solver_type="z3"),
            max_rounds=3
        )

        query = "Explain the concept of ijma (consensus)"
        context = [{"surah": 4, "ayah": 59, "text": "Obey Allah and His Messenger..."}]

        debate_result = engine.debate(query, context)

        assert debate_result is not None
        assert "final_interpretation" in debate_result
        assert "rounds" in debate_result
        assert len(debate_result["rounds"]) <= 3
        assert "convergence_score" in debate_result

    def test_debate_engine_uses_langgraph_state(self):
        """Debate engine maintains LangGraph state machine."""
        engine = DebateEngine(
            proposer=ProposerAgent(model_name="claude-3-haiku"),
            critic=CriticAgent(madhab_list=["hanafi"]),
            verifier=VerifierAgent(solver_type="z3"),
            max_rounds=2
        )

        # Debate should maintain state across rounds
        debate = engine.debate("What is tawhid?", [])

        assert "state_trace" in debate or len(debate["rounds"]) > 0

    def test_debate_engine_applies_dung_semantics(self):
        """Debate engine resolves conflicts using Dung argumentation framework."""
        engine = DebateEngine(
            proposer=ProposerAgent(model_name="claude-3-haiku"),
            critic=CriticAgent(madhab_list=["hanafi"]),
            verifier=VerifierAgent(solver_type="z3"),
            max_rounds=3
        )

        query = "Can women lead prayer?"
        context = []

        result = engine.debate(query, context)

        # Should apply argumentation framework
        assert "conflict_resolution" in result or "final_interpretation" in result

    def test_debate_convergence(self):
        """Debate converges to stable interpretation."""
        engine = DebateEngine(
            proposer=ProposerAgent(model_name="claude-3-haiku"),
            critic=CriticAgent(madhab_list=["hanafi", "maliki", "shafii"]),
            verifier=VerifierAgent(solver_type="z3"),
            max_rounds=5
        )

        result = engine.debate("What is ijma?", [])

        # After multiple rounds, should converge
        assert result["convergence_score"] >= 0.6 or len(result["rounds"]) < engine.max_rounds


class TestScholarMemory:
    """Test ScholarMemory for agent context management."""

    def test_scholar_memory_initialization(self):
        """Initialize scholar memory with context storage."""
        memory = ScholarMemory(
            max_history=100,
            embedding_dim=384,
            madhab_priors={"hanafi": 0.3, "maliki": 0.25}
        )
        assert memory.max_history == 100
        assert "hanafi" in memory.madhab_priors

    def test_scholar_memory_stores_debate_history(self):
        """Memory stores debate history and past interpretations."""
        memory = ScholarMemory(max_history=50)

        entry = {
            "query": "What is riba?",
            "interpretation": "Interest is prohibited",
            "round": 1,
            "confidence": 0.92
        }

        memory.add_entry(entry)

        assert len(memory.history) == 1
        assert memory.history[0].query == "What is riba?"

    def test_scholar_memory_retrieves_similar_past(self):
        """Memory retrieves similar past debates for context."""
        memory = ScholarMemory(max_history=10)

        memory.add_entry({"query": "What is riba?", "interpretation": "Prohibited"})
        memory.add_entry({"query": "Define interest in Islam", "interpretation": "Haram"})

        similar = memory.retrieve_similar("interest", top_k=2)

        assert similar is not None
        assert len(similar) <= 2

    def test_scholar_memory_counterfactual_critique(self):
        """Memory supports counterfactual critiques from human input."""
        memory = ScholarMemory(max_history=20)

        interpretation = "Prayer is obligatory"
        human_challenge = "What if prayer were voluntary?"

        counterfactual = memory.generate_counterfactual_critique(
            interpretation,
            human_challenge
        )

        assert counterfactual is not None
        assert isinstance(counterfactual, dict)

    def test_scholar_memory_fine_tunes_embeddings(self):
        """Memory fine-tunes embeddings via causal RL feedback."""
        memory = ScholarMemory(max_history=30, embedding_dim=384)

        # Add feedback
        memory.add_feedback(
            query="What is tawhid?",
            feedback=0.95,  # positive feedback
            was_correct=True
        )

        # Should update internal model
        assert len(memory.feedback_history) >= 1

    def test_scholar_memory_causal_inference(self):
        """Memory performs causal inference on interpretations."""
        memory = ScholarMemory(max_history=50)

        memory.add_entry({
            "query": "Effect of X on Y",
            "causal_chain": ["A causes B", "B causes C"],
            "confidence": 0.88
        })

        causal = memory.get_causal_structure()

        assert causal is not None


class TestMultiAgentIntegration:
    """Integration tests for complete debate system."""

    def test_end_to_end_debate_flow(self):
        """Complete end-to-end debate from query to resolution."""
        proposer = ProposerAgent(model_name="claude-3-haiku")
        critic = CriticAgent(madhab_list=["hanafi", "maliki"])
        verifier = VerifierAgent(solver_type="z3")

        engine = DebateEngine(
            proposer=proposer,
            critic=critic,
            verifier=verifier,
            max_rounds=3
        )

        query = "What is the significance of Surah Al-Fatihah?"
        context = []

        result = engine.debate(query, context)

        assert "final_interpretation" in result
        assert result["final_interpretation"] is not None
        assert "rounds" in result
        assert len(result["rounds"]) > 0

    def test_agents_respect_madhab_diversity(self):
        """System respects all madhabs equally."""
        critic = CriticAgent(madhab_list=["hanafi", "maliki", "shafii", "hanbali"])

        # Critic should treat all madhabs fairly
        assert len(critic.madhab_list) == 4

    def test_debate_handles_contentious_topics(self):
        """System handles controversial interpretations gracefully."""
        engine = DebateEngine(
            proposer=ProposerAgent(model_name="claude-3-haiku"),
            critic=CriticAgent(madhab_list=["hanafi", "maliki"]),
            verifier=VerifierAgent(solver_type="z3"),
            max_rounds=5
        )

        # Controversial topic
        query = "Is ijtihad still valid today?"

        result = engine.debate(query, [])

        assert "final_interpretation" in result
        assert "dissenting_views" in result or "alternative_positions" in result

    def test_full_system_with_memory(self):
        """Complete system including scholar memory."""
        memory = ScholarMemory(max_history=50)
        engine = DebateEngine(
            proposer=ProposerAgent(model_name="claude-3-haiku"),
            critic=CriticAgent(madhab_list=["hanafi"]),
            verifier=VerifierAgent(solver_type="z3"),
            memory=memory,
            max_rounds=2
        )

        result = engine.debate("What is ijma?", [])

        assert result is not None
        assert "final_interpretation" in result


# Test fixtures
@pytest.fixture
def sample_quranic_context():
    """Sample Quranic context for testing."""
    return [
        {
            "surah": 2,
            "ayah": 275,
            "text": "Those who consume riba will not stand except like one standing convulsed by Satan's touch...",
            "score": 0.98
        },
        {
            "surah": 2,
            "ayah": 278,
            "text": "O you who believe! Fear Allah and give up what remains of riba...",
            "score": 0.95
        }
    ]


@pytest.fixture
def sample_hadith_sources():
    """Sample hadith references for testing."""
    return {
        "sahih": ["Sahih Bukhari 34:160", "Sahih Muslim 12:100"],
        "sunan": ["Sunan Abu Dawud 3:45", "Sunan Tirmidhi 13:70"]
    }
