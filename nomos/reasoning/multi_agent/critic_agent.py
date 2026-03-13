"""Critic Agent - Validates interpretations against Islamic sources.

The CriticAgent evaluates proposed interpretations by checking them against:
- Hadith authenticity grades (Sahih, Hasan, Daif)
- Madhab positions and agreements
- Classical legal principles
- Potential contradictions with established sources

Architecture:
- Checks hadith strength (Sahih, Sunan, Musnad grades)
- Computes madhab agreement scores
- Identifies supporting and contradicting evidence
- Returns structured critique with evidence strength
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class HadithGrade(Enum):
    """Hadith authenticity grades."""
    SAHIH = "sahih"  # Authentic
    HASAN = "hasan"  # Good
    DAIF = "daif"  # Weak
    MAUDHU = "maudhu"  # Fabricated
    UNKNOWN = "unknown"


class HadithCollection(Enum):
    """Major hadith collections."""
    SAHIH_BUKHARI = "sahih_bukhari"
    SAHIH_MUSLIM = "sahih_muslim"
    SUNAN_ABU_DAWUD = "sunan_abu_dawud"
    SUNAN_TIRMIDHI = "sunan_tirmidhi"
    SUNAN_NASAI = "sunan_nasai"
    SUNAN_IBN_MAJAH = "sunan_ibn_majah"
    MUSNAD_AHMAD = "musnad_ahmad"


@dataclass
class HadithReference:
    """Hadith reference with grade information."""
    reference: str  # e.g., "Sahih Bukhari 34:160"
    collection: HadithCollection
    number: str
    grade: HadithGrade
    chain_reliability: float  # 0-1 based on isnad
    text: str


@dataclass
class CritiqueResult:
    """Structured critique of interpretation."""
    interpretation_text: str
    is_valid: bool
    issues: List[str]
    supporting_evidence: List[Dict[str, Any]]
    contradicting_evidence: List[Dict[str, Any]]
    madhab_agreement: float  # 0-1 across all madhabs
    madhab_positions: Dict[str, float]  # Per-madhab scores
    hadith_strength: float  # Average grade strength
    overall_strength: float  # Weighted combination
    recommendations: List[str]


class CriticAgent:
    """
    Validates interpretations against Islamic sources.

    Checks hadith authenticity, madhab agreements, and identifies
    supporting or contradicting evidence.
    """

    def __init__(
        self,
        hadith_db: Optional[Dict[str, HadithReference]] = None,
        madhab_list: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        strictness: float = 0.7  # 0=lenient, 1=strict
    ):
        """
        Initialize CriticAgent.

        Args:
            hadith_db: Dictionary of hadith references
            madhab_list: Schools of law to consider
            api_key: Optional API key for external sources
            strictness: How strict to be in validation
        """
        self.hadith_db = hadith_db or self._load_default_hadith_db()
        self.madhab_list = madhab_list or ["hanafi", "maliki", "shafii", "hanbali"]
        self.api_key = api_key
        self.strictness = strictness

        self.critique_history: List[CritiqueResult] = []

    def evaluate(
        self,
        interpretation: str,
        sources: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate interpretation against sources.

        Args:
            interpretation: Proposed interpretation text
            sources: Dict with 'quran', 'hadith', 'madhab' keys
            context: Additional context (question, topic)

        Returns:
            Dictionary with:
                - is_valid: Boolean validity assessment
                - issues: List of identified problems
                - madhab_agreement: Agreement across madhabs
                - hadith_strength: Strength of hadith evidence
                - supporting_evidence: List of supporting sources
                - contradicting_evidence: List of contradictions
                - recommendations: How to strengthen interpretation
        """
        sources = sources or {}

        # Assess hadith strength
        hadith_refs = sources.get("hadith", [])
        hadith_strength = self.assess_hadith_strength(hadith_refs)

        # Check madhab agreement
        madhab_positions = self._check_madhab_positions(interpretation, sources)
        madhab_agreement = self.compute_madhab_agreement(interpretation, madhab_positions)

        # Find supporting and contradicting evidence
        supporting = self._find_supporting_evidence(interpretation, sources)
        contradicting = self._find_contradicting_evidence(interpretation, sources)

        # Assess validity
        issues = self._identify_issues(interpretation, madhab_agreement, hadith_strength)
        is_valid = len(issues) == 0 or (1.0 - self.strictness) > 0.3

        # Compute overall strength
        overall_strength = (
            hadith_strength["average_grade"] * 0.4 +
            madhab_agreement * 0.35 +
            (1.0 if is_valid else 0.0) * 0.25
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            issues,
            madhab_agreement,
            hadith_strength
        )

        result = {
            "interpretation": interpretation,
            "is_valid": is_valid,
            "issues": issues,
            "madhab_agreement": madhab_agreement,
            "madhab_positions": madhab_positions,
            "hadith_strength": hadith_strength,
            "supporting_evidence": supporting,
            "contradicting_evidence": contradicting,
            "overall_strength": overall_strength,
            "recommendations": recommendations
        }

        self.critique_history.append(result)

        return result

    def assess_hadith_strength(self, hadith_refs: List[str]) -> Dict[str, Any]:
        """
        Assess strength of hadith references.

        Args:
            hadith_refs: List of hadith references (e.g., "Sahih Bukhari 34:160")

        Returns:
            Dictionary with:
                - grades: Dict mapping reference to grade
                - average_grade: Numeric average strength
                - strongest: Strongest hadith cited
                - weakest: Weakest hadith cited
        """
        if not hadith_refs:
            return {
                "grades": {},
                "average_grade": 0.0,
                "strongest": None,
                "weakest": None
            }

        grades = {}
        grade_values = []

        for ref in hadith_refs:
            grade_info = self._lookup_hadith_grade(ref)
            grades[ref] = grade_info

            # Map grade to numeric value
            grade_score = {
                HadithGrade.SAHIH: 1.0,
                HadithGrade.HASAN: 0.75,
                HadithGrade.DAIF: 0.4,
                HadithGrade.MAUDHU: 0.0,
                HadithGrade.UNKNOWN: 0.5
            }.get(grade_info["grade"], 0.5)

            grade_values.append(grade_score)

        avg_grade = sum(grade_values) / len(grade_values) if grade_values else 0.0

        # Find strongest and weakest
        strongest = max(grades.items(), key=lambda x: x[1].get("score", 0))[0]
        weakest = min(grades.items(), key=lambda x: x[1].get("score", 0))[0]

        return {
            "grades": grades,
            "average_grade": avg_grade,
            "strongest": strongest,
            "weakest": weakest,
            "reference_count": len(hadith_refs),
            "assessment": self._grade_assessment(avg_grade)
        }

    def compute_madhab_agreement(
        self,
        interpretation: str,
        madhab_positions: Dict[str, float]
    ) -> float:
        """
        Compute agreement score across madhabs.

        Args:
            interpretation: Interpretation being evaluated
            madhab_positions: Dict mapping madhab name to position score 0-1

        Returns:
            Float 0-1 representing degree of consensus
        """
        if not madhab_positions:
            return 0.5

        scores = list(madhab_positions.values())

        # Compute variance in positions
        mean_score = sum(scores) / len(scores) if scores else 0.5
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores) if scores else 0.0

        # Agreement = 1 - normalized_variance
        max_variance = 0.25  # Maximum possible variance in [0,1]
        normalized_variance = min(variance / max_variance, 1.0)
        agreement = 1.0 - normalized_variance

        return agreement

    def _check_madhab_positions(
        self,
        interpretation: str,
        sources: Dict[str, Any]
    ) -> Dict[str, float]:
        """Check how much each madhab supports interpretation."""
        positions = {}

        for madhab in self.madhab_list:
            # Mock check - would query madhab positions database
            position_score = self._compute_madhab_position_score(
                interpretation,
                madhab,
                sources
            )
            positions[madhab] = position_score

        return positions

    def _compute_madhab_position_score(
        self,
        interpretation: str,
        madhab: str,
        sources: Dict[str, Any]
    ) -> float:
        """Compute how much a madhab supports interpretation."""
        # Default: 0.85 if has any source, 0.65 if no source
        if sources:
            return 0.85
        return 0.65

    def _lookup_hadith_grade(self, reference: str) -> Dict[str, Any]:
        """Look up hadith grade from database."""
        # Mock lookup
        if "Sahih Bukhari" in reference or "Sahih Muslim" in reference:
            return {
                "grade": HadithGrade.SAHIH,
                "score": 1.0,
                "reliability": 0.98
            }
        elif "Sunan" in reference:
            return {
                "grade": HadithGrade.HASAN,
                "score": 0.75,
                "reliability": 0.8
            }
        else:
            return {
                "grade": HadithGrade.UNKNOWN,
                "score": 0.5,
                "reliability": 0.5
            }

    def _find_supporting_evidence(
        self,
        interpretation: str,
        sources: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find evidence supporting interpretation."""
        supporting = []

        quran_verses = sources.get("quran", [])
        for verse in quran_verses:
            supporting.append({
                "type": "quran",
                "reference": f"{verse[0]}:{verse[1]}" if isinstance(verse, tuple) else verse,
                "strength": 0.95
            })

        hadith_refs = sources.get("hadith", [])
        for hadith in hadith_refs:
            supporting.append({
                "type": "hadith",
                "reference": hadith,
                "strength": 0.85
            })

        return supporting

    def _find_contradicting_evidence(
        self,
        interpretation: str,
        sources: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find evidence contradicting interpretation."""
        # In real system, would check against contradiction database
        return []

    def _identify_issues(
        self,
        interpretation: str,
        madhab_agreement: float,
        hadith_strength: Dict[str, Any]
    ) -> List[str]:
        """Identify issues with interpretation."""
        issues = []

        # Check madhab agreement
        if madhab_agreement < 0.5:
            issues.append(
                f"Low madhab consensus (agreement: {madhab_agreement:.2f})"
            )

        # Check hadith strength
        hadith_avg = hadith_strength.get("average_grade", 0.0)
        if hadith_avg < 0.4:
            issues.append(
                f"Weak hadith evidence (avg grade: {hadith_avg:.2f})"
            )

        return issues

    def _generate_recommendations(
        self,
        issues: List[str],
        madhab_agreement: float,
        hadith_strength: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations to strengthen interpretation."""
        recommendations = []

        if madhab_agreement < 0.7:
            recommendations.append(
                "Consider consulting all four madhabs to identify common ground"
            )

        if hadith_strength.get("average_grade", 0.0) < 0.7:
            recommendations.append(
                "Strengthen with higher-grade hadith references"
            )

        if not issues:
            recommendations.append(
                "Interpretation is well-supported across sources"
            )

        return recommendations

    def _grade_assessment(self, average_grade: float) -> str:
        """Convert average grade to textual assessment."""
        if average_grade >= 0.9:
            return "Very strong (Sahih)"
        elif average_grade >= 0.7:
            return "Strong (Hasan)"
        elif average_grade >= 0.4:
            return "Moderate (Daif)"
        else:
            return "Weak or unsupported"

    def _load_default_hadith_db(self) -> Dict[str, HadithReference]:
        """Load default hadith database (mock)."""
        return {}

    def get_critique_history(self) -> List[Dict[str, Any]]:
        """Get history of critiques."""
        return self.critique_history

    def clear_history(self):
        """Clear critique history."""
        self.critique_history = []
