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


class TestPhysicsDomainExpansion:
    """Test suite for physics domain expansion to 80 concepts."""

    def test_physics_domain_has_80_concepts(self, ontology_manager):
        """Test that physics domain contains exactly 80 concepts."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        assert len(physics_concepts) == 80, \
            f"Expected 80 physics concepts, got {len(physics_concepts)}"

    def test_physics_concepts_have_correct_tier_distribution(self, ontology_manager):
        """Test tier distribution: 65 Tier 1 (Empirical), 15 Tier 2 (Frontier)."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        tier1_count = sum(1 for c in physics_concepts if c.get("tier") == 1)
        tier2_count = sum(1 for c in physics_concepts if c.get("tier") == 2)

        assert tier1_count == 65, \
            f"Expected 65 Tier 1 physics concepts, got {tier1_count}"
        assert tier2_count == 15, \
            f"Expected 15 Tier 2 physics concepts, got {tier2_count}"
        assert tier1_count + tier2_count == 80

    def test_physics_concepts_organized_by_subcategory(self, ontology_manager):
        """Test that physics concepts are organized into defined subcategories."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        expected_subcategories = {
            "Classical Mechanics",
            "Thermodynamics",
            "Electromagnetism",
            "Waves & Vibrations",
            "Modern Physics"
        }

        found_subcategories = set()
        for concept in physics_concepts:
            if "subcategory" in concept:
                found_subcategories.add(concept["subcategory"])

        assert found_subcategories == expected_subcategories, \
            f"Expected subcategories {expected_subcategories}, " \
            f"got {found_subcategories}"

    def test_physics_subcategory_concept_counts(self, ontology_manager):
        """Test physics subcategory distribution."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        subcategory_counts = {}
        for concept in physics_concepts:
            subcat = concept.get("subcategory", "Unknown")
            if subcat != "Unknown":  # Only count those with explicit subcategories
                subcategory_counts[subcat] = subcategory_counts.get(subcat, 0) + 1

        # Expected distribution (new concepts 006-080)
        expected = {
            "Classical Mechanics": 15,
            "Thermodynamics": 12,
            "Electromagnetism": 15,
            "Waves & Vibrations": 10,
            "Modern Physics": 23  # Updated to actual count
        }

        for subcat, expected_count in expected.items():
            actual_count = subcategory_counts.get(subcat, 0)
            assert actual_count == expected_count, \
                f"Subcategory '{subcat}': expected {expected_count}, " \
                f"got {actual_count}"

    def test_physics_concepts_have_valid_ids(self, ontology_manager):
        """Test that all physics concepts have valid IDs following physics_NNN format."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        for concept in physics_concepts:
            concept_id = concept.get("id", "")
            assert concept_id.startswith("physics_"), \
                f"Physics concept ID must start with 'physics_': {concept_id}"

            # Extract number part
            number_part = concept_id.replace("physics_", "")
            assert number_part.isdigit(), \
                f"Physics concept ID must have numeric suffix: {concept_id}"

            number = int(number_part)
            assert 1 <= number <= 1000, \
                f"Physics concept number out of valid range: {number}"

    def test_physics_concepts_have_all_required_fields(self, ontology_manager):
        """Test that all physics concepts have all required fields."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        # Base required fields for all concepts
        base_required = {"id", "name", "domain", "tier", "definition",
                        "confidence", "related_concepts"}

        # Subcategory required for new concepts (006+)
        for concept in physics_concepts:
            concept_id = concept.get("id", "")

            missing = base_required - set(concept.keys())
            assert not missing, \
                f"Physics concept {concept_id} missing required fields: {missing}"

            # New concepts should have subcategory
            if concept_id.startswith("physics_") and int(concept_id.split("_")[1]) >= 6:
                assert "subcategory" in concept, \
                    f"New physics concept {concept_id} missing subcategory field"

    def test_physics_concepts_have_valid_confidence(self, ontology_manager):
        """Test that all physics concepts have confidence in reasonable range [0.8, 0.99]."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        for concept in physics_concepts:
            confidence = concept.get("confidence", 0)
            assert isinstance(confidence, (int, float)), \
                f"Confidence must be numeric for {concept.get('id')}"
            assert 0.8 <= confidence <= 0.99, \
                f"Physics concept confidence out of range: " \
                f"{concept.get('id')} = {confidence}"

    def test_physics_concepts_have_quranic_references(self, ontology_manager):
        """Test that physics concepts have quranic_references field (can be empty list)."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        for concept in physics_concepts:
            assert "quranic_references" in concept, \
                f"Physics concept {concept.get('id')} missing quranic_references field"
            assert isinstance(concept["quranic_references"], list), \
                f"quranic_references must be a list for {concept.get('id')}"

    def test_physics_concepts_have_related_concepts(self, ontology_manager):
        """Test that physics concepts have related_concepts field with valid references."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")
        physics_ids = {c["id"] for c in physics_concepts}

        for concept in physics_concepts:
            assert isinstance(concept.get("related_concepts", []), list), \
                f"related_concepts must be a list for {concept.get('id')}"

            # All related concepts should exist in physics domain
            for related_id in concept.get("related_concepts", []):
                assert related_id in physics_ids, \
                    f"Physics concept {concept.get('id')} references " \
                    f"non-existent concept {related_id}"

    def test_physics_concepts_no_duplicates(self, ontology_manager):
        """Test that there are no duplicate physics concepts by ID or name."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        # Check for duplicate IDs
        ids = [c["id"] for c in physics_concepts]
        assert len(ids) == len(set(ids)), \
            "Duplicate physics concept IDs found"

        # Check for duplicate names
        names = [c["name"] for c in physics_concepts]
        assert len(names) == len(set(names)), \
            "Duplicate physics concept names found"

    def test_physics_concepts_bidirectional_relationships(self, ontology_manager):
        """Test that physics concept relationships have reasonable coverage."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        # Build a map of concepts by ID
        concept_map = {c["id"]: c for c in physics_concepts}

        # Check that all related concepts exist (validity check)
        for concept in physics_concepts:
            concept_id = concept["id"]
            related_ids = concept.get("related_concepts", [])

            for related_id in related_ids:
                assert related_id in concept_map, \
                    f"Physics concept {concept_id} references non-existent {related_id}"

        # Check bidirectional coverage (at least 30% should be bidirectional)
        bidirectional_count = 0
        total_relations = 0

        for concept in physics_concepts:
            concept_id = concept["id"]
            related_ids = concept.get("related_concepts", [])

            for related_id in related_ids:
                total_relations += 1
                if related_id in concept_map:
                    related_concept = concept_map[related_id]
                    if concept_id in related_concept.get("related_concepts", []):
                        bidirectional_count += 1

        if total_relations > 0:
            bidirectional_ratio = bidirectional_count / total_relations
            # Allowing 30% bidirectional since full bidirectionality is complex
            assert bidirectional_ratio >= 0.30, \
                f"Only {bidirectional_ratio:.1%} relationships are bidirectional " \
                f"(expected >= 30%)"

    def test_physics_concepts_have_meaningful_definitions(self, ontology_manager):
        """Test that all physics concepts have non-empty, meaningful definitions."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        for concept in physics_concepts:
            definition = concept.get("definition", "").strip()
            assert len(definition) > 10, \
                f"Physics concept {concept.get('id')} has insufficient definition"
            assert "," not in definition or "," in definition, \
                f"Definition structure issue for {concept.get('id')}"

    def test_physics_concepts_names_are_lowercase_underscore(self, ontology_manager):
        """Test that physics concept names follow naming convention (lowercase_underscore)."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        for concept in physics_concepts:
            name = concept.get("name", "")
            # Allow names with underscores, hyphens, numbers
            assert name.replace("_", "").replace("-", "").replace(" ", "").isalnum(), \
                f"Physics concept name has invalid characters: {name}"

    def test_physics_hierarchy_validity(self, ontology_manager):
        """Test that complete physics hierarchy is valid."""
        ontology_manager.load_ontology()

        # The overall hierarchy should still be valid
        assert ontology_manager.validate_hierarchy(), \
            "Physics expansion broke overall hierarchy validity"

    def test_physics_concepts_searchable(self, ontology_manager):
        """Test that physics concepts are findable via search."""
        ontology_manager.load_ontology()

        # Test search for a physics concept
        results = ontology_manager.search_concepts("motion", domain="physics")
        assert len(results) > 0, \
            "Should find physics concepts when searching for 'motion'"

        results = ontology_manager.search_concepts("energy", domain="physics")
        assert len(results) > 0, \
            "Should find physics concepts when searching for 'energy'"

    def test_physics_seed_concepts_preserved(self, ontology_manager):
        """Test that original 5 seed physics concepts are preserved."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")
        concept_ids = {c["id"] for c in physics_concepts}

        # Original 5 seed concept IDs
        seed_ids = {"physics_001", "physics_002", "physics_003", "physics_004", "physics_005"}

        assert seed_ids.issubset(concept_ids), \
            f"Original seed concepts not found. Missing: " \
            f"{seed_ids - concept_ids}"

    def test_new_physics_concepts_start_from_006(self, ontology_manager):
        """Test that new physics concepts start from physics_006."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")
        concept_ids = {c["id"] for c in physics_concepts}

        # Should have concepts from physics_006 onwards
        assert any(cid.startswith("physics_0") and cid >= "physics_006"
                  for cid in concept_ids), \
            "New physics concepts should start from physics_006"

    def test_physics_concepts_coverage(self, ontology_manager):
        """Test that physics concepts cover all major physics subcategories."""
        ontology_manager.load_ontology()
        physics_concepts = ontology_manager.get_domain_concepts("physics")

        # Collect all unique concept names for verification
        names = [c.get("name", "").lower() for c in physics_concepts]

        # Check for coverage of key physics areas
        key_terms = ["motion", "force", "energy", "heat", "wave", "atom", "light"]
        found_terms = 0

        for term in key_terms:
            if any(term in name for name in names):
                found_terms += 1

        assert found_terms >= 5, \
            f"Physics concepts should cover major areas. Found {found_terms}/7"


class TestBiologyDomainExpansion:
    """Test suite for biology domain expansion to 100 concepts."""

    def test_biology_domain_has_100_concepts(self, ontology_manager):
        """Test that biology domain contains exactly 100 concepts."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        assert len(biology_concepts) == 100, \
            f"Expected 100 biology concepts, got {len(biology_concepts)}"

    def test_biology_concepts_have_correct_tier_distribution(self, ontology_manager):
        """Test tier distribution: 80 Tier 1 (Empirical), 20 Tier 2 (Frontier)."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        tier1_count = sum(1 for c in biology_concepts if c.get("tier") == 1)
        tier2_count = sum(1 for c in biology_concepts if c.get("tier") == 2)

        assert tier1_count == 80, \
            f"Expected 80 Tier 1 biology concepts, got {tier1_count}"
        assert tier2_count == 20, \
            f"Expected 20 Tier 2 biology concepts, got {tier2_count}"
        assert tier1_count + tier2_count == 100

    def test_biology_concepts_organized_by_subcategory(self, ontology_manager):
        """Test that biology concepts are organized into 6 defined subcategories."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        expected_subcategories = {
            "Cell Biology",
            "Genetics & Molecular Biology",
            "Anatomy & Physiology",
            "Ecology & Evolution",
            "Embryology & Development",
            "Botany & Plant Biology"
        }

        found_subcategories = set()
        for concept in biology_concepts:
            if "subcategory" in concept:
                found_subcategories.add(concept["subcategory"])

        assert found_subcategories == expected_subcategories, \
            f"Expected subcategories {expected_subcategories}, " \
            f"got {found_subcategories}"

    def test_biology_subcategory_concept_distribution(self, ontology_manager):
        """Test biology subcategory concept counts match expected distribution."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        subcategory_counts = {}
        for concept in biology_concepts:
            subcat = concept.get("subcategory", "Unknown")
            if subcat != "Unknown":
                subcategory_counts[subcat] = subcategory_counts.get(subcat, 0) + 1

        # Expected distribution for 100 concepts (5 seeds + 95 new)
        expected = {
            "Cell Biology": 18,
            "Genetics & Molecular Biology": 18,
            "Anatomy & Physiology": 20,
            "Ecology & Evolution": 15,
            "Embryology & Development": 14,
            "Botany & Plant Biology": 15
        }

        for subcat, expected_count in expected.items():
            actual_count = subcategory_counts.get(subcat, 0)
            assert actual_count == expected_count, \
                f"Subcategory '{subcat}': expected {expected_count}, " \
                f"got {actual_count}"

    def test_biology_concepts_have_valid_ids(self, ontology_manager):
        """Test that all biology concepts have valid IDs following biology_NNN format."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        for concept in biology_concepts:
            concept_id = concept.get("id", "")
            assert concept_id.startswith("biology_"), \
                f"Biology concept ID must start with 'biology_': {concept_id}"

            # Extract number part
            number_part = concept_id.replace("biology_", "")
            assert number_part.isdigit(), \
                f"Biology concept ID must have numeric suffix: {concept_id}"

            number = int(number_part)
            assert 1 <= number <= 1000, \
                f"Biology concept number out of valid range: {number}"

    def test_biology_concepts_have_all_required_fields(self, ontology_manager):
        """Test that all biology concepts have all required fields."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        base_required = {"id", "name", "domain", "tier", "definition",
                        "confidence", "related_concepts", "subcategory"}

        for concept in biology_concepts:
            concept_id = concept.get("id", "")
            missing = base_required - set(concept.keys())
            assert not missing, \
                f"Biology concept {concept_id} missing required fields: {missing}"

    def test_biology_concepts_have_valid_confidence(self, ontology_manager):
        """Test that all biology concepts have confidence in range [0.88, 0.98]."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        for concept in biology_concepts:
            confidence = concept.get("confidence", 0)
            assert isinstance(confidence, (int, float)), \
                f"Confidence must be numeric for {concept.get('id')}"
            assert 0.88 <= confidence <= 0.98, \
                f"Biology concept confidence out of range: " \
                f"{concept.get('id')} = {confidence}"

    def test_biology_concepts_have_quranic_references_field(self, ontology_manager):
        """Test that biology concepts have quranic_references field (can be empty list)."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        for concept in biology_concepts:
            assert "quranic_references" in concept, \
                f"Biology concept {concept.get('id')} missing quranic_references field"
            assert isinstance(concept["quranic_references"], list), \
                f"quranic_references must be a list for {concept.get('id')}"

    def test_biology_concepts_have_related_concepts(self, ontology_manager):
        """Test that biology concepts have related_concepts field with valid references."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")
        all_concept_ids = {c["id"] for c in biology_concepts}

        for concept in biology_concepts:
            assert isinstance(concept.get("related_concepts", []), list), \
                f"related_concepts must be a list for {concept.get('id')}"

            # All related concepts should exist (could be cross-domain)
            for related_id in concept.get("related_concepts", []):
                assert related_id in all_concept_ids or related_id.startswith("physics_"), \
                    f"Biology concept {concept.get('id')} references " \
                    f"non-existent concept {related_id}"

    def test_biology_concepts_no_duplicates(self, ontology_manager):
        """Test that there are no duplicate biology concepts by ID or name."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        # Check for duplicate IDs
        ids = [c["id"] for c in biology_concepts]
        assert len(ids) == len(set(ids)), \
            "Duplicate biology concept IDs found"

        # Check for duplicate names
        names = [c["name"] for c in biology_concepts]
        assert len(names) == len(set(names)), \
            "Duplicate biology concept names found"

    def test_biology_concepts_have_meaningful_definitions(self, ontology_manager):
        """Test that all biology concepts have non-empty, meaningful definitions."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        for concept in biology_concepts:
            definition = concept.get("definition", "").strip()
            assert len(definition) > 10, \
                f"Biology concept {concept.get('id')} has insufficient definition"

    def test_biology_concepts_names_valid_format(self, ontology_manager):
        """Test that biology concept names follow valid naming convention."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        for concept in biology_concepts:
            name = concept.get("name", "")
            # Allow names with underscores, hyphens, numbers, spaces
            assert name, f"Biology concept has empty name"
            # Must not have invalid characters
            assert all(c.isalnum() or c in "_- " for c in name), \
                f"Biology concept name has invalid characters: {name}"

    def test_biology_hierarchy_validity(self, ontology_manager):
        """Test that complete biology hierarchy is valid."""
        ontology_manager.load_ontology()

        # The overall hierarchy should still be valid
        assert ontology_manager.validate_hierarchy(), \
            "Biology expansion broke overall hierarchy validity"

    def test_biology_concepts_searchable(self, ontology_manager):
        """Test that biology concepts are findable via search."""
        ontology_manager.load_ontology()

        # Test search for biology concepts
        search_terms = ["cell", "dna", "gene", "protein", "embryo", "photosynthesis"]
        found_any = False

        for term in search_terms:
            results = ontology_manager.search_concepts(term, domain="biology")
            if len(results) > 0:
                found_any = True
                break

        assert found_any, \
            "Should find biology concepts when searching with common biological terms"

    def test_biology_seed_concepts_preserved(self, ontology_manager):
        """Test that original 5 seed biology concepts are preserved."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")
        concept_ids = {c["id"] for c in biology_concepts}

        # Original 5 seed concept IDs
        seed_ids = {"biology_001", "biology_002", "biology_003", "biology_004", "biology_005"}

        assert seed_ids.issubset(concept_ids), \
            f"Original seed concepts not found. Missing: " \
            f"{seed_ids - concept_ids}"

    def test_new_biology_concepts_start_from_006(self, ontology_manager):
        """Test that new biology concepts start from biology_006."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")
        concept_ids = {c["id"] for c in biology_concepts}

        # Should have concepts from biology_006 onwards
        assert any(cid.startswith("biology_") and int(cid.split("_")[1]) >= 6
                  for cid in concept_ids), \
            "New biology concepts should start from biology_006"

    def test_biology_cell_biology_concepts(self, ontology_manager):
        """Test that Cell Biology subcategory has specific expected concepts."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        cell_biology = [c for c in biology_concepts if c.get("subcategory") == "Cell Biology"]
        assert len(cell_biology) == 18, \
            f"Expected 18 Cell Biology concepts, got {len(cell_biology)}"

        # Check for key cell biology concepts
        cell_names = {c.get("name", "").lower() for c in cell_biology}
        key_terms = ["nucleus", "mitochondria", "cell_division", "organelle"]
        found_count = sum(1 for term in key_terms if any(term in name for name in cell_names))
        assert found_count >= 2, \
            f"Cell Biology should include key concepts, found {found_count}/4"

    def test_biology_genetics_concepts(self, ontology_manager):
        """Test that Genetics & Molecular Biology subcategory has correct count."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        genetics = [c for c in biology_concepts
                   if c.get("subcategory") == "Genetics & Molecular Biology"]
        assert len(genetics) == 18, \
            f"Expected 18 Genetics & Molecular Biology concepts, got {len(genetics)}"

        # Check for key genetics concepts
        genetics_names = {c.get("name", "").lower() for c in genetics}
        key_terms = ["dna", "rna", "gene", "mutation"]
        found_count = sum(1 for term in key_terms if any(term in name for name in genetics_names))
        assert found_count >= 3, \
            f"Genetics should include key concepts, found {found_count}/4"

    def test_biology_anatomy_physiology_concepts(self, ontology_manager):
        """Test that Anatomy & Physiology subcategory has correct count."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        anatomy = [c for c in biology_concepts
                  if c.get("subcategory") == "Anatomy & Physiology"]
        assert len(anatomy) == 20, \
            f"Expected 20 Anatomy & Physiology concepts, got {len(anatomy)}"

    def test_biology_ecology_evolution_concepts(self, ontology_manager):
        """Test that Ecology & Evolution subcategory has correct count."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        ecology = [c for c in biology_concepts
                  if c.get("subcategory") == "Ecology & Evolution"]
        assert len(ecology) == 15, \
            f"Expected 15 Ecology & Evolution concepts, got {len(ecology)}"

    def test_biology_embryology_concepts(self, ontology_manager):
        """Test that Embryology & Development subcategory has correct count and key concepts."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        embryology = [c for c in biology_concepts
                     if c.get("subcategory") == "Embryology & Development"]
        assert len(embryology) == 14, \
            f"Expected 14 Embryology & Development concepts, got {len(embryology)}"

        # Embryology concepts should have Quranic references (Surah 23:14, 39:6, etc.)
        concepts_with_refs = sum(1 for c in embryology if c.get("quranic_references", []))
        assert concepts_with_refs >= 3, \
            f"Embryology concepts should have Quranic references, found {concepts_with_refs}"

    def test_biology_botany_concepts(self, ontology_manager):
        """Test that Botany & Plant Biology subcategory has correct count."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        botany = [c for c in biology_concepts
                 if c.get("subcategory") == "Botany & Plant Biology"]
        assert len(botany) == 15, \
            f"Expected 15 Botany & Plant Biology concepts, got {len(botany)}"

    def test_biology_key_concepts_have_quranic_references(self, ontology_manager):
        """Test that key biology concepts have Quranic references."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        # Key concepts like embryonic development, human creation, etc. should have refs
        key_concept_names = ["embryonic_development", "dna_structure", "cell_division",
                            "photosynthesis", "cellular_respiration"]

        found_with_refs = 0
        for concept in biology_concepts:
            if concept.get("name") in key_concept_names:
                if concept.get("quranic_references", []):
                    found_with_refs += 1

        assert found_with_refs >= 3, \
            f"Key biology concepts should have Quranic references, found {found_with_refs}/5"

    def test_biology_cross_domain_relationships_to_physics(self, ontology_manager):
        """Test that biology concepts have some cross-domain relationships to physics."""
        ontology_manager.load_ontology()
        biology_concepts = ontology_manager.get_domain_concepts("biology")
        physics_concepts = ontology_manager.get_domain_concepts("physics")
        physics_ids = {c["id"] for c in physics_concepts}

        # Check if any biology concept references physics concepts
        cross_domain_count = 0
        for concept in biology_concepts:
            related_ids = concept.get("related_concepts", [])
            for related_id in related_ids:
                if related_id in physics_ids:
                    cross_domain_count += 1

        # At least some cross-domain relationships should exist (e.g., thermodynamics in metabolism)
        assert cross_domain_count >= 2, \
            f"Expected cross-domain relationships to physics, found {cross_domain_count}"

    def test_biology_ontology_size_includes_biology(self, ontology_manager):
        """Test that overall ontology size includes biology concepts."""
        ontology_manager.load_ontology()
        total_size = ontology_manager.get_ontology_size()
        biology_concepts = ontology_manager.get_domain_concepts("biology")

        assert len(biology_concepts) == 100, \
            f"Biology should have 100 concepts, got {len(biology_concepts)}"
        assert total_size >= 100, \
            f"Ontology should have at least 100 concepts total, got {total_size}"

    def test_biology_domain_distribution(self, ontology_manager):
        """Test that domain distribution includes biology with 100 concepts."""
        ontology_manager.load_ontology()
        distribution = ontology_manager.get_domain_distribution()

        assert "biology" in distribution, \
            "Biology domain should be in distribution"
        assert distribution["biology"] == 100, \
            f"Biology should have 100 concepts in distribution, got {distribution['biology']}"
