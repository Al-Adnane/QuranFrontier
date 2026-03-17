"""
OntologyManager: Manages scientific concepts ontology for Quranic corpus analysis.

This module provides a comprehensive interface for loading, querying, and managing
a hierarchical ontology of 1,000+ scientific concepts across 5 domains:
- Physics
- Biology
- Medicine
- Engineering
- Agriculture

Each concept is organized by tier (1=Empirical, 2=Frontier, 3=Metaphorical)
and includes domain-specific mappings and relationships.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class OntologyManager:
    """
    Manages scientific concepts ontology across multiple domains.

    This class loads and maintains a hierarchical ontology of scientific concepts
    with support for querying by domain, tier, and relationships. It provides
    methods for loading ontology data, managing concepts, and validating
    hierarchy integrity.

    Attributes:
        concepts: Dictionary storing all loaded concepts by ID
        domain_mappings: Dictionary storing domain metadata and statistics
        valid_domains: Set of valid domain names
    """

    VALID_DOMAINS = {"physics", "biology", "medicine", "engineering", "agriculture"}
    VALID_TIERS = {1, 2, 3}
    REQUIRED_CONCEPT_FIELDS = {"id", "name", "domain", "tier", "definition", "confidence"}

    def __init__(self):
        """Initialize OntologyManager with empty concept store."""
        self.concepts: Dict[str, Dict] = {}
        self.domain_mappings: Dict[str, Dict] = {}
        self._load_seed_data()

    def _load_seed_data(self) -> None:
        """Load seed data from JSON files in the ontology module directory."""
        module_dir = Path(__file__).parent

        # Load scientific concepts
        concepts_file = module_dir / "scientific_concepts.json"
        if concepts_file.exists():
            with open(concepts_file, "r") as f:
                data = json.load(f)
                for concept in data.get("concepts", []):
                    self.concepts[concept["id"]] = concept

        # Load domain mappings
        mappings_file = module_dir / "domain_mappings.json"
        if mappings_file.exists():
            with open(mappings_file, "r") as f:
                data = json.load(f)
                self.domain_mappings = data.get("domains", {})

    def load_ontology(self) -> Dict[str, Dict]:
        """
        Load the complete ontology.

        Returns:
            Dictionary of all concepts keyed by concept ID
        """
        return self.concepts

    def get_concept(self, concept_id: str) -> Optional[Dict]:
        """
        Retrieve a specific concept by ID.

        Args:
            concept_id: The unique identifier of the concept

        Returns:
            Concept dictionary if found, None otherwise
        """
        return self.concepts.get(concept_id)

    def add_concept(self, concept: Dict) -> None:
        """
        Add a new concept to the ontology.

        Args:
            concept: Dictionary containing concept data with required fields:
                - id: Unique identifier
                - name: Concept name
                - domain: Scientific domain
                - tier: Classification tier (1, 2, or 3)
                - definition: Concept definition
                - confidence: Confidence value (0.0-1.0)

        Raises:
            ValueError: If concept is missing required fields or has invalid values
        """
        # Validate required fields
        missing_fields = self.REQUIRED_CONCEPT_FIELDS - set(concept.keys())
        if missing_fields:
            raise ValueError(f"Concept missing required fields: {missing_fields}")

        # Validate domain
        if concept.get("domain") not in self.VALID_DOMAINS:
            raise ValueError(f"Invalid domain: {concept.get('domain')}")

        # Validate tier
        if concept.get("tier") not in self.VALID_TIERS:
            raise ValueError(f"Invalid tier: {concept.get('tier')}")

        # Validate confidence
        confidence = concept.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            raise ValueError(f"Confidence must be between 0 and 1, got {confidence}")

        # Add concept
        self.concepts[concept["id"]] = concept

    def get_domain_concepts(self, domain: str) -> List[Dict]:
        """
        Retrieve all concepts from a specific domain.

        Args:
            domain: The scientific domain name

        Returns:
            List of concepts in the specified domain
        """
        return [
            concept for concept in self.concepts.values()
            if isinstance(concept, dict) and concept.get("domain") == domain
        ]

    def get_concepts_by_tier(self, tier: int) -> List[Dict]:
        """
        Retrieve all concepts with a specific tier classification.

        Args:
            tier: The classification tier (1, 2, or 3)

        Returns:
            List of concepts with the specified tier
        """
        return [
            concept for concept in self.concepts.values()
            if isinstance(concept, dict) and concept.get("tier") == tier
        ]

    def get_domain_count(self, domain: str) -> int:
        """
        Get the count of concepts in a specific domain.

        Args:
            domain: The scientific domain name

        Returns:
            Number of concepts in the domain
        """
        return len(self.get_domain_concepts(domain))

    def get_ontology_size(self) -> int:
        """
        Get the total number of concepts in the ontology.

        Returns:
            Total concept count
        """
        return len(self.concepts)

    def get_domain_distribution(self) -> Dict[str, int]:
        """
        Get distribution of concepts across all domains.

        Returns:
            Dictionary mapping domain names to concept counts
        """
        distribution = {}
        for domain in self.VALID_DOMAINS:
            distribution[domain] = self.get_domain_count(domain)
        return distribution

    def get_tier_distribution(self) -> Dict[int, int]:
        """
        Get distribution of concepts across all tiers.

        Returns:
            Dictionary mapping tier numbers to concept counts
        """
        distribution = {1: 0, 2: 0, 3: 0}
        for concept in self.concepts.values():
            if isinstance(concept, dict) and "tier" in concept:
                tier = concept["tier"]
                if tier in distribution:
                    distribution[tier] += 1
        return distribution

    def validate_hierarchy(self) -> bool:
        """
        Validate the integrity of the concept hierarchy.

        Performs the following validation checks:
        - All concepts have required fields
        - All tier values are valid (1, 2, or 3)
        - All domain values are valid
        - All confidence values are in range [0.0, 1.0]
        - Related concepts exist in the ontology

        Returns:
            True if hierarchy is valid, False otherwise
        """
        for concept_id, concept in self.concepts.items():
            if not isinstance(concept, dict):
                return False

            # Check required fields
            if not self.REQUIRED_CONCEPT_FIELDS.issubset(concept.keys()):
                return False

            # Check tier validity
            if concept.get("tier") not in self.VALID_TIERS:
                return False

            # Check domain validity
            if concept.get("domain") not in self.VALID_DOMAINS:
                return False

            # Check confidence range
            confidence = concept.get("confidence", 0)
            if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
                return False

            # Check related concepts exist
            related = concept.get("related_concepts", [])
            for related_id in related:
                if related_id not in self.concepts:
                    return False

        return True

    def get_related_concepts(self, concept_id: str) -> List[Dict]:
        """
        Get all concepts related to a specific concept.

        Args:
            concept_id: The concept to find relations for

        Returns:
            List of related concept dictionaries
        """
        concept = self.get_concept(concept_id)
        if not concept:
            return []

        related_ids = concept.get("related_concepts", [])
        related_concepts = []
        for related_id in related_ids:
            related = self.get_concept(related_id)
            if related:
                related_concepts.append(related)

        return related_concepts

    def search_concepts(self, query: str, domain: Optional[str] = None) -> List[Dict]:
        """
        Search for concepts by name or definition.

        Args:
            query: Search term to match against concept names and definitions
            domain: Optional domain filter

        Returns:
            List of matching concepts
        """
        query_lower = query.lower()
        results = []

        for concept in self.concepts.values():
            if not isinstance(concept, dict):
                continue

            # Check domain filter
            if domain and concept.get("domain") != domain:
                continue

            # Check name and definition
            name_match = query_lower in concept.get("name", "").lower()
            definition_match = query_lower in concept.get("definition", "").lower()

            if name_match or definition_match:
                results.append(concept)

        return results
