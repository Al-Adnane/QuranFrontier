"""
Comprehensive test suite for Q-SDK Mirah (Q4:11 Inheritance Algorithm)

Tests cover:
- Data model integrity
- Algorithm correctness (children, parents, siblings inheritance)
- Mathematical precision (fractions, gender ratio)
- Quranic compliance (Q4:11 adherence)
- Maqasid al-Shariah validation (5 objectives)
- Edge cases and error handling
- Classical madhab variations

Test organization (TDD approach):
1. Model tests - verify data structures
2. Algorithm core tests - basic distributions
3. Case-specific tests - iddah, qibla, etc. from classical sources
4. Validation tests - Maqasid verification
5. Edge case tests - error conditions
"""

import pytest
from fractions import Fraction
from datetime import datetime

from q_sdk import (
    # Models
    Relationship, Gender, HeritageDisqualification, MadhabSchool,
    ValidationStatus, Heir, Bequest, InheritanceCase,
    ShareDistribution, InheritanceDistributionResult,
    # Algorithm
    MirahAlgorithm, MirahAlgorithmError, NoQualifiedHeirsError,
    NegativeEstateError,
    # Validation
    MaqasidObjective, MaqasidValidator,
)


# ========== MODEL TESTS ==========

class TestHeirModel:
    """Test Heir dataclass"""

    def test_heir_creation_qualified(self):
        """Create a qualified heir"""
        heir = Heir(
            name="Ahmed",
            gender=Gender.MALE,
            relationship=Relationship.CHILD
        )
        assert heir.is_qualified
        assert heir.disqualified == HeritageDisqualification.NONE

    def test_heir_creation_disqualified(self):
        """Create a disqualified heir (murderer)"""
        heir = Heir(
            name="Hassan",
            gender=Gender.MALE,
            relationship=Relationship.CHILD,
            disqualified=HeritageDisqualification.MURDERER
        )
        assert not heir.is_qualified
        assert heir.disqualified == HeritageDisqualification.MURDERER

    def test_heir_age_category_minor(self):
        """Heir age categorization: minor"""
        heir = Heir(
            name="Young",
            gender=Gender.FEMALE,
            relationship=Relationship.CHILD,
            birth_year=datetime.now().year - 10
        )
        assert heir.age_category == "minor"

    def test_heir_age_category_adult(self):
        """Heir age categorization: adult"""
        heir = Heir(
            name="Adult",
            gender=Gender.MALE,
            relationship=Relationship.CHILD,
            birth_year=datetime.now().year - 35
        )
        assert heir.age_category == "adult"

    def test_heir_age_category_senior(self):
        """Heir age categorization: senior"""
        heir = Heir(
            name="Elder",
            gender=Gender.FEMALE,
            relationship=Relationship.PARENT,
            birth_year=datetime.now().year - 75
        )
        assert heir.age_category == "senior"


class TestInheritanceCaseModel:
    """Test InheritanceCase dataclass"""

    def test_case_creation_minimal(self):
        """Create minimal inheritance case"""
        case = InheritanceCase(
            deceased_name="Muhammad",
            deceased_death_year=2024,
            estate_value=Fraction(100_000)
        )
        assert case.deceased_name == "Muhammad"
        assert case.distributable_estate == Fraction(100_000)

    def test_case_with_heirs(self):
        """Create case with heirs"""
        heir1 = Heir("Son", Gender.MALE, Relationship.CHILD)
        heir2 = Heir("Daughter", Gender.FEMALE, Relationship.CHILD)

        case = InheritanceCase(
            deceased_name="Abdullah",
            deceased_death_year=2024,
            estate_value=Fraction(600_000),
            heirs=[heir1, heir2]
        )

        assert len(case.heirs) == 2
        assert len(case.qualified_heirs) == 2
        assert case.get_heirs_by_relationship(Relationship.CHILD) == [heir1, heir2]

    def test_case_with_debts(self):
        """Estate with debts deducted"""
        case = InheritanceCase(
            deceased_name="Hassan",
            deceased_death_year=2024,
            estate_value=Fraction(100_000),
            debts=Fraction(20_000)
        )
        assert case.distributable_estate == Fraction(80_000)

    def test_case_with_bequests(self):
        """Estate with testamentary bequests"""
        bequest = Bequest(
            beneficiary="Mosque",
            amount=Fraction(10_000),
            description="Building endowment"
        )
        case = InheritanceCase(
            deceased_name="Ali",
            deceased_death_year=2024,
            estate_value=Fraction(100_000),
            bequests=[bequest]
        )
        assert case.total_debts_and_bequests == Fraction(10_000)
        assert case.distributable_estate == Fraction(90_000)

    def test_case_qualified_vs_disqualified_heirs(self):
        """Separate qualified and disqualified heirs"""
        heir_qualified = Heir("Son", Gender.MALE, Relationship.CHILD)
        heir_disqualified = Heir(
            "Apostate",
            Gender.MALE,
            Relationship.CHILD,
            disqualified=HeritageDisqualification.APOSTATE
        )

        case = InheritanceCase(
            deceased_name="Muhammad",
            deceased_death_year=2024,
            estate_value=Fraction(100_000),
            heirs=[heir_qualified, heir_disqualified]
        )

        assert len(case.qualified_heirs) == 1
        assert len(case.disqualified_heirs) == 1


# ========== ALGORITHM CORE TESTS ==========

class TestMirahAlgorithmChildren:
    """Test Q4:11 child inheritance: male = 2 × female"""

    def test_single_son_only(self):
        """Single son inherits entire estate"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(100_000),
            heirs=[Heir("Son", Gender.MALE, Relationship.CHILD)]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        assert len(result.distributions) == 1
        assert result.distributions["Son"].absolute_amount == Fraction(100_000)
        assert result.distributions["Son"].share_percentage == 100.0

    def test_single_daughter_only(self):
        """Single daughter inherits entire estate"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(100_000),
            heirs=[Heir("Daughter", Gender.FEMALE, Relationship.CHILD)]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        assert len(result.distributions) == 1
        assert result.distributions["Daughter"].absolute_amount == Fraction(100_000)

    def test_one_son_one_daughter_2_to_1_ratio(self):
        """Q4:11: Son and daughter - male gets 2:1 ratio"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(300),  # Use 300 for clean thirds
            heirs=[
                Heir("Son", Gender.MALE, Relationship.CHILD),
                Heir("Daughter", Gender.FEMALE, Relationship.CHILD),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        son_amount = result.distributions["Son"].absolute_amount
        daughter_amount = result.distributions["Daughter"].absolute_amount

        # Son should get 2/3, daughter 1/3
        assert son_amount == Fraction(200)
        assert daughter_amount == Fraction(100)
        assert son_amount / daughter_amount == Fraction(2, 1)

    def test_two_sons_one_daughter(self):
        """Two sons and one daughter"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(500),
            heirs=[
                Heir("Son1", Gender.MALE, Relationship.CHILD),
                Heir("Son2", Gender.MALE, Relationship.CHILD),
                Heir("Daughter", Gender.FEMALE, Relationship.CHILD),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        # Total units: 2+2+1 = 5
        # Son1: 2 units = 200, Son2: 2 units = 200, Daughter: 1 unit = 100
        assert result.distributions["Son1"].absolute_amount == Fraction(200)
        assert result.distributions["Son2"].absolute_amount == Fraction(200)
        assert result.distributions["Daughter"].absolute_amount == Fraction(100)

    def test_one_son_two_daughters(self):
        """One son and two daughters"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(400),
            heirs=[
                Heir("Son", Gender.MALE, Relationship.CHILD),
                Heir("Daughter1", Gender.FEMALE, Relationship.CHILD),
                Heir("Daughter2", Gender.FEMALE, Relationship.CHILD),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        # Total units: 2+1+1 = 4
        # Son: 2 units = 200, each daughter: 1 unit = 100
        assert result.distributions["Son"].absolute_amount == Fraction(200)
        assert result.distributions["Daughter1"].absolute_amount == Fraction(100)
        assert result.distributions["Daughter2"].absolute_amount == Fraction(100)


class TestMirahAlgorithmParents:
    """Test Q4:11 parent inheritance (no children)"""

    def test_both_parents_1_6_each(self):
        """Both parents: 1/6 each (Q4:11 explicit)"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(600),
            heirs=[
                Heir("Father", Gender.MALE, Relationship.PARENT),
                Heir("Mother", Gender.FEMALE, Relationship.PARENT),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        # Mother: 1/6 = 100
        # Father: 1/6 + remainder = 500
        assert result.distributions["Mother"].absolute_amount == Fraction(100)
        assert result.distributions["Father"].absolute_amount == Fraction(500)

    def test_mother_only_no_siblings_1_3(self):
        """Mother only (no children/siblings): 1/3 (Q4:11 explicit)"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(300),
            heirs=[
                Heir("Mother", Gender.FEMALE, Relationship.PARENT),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        # Mother: 1/3 = 100
        assert result.distributions["Mother"].absolute_amount == Fraction(100)
        assert result.distributions["Mother"].share_fraction == Fraction(1, 3)

    def test_mother_with_siblings_1_6(self):
        """Mother with siblings: 1/6 (Q4:11 explicit when siblings present)"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(600),
            heirs=[
                Heir("Mother", Gender.FEMALE, Relationship.PARENT),
                Heir("Brother", Gender.MALE, Relationship.SIBLING),
                Heir("Sister", Gender.FEMALE, Relationship.SIBLING),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        # Mother: 1/6 = 100 (reduced due to siblings)
        assert result.distributions["Mother"].absolute_amount == Fraction(100)
        assert result.distributions["Mother"].share_fraction == Fraction(1, 6)


class TestMirahAlgorithmSiblings:
    """Test sibling inheritance (no children/parents)"""

    def test_one_brother_one_sister_2_1_ratio(self):
        """Brother and sister: 2:1 ratio"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(300),
            heirs=[
                Heir("Brother", Gender.MALE, Relationship.SIBLING),
                Heir("Sister", Gender.FEMALE, Relationship.SIBLING),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        # Brother: 2/3 = 200, Sister: 1/3 = 100
        assert result.distributions["Brother"].absolute_amount == Fraction(200)
        assert result.distributions["Sister"].absolute_amount == Fraction(100)


# ========== VALIDATION TESTS ==========

class TestMaqasidValidation:
    """Test Maqasid al-Shariah validation"""

    def test_simple_case_passes_all_maqasid(self):
        """Simple child distribution passes all 5 Maqasid objectives"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(300),
            heirs=[
                Heir("Son", Gender.MALE, Relationship.CHILD),
                Heir("Daughter", Gender.FEMALE, Relationship.CHILD),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        validator = MaqasidValidator()
        validations = validator.validate_distribution(result)

        # All 5 objectives should pass
        for objective, validation in validations.items():
            assert validation.is_valid, f"{objective.value} failed"

    def test_maqasid_faith_quranic_basis(self):
        """Maqasid 1 (Faith): All shares have Quranic basis"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(100),
            heirs=[Heir("Son", Gender.MALE, Relationship.CHILD)]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        validator = MaqasidValidator()
        validations = validator.validate_distribution(result)

        faith_validation = validations[MaqasidObjective.PROTECTION_OF_FAITH]
        assert faith_validation.score >= 0.85

    def test_maqasid_intellect_mathematical_precision(self):
        """Maqasid 3 (Intellect): Distribution is mathematically precise"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(600),
            heirs=[
                Heir("Son", Gender.MALE, Relationship.CHILD),
                Heir("Daughter", Gender.FEMALE, Relationship.CHILD),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        validator = MaqasidValidator()
        validations = validator.validate_distribution(result)

        intellect_validation = validations[MaqasidObjective.PROTECTION_OF_INTELLECT]
        # Must be high - system is deterministic
        assert intellect_validation.score >= 0.85


# ========== EDGE CASE & ERROR TESTS ==========

class TestEdgeCasesAndErrors:
    """Test error conditions and edge cases"""

    def test_no_qualified_heirs_raises_error(self):
        """No qualified heirs raises error"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(100),
            heirs=[
                Heir(
                    "Apostate",
                    Gender.MALE,
                    Relationship.CHILD,
                    disqualified=HeritageDisqualification.APOSTATE
                )
            ]
        )

        algo = MirahAlgorithm(strict_mode=True)
        with pytest.raises(NoQualifiedHeirsError):
            algo.distribute_inheritance(case)

    def test_negative_distributable_estate_raises_error(self):
        """Estate becomes negative after debts - raises error"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(100),
            debts=Fraction(200),  # Debts > estate
            heirs=[Heir("Son", Gender.MALE, Relationship.CHILD)]
        )

        algo = MirahAlgorithm(strict_mode=True)
        with pytest.raises(NegativeEstateError):
            algo.distribute_inheritance(case)

    def test_result_is_balanced(self):
        """Verify distribution result is balanced"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(1_000_000),
            heirs=[
                Heir("Son", Gender.MALE, Relationship.CHILD),
                Heir("Daughter", Gender.FEMALE, Relationship.CHILD),
            ]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        # Verify total distributed = distributable estate
        assert result.is_balanced
        assert result.total_distributed == case.distributable_estate

    def test_audit_trail_recorded(self):
        """Verify audit trail is recorded"""
        case = InheritanceCase(
            deceased_name="Test",
            deceased_death_year=2024,
            estate_value=Fraction(100),
            heirs=[Heir("Son", Gender.MALE, Relationship.CHILD)]
        )

        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        assert len(result.audit_trail) > 0
        assert any("Child distribution" in entry for entry in result.audit_trail)


# ========== CLASSICAL MADHAB TESTS ==========

class TestMadhabVariations:
    """Test madhab-specific variations"""

    def test_algorithm_supports_hanafi_school(self):
        """Algorithm can be initialized with Hanafi madhab"""
        algo = MirahAlgorithm(madhab=MadhabSchool.HANAFI)
        assert algo.madhab == MadhabSchool.HANAFI

    def test_algorithm_supports_maliki_school(self):
        """Algorithm can be initialized with Maliki madhab"""
        algo = MirahAlgorithm(madhab=MadhabSchool.MALIKI)
        assert algo.madhab == MadhabSchool.MALIKI

    def test_algorithm_supports_shafii_school(self):
        """Algorithm can be initialized with Shafi'i madhab"""
        algo = MirahAlgorithm(madhab=MadhabSchool.SHAFI_I)
        assert algo.madhab == MadhabSchool.SHAFI_I

    def test_algorithm_supports_hanbali_school(self):
        """Algorithm can be initialized with Hanbali madhab"""
        algo = MirahAlgorithm(madhab=MadhabSchool.HANBALI)
        assert algo.madhab == MadhabSchool.HANBALI


# ========== INTEGRATION TESTS ==========

class TestIntegration:
    """End-to-end integration tests"""

    def test_full_distribution_workflow(self):
        """Complete workflow: create case → distribute → validate"""
        # Create inheritance case
        case = InheritanceCase(
            deceased_name="Muhammad ibn Abdullah",
            deceased_death_year=2024,
            estate_value=Fraction(1_000_000),
            estate_currency="USD",
            heirs=[
                Heir("Ali (son)", Gender.MALE, Relationship.CHILD),
                Heir("Fatima (daughter)", Gender.FEMALE, Relationship.CHILD),
                Heir("Hassan (son)", Gender.MALE, Relationship.CHILD),
            ],
            debts=Fraction(50_000)
        )

        # Distribute
        algo = MirahAlgorithm()
        result = algo.distribute_inheritance(case)

        # Validate
        validator = MaqasidValidator()
        validations = validator.validate_distribution(result)

        # Verify
        assert not result.errors
        assert result.is_balanced
        assert all(val.is_valid for val in validations.values())
        assert len(result.distributions) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
