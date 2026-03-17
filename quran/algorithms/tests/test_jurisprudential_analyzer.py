"""Tests for quran/algorithms/jurisprudential_analyzer.py – Algorithm 4.

Covers:
1. calculate_evidence_strength returns correct weighted sum
2. find_school_positions finds positions for a "wine" question
3. determine_confidence returns HIGH when all schools agree
4. determine_confidence returns LOW when schools disagree
5. build_qiyas_argument derives HARAM ruling from wine analogy for "beer"
6. analyze returns JurisprudentialAnalysis with non-empty school_positions
7. calculate_istislah_score returns > 0.5 for obligatory (FARD) ruling
8. compare_schools returns a dict keyed by school name
9. build_disagreement_graph detects consensus when all agree
10. build_qiyas_argument returns None for unknown analogous case
"""

import sys
import os

# Ensure the algorithms package is importable from the repository root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from quran.algorithms.jurisprudential_analyzer import (
    IslamicJurisprudenceAnalyzer,
    EvidenceType,
    Evidence,
    SchoolPosition,
    JurisprudentialSchool,
    IslamicRuling,
    ConfidenceLevel,
    JurisprudentialAnalysis,
    QiyasArgument,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def analyzer():
    return IslamicJurisprudenceAnalyzer()


def _make_evidence(ev_type: EvidenceType, reliability: float) -> Evidence:
    return Evidence(
        source="test-source",
        evidence_type=ev_type,
        text="test evidence text",
        reliability=reliability,
    )


# ---------------------------------------------------------------------------
# Test 1 – calculate_evidence_strength returns correct weighted sum
# ---------------------------------------------------------------------------

class TestCalculateEvidenceStrength:
    def test_single_quran_evidence_full_reliability(self, analyzer):
        """One Quran evidence with reliability 1.0 -> weight = 1.0*1.0 = 1.0; /2 = 0.5."""
        ev = _make_evidence(EvidenceType.QURAN, 1.0)
        result = analyzer.calculate_evidence_strength([ev])
        assert abs(result - 0.5) < 1e-9

    def test_two_high_weight_evidence_capped_at_one(self, analyzer):
        """Two Quran evidences each with reliability 1.0 -> total 2.0; /2 = 1.0."""
        ev1 = _make_evidence(EvidenceType.QURAN, 1.0)
        ev2 = _make_evidence(EvidenceType.QURAN, 1.0)
        result = analyzer.calculate_evidence_strength([ev1, ev2])
        assert result == 1.0

    def test_empty_list_returns_zero(self, analyzer):
        result = analyzer.calculate_evidence_strength([])
        assert result == 0.0

    def test_weighted_sum_correct(self, analyzer):
        """QIYAS (0.70) × 0.5 = 0.35; ISTIHSAN (0.60) × 0.5 = 0.30 -> total 0.65; /2 = 0.325."""
        ev1 = _make_evidence(EvidenceType.QIYAS, 0.5)
        ev2 = _make_evidence(EvidenceType.ISTIHSAN, 0.5)
        result = analyzer.calculate_evidence_strength([ev1, ev2])
        expected = min(1.0, (0.70 * 0.5 + 0.60 * 0.5) / 2.0)
        assert abs(result - expected) < 1e-9


# ---------------------------------------------------------------------------
# Test 2 – find_school_positions finds positions for "wine" question
# ---------------------------------------------------------------------------

class TestFindSchoolPositions:
    def test_wine_question_returns_four_schools(self, analyzer):
        positions = analyzer.find_school_positions("Is wine forbidden?")
        assert len(positions) == 4

    def test_wine_positions_are_haram(self, analyzer):
        positions = analyzer.find_school_positions("Is wine permissible in Islam?")
        for school, sp in positions.items():
            assert sp.ruling == IslamicRuling.HARAM, (
                f"{school.value} should be HARAM for wine"
            )

    def test_unknown_question_returns_empty(self, analyzer):
        positions = analyzer.find_school_positions("What is the colour of the sky?")
        assert positions == {}

    def test_prayer_question_found(self, analyzer):
        positions = analyzer.find_school_positions("Is salah obligatory?")
        assert len(positions) == 4


# ---------------------------------------------------------------------------
# Test 3 – determine_confidence returns HIGH when all schools agree
# ---------------------------------------------------------------------------

class TestDetermineConfidenceHigh:
    def test_all_agree_returns_high(self, analyzer):
        ev = _make_evidence(EvidenceType.QURAN, 1.0)
        positions = {
            JurisprudentialSchool.HANAFI: SchoolPosition(
                school=JurisprudentialSchool.HANAFI,
                ruling=IslamicRuling.HARAM,
                reasoning="test",
                evidence=[ev],
            ),
            JurisprudentialSchool.MALIKI: SchoolPosition(
                school=JurisprudentialSchool.MALIKI,
                ruling=IslamicRuling.HARAM,
                reasoning="test",
                evidence=[ev],
            ),
            JurisprudentialSchool.SHAFI: SchoolPosition(
                school=JurisprudentialSchool.SHAFI,
                ruling=IslamicRuling.HARAM,
                reasoning="test",
                evidence=[ev],
            ),
            JurisprudentialSchool.HANBALI: SchoolPosition(
                school=JurisprudentialSchool.HANBALI,
                ruling=IslamicRuling.HARAM,
                reasoning="test",
                evidence=[ev],
            ),
        }
        confidence = analyzer.determine_confidence(positions)
        assert confidence == ConfidenceLevel.HIGH

    def test_wine_analysis_returns_high_confidence(self, analyzer):
        """Wine is unanimous across schools -> should be HIGH."""
        positions = analyzer.find_school_positions("Is wine permissible?")
        confidence = analyzer.determine_confidence(positions)
        assert confidence == ConfidenceLevel.HIGH


# ---------------------------------------------------------------------------
# Test 4 – determine_confidence returns LOW when schools disagree
# ---------------------------------------------------------------------------

class TestDetermineConfidenceLow:
    def test_split_schools_returns_low(self, analyzer):
        ev = _make_evidence(EvidenceType.QURAN, 1.0)
        positions = {
            JurisprudentialSchool.HANAFI: SchoolPosition(
                school=JurisprudentialSchool.HANAFI,
                ruling=IslamicRuling.HARAM,
                reasoning="test",
                evidence=[ev],
            ),
            JurisprudentialSchool.MALIKI: SchoolPosition(
                school=JurisprudentialSchool.MALIKI,
                ruling=IslamicRuling.MAKRUH,
                reasoning="test",
                evidence=[ev],
            ),
        }
        confidence = analyzer.determine_confidence(positions)
        assert confidence == ConfidenceLevel.LOW

    def test_empty_positions_returns_low(self, analyzer):
        confidence = analyzer.determine_confidence({})
        assert confidence == ConfidenceLevel.LOW


# ---------------------------------------------------------------------------
# Test 5 – build_qiyas_argument derives HARAM ruling for "beer" via wine
# ---------------------------------------------------------------------------

class TestBuildQiyasArgument:
    def test_beer_by_wine_analogy_is_haram(self, analyzer):
        qarg = analyzer.build_qiyas_argument("Is beer forbidden?", "wine")
        assert qarg is not None
        assert qarg.valid is True
        assert qarg.derived_ruling == IslamicRuling.HARAM

    def test_beer_analogy_effective_cause_is_intoxication(self, analyzer):
        qarg = analyzer.build_qiyas_argument("Is beer forbidden?", "wine")
        assert qarg.effective_cause == "intoxication"

    def test_cause_similarity_is_positive(self, analyzer):
        qarg = analyzer.build_qiyas_argument("Is beer forbidden?", "wine")
        assert qarg.cause_similarity >= 0.0

    def test_unknown_analogous_case_returns_none(self, analyzer):
        qarg = analyzer.build_qiyas_argument("Is coffee allowed?", "unknown_case")
        assert qarg is None


# ---------------------------------------------------------------------------
# Test 6 – analyze returns JurisprudentialAnalysis with non-empty school_positions
# ---------------------------------------------------------------------------

class TestAnalyze:
    def test_returns_jurisprudential_analysis_type(self, analyzer):
        result = analyzer.analyze("Is wine permissible?")
        assert isinstance(result, JurisprudentialAnalysis)

    def test_wine_school_positions_non_empty(self, analyzer):
        result = analyzer.analyze("Is wine permissible?")
        assert len(result.school_positions) > 0

    def test_wine_recommended_ruling_is_haram(self, analyzer):
        result = analyzer.analyze("Is wine permissible?")
        assert result.recommended_ruling == IslamicRuling.HARAM

    def test_prayer_analysis_returns_fard(self, analyzer):
        result = analyzer.analyze("Is daily prayer obligatory?")
        assert result.recommended_ruling == IslamicRuling.FARD

    def test_reasoning_summary_non_empty(self, analyzer):
        result = analyzer.analyze("Is fasting during Ramadan obligatory?")
        assert isinstance(result.reasoning_summary, str)
        assert len(result.reasoning_summary) > 0

    def test_confidence_is_confidence_level_enum(self, analyzer):
        result = analyzer.analyze("Is zakat obligatory?")
        assert isinstance(result.confidence, ConfidenceLevel)


# ---------------------------------------------------------------------------
# Test 7 – calculate_istislah_score returns > 0.5 for obligatory ruling
# ---------------------------------------------------------------------------

class TestCalculateIstislahScore:
    def test_fard_ruling_score_above_half(self, analyzer):
        score = analyzer.calculate_istislah_score(IslamicRuling.FARD)
        assert score > 0.5, f"Expected > 0.5 for FARD, got {score}"

    def test_wajib_ruling_score_above_half(self, analyzer):
        score = analyzer.calculate_istislah_score(IslamicRuling.WAJIB)
        assert score > 0.5

    def test_haram_ruling_score_is_positive(self, analyzer):
        """HARAM represents preventing harm, score should be positive."""
        score = analyzer.calculate_istislah_score(IslamicRuling.HARAM)
        assert score > 0.0

    def test_score_bounded_zero_to_one(self, analyzer):
        for ruling in IslamicRuling:
            score = analyzer.calculate_istislah_score(ruling)
            assert 0.0 <= score <= 1.0, f"Score out of bounds for {ruling}: {score}"


# ---------------------------------------------------------------------------
# Test 8 – compare_schools returns dict keyed by school name
# ---------------------------------------------------------------------------

class TestCompareSchools:
    def test_returns_dict_with_school_names(self, analyzer):
        result = analyzer.compare_schools("Is wine permissible?")
        assert isinstance(result, dict)
        assert len(result) == 4
        for key in result:
            assert isinstance(key, str)

    def test_each_entry_has_ruling_key(self, analyzer):
        result = analyzer.compare_schools("Is wine permissible?")
        for school_name, data in result.items():
            assert "ruling" in data
            assert "reasoning" in data
            assert "strength" in data


# ---------------------------------------------------------------------------
# Test 9 – build_disagreement_graph detects consensus when all agree
# ---------------------------------------------------------------------------

class TestBuildDisagreementGraph:
    def test_wine_has_consensus(self, analyzer):
        graph = analyzer.build_disagreement_graph("Is wine permissible?")
        assert graph["consensus"] is True
        assert len(graph["disagreements"]) == 0

    def test_graph_has_expected_keys(self, analyzer):
        graph = analyzer.build_disagreement_graph("Is wine permissible?")
        assert "agreements" in graph
        assert "disagreements" in graph
        assert "ruling_clusters" in graph
        assert "consensus" in graph

    def test_ruling_clusters_contains_haram_for_wine(self, analyzer):
        graph = analyzer.build_disagreement_graph("Is wine permissible?")
        assert "forbidden" in graph["ruling_clusters"]
        assert len(graph["ruling_clusters"]["forbidden"]) == 4


# ---------------------------------------------------------------------------
# Test 10 – evidence weight property
# ---------------------------------------------------------------------------

class TestEvidenceWeight:
    def test_quran_full_reliability_weight_is_one(self):
        ev = Evidence(source="Q5:90", evidence_type=EvidenceType.QURAN,
                      text="O believers", reliability=1.0)
        assert ev.weight == pytest.approx(1.0)

    def test_qiyas_half_reliability(self):
        ev = Evidence(source="analogy", evidence_type=EvidenceType.QIYAS,
                      text="by analogy", reliability=0.5)
        assert ev.weight == pytest.approx(0.35)
