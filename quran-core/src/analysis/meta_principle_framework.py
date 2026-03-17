"""
META-PRINCIPLE FRAMEWORK: Formalized Axioms Governing All Quranic Principles

This module implements the 6 meta-axioms that govern all 30+ Quranic principles:
1. Tawhid (Unity/Consistency)
2. Mizan (Balance/Equilibrium)
3. Tadarruj (Gradualism/Staging)
4. Maqasid (Higher Objectives)
5. Fitrah (Innate Nature)
6. Observer Effect (Participatory Understanding)

Each principle is validated against all 6 axioms. A principle is valid only if:
- Tawhid_Score >= 0.85 (consistency check)
- Mizan_Score >= 0.70 (balance across 5 dimensions)
- Tadarruj_Score >= 0.80 (appropriate staging)
- Maqasid_Score >= 0.70 (serves at least one objective)
- Fitrah_Score >= 0.75 (aligns with human nature)
- Observer_Score >= 0.70 (has engagement/revelation potential)

Overall validity: (weighted average of 6 scores) >= 0.85
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json


class Maqasid(Enum):
    """The 5 Core Higher Objectives of Islamic Law"""
    DEEN = "Deen (Religion/Values)"  # Protect faith and values
    NAFS = "Nafs (Life/Soul)"  # Preserve and develop life
    AQL = "Aql (Intellect)"  # Develop reason and knowledge
    MAL = "Mal (Wealth)"  # Enable just economies
    IRD = "Ird (Honor)"  # Maintain dignity and family


class StagingPattern(Enum):
    """The 3 Primary Staging Patterns"""
    LINEAR = "Linear progression"  # Stage 1 → 2 → 3 → ... → Final
    LAYERED = "Layered parallel"  # Foundations layer + support + core
    CYCLIC = "Cyclic refinement"  # Cycle 1 → Cycle 2 → ... (deepening)


@dataclass
class BalanceDimensions:
    """The 5 Dimensions of Mizan (Balance)"""
    individual_collective: float  # Individual rights vs collective welfare
    effort_result: float  # Effort required vs results achieved
    short_long_term: float  # Short-term benefits vs long-term growth
    rigor_mercy: float  # Rule strictness vs contextual mercy
    certainty_flexibility: float  # Fixed principles vs flexible implementation

    def average(self) -> float:
        """Calculate average balance across all dimensions"""
        values = [
            self.individual_collective,
            self.effort_result,
            self.short_long_term,
            self.rigor_mercy,
            self.certainty_flexibility
        ]
        return sum(values) / len(values)

    def to_dict(self) -> Dict[str, float]:
        return {
            "individual_collective": self.individual_collective,
            "effort_result": self.effort_result,
            "short_long_term": self.short_long_term,
            "rigor_mercy": self.rigor_mercy,
            "certainty_flexibility": self.certainty_flexibility,
        }


@dataclass
class FitrahDimensions:
    """The 8 Dimensions of Fitrah (Innate Nature)"""
    survival_instinct: float  # Aligns with seeking safety/food
    social_bonding: float  # Leverages group belonging
    parental_love: float  # Works with parent-child love
    intellectual_curiosity: float  # Leverages desire to learn
    fairness_justice: float  # Appeals to innate justice sense
    autonomy_freedom: float  # Respects desire for freedom
    achievement_mastery: float  # Leverages desire to excel
    transcendence_meaning: float  # Appeals to spiritual need

    def average(self) -> float:
        """Calculate average Fitrah alignment"""
        values = [
            self.survival_instinct,
            self.social_bonding,
            self.parental_love,
            self.intellectual_curiosity,
            self.fairness_justice,
            self.autonomy_freedom,
            self.achievement_mastery,
            self.transcendence_meaning
        ]
        return sum(values) / len(values)

    def to_dict(self) -> Dict[str, float]:
        return {
            "survival_instinct": self.survival_instinct,
            "social_bonding": self.social_bonding,
            "parental_love": self.parental_love,
            "intellectual_curiosity": self.intellectual_curiosity,
            "fairness_justice": self.fairness_justice,
            "autonomy_freedom": self.autonomy_freedom,
            "achievement_mastery": self.achievement_mastery,
            "transcendence_meaning": self.transcendence_meaning,
        }


@dataclass
class EngagementPathways:
    """The 5 Engagement Pathways for Observer Effect"""
    active_reading: float  # 0.4 base engagement
    practical_application: float  # 0.7 base engagement
    teaching_others: float  # 0.85 base engagement
    comparative_analysis: float  # 0.65 base engagement
    mystical_contemplation: float  # 0.75 base engagement

    def total_understanding(self, revelation_factor: float = 0.8) -> float:
        """
        Calculate total understanding from all pathways
        Total = sum of all engagement levels, scaled by revelation factor
        """
        total = (
            self.active_reading +
            self.practical_application +
            self.teaching_others +
            self.comparative_analysis +
            self.mystical_contemplation
        )
        return min(total * revelation_factor / 5.0, 1.0)

    def to_dict(self) -> Dict[str, float]:
        return {
            "active_reading": self.active_reading,
            "practical_application": self.practical_application,
            "teaching_others": self.teaching_others,
            "comparative_analysis": self.comparative_analysis,
            "mystical_contemplation": self.mystical_contemplation,
        }


@dataclass
class StagingInfo:
    """Information about a principle's staging"""
    pattern: StagingPattern
    stages: List[str]  # Names of each stage
    durations: List[str]  # Duration of each stage
    prerequisites: Dict[int, List[int]]  # stage_i requires stages in prerequisites[i]
    readiness_threshold: float = 0.85  # Min readiness score to advance

    def is_valid_progression(self, current_stage: int, next_stage: int) -> bool:
        """Check if progression from current to next stage is valid"""
        if next_stage <= current_stage:
            return False
        if next_stage not in self.prerequisites.get(current_stage, []):
            return False
        return True


@dataclass
class PrincipleAssessment:
    """Assessment of a principle against all 6 meta-axioms"""
    name: str
    quranic_reference: str
    domain: str

    # The 6 axiom scores
    tawhid_score: float  # Consistency check
    mizan_score: float  # Balance score
    tadarruj_score: float  # Staging score
    maqasid_score: float  # Objective alignment
    fitrah_score: float  # Human nature alignment
    observer_score: float  # Engagement potential

    # Detailed breakdowns
    balance_dimensions: Optional[BalanceDimensions] = None
    fitrah_dimensions: Optional[FitrahDimensions] = None
    maqasid_weights: Dict[Maqasid, float] = field(default_factory=dict)
    engagement_pathways: Optional[EngagementPathways] = None
    staging_info: Optional[StagingInfo] = None

    def validity_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate overall validity score using all 6 axioms
        Default weights: equal (0.167 each)
        """
        if weights is None:
            weights = {
                "tawhid": 0.167,
                "mizan": 0.167,
                "tadarruj": 0.167,
                "maqasid": 0.167,
                "fitrah": 0.167,
                "observer": 0.167,
            }

        weighted_score = (
            weights["tawhid"] * self.tawhid_score +
            weights["mizan"] * self.mizan_score +
            weights["tadarruj"] * self.tadarruj_score +
            weights["maqasid"] * self.maqasid_score +
            weights["fitrah"] * self.fitrah_score +
            weights["observer"] * self.observer_score
        )
        return weighted_score

    def is_valid(self, threshold: float = 0.85) -> bool:
        """Check if principle is valid according to all axioms"""
        # Individual minimums
        if self.tawhid_score < 0.85:
            return False
        if self.mizan_score < 0.70:
            return False
        if self.tadarruj_score < 0.80:
            return False
        if self.maqasid_score < 0.70:
            return False
        if self.fitrah_score < 0.75:
            return False
        if self.observer_score < 0.70:
            return False

        # Overall validity
        return self.validity_score() >= threshold

    def validation_report(self) -> str:
        """Generate detailed validation report"""
        valid = self.is_valid()
        overall = self.validity_score()

        report = f"""
PRINCIPLE VALIDATION REPORT
===========================
Name: {self.name}
Reference: {self.quranic_reference}
Domain: {self.domain}

OVERALL VALIDITY: {'✓ VALID' if valid else '✗ NEEDS REVISION'}
Overall Score: {overall:.2f}/1.00

AXIOM SCORES (all must pass minimum thresholds):
──────────────────────────────────────────────
Tawhid (Consistency):     {self.tawhid_score:.2f}/1.00  {'✓' if self.tawhid_score >= 0.85 else '✗'} (min: 0.85)
Mizan (Balance):          {self.mizan_score:.2f}/1.00  {'✓' if self.mizan_score >= 0.70 else '✗'} (min: 0.70)
Tadarruj (Staging):       {self.tadarruj_score:.2f}/1.00  {'✓' if self.tadarruj_score >= 0.80 else '✗'} (min: 0.80)
Maqasid (Objectives):     {self.maqasid_score:.2f}/1.00  {'✓' if self.maqasid_score >= 0.70 else '✗'} (min: 0.70)
Fitrah (Human Nature):    {self.fitrah_score:.2f}/1.00  {'✓' if self.fitrah_score >= 0.75 else '✗'} (min: 0.75)
Observer (Engagement):    {self.observer_score:.2f}/1.00  {'✓' if self.observer_score >= 0.70 else '✗'} (min: 0.70)

"""

        if self.balance_dimensions:
            report += f"""MIZAN BALANCE BREAKDOWN:
──────────────────────
Individual-Collective:  {self.balance_dimensions.individual_collective:.2f}
Effort-Result:          {self.balance_dimensions.effort_result:.2f}
Short-Long Term:        {self.balance_dimensions.short_long_term:.2f}
Rigor-Mercy:           {self.balance_dimensions.rigor_mercy:.2f}
Certainty-Flexibility:  {self.balance_dimensions.certainty_flexibility:.2f}
Average:                {self.balance_dimensions.average():.2f}

"""

        if self.fitrah_dimensions:
            report += f"""FITRAH ALIGNMENT BREAKDOWN:
──────────────────────────
Survival Instinct:      {self.fitrah_dimensions.survival_instinct:.2f}
Social Bonding:         {self.fitrah_dimensions.social_bonding:.2f}
Parental Love:          {self.fitrah_dimensions.parental_love:.2f}
Intellectual Curiosity: {self.fitrah_dimensions.intellectual_curiosity:.2f}
Fairness/Justice:       {self.fitrah_dimensions.fairness_justice:.2f}
Autonomy/Freedom:       {self.fitrah_dimensions.autonomy_freedom:.2f}
Achievement/Mastery:    {self.fitrah_dimensions.achievement_mastery:.2f}
Transcendence/Meaning:  {self.fitrah_dimensions.transcendence_meaning:.2f}
Average:                {self.fitrah_dimensions.average():.2f}

"""

        if self.maqasid_weights:
            report += "MAQASID ALIGNMENT:\n──────────────────\n"
            for maqasid, weight in self.maqasid_weights.items():
                report += f"{maqasid.value:20s}: {weight:.2f}\n"
            report += "\n"

        if self.staging_info:
            report += f"""STAGING INFORMATION:
──────────────────
Pattern: {self.staging_info.pattern.value}
Number of Stages: {len(self.staging_info.stages)}
Stages: {' → '.join(self.staging_info.stages)}

"""

        return report

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {
            "name": self.name,
            "quranic_reference": self.quranic_reference,
            "domain": self.domain,
            "validity_score": self.validity_score(),
            "is_valid": self.is_valid(),
            "scores": {
                "tawhid": self.tawhid_score,
                "mizan": self.mizan_score,
                "tadarruj": self.tadarruj_score,
                "maqasid": self.maqasid_score,
                "fitrah": self.fitrah_score,
                "observer": self.observer_score,
            }
        }

        if self.balance_dimensions:
            result["balance"] = self.balance_dimensions.to_dict()

        if self.fitrah_dimensions:
            result["fitrah"] = self.fitrah_dimensions.to_dict()

        if self.maqasid_weights:
            result["maqasid"] = {k.name: v for k, v in self.maqasid_weights.items()}

        return result


class MetaPrincipleValidator:
    """
    Validates principles against the 6 meta-axioms
    """

    def __init__(self):
        self.principles: Dict[str, PrincipleAssessment] = {}

    def register_principle(self, assessment: PrincipleAssessment) -> None:
        """Register a principle for validation"""
        key = f"{assessment.quranic_reference}_{assessment.name}"
        self.principles[key] = assessment

    def validate_all(self) -> Tuple[List[PrincipleAssessment], List[PrincipleAssessment]]:
        """
        Validate all registered principles
        Returns: (valid_principles, invalid_principles)
        """
        valid = []
        invalid = []

        for principle in self.principles.values():
            if principle.is_valid():
                valid.append(principle)
            else:
                invalid.append(principle)

        return valid, invalid

    def print_summary(self) -> None:
        """Print summary of all principles"""
        valid, invalid = self.validate_all()

        print("\n" + "="*70)
        print("META-PRINCIPLE SYSTEM VALIDATION SUMMARY")
        print("="*70)
        print(f"\nTotal Principles: {len(self.principles)}")
        print(f"Valid Principles: {len(valid)}")
        print(f"Invalid Principles: {len(invalid)}")
        print(f"Validity Rate: {100*len(valid)/len(self.principles):.1f}%")

        if valid:
            print("\n" + "VALID PRINCIPLES:")
            print("-" * 70)
            for p in sorted(valid, key=lambda x: x.validity_score(), reverse=True):
                print(f"{p.quranic_reference:12s} {p.name:30s} Score: {p.validity_score():.3f}")

        if invalid:
            print("\n" + "PRINCIPLES NEEDING REVISION:")
            print("-" * 70)
            for p in sorted(invalid, key=lambda x: x.validity_score()):
                print(f"{p.quranic_reference:12s} {p.name:30s} Score: {p.validity_score():.3f}")

        # Calculate average scores across all principles
        print("\n" + "AVERAGE AXIOM SCORES:")
        print("-" * 70)
        avg_tawhid = np.mean([p.tawhid_score for p in self.principles.values()])
        avg_mizan = np.mean([p.mizan_score for p in self.principles.values()])
        avg_tadarruj = np.mean([p.tadarruj_score for p in self.principles.values()])
        avg_maqasid = np.mean([p.maqasid_score for p in self.principles.values()])
        avg_fitrah = np.mean([p.fitrah_score for p in self.principles.values()])
        avg_observer = np.mean([p.observer_score for p in self.principles.values()])

        print(f"Tawhid (Consistency):   {avg_tawhid:.3f}")
        print(f"Mizan (Balance):        {avg_mizan:.3f}")
        print(f"Tadarruj (Staging):     {avg_tadarruj:.3f}")
        print(f"Maqasid (Objectives):   {avg_maqasid:.3f}")
        print(f"Fitrah (Human Nature):  {avg_fitrah:.3f}")
        print(f"Observer (Engagement):  {avg_observer:.3f}")
        print(f"\nSystemwide Average:     {(avg_tawhid + avg_mizan + avg_tadarruj + avg_maqasid + avg_fitrah + avg_observer)/6:.3f}")

    def to_json(self, filepath: str) -> None:
        """Export all principles to JSON"""
        data = {
            "timestamp": "2026-03-15",
            "total_principles": len(self.principles),
            "principles": [p.to_dict() for p in self.principles.values()]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# ============================================================================
# EXAMPLE PRINCIPLES WITH FULL VALIDATION
# ============================================================================

def create_example_principles() -> MetaPrincipleValidator:
    """Create and validate example principles"""
    validator = MetaPrincipleValidator()

    # Example 1: Q2:168 - Tayyib (Good Food)
    tayyib = PrincipleAssessment(
        name="Tayyib (Good Food/Nutrition)",
        quranic_reference="Q2:168",
        domain="Healthcare",
        tawhid_score=0.92,
        mizan_score=0.87,
        tadarruj_score=0.85,
        maqasid_score=0.88,
        fitrah_score=0.84,
        observer_score=0.85,
        balance_dimensions=BalanceDimensions(
            individual_collective=0.85,
            effort_result=0.90,
            short_long_term=0.88,
            rigor_mercy=0.92,
            certainty_flexibility=0.80
        ),
        fitrah_dimensions=FitrahDimensions(
            survival_instinct=0.95,
            social_bonding=0.85,
            parental_love=0.90,
            intellectual_curiosity=0.80,
            fairness_justice=0.88,
            autonomy_freedom=0.75,
            achievement_mastery=0.85,
            transcendence_meaning=0.70
        ),
        maqasid_weights={
            Maqasid.NAFS: 0.80,
            Maqasid.AQL: 0.15,
            Maqasid.DEEN: 0.05
        }
    )
    validator.register_principle(tayyib)

    # Example 2: Q96:1-5 - Knowledge Acquisition
    knowledge = PrincipleAssessment(
        name="Knowledge Acquisition",
        quranic_reference="Q96:1-5",
        domain="Cognition",
        tawhid_score=0.95,
        mizan_score=0.87,
        tadarruj_score=0.88,
        maqasid_score=0.92,
        fitrah_score=0.86,
        observer_score=0.95,
        balance_dimensions=BalanceDimensions(
            individual_collective=0.85,
            effort_result=0.88,
            short_long_term=0.90,
            rigor_mercy=0.82,
            certainty_flexibility=0.90
        ),
        fitrah_dimensions=FitrahDimensions(
            survival_instinct=0.70,
            social_bonding=0.80,
            parental_love=0.75,
            intellectual_curiosity=0.98,
            fairness_justice=0.85,
            autonomy_freedom=0.90,
            achievement_mastery=0.95,
            transcendence_meaning=0.95
        ),
        maqasid_weights={
            Maqasid.AQL: 0.50,
            Maqasid.NAFS: 0.30,
            Maqasid.DEEN: 0.15,
            Maqasid.MAL: 0.05
        }
    )
    validator.register_principle(knowledge)

    # Example 3: Q39:6 - Structural Layers
    layers = PrincipleAssessment(
        name="Seven Structural Layers",
        quranic_reference="Q39:6",
        domain="Engineering",
        tawhid_score=0.93,
        mizan_score=0.84,
        tadarruj_score=0.90,
        maqasid_score=0.85,
        fitrah_score=0.84,
        observer_score=0.82,
        balance_dimensions=BalanceDimensions(
            individual_collective=0.82,
            effort_result=0.88,
            short_long_term=0.85,
            rigor_mercy=0.78,
            certainty_flexibility=0.85
        ),
        fitrah_dimensions=FitrahDimensions(
            survival_instinct=0.88,
            social_bonding=0.82,
            parental_love=0.80,
            intellectual_curiosity=0.85,
            fairness_justice=0.85,
            autonomy_freedom=0.78,
            achievement_mastery=0.92,
            transcendence_meaning=0.75
        ),
        maqasid_weights={
            Maqasid.NAFS: 0.60,
            Maqasid.AQL: 0.25,
            Maqasid.MAL: 0.15
        }
    )
    validator.register_principle(layers)

    # Example 4: Q2:275 - Riba (Interest) Prohibition
    riba = PrincipleAssessment(
        name="Riba (Interest) Prohibition",
        quranic_reference="Q2:275",
        domain="Finance",
        tawhid_score=0.91,
        mizan_score=0.87,
        tadarruj_score=0.82,
        maqasid_score=0.94,
        fitrah_score=0.77,
        observer_score=0.85,
        balance_dimensions=BalanceDimensions(
            individual_collective=0.90,
            effort_result=0.85,
            short_long_term=0.92,
            rigor_mercy=0.88,
            certainty_flexibility=0.80
        ),
        fitrah_dimensions=FitrahDimensions(
            survival_instinct=0.45,
            social_bonding=0.70,
            parental_love=0.75,
            intellectual_curiosity=0.85,
            fairness_justice=0.95,
            autonomy_freedom=0.80,
            achievement_mastery=0.80,
            transcendence_meaning=0.85
        ),
        maqasid_weights={
            Maqasid.MAL: 0.70,
            Maqasid.NAFS: 0.20,
            Maqasid.AQL: 0.10
        }
    )
    validator.register_principle(riba)

    # Example 5: Q29:69 - Struggle for Guidance
    struggle = PrincipleAssessment(
        name="Struggle-Driven Learning",
        quranic_reference="Q29:69",
        domain="Cognition",
        tawhid_score=0.94,
        mizan_score=0.88,
        tadarruj_score=0.87,
        maqasid_score=0.90,
        fitrah_score=0.88,
        observer_score=0.92,
        balance_dimensions=BalanceDimensions(
            individual_collective=0.85,
            effort_result=0.92,
            short_long_term=0.90,
            rigor_mercy=0.85,
            certainty_flexibility=0.85
        ),
        fitrah_dimensions=FitrahDimensions(
            survival_instinct=0.75,
            social_bonding=0.85,
            parental_love=0.80,
            intellectual_curiosity=0.92,
            fairness_justice=0.88,
            autonomy_freedom=0.90,
            achievement_mastery=0.98,
            transcendence_meaning=0.92
        ),
        maqasid_weights={
            Maqasid.AQL: 0.60,
            Maqasid.NAFS: 0.25,
            Maqasid.DEEN: 0.15
        }
    )
    validator.register_principle(struggle)

    return validator


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\nINITIALIZING META-PRINCIPLE FRAMEWORK")
    print("="*70)

    # Create and validate example principles
    validator = create_example_principles()

    # Print summary
    validator.print_summary()

    # Print detailed reports for each principle
    print("\n\n" + "="*70)
    print("DETAILED VALIDATION REPORTS")
    print("="*70)

    for principle in validator.principles.values():
        print(principle.validation_report())

    # Export to JSON
    output_path = "/Users/mac/Desktop/QuranFrontier/quran-core/docs/meta_principles_validation.json"
    validator.to_json(output_path)
    print(f"\nValidation data exported to: {output_path}")
