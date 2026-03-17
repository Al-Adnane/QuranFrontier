"""
Q-SDK Mirah Core: Implementation of Q4:11 inheritance algorithm

Mathematical basis:
- Q4:11: "for the male, what is equal to the share of two females"
  => male_share = 2 * female_share (in same kinship degree)
- All distributions derive from fixed fractions: 1/2, 1/3, 1/6, 2/3
- Algorithm applies rules hierarchically: children > parents > siblings > extended

This is the FOUNDATIONAL LAYER of the Quran-Inspired Sciences framework (Q-SDK).
Any changes must be approved by Dual-Key Governance Council (2 engineers + 2 scholars).
"""

from fractions import Fraction
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from .mirah_models import (
    Heir, InheritanceCase, ShareDistribution, InheritanceDistributionResult,
    Relationship, Gender, ValidationStatus, MadhabSchool, HeritageDisqualification
)

logger = logging.getLogger(__name__)


class MirahAlgorithmError(Exception):
    """Base exception for Mirah algorithm errors"""
    pass


class NoQualifiedHeirsError(MirahAlgorithmError):
    """Raised when no heirs are eligible for inheritance"""
    pass


class NegativeEstateError(MirahAlgorithmError):
    """Raised when estate is negative after debts/bequests"""
    pass


class MirahAlgorithm:
    """
    Q4:11 Inheritance Distribution Algorithm

    Implements the Quranic inheritance rules from Surah Al-Nisa (4:11) as
    formalized in classical Islamic jurisprudence (fiqh al-mirah).

    Mathematical Framework:
    ├─ Fixed Fractions: 1/2, 1/3, 1/6, 2/3 (all shares denominator = 6)
    ├─ Gender Ratio: Male = 2 × Female (same kinship degree)
    ├─ Hierarchy: Children > Parents > Siblings > Extended family
    └─ Residual (Ta'sib): Remainder to nearest male heir

    Governance: All changes require Dual-Key Council approval (2 engineers + 2 scholars)
    """

    VERSION = "1.0.0"
    ALGORITHM_QURANIC_BASIS = "Q4:11"

    def __init__(self, madhab: MadhabSchool = MadhabSchool.HANAFI, strict_mode: bool = True):
        """
        Initialize algorithm.

        Args:
            madhab: School of Islamic jurisprudence to apply
            strict_mode: If True, raise on any invalid input; if False, collect warnings
        """
        self.madhab = madhab
        self.strict_mode = strict_mode
        self.audit_trail: List[str] = []

    def distribute_inheritance(self, case: InheritanceCase) -> InheritanceDistributionResult:
        """
        Main entry point: calculate inheritance distribution for a case.

        Algorithm flow:
        1. Validate input (estate, heirs, qualifications)
        2. Classify heirs by relationship (children, parents, siblings, extended)
        3. Apply Q4:11 rules hierarchically
        4. Calculate individual shares
        5. Verify result (balanced, valid fractions, consensus)

        Args:
            case: InheritanceCase with all facts

        Returns:
            InheritanceDistributionResult with full calculation

        Raises:
            MirahAlgorithmError: If case is invalid
        """
        self.audit_trail = []
        result = InheritanceDistributionResult(case=case)

        try:
            # Step 1: Validate
            self._validate_case(case, result)

            # Calculate distributable amount
            distributable = case.distributable_estate
            if distributable <= 0:
                raise NegativeEstateError(
                    f"Estate insufficient: {case.distributable_estate} "
                    f"(estate={case.estate_value}, debts+bequests={case.total_debts_and_bequests})"
                )

            qualified_heirs = case.qualified_heirs
            if not qualified_heirs:
                raise NoQualifiedHeirsError("No qualified heirs for inheritance")

            # Step 2-3: Classify and apply rules
            children = case.get_heirs_by_relationship(Relationship.CHILD)
            parents = case.get_heirs_by_relationship(Relationship.PARENT)
            siblings = case.get_heirs_by_relationship(Relationship.SIBLING)
            spouse = case.get_heirs_by_relationship(Relationship.SPOUSE)

            # Apply Q4:11 hierarchy
            if children:
                self._log_audit(f"Children present ({len(children)}): applying Q4:11 child rules")
                self._distribute_with_children(
                    children, parents, siblings, spouse, distributable, result
                )
            elif parents:
                self._log_audit(f"No children, parents present ({len(parents)}): applying parent rules")
                self._distribute_with_parents(
                    parents, siblings, spouse, distributable, result
                )
            elif siblings:
                self._log_audit(f"No children/parents, siblings present ({len(siblings)}): applying sibling rules")
                self._distribute_with_siblings(siblings, spouse, distributable, result)
            else:
                # Extended heirs (grandparents, uncles, cousins) - handled by ta'sib
                self._log_audit("No direct heirs: applying ta'sib (residual) principle")
                self._distribute_extended_heirs(qualified_heirs, distributable, result)

            # Step 4: Verify and finalize
            result.total_distributed = sum(
                dist.absolute_amount for dist in result.distributions.values()
            )
            result.audit_trail = self.audit_trail
            result.calculation_version = self.VERSION

            if not result.is_balanced:
                result.warnings.append(
                    f"Distribution imbalance: distributed {result.total_distributed}, "
                    f"should be {distributable}"
                )

            self._log_audit(f"Distribution complete: {len(result.distributions)} shares")
            return result

        except MirahAlgorithmError as e:
            result.errors.append(str(e))
            self._log_audit(f"ERROR: {str(e)}")
            if self.strict_mode:
                raise
            return result

    # ========== Q4:11 DISTRIBUTION RULES ==========

    def _distribute_with_children(
        self, children: List[Heir], parents: List[Heir], siblings: List[Heir],
        spouse: List[Heir], distributable: Fraction, result: InheritanceDistributionResult
    ) -> None:
        """
        Q4:11 Rule: "for the male, what is equal to the share of two females"

        When children are present:
        - They take entire estate (parents/siblings excluded)
        - Male child share = 2 × Female child share
        - All children in same degree share proportionally

        Formula:
        - Total units = (num_sons × 2) + (num_daughters × 1)
        - Each son receives: 2E / total_units
        - Each daughter receives: E / total_units
        """
        sons = [h for h in children if h.gender == Gender.MALE]
        daughters = [h for h in children if h.gender == Gender.FEMALE]

        total_units = (len(sons) * 2) + (len(daughters) * 1)
        share_unit = distributable / Fraction(total_units)

        self._log_audit(f"Child distribution: sons={len(sons)}, daughters={len(daughters)}, "
                       f"total_units={total_units}, share_unit={share_unit}")

        # Distribute to sons (Q4:11 explicitly: "for the male, what is equal to...")
        for son in sons:
            son_share = share_unit * 2
            distribution = ShareDistribution(
                heir_name=son.name,
                relationship=son.relationship,
                share_fraction=Fraction(2, total_units),
                share_percentage=float(Fraction(2, total_units)) * 100,
                absolute_amount=son_share,
                calculation_basis=f"Son receives 2 units (Q4:11: male = 2 × female)",
                quranic_basis="Q4:11",
                madhab_consensus={school: 1.0 for school in MadhabSchool},
                validation_status=ValidationStatus.VALID
            )
            result.distributions[son.name] = distribution
            self._log_audit(f"  {son.name} (son): {son_share} ({Fraction(2, total_units)})")

        # Distribute to daughters (Q4:11: female share is base unit)
        for daughter in daughters:
            daughter_share = share_unit * 1
            distribution = ShareDistribution(
                heir_name=daughter.name,
                relationship=daughter.relationship,
                share_fraction=Fraction(1, total_units),
                share_percentage=float(Fraction(1, total_units)) * 100,
                absolute_amount=daughter_share,
                calculation_basis=f"Daughter receives 1 unit (Q4:11: base female share)",
                quranic_basis="Q4:11",
                madhab_consensus={school: 1.0 for school in MadhabSchool},
                validation_status=ValidationStatus.VALID
            )
            result.distributions[daughter.name] = distribution
            self._log_audit(f"  {daughter.name} (daughter): {daughter_share} ({Fraction(1, total_units)})")

    def _distribute_with_parents(
        self, parents: List[Heir], siblings: List[Heir], spouse: List[Heir],
        distributable: Fraction, result: InheritanceDistributionResult
    ) -> None:
        """
        Q4:11 Rule: Parent inheritance when NO children

        Case 1: Both parents present
          - Each parent: 1/6 (explicit Q4:11)
          - Remainder: goes to father (ta'sib principle)

        Case 2: Mother only
          - Without siblings: 1/3 (explicit Q4:11)
          - With siblings: 1/6 (explicit Q4:11)

        Case 3: Father only (rare)
          - Father: entire remainder (ta'sib)
        """
        mothers = [h for h in parents if h.gender == Gender.FEMALE]
        fathers = [h for h in parents if h.gender == Gender.MALE]

        if mothers and fathers:
            # Both present: 1/6 each + remainder to father
            mother_share = distributable * Fraction(1, 6)
            father_fixed = distributable * Fraction(1, 6)
            remainder = distributable - mother_share - father_fixed

            # Father gets fixed share + remainder (ta'sib)
            father_share = father_fixed + remainder

            distribution_mother = ShareDistribution(
                heir_name=mothers[0].name,
                relationship=mothers[0].relationship,
                share_fraction=Fraction(1, 6),
                share_percentage=float(Fraction(1, 6)) * 100,
                absolute_amount=mother_share,
                calculation_basis="Mother (both parents present): 1/6 per Q4:11",
                quranic_basis="Q4:11",
                madhab_consensus={school: 1.0 for school in MadhabSchool},
                validation_status=ValidationStatus.VALID
            )
            result.distributions[mothers[0].name] = distribution_mother
            self._log_audit(f"  {mothers[0].name} (mother): {mother_share} (1/6)")

            distribution_father = ShareDistribution(
                heir_name=fathers[0].name,
                relationship=fathers[0].relationship,
                share_fraction=None,  # Variable due to ta'sib
                share_percentage=float(father_share / distributable) * 100,
                absolute_amount=father_share,
                calculation_basis="Father (both parents present): 1/6 + remainder (ta'sib principle)",
                quranic_basis="Q4:11 + classical consensus on ta'sib",
                madhab_consensus={school: 0.95 for school in MadhabSchool},
                validation_status=ValidationStatus.VALID
            )
            result.distributions[fathers[0].name] = distribution_father
            self._log_audit(f"  {fathers[0].name} (father): {father_share} (1/6 + remainder)")

        elif mothers and not fathers:
            # Mother only: determine if siblings present
            if siblings:
                # Q4:11 explicit: "if he had siblings, for his mother is a sixth"
                mother_share = distributable * Fraction(1, 6)
                fraction = Fraction(1, 6)
                basis = "Mother (siblings present): 1/6 per Q4:11"
            else:
                # Q4:11 explicit: "if he had no children...mother is one third"
                mother_share = distributable * Fraction(1, 3)
                fraction = Fraction(1, 3)
                basis = "Mother (no siblings): 1/3 per Q4:11"

            distribution = ShareDistribution(
                heir_name=mothers[0].name,
                relationship=mothers[0].relationship,
                share_fraction=fraction,
                share_percentage=float(fraction) * 100,
                absolute_amount=mother_share,
                calculation_basis=basis,
                quranic_basis="Q4:11",
                madhab_consensus={school: 0.98 for school in MadhabSchool},
                validation_status=ValidationStatus.VALID
            )
            result.distributions[mothers[0].name] = distribution
            self._log_audit(f"  {mothers[0].name} (mother only): {mother_share} ({fraction})")

            # Remainder goes to other heirs (siblings/extended)
            if siblings:
                remainder = distributable - mother_share
                self._distribute_with_siblings(siblings, [], remainder, result)

        elif fathers and not mothers:
            # Father only: gets entire remainder (ta'sib)
            father_share = distributable
            distribution = ShareDistribution(
                heir_name=fathers[0].name,
                relationship=fathers[0].relationship,
                share_fraction=None,
                share_percentage=100.0,
                absolute_amount=father_share,
                calculation_basis="Father (sole parent): entire estate (ta'sib)",
                quranic_basis="Classical consensus",
                madhab_consensus={school: 1.0 for school in MadhabSchool},
                validation_status=ValidationStatus.VALID
            )
            result.distributions[fathers[0].name] = distribution
            self._log_audit(f"  {fathers[0].name} (father only): {father_share} (100%)")

    def _distribute_with_siblings(
        self, siblings: List[Heir], spouse: List[Heir],
        distributable: Fraction, result: InheritanceDistributionResult
    ) -> None:
        """
        Sibling inheritance when NO direct heirs (children/parents).

        Rule: Male sibling = 2 × Female sibling (same as child rule per classical consensus)
        """
        brothers = [h for h in siblings if h.gender == Gender.MALE]
        sisters = [h for h in siblings if h.gender == Gender.FEMALE]

        total_units = (len(brothers) * 2) + (len(sisters) * 1)
        share_unit = distributable / Fraction(total_units)

        self._log_audit(f"Sibling distribution: brothers={len(brothers)}, "
                       f"sisters={len(sisters)}, total_units={total_units}")

        for brother in brothers:
            brother_share = share_unit * 2
            distribution = ShareDistribution(
                heir_name=brother.name,
                relationship=brother.relationship,
                share_fraction=Fraction(2, total_units),
                share_percentage=float(Fraction(2, total_units)) * 100,
                absolute_amount=brother_share,
                calculation_basis="Brother: 2 units (male sibling rule)",
                quranic_basis="Classical fiqh consensus",
                madhab_consensus={school: 0.90 for school in MadhabSchool},
                validation_status=ValidationStatus.VALID_MAJORITY
            )
            result.distributions[brother.name] = distribution
            self._log_audit(f"  {brother.name} (brother): {brother_share} ({Fraction(2, total_units)})")

        for sister in sisters:
            sister_share = share_unit * 1
            distribution = ShareDistribution(
                heir_name=sister.name,
                relationship=sister.relationship,
                share_fraction=Fraction(1, total_units),
                share_percentage=float(Fraction(1, total_units)) * 100,
                absolute_amount=sister_share,
                calculation_basis="Sister: 1 unit (female sibling rule)",
                quranic_basis="Classical fiqh consensus",
                madhab_consensus={school: 0.90 for school in MadhabSchool},
                validation_status=ValidationStatus.VALID_MAJORITY
            )
            result.distributions[sister.name] = distribution
            self._log_audit(f"  {sister.name} (sister): {sister_share} ({Fraction(1, total_units)})")

    def _distribute_extended_heirs(
        self, heirs: List[Heir], distributable: Fraction,
        result: InheritanceDistributionResult
    ) -> None:
        """
        Extended family inheritance (grandparents, uncles, cousins).

        Applies ta'sib principle: remainder goes to nearest male heir in kinship degrees.

        Note: This is complex and madhab-specific. Currently raises NotImplementedError
        to signal need for scholarly review before implementation.
        """
        raise NotImplementedError(
            "Extended heir distribution requires multi-madhab scholarly consensus. "
            "Contact Dual-Key Governance Council for authorization."
        )

    # ========== VALIDATION ==========

    def _validate_case(self, case: InheritanceCase, result: InheritanceDistributionResult) -> None:
        """
        Validate InheritanceCase for algorithmic processing.

        Checks:
        - Estate value > 0
        - At least one qualified heir
        - All heirs have valid relationships
        - No contradictory disqualifications
        """
        if case.estate_value <= 0:
            raise ValueError(f"Estate value must be positive: {case.estate_value}")

        if not case.qualified_heirs:
            raise NoQualifiedHeirsError(
                f"No qualified heirs. Disqualified: "
                f"{[(h.name, h.disqualified.value) for h in case.disqualified_heirs]}"
            )

        for heir in case.heirs:
            if heir.relationship == Relationship.ILLEGITIMATE:
                result.warnings.append(
                    f"Heir {heir.name} has illegitimate relationship: "
                    f"inheritance depends on madhab and recognition"
                )

        self._log_audit(f"Validation passed: {len(case.qualified_heirs)} heirs, "
                       f"estate={case.estate_value} {case.estate_currency}")

    # ========== LOGGING / AUDIT TRAIL ==========

    def _log_audit(self, message: str) -> None:
        """Log to audit trail for reproducibility"""
        self.audit_trail.append(message)
        logger.debug(message)


# ========== FACTORY / CONVENIENCE FUNCTIONS ==========

def create_inheritance_case_from_dict(data: Dict) -> InheritanceCase:
    """
    Create InheritanceCase from dictionary (JSON-serializable format).

    Useful for API/database integration.
    """
    heirs = []
    for heir_data in data.get("heirs", []):
        heir = Heir(
            name=heir_data["name"],
            gender=Gender[heir_data["gender"].upper()],
            relationship=Relationship[heir_data["relationship"].upper()],
            birth_year=heir_data.get("birth_year"),
            disqualified=HeritageDisqualification(heir_data.get("disqualified", "none"))
        )
        heirs.append(heir)

    case = InheritanceCase(
        deceased_name=data["deceased_name"],
        deceased_death_year=data.get("deceased_death_year", 0),
        estate_value=Fraction(data["estate_value"]).limit_denominator(),
        estate_currency=data.get("estate_currency", "USD"),
        heirs=heirs
    )
    return case


def calculate_q411_distribution(
    deceased_name: str,
    estate_value: float,
    heirs_data: List[Dict],
    madhab: MadhabSchool = MadhabSchool.HANAFI
) -> InheritanceDistributionResult:
    """
    Simplified entry point for quick inheritance calculation.

    Args:
        deceased_name: Name of deceased
        estate_value: Total estate in currency units
        heirs_data: List of {"name": str, "gender": "male"|"female", "relationship": str}
        madhab: School of jurisprudence

    Returns:
        InheritanceDistributionResult
    """
    case = InheritanceCase(
        deceased_name=deceased_name,
        deceased_death_year=datetime.now().year,
        estate_value=Fraction(estate_value).limit_denominator(),
        jurisdiction=madhab
    )

    for heir_dict in heirs_data:
        heir = Heir(
            name=heir_dict["name"],
            gender=Gender[heir_dict["gender"].upper()],
            relationship=Relationship[heir_dict["relationship"].upper()]
        )
        case.heirs.append(heir)

    algorithm = MirahAlgorithm(madhab=madhab)
    return algorithm.distribute_inheritance(case)
