"""Algorithm 4: Classical Islamic Scholarly Logic and Jurisprudential Reasoning.

Formalizes Islamic jurisprudential reasoning using multi-valued logic,
school of thought (madhab) positions, qiyas (analogical reasoning),
and istislah (public interest) scoring.

Wires to quran-core/src/logic/deontic.py for DeonticStatus when available.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import sys
import os

# ---------------------------------------------------------------------------
# Optional integration with quran-core deontic logic
# ---------------------------------------------------------------------------
_DEONTIC_AVAILABLE = False
_DeonticStatus = None

def _try_import_deontic():
    """Attempt to import DeonticStatus from quran-core."""
    global _DEONTIC_AVAILABLE, _DeonticStatus
    # Resolve path relative to this file: ../../quran-core/src
    _here = os.path.dirname(os.path.abspath(__file__))
    _root = os.path.abspath(os.path.join(_here, "..", "..", "quran-core", "src"))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    try:
        from logic.deontic import DeonticStatus  # type: ignore
        _DeonticStatus = DeonticStatus
        _DEONTIC_AVAILABLE = True
    except ImportError:
        pass

_try_import_deontic()


# ---------------------------------------------------------------------------
# Core enumerations
# ---------------------------------------------------------------------------

class EvidenceType(Enum):
    """Evidence source types with inherent weights per usul al-fiqh hierarchy."""
    QURAN = 1.0
    AUTHENTIC_HADITH = 0.95
    GOOD_HADITH = 0.85
    IJMA = 0.90
    QIYAS = 0.70
    ISTIHSAN = 0.60
    ISTISLAH = 0.50
    CUSTOM = 0.40


class JurisprudentialSchool(Enum):
    HANAFI = "Hanafi"
    MALIKI = "Maliki"
    SHAFI = "Shafi'i"
    HANBALI = "Hanbali"


class ConfidenceLevel(Enum):
    HIGH = "HIGH"       # >= 0.85 or unanimous school agreement
    MODERATE = "MODERATE"  # >= 0.65 or majority school agreement
    LOW = "LOW"         # < 0.65 or split schools


class IslamicRuling(Enum):
    FARD = "obligatory"
    WAJIB = "necessary"
    MANDUB = "recommended"
    MUBAH = "permissible"
    MAKRUH = "disliked"
    HARAM = "forbidden"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Evidence:
    source: str
    evidence_type: EvidenceType
    text: str
    reliability: float  # 0-1

    @property
    def weight(self) -> float:
        """Effective weight = type_value × reliability."""
        return self.evidence_type.value * self.reliability


@dataclass
class SchoolPosition:
    school: JurisprudentialSchool
    ruling: IslamicRuling
    reasoning: str
    evidence: List[Evidence] = field(default_factory=list)

    @property
    def strength(self) -> float:
        """Position strength: min(1.0, Σ weights / 2.0)."""
        if not self.evidence:
            return 0.0
        return min(1.0, sum(e.weight for e in self.evidence) / 2.0)


@dataclass
class QiyasArgument:
    primary_case: str
    primary_ruling: IslamicRuling
    effective_cause: str    # 'illa (ratio legis)
    secondary_case: str
    cause_similarity: float  # 0-1
    derived_ruling: Optional[IslamicRuling] = None
    valid: bool = False


@dataclass
class JurisprudentialAnalysis:
    question: str
    direct_evidence: List[Evidence]
    school_positions: Dict[str, SchoolPosition]
    qiyas_arguments: List[QiyasArgument]
    recommended_ruling: Optional[IslamicRuling]
    confidence: ConfidenceLevel
    reasoning_summary: str


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

class IslamicJurisprudenceAnalyzer:
    """Implements Algorithm 4: Classical Islamic Scholarly Logic.

    Covers:
    - Multi-valued evidence strength calculation
    - School-of-thought (madhab) position lookup
    - Qiyas (analogical reasoning)
    - Istislah (public interest) scoring
    - School disagreement graph
    """

    # Built-in knowledge base of classic rulings per school.
    # Format: question_key -> {school -> (ruling, reasoning, evidence_weight)}
    SCHOOL_POSITIONS_DB: Dict[str, Dict] = {
        "prayer_5_times": {
            JurisprudentialSchool.HANAFI: (IslamicRuling.FARD, "Established by Quran 4:103 and prophetic tradition", 1.0),
            JurisprudentialSchool.MALIKI: (IslamicRuling.FARD, "Established by Quran and mass-transmitted hadith", 1.0),
            JurisprudentialSchool.SHAFI:  (IslamicRuling.FARD, "Q4:103 decisive, supported by mutawatir hadith", 1.0),
            JurisprudentialSchool.HANBALI:(IslamicRuling.FARD, "Quran, Sunnah, Ijma all agree", 1.0),
        },
        "fasting_ramadan": {
            JurisprudentialSchool.HANAFI: (IslamicRuling.FARD, "Q2:183-185 explicit command", 1.0),
            JurisprudentialSchool.MALIKI: (IslamicRuling.FARD, "Q2:183 and prophetic narrations", 1.0),
            JurisprudentialSchool.SHAFI:  (IslamicRuling.FARD, "Q2:183 direct obligation", 1.0),
            JurisprudentialSchool.HANBALI:(IslamicRuling.FARD, "Quran, Sunnah, Ijma consensus", 1.0),
        },
        "wine_prohibition": {
            JurisprudentialSchool.HANAFI: (IslamicRuling.HARAM, "Q5:90 explicit, effective cause is intoxication", 0.95),
            JurisprudentialSchool.MALIKI: (IslamicRuling.HARAM, "Q5:90 and hadiths on khamr", 0.95),
            JurisprudentialSchool.SHAFI:  (IslamicRuling.HARAM, "Q5:90 decisive prohibition", 0.95),
            JurisprudentialSchool.HANBALI:(IslamicRuling.HARAM, "Q5:90, mass-narrated hadith, ijma", 0.95),
        },
        "charity_zakat": {
            JurisprudentialSchool.HANAFI: (IslamicRuling.FARD, "Q2:43 explicit, nisab threshold applies", 0.9),
            JurisprudentialSchool.MALIKI: (IslamicRuling.FARD, "Q9:103, with specific calculation rules", 0.9),
            JurisprudentialSchool.SHAFI:  (IslamicRuling.FARD, "Q2:43, Q9:103, scholarly consensus", 0.9),
            JurisprudentialSchool.HANBALI:(IslamicRuling.FARD, "Quran and Sunnah both establish it", 0.9),
        },
    }

    # Classic qiyas cases: primary_case_key -> (effective_cause, ruling)
    QIYAS_CASES: Dict[str, Tuple[str, IslamicRuling]] = {
        "wine":     ("intoxication",      IslamicRuling.HARAM),
        "gambling": ("unjust_enrichment", IslamicRuling.HARAM),
        "usury":    ("exploitation",      IslamicRuling.HARAM),
    }

    # Synonyms / related terms for each QIYAS_CASES primary case.
    # Used to detect when a question's subject shares the effective cause.
    _QIYAS_SYNONYMS: Dict[str, List[str]] = {
        "wine":     ["beer", "alcohol", "spirits", "liquor", "khamr", "intoxicant",
                     "intoxication", "fermented", "brew"],
        "gambling": ["lottery", "bet", "wager", "casino", "speculation"],
        "usury":    ["interest", "riba", "loan", "debt", "usurious"],
    }

    # Keyword synonyms used for DB fuzzy-matching
    _KEY_SYNONYMS: Dict[str, List[str]] = {
        "wine_prohibition": ["wine", "khamr", "alcohol", "intoxicant", "liquor", "beer", "spirits"],
        "prayer_5_times":   ["prayer", "salah", "salat", "namaz"],
        "fasting_ramadan":  ["fast", "fasting", "ramadan", "sawm", "siyam"],
        "charity_zakat":    ["zakat", "charity", "zakah", "sadaqa"],
    }

    def __init__(self):
        self.deontic_available = _DEONTIC_AVAILABLE
        self.DeonticStatus = _DeonticStatus

    # ------------------------------------------------------------------
    # Core calculation methods
    # ------------------------------------------------------------------

    def calculate_evidence_strength(self, evidence_list: List[Evidence]) -> float:
        """Return min(1.0, Σ(type.value × reliability) / 2.0)."""
        if not evidence_list:
            return 0.0
        total = sum(e.weight for e in evidence_list)
        return min(1.0, total / 2.0)

    def find_school_positions(self, question: str) -> Dict[JurisprudentialSchool, SchoolPosition]:
        """Look up school positions from DB using keyword matching on question."""
        question_lower = question.lower()
        matched_key = self._match_db_key(question_lower)

        if matched_key is None:
            return {}

        db_entry = self.SCHOOL_POSITIONS_DB[matched_key]
        positions: Dict[JurisprudentialSchool, SchoolPosition] = {}

        for school, (ruling, reasoning, evidence_weight) in db_entry.items():
            # Construct representative evidence from the entry's weight
            ev = Evidence(
                source=reasoning,
                evidence_type=EvidenceType.QURAN if evidence_weight >= 1.0 else EvidenceType.AUTHENTIC_HADITH,
                text=reasoning,
                reliability=evidence_weight,
            )
            positions[school] = SchoolPosition(
                school=school,
                ruling=ruling,
                reasoning=reasoning,
                evidence=[ev],
            )

        return positions

    def _match_db_key(self, question_lower: str) -> Optional[str]:
        """Return the first DB key whose synonyms appear in the question string."""
        for db_key, synonyms in self._KEY_SYNONYMS.items():
            for word in synonyms:
                if word in question_lower:
                    return db_key
        # Fallback: try direct substring match on DB keys
        for db_key in self.SCHOOL_POSITIONS_DB:
            if db_key.replace("_", " ") in question_lower or db_key in question_lower:
                return db_key
        return None

    def build_qiyas_argument(
        self,
        question: str,
        analogous_case: str,
    ) -> Optional[QiyasArgument]:
        """Build a qiyas argument by analogy from *analogous_case*.

        If the analogous case is in QIYAS_CASES, derive the same ruling for
        *question*.  cause_similarity is computed from keyword overlap between
        question and the primary case keywords.
        """
        case_key = analogous_case.lower().strip()
        if case_key not in self.QIYAS_CASES:
            return None

        effective_cause, primary_ruling = self.QIYAS_CASES[case_key]

        # Measure similarity: fraction of primary-case keywords present in question.
        # Include synonyms to handle semantically related terms (e.g. "beer" ~ "wine").
        synonyms = self._QIYAS_SYNONYMS.get(case_key, [])
        primary_keywords = (
            set(case_key.split())
            | set(effective_cause.split("_"))
            | set(synonyms)
        )
        question_lower_str = question.lower()
        question_words = set(question_lower_str.split())
        overlap = len(primary_keywords & question_words)
        cause_similarity = min(1.0, overlap / max(1, len(primary_keywords)))

        # Qiyas is valid if the question shares the effective cause conceptually:
        # - direct case-key match, or
        # - effective cause tokens present in the question, or
        # - any synonym appears in the question, or
        # - non-zero keyword overlap
        valid = (
            case_key in question_lower_str
            or any(tok in question_lower_str for tok in effective_cause.split("_"))
            or any(syn in question_lower_str for syn in synonyms)
            or cause_similarity > 0.0
        )

        derived_ruling = primary_ruling if valid else None

        return QiyasArgument(
            primary_case=analogous_case,
            primary_ruling=primary_ruling,
            effective_cause=effective_cause,
            secondary_case=question,
            cause_similarity=cause_similarity,
            derived_ruling=derived_ruling,
            valid=valid,
        )

    def calculate_istislah_score(self, ruling: IslamicRuling, context: str = "") -> float:
        """Public interest score: (benefit - harm) × scriptural consonance.

        Simplified mapping based on ruling type:
          FARD/WAJIB  -> high benefit (0.9)
          MANDUB      -> moderate benefit (0.7)
          MUBAH       -> neutral (0.5)
          MAKRUH      -> slight harm (0.4)
          HARAM       -> preventing major harm (0.8)
        """
        ruling_scores = {
            IslamicRuling.FARD:   (0.95, 0.05, 0.95),  # (benefit, harm, consonance)
            IslamicRuling.WAJIB:  (0.90, 0.05, 0.90),
            IslamicRuling.MANDUB: (0.70, 0.10, 0.80),
            IslamicRuling.MUBAH:  (0.55, 0.05, 0.70),
            IslamicRuling.MAKRUH: (0.30, 0.40, 0.60),
            IslamicRuling.HARAM:  (0.05, 0.90, 0.95),  # preventing harm
        }
        benefit, harm, consonance = ruling_scores.get(ruling, (0.5, 0.5, 0.5))
        # For HARAM, the "benefit" of the rule is preventing harm
        if ruling == IslamicRuling.HARAM:
            net = harm - benefit  # net benefit of the prohibition
            return float(min(1.0, max(0.0, net * consonance)))
        score = (benefit - harm) * consonance
        return float(min(1.0, max(0.0, score)))

    def determine_confidence(
        self, school_positions: Dict
    ) -> ConfidenceLevel:
        """HIGH if all schools agree, MODERATE if >= 3 agree, LOW if split."""
        if not school_positions:
            return ConfidenceLevel.LOW

        # Normalise values – accept both SchoolPosition objects and raw tuples
        rulings = []
        for v in school_positions.values():
            if isinstance(v, SchoolPosition):
                rulings.append(v.ruling)
            elif isinstance(v, tuple) and len(v) >= 1:
                rulings.append(v[0])
            else:
                rulings.append(v)

        if len(set(rulings)) == 1:
            return ConfidenceLevel.HIGH

        from collections import Counter
        most_common_count = Counter(rulings).most_common(1)[0][1]
        total = len(rulings)

        if most_common_count >= 3 or most_common_count / total >= 0.75:
            return ConfidenceLevel.MODERATE

        return ConfidenceLevel.LOW

    # ------------------------------------------------------------------
    # High-level analysis
    # ------------------------------------------------------------------

    def analyze(self, question: str, context: str = "") -> JurisprudentialAnalysis:
        """Complete jurisprudential analysis of *question*."""
        # 1. Find school positions
        positions = self.find_school_positions(question)

        # 2. Gather direct evidence from all positions
        direct_evidence: List[Evidence] = []
        for sp in positions.values():
            direct_evidence.extend(sp.evidence)

        # 3. Attempt qiyas for each known primary case
        qiyas_args: List[QiyasArgument] = []
        for case_key in self.QIYAS_CASES:
            qarg = self.build_qiyas_argument(question, case_key)
            if qarg is not None and qarg.valid:
                qiyas_args.append(qarg)

        # 4. Determine recommended ruling (majority vote among schools)
        recommended: Optional[IslamicRuling] = None
        if positions:
            from collections import Counter
            ruling_counts = Counter(sp.ruling for sp in positions.values())
            recommended = ruling_counts.most_common(1)[0][0]
        elif qiyas_args:
            recommended = qiyas_args[0].derived_ruling

        # 5. Confidence level
        confidence = self.determine_confidence(positions)

        # 6. Reasoning summary
        school_names = [sp.school.value for sp in positions.values()]
        methods_used = ["direct textual evidence"] if direct_evidence else []
        if qiyas_args:
            methods_used.append("qiyas (analogical reasoning)")
        summary = (
            f"Analysis of '{question}'. "
            f"Schools consulted: {', '.join(school_names) if school_names else 'none'}. "
            f"Methods used: {', '.join(methods_used) if methods_used else 'general principles'}. "
            f"Recommended ruling: {recommended.value if recommended else 'undetermined'}."
        )

        return JurisprudentialAnalysis(
            question=question,
            direct_evidence=direct_evidence,
            school_positions={s.value: p for s, p in positions.items()},
            qiyas_arguments=qiyas_args,
            recommended_ruling=recommended,
            confidence=confidence,
            reasoning_summary=summary,
        )

    def compare_schools(self, question: str) -> Dict:
        """Return all school positions side by side for *question*."""
        positions = self.find_school_positions(question)
        result = {}
        for school, sp in positions.items():
            result[school.value] = {
                "ruling": sp.ruling.value,
                "reasoning": sp.reasoning,
                "strength": sp.strength,
            }
        return result

    def build_disagreement_graph(self, question: str) -> Dict:
        """Map which schools agree / disagree and why.

        Returns a dict with:
          - agreements: list of (school_a, school_b) pairs sharing the same ruling
          - disagreements: list of (school_a, school_b, ruling_a, ruling_b) tuples
          - ruling_clusters: {ruling -> [schools]}
        """
        positions = self.find_school_positions(question)
        schools = list(positions.keys())

        agreements = []
        disagreements = []
        ruling_clusters: Dict[str, List[str]] = {}

        for school, sp in positions.items():
            ruling_val = sp.ruling.value
            ruling_clusters.setdefault(ruling_val, []).append(school.value)

        for i, s_a in enumerate(schools):
            for s_b in schools[i + 1:]:
                if positions[s_a].ruling == positions[s_b].ruling:
                    agreements.append((s_a.value, s_b.value))
                else:
                    disagreements.append((
                        s_a.value, s_b.value,
                        positions[s_a].ruling.value,
                        positions[s_b].ruling.value,
                    ))

        return {
            "question": question,
            "agreements": agreements,
            "disagreements": disagreements,
            "ruling_clusters": ruling_clusters,
            "consensus": len(disagreements) == 0 and len(agreements) > 0,
        }


# ---------------------------------------------------------------------------
# Demo / runnable entry point
# ---------------------------------------------------------------------------

def _demo():
    analyzer = IslamicJurisprudenceAnalyzer()
    print("=" * 60)
    print("Demo: Wine Question")
    print("=" * 60)
    analysis = analyzer.analyze("Is wine permissible in Islam?")
    print(f"Question : {analysis.question}")
    print(f"Ruling   : {analysis.recommended_ruling}")
    print(f"Confidence: {analysis.confidence.value}")
    print(f"Summary  : {analysis.reasoning_summary}")
    print()
    graph = analyzer.build_disagreement_graph("wine")
    print("Disagreement graph:", json.dumps(graph, indent=2))

    print()
    print("=" * 60)
    print("Demo: Prayer Question")
    print("=" * 60)
    analysis2 = analyzer.analyze("Is daily prayer obligatory?")
    print(f"Question : {analysis2.question}")
    print(f"Ruling   : {analysis2.recommended_ruling}")
    print(f"Confidence: {analysis2.confidence.value}")
    print(f"Summary  : {analysis2.reasoning_summary}")

    print()
    print("=" * 60)
    print("Demo: Qiyas – Beer question")
    print("=" * 60)
    qarg = analyzer.build_qiyas_argument("Is beer forbidden?", "wine")
    if qarg:
        print(f"Primary case     : {qarg.primary_case}")
        print(f"Effective cause  : {qarg.effective_cause}")
        print(f"Derived ruling   : {qarg.derived_ruling}")
        print(f"Valid            : {qarg.valid}")
        print(f"Cause similarity : {qarg.cause_similarity:.2f}")


if __name__ == "__main__":
    _demo()
