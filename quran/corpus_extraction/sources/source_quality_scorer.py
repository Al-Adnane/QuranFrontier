"""
Source Quality Scorer module for assessing academic paper quality and reliability.

This module provides:
- Quality scoring based on journal impact, recency, citations, and peer review status
- Batch scoring of multiple sources
- Statistical analysis of quality distributions
"""

import statistics
from typing import Dict, List, Optional
from datetime import datetime


class SourceQualityScorer:
    """Scores academic papers based on multiple quality metrics."""

    # Top-tier journals (highest impact)
    TOP_TIER_JOURNALS = {
        "Nature", "Science", "Cell", "PNAS",
        "Nature Medicine", "Nature Biotechnology",
        "The Lancet", "JAMA", "BMJ"
    }

    # High-tier journals
    HIGH_TIER_JOURNALS = {
        "Nature Physics", "Nature Chemistry", "Nature Astronomy",
        "Science Translational Medicine", "eLife",
        "PLOS Biology", "PLOS Medicine"
    }

    # Preprint servers (no peer review)
    PREPRINT_SERVERS = {"arXiv", "bioRxiv", "medRxiv", "chemRxiv"}

    def __init__(self):
        """Initialize SourceQualityScorer with scoring configuration."""
        self.current_year = datetime.now().year

    def calculate_quality_score(self, source: Dict) -> float:
        """
        Calculate quality score for a single source (0.0 to 1.0).

        Scoring factors:
        - Journal impact (0-0.3): Nature/Science/Cell=0.3, top-tier=0.2, others=0.1
        - Recency (0-0.2): last 2 years=0.2, last 5 years=0.15, older=0.1
        - Citation count (0-0.3): 100+=0.3, 10+=0.2, <10=0.1
        - Peer review status (0-0.2): peer-reviewed=0.2, preprint=0.0

        Args:
            source: Dict with journal, year, citations, peer_reviewed

        Returns:
            float: Quality score between 0.0 and 1.0
        """
        score = 0.0

        # Journal impact scoring (0-0.3)
        score += self._score_journal_impact(source.get("journal", ""))

        # Recency scoring (0-0.2)
        score += self._score_recency(source.get("year"))

        # Citation count scoring (0-0.3)
        score += self._score_citations(source.get("citations", 0))

        # Peer review scoring (0-0.2)
        score += self._score_peer_review(source.get("peer_reviewed", False))

        return round(min(1.0, max(0.0, score)), 3)

    def _score_journal_impact(self, journal: str) -> float:
        """
        Score journal impact factor (0-0.3 points).

        Args:
            journal: Journal name

        Returns:
            float: Impact score (0-0.3)
        """
        if not journal:
            return 0.05

        journal_lower = journal.lower().strip()

        # Check for preprint server
        for preprint in self.PREPRINT_SERVERS:
            if preprint.lower() in journal_lower:
                return 0.0

        # Top-tier journals
        for top_journal in self.TOP_TIER_JOURNALS:
            if top_journal.lower() in journal_lower:
                return 0.3

        # High-tier journals
        for high_journal in self.HIGH_TIER_JOURNALS:
            if high_journal.lower() in journal_lower:
                return 0.2

        # Other peer-reviewed journals (lower score for unknown journals)
        return 0.08

    def _score_recency(self, year: Optional[int]) -> float:
        """
        Score paper recency (0-0.2 points).

        Args:
            year: Publication year

        Returns:
            float: Recency score (0-0.2)
        """
        if not year or not isinstance(year, int):
            return 0.1

        age = self.current_year - year

        if age <= 2:
            return 0.2
        elif age <= 5:
            return 0.15
        elif age <= 10:
            return 0.12
        else:
            return 0.1

    def _score_citations(self, citations: int) -> float:
        """
        Score based on citation count (0-0.3 points).

        Args:
            citations: Number of citations

        Returns:
            float: Citation score (0-0.3)
        """
        if citations is None or citations < 0:
            return 0.0

        if citations >= 100:
            return 0.3
        elif citations >= 50:
            return 0.25
        elif citations >= 10:
            return 0.2
        elif citations >= 1:
            return 0.1
        else:
            return 0.0

    def _score_peer_review(self, peer_reviewed: bool) -> float:
        """
        Score peer review status (0-0.2 points).

        Args:
            peer_reviewed: Whether paper is peer-reviewed

        Returns:
            float: Peer review score (0-0.2)
        """
        return 0.2 if peer_reviewed else 0.0

    def score_all_sources(self, sources: List[Dict]) -> List[Dict]:
        """
        Score all sources in batch.

        Args:
            sources: List of source dicts

        Returns:
            list: Sources with added 'quality_score' field
        """
        scored_sources = []

        for source in sources:
            scored_source = source.copy()
            scored_source["quality_score"] = self.calculate_quality_score(source)
            scored_sources.append(scored_source)

        return scored_sources

    def get_quality_statistics(self, scored_sources: List[Dict]) -> Dict:
        """
        Generate statistics for quality scores.

        Args:
            scored_sources: List of sources with 'quality_score' field

        Returns:
            dict: Statistics including mean, std_dev, min, max, quartiles
        """
        scores = [s.get("quality_score", 0) for s in scored_sources if "quality_score" in s]

        if not scores:
            return {
                "total": 0,
                "mean": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "median": 0.0,
                "q1": 0.0,
                "q3": 0.0
            }

        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        # Calculate quartiles
        q1_index = n // 4
        median_index = n // 2
        q3_index = 3 * n // 4

        return {
            "total": n,
            "mean": round(statistics.mean(scores), 3),
            "std_dev": round(statistics.stdev(scores), 3) if n > 1 else 0.0,
            "min": round(min(scores), 3),
            "max": round(max(scores), 3),
            "median": round(sorted_scores[median_index], 3),
            "q1": round(sorted_scores[q1_index], 3),
            "q3": round(sorted_scores[q3_index], 3),
            "percentile_75": round(sorted_scores[int(0.75 * n)], 3) if n > 0 else 0.0,
            "percentile_90": round(sorted_scores[int(0.90 * n)], 3) if n > 0 else 0.0
        }

    def categorize_by_quality(self, scored_sources: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize sources by quality tier.

        Args:
            scored_sources: List of sources with 'quality_score' field

        Returns:
            dict: {
                'excellent': [sources with score >= 0.8],
                'good': [sources with 0.6-0.8],
                'acceptable': [sources with 0.4-0.6],
                'poor': [sources with < 0.4]
            }
        """
        categories = {
            'excellent': [],
            'good': [],
            'acceptable': [],
            'poor': []
        }

        for source in scored_sources:
            score = source.get("quality_score", 0)

            if score >= 0.8:
                categories['excellent'].append(source)
            elif score >= 0.6:
                categories['good'].append(source)
            elif score >= 0.4:
                categories['acceptable'].append(source)
            else:
                categories['poor'].append(source)

        return categories

    def get_recommendation(self, quality_score: float) -> str:
        """
        Get recommendation based on quality score.

        Args:
            quality_score: Quality score (0-1)

        Returns:
            str: Recommendation text
        """
        if quality_score >= 0.8:
            return "HIGHLY RECOMMENDED - Top quality source"
        elif quality_score >= 0.6:
            return "RECOMMENDED - Good quality source"
        elif quality_score >= 0.4:
            return "ACCEPTABLE - Can be used with caution"
        else:
            return "NOT RECOMMENDED - Consider alternative sources"
