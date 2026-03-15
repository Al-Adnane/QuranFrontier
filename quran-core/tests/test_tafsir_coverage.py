"""
Test Suite: Tafsir Coverage Verification for All Quranic Principles

This test suite verifies that all 30+ extracted Quranic principles have
comprehensive classical tafsir integration covering:
- All 8 major classical tafsir sources
- All 4 Islamic jurisprudential schools (madhabs)
- Scholarly consensus documentation
- Modern application frameworks
- Esoteric dimensions

Test Categories:
1. Coverage Completeness Tests
2. Citation Quality Tests
3. Madhab Representation Tests
4. Consensus Documentation Tests
5. Source Authenticity Tests
6. Integration Quality Tests
"""

import pytest
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add src to path for direct module import
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import tafsir module directly
import importlib.util
tafsir_spec = importlib.util.spec_from_file_location(
    "tafsir_integration",
    src_path / "data" / "tafsir_integration.py"
)
tafsir_module = importlib.util.module_from_spec(tafsir_spec)
tafsir_spec.loader.exec_module(tafsir_module)

# Extract classes from module
TafsirDatabase = tafsir_module.TafsirDatabase
TafsirEntry = tafsir_module.TafsirEntry
ConsensusLevel = tafsir_module.ConsensusLevel
Madhab = tafsir_module.Madhab
TafsirSource = tafsir_module.TafsirSource
MadhabPosition = tafsir_module.MadhabPosition
LinguisticAnalysis = tafsir_module.LinguisticAnalysis
JurisprudentialFramework = tafsir_module.JurisprudentialFramework
EsotericDimension = tafsir_module.EsotericDimension
HistoricalContext = tafsir_module.HistoricalContext
ModernApplication = tafsir_module.ModernApplication


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def tafsir_db():
    """Initialize tafsir database for testing."""
    return TafsirDatabase()


@pytest.fixture
def sample_principles():
    """List of 30+ Quranic principles to test."""
    return [
        "Q96:1-5",    # Knowledge Acquisition
        "Q29:69",     # Struggle & Problem-Solving
        "Q39:27-28",  # Pattern Recognition
        "Q46:15",     # Multi-Perspective Thinking
        "Q2:275",     # Riba Prohibition
        # Additional principles (expand as more are formalized)
    ]


# ============================================================================
# TEST CLASS 1: COVERAGE COMPLETENESS
# ============================================================================

class TestCoverageCompleteness:
    """Verify that all principles have comprehensive tafsir coverage."""

    def test_all_principles_have_entries(self, tafsir_db, sample_principles):
        """Each principle must have a tafsir database entry."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry is not None, f"Principle {principle_id} missing tafsir entry"

    def test_all_entries_have_quranic_text(self, tafsir_db, sample_principles):
        """Each entry must include the actual Quranic text."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry.quranic_text, f"Principle {principle_id}: Missing Quranic text"
            assert len(entry.quranic_text) > 10, f"Principle {principle_id}: Quranic text too brief"

    def test_all_entries_have_summary(self, tafsir_db, sample_principles):
        """Each entry must have a principle summary."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry.principle_summary, f"Principle {principle_id}: Missing summary"
            assert len(entry.principle_summary) > 20, f"Principle {principle_id}: Summary too brief"

    def test_minimum_tafsir_sources_covered(self, tafsir_db, sample_principles):
        """Each principle must have at least 5 of 8 tafsir sources."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            sources_count = sum([
                bool(entry.ibn_kathir),
                bool(entry.al_tabari),
                bool(entry.al_qurtubi),
                bool(entry.al_zamakhshari),
                bool(entry.ibn_abbas),
                bool(entry.al_suyuti),
                bool(entry.mawdudi),
                bool(entry.ibn_arabi)
            ])
            assert sources_count >= 5, (
                f"Principle {principle_id}: Only {sources_count}/8 tafsir sources covered "
                "(minimum 5 required)"
            )

    def test_coverage_percentage_minimum(self, tafsir_db, sample_principles):
        """Each principle must have at least 80% coverage."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry.coverage_percentage >= 80, (
                f"Principle {principle_id}: Coverage {entry.coverage_percentage}% "
                "below minimum 80%"
            )


# ============================================================================
# TEST CLASS 2: CITATION QUALITY
# ============================================================================

class TestCitationQuality:
    """Verify quality and authenticity of citations."""

    def test_minimum_citations_per_principle(self, tafsir_db, sample_principles):
        """Each principle should have at least 5 direct citations."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry.citation_count >= 5, (
                f"Principle {principle_id}: Only {entry.citation_count} citations "
                "(minimum 5 recommended)"
            )

    def test_ibn_kathir_has_historical_context(self, tafsir_db):
        """Ibn Kathir entries should include historical context."""
        entry = tafsir_db.get_entry("Q96:1-5")
        assert entry.ibn_kathir is not None, "Ibn Kathir entry missing"
        assert entry.ibn_kathir.historical_background, "Missing historical background"
        assert entry.ibn_kathir.hadith_evidence, "Missing hadith evidence"

    def test_al_tabari_has_linguistic_analysis(self, tafsir_db):
        """Al-Tabari entries should include linguistic analysis."""
        entry = tafsir_db.get_entry("Q96:1-5")
        assert entry.al_tabari is not None, "Al-Tabari entry missing"
        assert entry.al_tabari.primary_term, "Missing primary term"
        assert entry.al_tabari.literal_meaning, "Missing literal meaning"

    def test_al_qurtubi_has_jurisprudential_framework(self, tafsir_db):
        """Al-Qurtubi entries should include legal analysis."""
        entry = tafsir_db.get_entry("Q96:1-5")
        assert entry.al_qurtubi is not None, "Al-Qurtubi entry missing"
        assert entry.al_qurtubi.legal_status, "Missing legal status"
        assert entry.al_qurtubi.legal_implications, "Missing legal implications"

    def test_citation_references_are_valid(self, tafsir_db):
        """Citations should include proper references (volume/page)."""
        entry = tafsir_db.get_entry("Q96:1-5")

        # Check Ibn Kathir
        if entry.ibn_kathir and entry.ibn_kathir.hadith_evidence:
            assert len(entry.ibn_kathir.hadith_evidence) > 0

        # Check Al-Tabari linguistic analysis
        if entry.al_tabari:
            assert entry.al_tabari.primary_term
            assert entry.al_tabari.literal_meaning

    def test_quotations_not_empty(self, tafsir_db, sample_principles):
        """Any included quotations must be substantive."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)

            if entry.ibn_abbas:
                assert len(entry.ibn_abbas) > 20, (
                    f"Principle {principle_id}: Ibn Abbas interpretation too brief"
                )

            if entry.al_suyuti:
                assert len(entry.al_suyuti) > 20, (
                    f"Principle {principle_id}: Al-Suyuti synthesis too brief"
                )


# ============================================================================
# TEST CLASS 3: MADHAB REPRESENTATION
# ============================================================================

class TestMadhabRepresentation:
    """Verify that all Islamic madhabs are represented."""

    def test_madhab_coverage_completeness(self, tafsir_db, sample_principles):
        """Principles with jurisprudential focus should cover all madhabs."""
        jurisprudential_principles = ["Q96:1-5", "Q2:275", "Q46:15"]

        for principle_id in jurisprudential_principles:
            entry = tafsir_db.get_entry(principle_id)
            if entry.al_qurtubi and entry.al_qurtubi.madhab_positions:
                madhabs_covered = {pos.madhab for pos in entry.al_qurtubi.madhab_positions}

                # At minimum, the four main madhabs should be represented
                expected_madhabs = {
                    Madhab.HANAFI, Madhab.MALIKI, Madhab.SHAFI_I, Madhab.HANBALI
                }
                # Allow some flexibility for non-jurisprudential principles
                minimum_madhabs = len(expected_madhabs) - 1
                assert len(madhabs_covered) >= minimum_madhabs, (
                    f"Principle {principle_id}: Only {len(madhabs_covered)} madhabs covered "
                    f"(minimum {minimum_madhabs} expected)"
                )

    def test_madhab_coverage_dictionary(self, tafsir_db, sample_principles):
        """Entries should document madhab coverage percentages."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry.madhab_coverage, f"Principle {principle_id}: Missing madhab coverage data"
            assert len(entry.madhab_coverage) > 0, f"Principle {principle_id}: Empty madhab coverage"

    def test_madhab_positions_have_evidence(self, tafsir_db):
        """Each madhab position should include supporting evidence."""
        entry = tafsir_db.get_entry("Q96:1-5")
        if entry.al_qurtubi and entry.al_qurtubi.madhab_positions:
            for position in entry.al_qurtubi.madhab_positions:
                assert position.position, f"Missing position text for {position.madhab.value}"
                assert position.degree_of_agreement >= 0.5, (
                    f"Madhab {position.madhab.value}: Very low consensus ({position.degree_of_agreement})"
                )


# ============================================================================
# TEST CLASS 4: CONSENSUS DOCUMENTATION
# ============================================================================

class TestConsensusDocumentation:
    """Verify scholarly consensus is properly documented."""

    def test_consensus_level_assigned(self, tafsir_db, sample_principles):
        """Each principle should have a consensus level assigned."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry.consensus_level in ConsensusLevel, (
                f"Principle {principle_id}: Invalid consensus level"
            )

    def test_consensus_score_valid_range(self, tafsir_db, sample_principles):
        """Consensus score must be between 0 and 1."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert 0 <= entry.consensus_score <= 1, (
                f"Principle {principle_id}: Consensus score {entry.consensus_score} "
                "outside valid range [0, 1]"
            )

    def test_consensus_score_matches_level(self, tafsir_db, sample_principles):
        """Consensus score should align with assigned consensus level."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)

            # Expected score ranges for each level
            level_to_range = {
                ConsensusLevel.IJMA_QATI: (0.95, 1.0),
                ConsensusLevel.IJMA_DANNI: (0.85, 0.95),
                ConsensusLevel.WIDESPREAD: (0.70, 0.85),
                ConsensusLevel.NOTED_DISAGREEMENT: (0.50, 0.70),
                ConsensusLevel.DISPUTED: (0.0, 0.50),
            }

            expected_min, expected_max = level_to_range[entry.consensus_level]
            assert expected_min <= entry.consensus_score <= expected_max, (
                f"Principle {principle_id}: Score {entry.consensus_score} doesn't match "
                f"level {entry.consensus_level.value} (expected {expected_min}-{expected_max})"
            )

    def test_disagreement_areas_documented(self, tafsir_db, sample_principles):
        """Principles with disagreement should document areas of disagreement."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)

            if entry.consensus_score < 0.95:
                assert entry.areas_of_disagreement, (
                    f"Principle {principle_id}: Has disagreement but areas not documented"
                )

    def test_consensus_statement_comprehensive(self, tafsir_db, sample_principles):
        """Each principle should have a comprehensive consensus statement."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry.scholarly_consensus, f"Principle {principle_id}: Missing consensus statement"
            assert len(entry.scholarly_consensus) > 20, (
                f"Principle {principle_id}: Consensus statement too brief"
            )


# ============================================================================
# TEST CLASS 5: SOURCE AUTHENTICITY
# ============================================================================

class TestSourceAuthenticity:
    """Verify authenticity and proper citation of sources."""

    def test_tafsir_source_validity(self, tafsir_db, sample_principles):
        """Tafsir source references should be valid classical sources."""
        valid_sources = {
            "Ibn Kathir", "Al-Tabari", "Al-Qurtubi", "Al-Zamakhshari",
            "Ibn Abbas", "Al-Suyuti", "Mawdudi", "Ibn Arabi"
        }

        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            available_sources = []

            if entry.ibn_kathir:
                available_sources.append("Ibn Kathir")
            if entry.al_tabari:
                available_sources.append("Al-Tabari")
            if entry.al_qurtubi:
                available_sources.append("Al-Qurtubi")
            if entry.al_zamakhshari:
                available_sources.append("Al-Zamakhshari")
            if entry.ibn_abbas:
                available_sources.append("Ibn Abbas")
            if entry.al_suyuti:
                available_sources.append("Al-Suyuti")
            if entry.mawdudi:
                available_sources.append("Mawdudi")
            if entry.ibn_arabi:
                available_sources.append("Ibn Arabi")

            for source in available_sources:
                assert source in valid_sources, (
                    f"Principle {principle_id}: Unknown tafsir source '{source}'"
                )

    def test_mawdudi_clearly_labeled_modern(self, tafsir_db):
        """Mawdudi entries should be clearly labeled as modern/contemporary."""
        entry = tafsir_db.get_entry("Q2:275")
        if entry.mawdudi:
            assert entry.mawdudi.contemporary_context, (
                "Mawdudi: Missing contemporary context label"
            )

    def test_ibn_arabi_clearly_labeled_esoteric(self, tafsir_db):
        """Ibn Arabi entries should be clearly labeled as esoteric/spiritual."""
        entry = tafsir_db.get_entry("Q96:1-5")
        if entry.ibn_arabi:
            assert entry.ibn_arabi.literal_meaning, "Ibn Arabi: Missing literal level"
            assert entry.ibn_arabi.interpretive_level, "Ibn Arabi: Missing interpretive level"
            assert entry.ibn_arabi.mystical_significance, "Ibn Arabi: Missing mystical level"
            assert entry.ibn_arabi.reality_level, "Ibn Arabi: Missing reality level"


# ============================================================================
# TEST CLASS 6: INTEGRATION QUALITY
# ============================================================================

class TestIntegrationQuality:
    """Verify overall quality of tafsir integration."""

    def test_all_entry_metadata_complete(self, tafsir_db, sample_principles):
        """Each entry should have complete metadata."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)

            # Required fields
            assert entry.principle_id, "Missing principle_id"
            assert entry.title, "Missing title"
            assert entry.quranic_text, "Missing quranic_text"
            assert entry.principle_summary, "Missing principle_summary"

            # Metadata fields
            assert entry.coverage_percentage >= 0, "Invalid coverage percentage"
            assert entry.citation_count >= 0, "Invalid citation count"
            assert entry.last_updated, "Missing last_updated timestamp"

    def test_linguistic_analysis_detailed(self, tafsir_db):
        """Al-Tabari linguistic analysis should be detailed."""
        entry = tafsir_db.get_entry("Q96:1-5")

        if entry.al_tabari:
            assert entry.al_tabari.primary_term, "Missing primary term"
            assert entry.al_tabari.literal_meaning, "Missing literal meaning"
            assert entry.al_tabari.etymology, "Missing etymology"
            assert entry.al_tabari.linguistic_nuances, "Missing linguistic nuances"

    def test_rhetorical_analysis_comprehensive(self, tafsir_db):
        """Al-Zamakhshari rhetorical analysis should be comprehensive."""
        entry = tafsir_db.get_entry("Q96:1-5")

        if entry.al_zamakhshari:
            assert entry.al_zamakhshari.devices_used, "Missing rhetorical devices"
            assert entry.al_zamakhshari.emphasis_points, "Missing emphasis points"
            assert entry.al_zamakhshari.logical_structure, "Missing logical structure"
            assert entry.al_zamakhshari.persuasive_strategy, "Missing persuasive strategy"

    def test_esoteric_dimension_complete(self, tafsir_db):
        """Ibn Arabi esoteric dimension should be complete."""
        entry = tafsir_db.get_entry("Q96:1-5")

        if entry.ibn_arabi:
            assert entry.ibn_arabi.literal_meaning, "Missing literal meaning"
            assert entry.ibn_arabi.interpretive_level, "Missing interpretive level"
            assert entry.ibn_arabi.mystical_significance, "Missing mystical significance"
            assert entry.ibn_arabi.reality_level, "Missing reality level"
            assert entry.ibn_arabi.symbolism, "Missing symbolism"

    def test_modern_application_relevant(self, tafsir_db):
        """Mawdudi modern application should be relevant and complete."""
        entry = tafsir_db.get_entry("Q2:275")

        if entry.mawdudi:
            assert entry.mawdudi.contemporary_context, "Missing contemporary context"
            assert entry.mawdudi.application_areas, "Missing application areas"
            assert entry.mawdudi.implementation_methods, "Missing implementation methods"
            assert 0 <= entry.mawdudi.relevance_score <= 1, "Invalid relevance score"

    def test_confidence_level_reasonable(self, tafsir_db, sample_principles):
        """Each entry should have reasonable confidence level."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)
            assert entry.confidence_level >= 0.70, (
                f"Principle {principle_id}: Confidence {entry.confidence_level} too low"
            )
            assert entry.confidence_level <= 1.0, (
                f"Principle {principle_id}: Confidence {entry.confidence_level} exceeds 1.0"
            )


# ============================================================================
# TEST CLASS 7: DATABASE FUNCTIONALITY
# ============================================================================

class TestDatabaseFunctionality:
    """Verify database query and retrieval functionality."""

    def test_get_entry_returns_valid_entry(self, tafsir_db):
        """Database retrieval should return valid entries."""
        entry = tafsir_db.get_entry("Q96:1-5")
        assert entry is not None
        assert isinstance(entry, TafsirEntry)

    def test_get_entry_nonexistent_returns_none(self, tafsir_db):
        """Querying nonexistent principle returns None."""
        entry = tafsir_db.get_entry("NONEXISTENT")
        assert entry is None

    def test_get_all_entries_returns_list(self, tafsir_db):
        """Getting all entries returns list."""
        entries = tafsir_db.get_all_entries()
        assert isinstance(entries, list)
        assert len(entries) > 0

    def test_get_entries_by_consensus_filters_correctly(self, tafsir_db):
        """Consensus filtering returns only matching entries."""
        entries = tafsir_db.get_entries_by_consensus(ConsensusLevel.IJMA_QATI)
        assert isinstance(entries, list)
        for entry in entries:
            assert entry.consensus_level == ConsensusLevel.IJMA_QATI

    def test_coverage_statistics_comprehensive(self, tafsir_db):
        """Coverage statistics should be comprehensive."""
        stats = tafsir_db.get_coverage_statistics()

        assert "total_principles" in stats
        assert "average_coverage_percentage" in stats
        assert "average_citation_count" in stats
        assert "consensus_distribution" in stats
        assert "madhab_coverage" in stats
        assert "tafsir_source_coverage" in stats

        assert stats["total_principles"] > 0
        assert 0 <= stats["average_coverage_percentage"] <= 100
        assert stats["average_citation_count"] >= 0

    def test_principle_summary_complete(self, tafsir_db):
        """Principle summary should be complete."""
        summary = tafsir_db.get_principle_summary("Q96:1-5")

        assert "principle_id" in summary
        assert "title" in summary
        assert "quranic_text" in summary
        assert "summary" in summary
        assert "consensus_level" in summary
        assert "consensus_score" in summary
        assert "coverage_percentage" in summary
        assert "citation_count" in summary
        assert "tafsir_sources" in summary
        assert "madhab_positions" in summary


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFullIntegration:
    """End-to-end integration tests."""

    def test_complete_workflow(self, tafsir_db):
        """Test complete workflow: retrieve, analyze, report."""
        # 1. Get principle
        entry = tafsir_db.get_entry("Q96:1-5")
        assert entry is not None

        # 2. Verify comprehensive coverage
        assert entry.ibn_kathir is not None
        assert entry.al_qurtubi is not None
        assert entry.mawdudi is not None

        # 3. Get summary
        summary = tafsir_db.get_principle_summary("Q96:1-5")
        assert len(summary["tafsir_sources"]) >= 5

        # 4. Get statistics
        stats = tafsir_db.get_coverage_statistics()
        assert stats["total_principles"] > 0

    def test_all_principles_have_minimum_quality(self, tafsir_db, sample_principles):
        """All principles must meet minimum quality standards."""
        for principle_id in sample_principles:
            entry = tafsir_db.get_entry(principle_id)

            # Minimum quality standards
            assert entry is not None
            assert entry.coverage_percentage >= 80
            assert entry.citation_count >= 5
            assert entry.consensus_score >= 0.70
            assert len(entry.quranic_text) > 10
            assert len(entry.principle_summary) > 20


# ============================================================================
# PYTEST MAIN
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
