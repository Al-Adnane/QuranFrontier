"""
Q-SDK Mirah Models: Data structures for Islamic inheritance (Q4:11)

Comprehensive modeling of:
- Heirs (individuals with kinship relationships)
- Inheritance cases (complete distribution scenarios)
- Share distributions (calculated results)
- Validation metadata (theological and mathematical verification)
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from fractions import Fraction
from datetime import datetime


class Relationship(Enum):
    """Kinship relationships to the deceased (mansub ila al-mayyit)"""
    CHILD = "child"                    # Direct child (ibn/ibna)
    PARENT = "parent"                  # Father/mother (ab/umm)
    SIBLING = "sibling"                # Full/half brother/sister (akh/ukht)
    GRANDPARENT = "grandparent"        # Paternal/maternal grandparent (jadd/jadda)
    UNCLE_AUNT = "uncle_aunt"          # Paternal uncle/aunt (amm/amma)
    NEPHEW_NIECE = "nephew_niece"      # Sibling's child (ibn/ibnat akh)
    SPOUSE = "spouse"                  # Widow/widower (zawj/zawja)
    COUSIN = "cousin"                  # First cousin and beyond
    ILLEGITIMATE = "illegitimate"      # Not recognized by Sharia


class Gender(Enum):
    """Biological gender (determining share ratio per Q4:11)"""
    MALE = "male"
    FEMALE = "female"


class HeritageDisqualification(Enum):
    """Islamic legal reasons for inheritance disqualification"""
    MURDERER = "murderer"              # Killed the deceased (qatala al-mayyit)
    APOSTATE = "apostate"              # Left Islam (murtadd)
    NON_MUSLIM = "non_muslim"          # Different faith (kafir)
    ENSLAVED = "enslaved"              # Legal slavery (raqq)
    DISOWNED = "disowned"              # Formally disowned by testator
    NONE = "none"                      # No disqualification


class MadhabSchool(Enum):
    """Four classical schools of Islamic jurisprudence (madhahib)"""
    HANAFI = "hanafi"                  # Hanafi school (Abu Hanifa)
    MALIKI = "maliki"                  # Maliki school (Malik)
    SHAFI_I = "shafi_i"                # Shafi'i school (Al-Shafi'i)
    HANBALI = "hanbali"                # Hanbali school (Ahmad ibn Hanbal)


class ValidationStatus(Enum):
    """Verification status of calculated share"""
    VALID = "valid"                    # Verified by all madhabs
    VALID_MAJORITY = "valid_majority"  # Consensus among 3/4 madhabs
    VALID_SINGLE = "valid_single"      # Valid in only one madhab
    PENDING_REVIEW = "pending_review"  # Awaiting scholarly review
    CHALLENGED = "challenged"          # Disputed among madhabs
    INVALID = "invalid"                # Does not comply with Sharia


@dataclass
class Heir:
    """
    Individual heir (waris) in inheritance distribution.

    Represents a person with a kinship relationship to the deceased (mayyit)
    and eligibility for inheritance under Q4:11 and classical fiqh rules.

    Attributes:
        name: Full name of heir
        gender: Biological gender (determines share ratio per Q4:11)
        relationship: Kinship relationship to deceased
        birth_year: Year of birth (optional, for age at death calculation)
        disqualified: Reason for disqualification from inheritance (if any)
        madhab_notes: School-specific notes (e.g., "Hanafi: counts as half-sibling")
        notes: General annotations
        verified: Whether heir identity verified by governance council
    """
    name: str
    gender: Gender
    relationship: Relationship
    birth_year: Optional[int] = None
    disqualified: HeritageDisqualification = HeritageDisqualification.NONE
    madhab_notes: str = ""
    notes: str = ""
    verified: bool = False

    @property
    def is_qualified(self) -> bool:
        """Check if heir is eligible for inheritance"""
        return self.disqualified == HeritageDisqualification.NONE

    @property
    def age_category(self) -> str:
        """Return age category for Waqf/guardianship considerations"""
        if self.birth_year is None:
            return "unknown"
        current_year = datetime.now().year
        age = current_year - self.birth_year
        if age < 18:
            return "minor"
        elif age < 65:
            return "adult"
        else:
            return "senior"

    def __repr__(self) -> str:
        status = "DISQUALIFIED" if not self.is_qualified else "qualified"
        return f"Heir({self.name}, {self.gender.value}, {self.relationship.value}, {status})"


@dataclass
class Bequest:
    """
    Testamentary disposition (wasiyyah) deducted before inheritance division.

    Per Q4:11: "from after any bequest he may have made or debt"

    Attributes:
        beneficiary: Name of bequest recipient (non-heir or specific heir)
        amount: Monetary amount of bequest
        percentage_of_estate: Alternative: percentage of total estate
        description: Purpose (e.g., "for building mosque")
        verified: Whether validated by legal guardian/court
    """
    beneficiary: str
    amount: Optional[Fraction] = None
    percentage_of_estate: Optional[Fraction] = None
    description: str = ""
    verified: bool = False

    @property
    def is_valid(self) -> bool:
        """Bequest must specify either amount or percentage"""
        return self.amount is not None or self.percentage_of_estate is not None

    def calculate_absolute_amount(self, total_estate: Fraction) -> Fraction:
        """Calculate bequest in absolute terms"""
        if self.amount is not None:
            return self.amount
        elif self.percentage_of_estate is not None:
            return total_estate * self.percentage_of_estate
        else:
            raise ValueError("Bequest must have amount or percentage_of_estate")


@dataclass
class InheritanceCase:
    """
    Complete inheritance scenario for distribution calculation.

    Represents all legal and financial facts of an estate to be distributed
    according to Q4:11 and Islamic inheritance law (fiqh al-mirah).

    Attributes:
        deceased_name: Name of deceased (al-mayyit)
        deceased_death_year: Year of death (for validity checks)
        estate_value: Total liquid estate value
        estate_currency: Currency denomination
        estate_description: Physical assets description (e.g., "Real estate + bank accounts")
        heirs: List of eligible heirs
        debts: Outstanding debts deducted before distribution
        bequests: Testamentary dispositions deducted before distribution
        jurisdiction: Islamic jurisdiction/madhab to apply (default: majority consensus)
        metadata: Arbitrary metadata dict for extended use cases
    """
    deceased_name: str
    deceased_death_year: int
    estate_value: Fraction
    estate_currency: str = "USD"
    estate_description: str = ""
    heirs: List[Heir] = field(default_factory=list)
    debts: Fraction = field(default_factory=lambda: Fraction(0))
    bequests: List[Bequest] = field(default_factory=list)
    jurisdiction: MadhabSchool = MadhabSchool.HANAFI
    metadata: Dict = field(default_factory=dict)

    @property
    def total_debts_and_bequests(self) -> Fraction:
        """Total amount deducted before heir distribution"""
        bequest_total = Fraction(0)
        for bequest in self.bequests:
            bequest_total += bequest.calculate_absolute_amount(self.estate_value)
        return self.debts + bequest_total

    @property
    def distributable_estate(self) -> Fraction:
        """Amount available for distribution to heirs"""
        return self.estate_value - self.total_debts_and_bequests

    @property
    def qualified_heirs(self) -> List[Heir]:
        """Filter to only qualified (non-disqualified) heirs"""
        return [h for h in self.heirs if h.is_qualified]

    @property
    def disqualified_heirs(self) -> List[Heir]:
        """Heirs excluded from inheritance"""
        return [h for h in self.heirs if not h.is_qualified]

    @property
    def is_valid(self) -> bool:
        """Case is valid if distributable estate is positive"""
        return self.distributable_estate > 0

    def get_heirs_by_relationship(self, relationship: Relationship) -> List[Heir]:
        """Get all qualified heirs with specific relationship"""
        return [h for h in self.qualified_heirs if h.relationship == relationship]

    def get_heirs_by_gender(self, gender: Gender) -> List[Heir]:
        """Get all qualified heirs with specific gender"""
        return [h for h in self.qualified_heirs if h.gender == gender]

    def __repr__(self) -> str:
        return (
            f"InheritanceCase(deceased={self.deceased_name}, "
            f"estate={self.estate_value} {self.estate_currency}, "
            f"heirs={len(self.qualified_heirs)}, "
            f"distributable={self.distributable_estate})"
        )


@dataclass
class ShareDistribution:
    """
    Calculated share for a single heir.

    Result of applying Q4:11 algorithm to inheritance case.

    Attributes:
        heir_name: Name of recipient heir
        relationship: Kinship relationship to deceased
        share_fraction: Fraction of estate (e.g., Fraction(1, 3))
        share_percentage: Percentage representation (0-100)
        absolute_amount: Monetary amount in currency
        calculation_basis: Human-readable explanation of how share was calculated
        quranic_basis: Relevant Quranic verses (e.g., "Q4:11")
        madhab_consensus: Dict mapping madhab → consensus score (0-1)
        validation_status: Verification status against Maqasid
        dual_key_signatures: Dict of {council_member: timestamp} for governance
        notes: Additional annotations
    """
    heir_name: str
    relationship: Relationship
    share_fraction: Optional[Fraction] = None
    share_percentage: float = 0.0
    absolute_amount: Fraction = field(default_factory=lambda: Fraction(0))
    calculation_basis: str = ""
    quranic_basis: str = ""
    madhab_consensus: Dict[MadhabSchool, float] = field(default_factory=dict)
    validation_status: ValidationStatus = ValidationStatus.PENDING_REVIEW
    dual_key_signatures: Dict[str, datetime] = field(default_factory=dict)
    notes: str = ""

    @property
    def average_consensus_score(self) -> float:
        """Average consensus across all 4 madhabs (0-1 scale)"""
        if not self.madhab_consensus:
            return 0.0
        return sum(self.madhab_consensus.values()) / len(self.madhab_consensus)

    @property
    def is_fully_signed(self) -> bool:
        """Check if both engineering and theological councils signed"""
        # Expected signatures: at least 2 engineering + 2 theological
        # This is a simplified check; actual governance layer would verify
        return len(self.dual_key_signatures) >= 4

    def __repr__(self) -> str:
        return (
            f"ShareDistribution(heir={self.heir_name}, "
            f"fraction={self.share_fraction}, "
            f"amount={self.absolute_amount}, "
            f"status={self.validation_status.value})"
        )


@dataclass
class InheritanceDistributionResult:
    """
    Complete result of inheritance distribution calculation.

    Container for all shares, metadata, and audit trail.

    Attributes:
        case: Original InheritanceCase
        distributions: Dict mapping heir name → ShareDistribution
        total_distributed: Sum of all shares (should equal distributable_estate)
        calculation_timestamp: When calculation was performed
        calculation_version: Algorithm version used
        audit_trail: List of calculation steps for reproducibility
        validation_report: Maqasid validation scores
        errors: Any errors encountered (empty if successful)
        warnings: Non-fatal issues (madhab disagreements, etc.)
    """
    case: InheritanceCase
    distributions: Dict[str, ShareDistribution] = field(default_factory=dict)
    total_distributed: Fraction = field(default_factory=lambda: Fraction(0))
    calculation_timestamp: datetime = field(default_factory=datetime.now)
    calculation_version: str = "1.0"
    audit_trail: List[str] = field(default_factory=list)
    validation_report: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def is_balanced(self) -> bool:
        """Check if distributed amount matches estate (allowing small rounding)"""
        difference = abs(self.total_distributed - self.case.distributable_estate)
        return difference < Fraction(1, 100)  # Allow < 1 cent difference

    @property
    def summary(self) -> str:
        """Human-readable summary of distribution"""
        lines = [
            f"Estate: {self.case.estate_value} {self.case.estate_currency}",
            f"Debts + Bequests: {self.case.total_debts_and_bequests}",
            f"Distributable: {self.case.distributable_estate}",
            f"Distributed: {self.total_distributed}",
            f"",
            "Distribution:",
        ]
        for heir, dist in self.distributions.items():
            lines.append(
                f"  {heir}: {dist.absolute_amount} ({dist.share_percentage:.2f}%)"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"InheritanceDistributionResult("
            f"heirs={len(self.distributions)}, "
            f"total_distributed={self.total_distributed}, "
            f"balanced={self.is_balanced})"
        )
