import pytest
import json
import os
from pathlib import Path
from quran.corpus_extraction.ontology.ontology_manager import OntologyManager


@pytest.fixture
def ontology_manager():
    """Create an OntologyManager instance for testing."""
    return OntologyManager()


@pytest.fixture
def sample_concept():
    """Create a sample concept for testing."""
    return {
        "id": "physics_test_001",
        "name": "test_gravitation",
        "domain": "physics",
        "tier": 1,
        "definition": "The force of attraction between masses",
        "related_concepts": [],
        "confidence": 0.95
    }


class TestOntologyManagerInitialization:
    """Test OntologyManager initialization and loading."""

    def test_ontology_manager_initializes(self, ontology_manager):
        """Test that OntologyManager can be instantiated."""
        assert ontology_manager is not None

    def test_load_ontology_returns_concepts(self, ontology_manager):
        """Test that load_ontology returns a dictionary of concepts."""
        concepts = ontology_manager.load_ontology()
        assert isinstance(concepts, dict)
        assert len(concepts) > 0

    def test_ontology_contains_expected_domains(self, ontology_manager):
        """Test that loaded ontology contains expected domains."""
        concepts = ontology_manager.load_ontology()
        domains = set()
        for concept in concepts.values():
            if isinstance(concept, dict) and "domain" in concept:
                domains.add(concept["domain"])

        expected_domains = {"physics", "biology", "medicine", "engineering", "agriculture"}
        assert len(domains & expected_domains) >= 3  # At least 3 domains present


class TestOntologyManagerMethods:
    """Test core OntologyManager methods."""

    def test_get_concept_returns_concept(self, ontology_manager):
        """Test that get_concept retrieves a concept by ID."""
        concepts = ontology_manager.load_ontology()
        if concepts:
            first_concept_id = list(concepts.keys())[0]
            concept = ontology_manager.get_concept(first_concept_id)
            assert concept is not None
            assert "id" in concept

    def test_get_concept_returns_none_for_invalid_id(self, ontology_manager):
        """Test that get_concept returns None for non-existent concept."""
        ontology_manager.load_ontology()
        concept = ontology_manager.get_concept("nonexistent_id")
        assert concept is None

    def test_add_concept_adds_new_concept(self, ontology_manager, sample_concept):
        """Test that add_concept adds a new concept to the ontology."""
        ontology_manager.load_ontology()
        initial_count = len(ontology_manager.concepts)

        ontology_manager.add_concept(sample_concept)

        assert len(ontology_manager.concepts) == initial_count + 1
        assert ontology_manager.get_concept("physics_test_001") == sample_concept

    def test_add_concept_validates_structure(self, ontology_manager):
        """Test that add_concept validates concept structure."""
        ontology_manager.load_ontology()
        invalid_concept = {"name": "incomplete"}  # Missing required fields

        with pytest.raises(ValueError):
            ontology_manager.add_concept(invalid_concept)

    def test_get_domain_concepts_returns_filtered_concepts(self, ontology_manager):
        """Test that get_domain_concepts returns concepts from specified domain."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        assert isinstance(physics_concepts, list)
        if physics_concepts:
            for concept in physics_concepts:
                assert concept["domain"] == "physics"

    def test_get_domain_concepts_returns_empty_for_invalid_domain(self, ontology_manager):
        """Test that get_domain_concepts returns empty list for non-existent domain."""
        ontology_manager.load_ontology()
        concepts = ontology_manager.get_domain_concepts("nonexistent_domain")

        assert isinstance(concepts, list)
        assert len(concepts) == 0


class TestOntologyManagerHierarchy:
    """Test hierarchy validation and organization."""

    def test_validate_hierarchy_returns_boolean(self, ontology_manager):
        """Test that validate_hierarchy returns a boolean."""
        ontology_manager.load_ontology()
        result = ontology_manager.validate_hierarchy()
        assert isinstance(result, bool)

    def test_hierarchy_validates_tier_constraints(self, ontology_manager):
        """Test that hierarchy validation checks tier constraints."""
        ontology_manager.load_ontology()
        valid = ontology_manager.validate_hierarchy()

        # All concepts should have tier 1, 2, or 3
        for concept in ontology_manager.concepts.values():
            if isinstance(concept, dict) and "tier" in concept:
                assert concept["tier"] in [1, 2, 3]

    def test_get_concepts_by_tier_returns_filtered_list(self, ontology_manager):
        """Test that get_concepts_by_tier returns concepts with specified tier."""
        ontology_manager.load_ontology()
        tier1_concepts = ontology_manager.get_concepts_by_tier(1)

        assert isinstance(tier1_concepts, list)
        for concept in tier1_concepts:
            assert concept["tier"] == 1

    def test_get_domain_count_returns_integer(self, ontology_manager):
        """Test that get_domain_count returns count of concepts in domain."""
        ontology_manager.load_ontology()
        physics_count = ontology_manager.get_domain_count("physics")

        assert isinstance(physics_count, int)
        assert physics_count >= 0


class TestOntologyManagerStatistics:
    """Test ontology statistics and metadata."""

    def test_get_ontology_size_returns_integer(self, ontology_manager):
        """Test that get_ontology_size returns total concept count."""
        ontology_manager.load_ontology()
        size = ontology_manager.get_ontology_size()

        assert isinstance(size, int)
        assert size > 0

    def test_get_domain_distribution_returns_dict(self, ontology_manager):
        """Test that get_domain_distribution returns domain statistics."""
        ontology_manager.load_ontology()
        distribution = ontology_manager.get_domain_distribution()

        assert isinstance(distribution, dict)
        total = sum(distribution.values())
        assert total == ontology_manager.get_ontology_size()

    def test_get_tier_distribution_returns_dict(self, ontology_manager):
        """Test that get_tier_distribution returns tier statistics."""
        ontology_manager.load_ontology()
        distribution = ontology_manager.get_tier_distribution()

        assert isinstance(distribution, dict)
        assert all(key in [1, 2, 3] for key in distribution.keys())


class TestOntologyDataIntegrity:
    """Test data integrity and consistency."""

    def test_concepts_have_required_fields(self, ontology_manager):
        """Test that all concepts have required fields."""
        ontology_manager.load_ontology()
        required_fields = {"id", "name", "domain", "tier", "definition", "confidence"}

        for concept in ontology_manager.concepts.values():
            if isinstance(concept, dict):
                assert required_fields.issubset(concept.keys())

    def test_concept_confidence_in_valid_range(self, ontology_manager):
        """Test that all concept confidence values are between 0 and 1."""
        ontology_manager.load_ontology()

        for concept in ontology_manager.concepts.values():
            if isinstance(concept, dict) and "confidence" in concept:
                assert 0 <= concept["confidence"] <= 1

    def test_concept_domains_are_valid(self, ontology_manager):
        """Test that all concepts have valid domain values."""
        ontology_manager.load_ontology()
        valid_domains = {"physics", "biology", "medicine", "engineering", "agriculture"}

        for concept in ontology_manager.concepts.values():
            if isinstance(concept, dict) and "domain" in concept:
                assert concept["domain"] in valid_domains
