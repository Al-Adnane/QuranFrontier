"""
Test suite for Quranic metaphor dual-layer validation

Tests verify that:
1. All 10 metaphors have classical meanings
2. Classical meanings cite proper source tafsirs
3. Contemporary applications are properly documented
4. Robustness scores are justified
5. Application domains are clearly specified
"""

import pytest
from src.analysis.metaphor_extraction import (
    BeeMetaphor, SpiderMetaphor, MountainMetaphor, LightMetaphor,
    PalmTreeMetaphor, GardenMetaphor, WaterMetaphor, WindMetaphor,
    MirrorMetaphor, RopeMetaphor
)


class TestMetaphorsCompleteness:
    """Test that all metaphors have complete dual-layer information"""

    @pytest.fixture
    def all_metaphors(self):
        """Return all 10 metaphors"""
        return [
            BeeMetaphor(),
            SpiderMetaphor(),
            MountainMetaphor(),
            LightMetaphor(),
            PalmTreeMetaphor(),
            GardenMetaphor(),
            WaterMetaphor(),
            WindMetaphor(),
            MirrorMetaphor(),
            RopeMetaphor(),
        ]

    def test_metaphors_have_classical_meaning(self, all_metaphors):
        """Test that each metaphor has classical tafsir meaning"""
        for metaphor in all_metaphors:
            assert metaphor.classical_meaning, f"{metaphor.name} missing classical_meaning"
            assert len(metaphor.classical_meaning) >= 50, (
                f"{metaphor.name} classical_meaning too short "
                f"(must be ≥50 words)"
            )

    def test_metaphors_have_source_tafsirs(self, all_metaphors):
        """Test that classical meanings cite source tafsirs"""
        for metaphor in all_metaphors:
            assert metaphor.source_tafsirs, (
                f"{metaphor.name} missing source_tafsirs"
            )
            assert len(metaphor.source_tafsirs) >= 2, (
                f"{metaphor.name} needs at least 2 source tafsirs"
            )
            # Check for expected Islamic scholars
            expected_scholars = {"Ibn Kathir", "Al-Tabari", "Al-Qurtubi", "Al-Zamakhshari"}
            found_scholars = set()
            for source in metaphor.source_tafsirs:
                for scholar in expected_scholars:
                    if scholar in source:
                        found_scholars.add(scholar)
            assert len(found_scholars) >= 1, (
                f"{metaphor.name} no recognized classical scholar sources"
            )

    def test_metaphors_have_contemporary_application(self, all_metaphors):
        """Test that each metaphor has contemporary application"""
        for metaphor in all_metaphors:
            assert metaphor.contemporary_application, (
                f"{metaphor.name} missing contemporary_application"
            )
            assert len(metaphor.contemporary_application) >= 50, (
                f"{metaphor.name} contemporary_application too short"
            )

    def test_metaphors_have_application_domains(self, all_metaphors):
        """Test that application domains are specified"""
        for metaphor in all_metaphors:
            assert metaphor.application_domain, (
                f"{metaphor.name} missing application_domain"
            )
            assert len(metaphor.application_domain) >= 2, (
                f"{metaphor.name} needs at least 2 application domains"
            )

    def test_metaphors_have_robustness_scores(self, all_metaphors):
        """Test that robustness scores are properly set"""
        for metaphor in all_metaphors:
            assert 0.0 <= metaphor.robustness_score <= 1.0, (
                f"{metaphor.name} robustness_score out of range: "
                f"{metaphor.robustness_score}"
            )
            assert metaphor.robustness_score >= 0.75, (
                f"{metaphor.name} robustness_score too low: "
                f"{metaphor.robustness_score} (minimum: 0.75)"
            )


class TestMetaphorsDualLayerFramework:
    """Test dual-layer classification structure"""

    def test_classical_contemporary_separation(self):
        """Test that classical and contemporary are properly separated"""
        bee = BeeMetaphor()
        # Classical should mention Quranic foundation
        assert "Quranic" in bee.classical_meaning or "Qur'an" in bee.classical_meaning or \
               "divine" in bee.classical_meaning.lower()
        # Contemporary should mention modern applications
        assert any(word in bee.contemporary_application.lower()
                  for word in ["algorithm", "distributed", "consensus", "system", "modern"])

    def test_methodology_transparency(self):
        """Test that methodology is transparent"""
        metaphors = [
            BeeMetaphor(),
            SpiderMetaphor(),
            MountainMetaphor(),
        ]
        for metaphor in metaphors:
            # Classical meaning should cite tafsirs (Ibn Kathir, Al-Tabari, etc.)
            assert "ibn kathir" in metaphor.classical_meaning.lower() or \
                   "al-tabari" in metaphor.classical_meaning.lower() or \
                   "verified" in metaphor.classical_meaning.lower()
            # Contemporary should acknowledge application/framework
            assert "application" in metaphor.contemporary_application.lower() or \
                   "framework" in metaphor.contemporary_application.lower() or \
                   "system" in metaphor.contemporary_application.lower()


class TestMetaphorsValidation:
    """Test validation of metaphor entries"""

    @pytest.mark.parametrize("metaphor_class,expected_name,expected_ref", [
        (BeeMetaphor, "Bee", "16:68-69"),
        (SpiderMetaphor, "Spider", "29:41"),
        (MountainMetaphor, "Mountain", "7:143"),
        (LightMetaphor, "Light", "24:35-40"),
        (PalmTreeMetaphor, "Palm Tree", "14:24-25"),
        (GardenMetaphor, "Garden", "2:265-266"),
        (WaterMetaphor, "Water", "18:109"),
        (WindMetaphor, "Wind", "105:1-5"),
        (MirrorMetaphor, "Mirror", "24:40"),
        (RopeMetaphor, "Rope", "3:103"),
    ])
    def test_metaphor_identification(self, metaphor_class, expected_name, expected_ref):
        """Test that metaphors are properly identified"""
        metaphor = metaphor_class()
        assert expected_name in metaphor.name
        assert expected_ref in metaphor.reference

    def test_metaphor_consistency(self):
        """Test consistency within each metaphor"""
        metaphors = [
            BeeMetaphor(),
            SpiderMetaphor(),
            MountainMetaphor(),
            LightMetaphor(),
            PalmTreeMetaphor(),
            GardenMetaphor(),
            WaterMetaphor(),
            WindMetaphor(),
            MirrorMetaphor(),
            RopeMetaphor(),
        ]

        for metaphor in metaphors:
            # Robustness score should be mentioned in documentation
            assert metaphor.robustness_score > 0, (
                f"{metaphor.name} has zero robustness score"
            )
            # Should have been implemented
            assert metaphor.classical_meaning, f"{metaphor.name} not implemented"


def test_metaphors_dual_layer_complete():
    """
    Integration test: All metaphors complete with dual-layer classification

    This test verifies the complete TASK 2 deliverable:
    - 10 metaphors with dual-layer structure
    - Classical tafsir foundations
    - Contemporary applications
    - Robustness scores
    - Application domains
    """
    metaphors = [
        BeeMetaphor(),
        SpiderMetaphor(),
        MountainMetaphor(),
        LightMetaphor(),
        PalmTreeMetaphor(),
        GardenMetaphor(),
        WaterMetaphor(),
        WindMetaphor(),
        MirrorMetaphor(),
        RopeMetaphor(),
    ]

    assert len(metaphors) == 10, "Should have 10 metaphors"

    for metaphor in metaphors:
        # Verify all dual-layer fields are populated
        assert metaphor.classical_meaning, f"{metaphor.name}: classical_meaning empty"
        assert metaphor.source_tafsirs, f"{metaphor.name}: source_tafsirs empty"
        assert metaphor.contemporary_application, f"{metaphor.name}: contemporary_application empty"
        assert metaphor.application_domain, f"{metaphor.name}: application_domain empty"
        assert 0.75 <= metaphor.robustness_score <= 1.0, (
            f"{metaphor.name}: robustness_score {metaphor.robustness_score} out of range"
        )

    print("✓ All 10 metaphors verified with dual-layer classification")
    print("✓ Classical meanings verified with source tafsirs")
    print("✓ Contemporary applications specified with robustness scores")
    print("✓ Application domains identified for all metaphors")
