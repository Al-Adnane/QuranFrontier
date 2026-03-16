from enum import IntEnum
from typing import Dict


class ClassificationTier(IntEnum):
    """Enumeration for three-tier classification system."""
    EMPIRICAL = 1        # Direct peer-reviewed consensus
    FRONTIER = 2         # Frontier/theoretical research
    METAPHORICAL = 3     # Historical/metaphorical only


class TieredClassifier:
    """
    Governance layer that enforces scientific rigor by categorizing claims
    into three tiers with confidence ceilings.
    """

    # Confidence ceilings for each tier
    CONFIDENCE_CEILINGS = {
        ClassificationTier.EMPIRICAL: 0.95,      # Tier 1
        ClassificationTier.FRONTIER: 0.60,       # Tier 2
        ClassificationTier.METAPHORICAL: 0.30    # Tier 3
    }

    def classify(self, claim: Dict) -> int:
        """
        Classify a claim into one of three tiers based on its supporting sources
        and metadata.

        Classification logic:
        - If metaphorical flag: return 3
        - If no sources: return 3
        - If ≥2 peer-reviewed sources: return 1
        - If ≥1 peer-reviewed, no preprints: return 1
        - If preprints exist: return 2
        - Default: return 3

        Args:
            claim: Dictionary containing claim information with keys:
                - supporting_sources: List of source dictionaries
                - is_metaphorical: Optional boolean flag

        Returns:
            int: Tier classification (1, 2, or 3)
        """
        # Check if metaphorical flag is set
        if claim.get("is_metaphorical", False):
            return ClassificationTier.METAPHORICAL

        # Get sources list
        supporting_sources = claim.get("supporting_sources", [])

        # If no sources, return tier 3
        if not supporting_sources:
            return ClassificationTier.METAPHORICAL

        # Count peer-reviewed and preprint sources
        peer_reviewed_count = sum(
            1 for source in supporting_sources
            if source.get("type") == "peer-reviewed"
        )

        preprint_count = sum(
            1 for source in supporting_sources
            if source.get("type") == "preprint"
        )

        # If ≥2 peer-reviewed sources: return tier 1
        if peer_reviewed_count >= 2:
            return ClassificationTier.EMPIRICAL

        # If ≥1 peer-reviewed and no preprints: return tier 1
        if peer_reviewed_count >= 1 and preprint_count == 0:
            return ClassificationTier.EMPIRICAL

        # If preprints exist: return tier 2
        if preprint_count > 0:
            return ClassificationTier.FRONTIER

        # Default: return tier 3
        return ClassificationTier.METAPHORICAL

    def get_confidence_ceiling(self, tier: int) -> float:
        """
        Get the maximum confidence level allowed for a given tier.

        Args:
            tier: Classification tier (1, 2, or 3)

        Returns:
            float: Maximum confidence ceiling for the tier
        """
        return self.CONFIDENCE_CEILINGS.get(tier, 0.30)

    def validate_confidence(self, tier: int, confidence: float) -> bool:
        """
        Validate that a confidence value is within the acceptable range for its tier.

        Args:
            tier: Classification tier (1, 2, or 3)
            confidence: Confidence value to validate (0.0 to 1.0)

        Returns:
            bool: True if confidence is <= ceiling for the tier, False otherwise
        """
        ceiling = self.get_confidence_ceiling(tier)
        return confidence <= ceiling
