#!/usr/bin/env python3
"""
Test Suite: Verse-to-Concept Mapping (Task 8)
Tests for mapping all 6,236 Quranic verses to 400 scientific concepts with confidence scoring
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Set
import statistics


class TestVerseConceptMapperBasics:
    """Basic functionality tests for verse-concept mapper"""

    @pytest.fixture(scope="module")
    def complete_corpus(self):
        """Load complete corpus with all 6,236 verses"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/output/complete_corpus.json")
        assert corpus_path.exists(), f"Complete corpus not found at {corpus_path}"

        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def scientific_concepts(self):
        """Load scientific concepts ontology"""
        concepts_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/ontology/scientific_concepts.json")
        assert concepts_path.exists(), f"Scientific concepts not found at {concepts_path}"

        with open(concepts_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def verse_concept_mapper(self, complete_corpus, scientific_concepts):
        """Import and instantiate the VerseConcept Mapper"""
        # This will fail initially until the module is created
        from verse_concept_mapper import VerseConceptMapper
        return VerseConceptMapper(complete_corpus, scientific_concepts)

    def test_corpus_loaded_with_6236_verses(self, complete_corpus):
        """TEST: Verify complete corpus contains all 6,236 verses"""
        verses = complete_corpus.get('verses', [])
        assert len(verses) == 6236, f"Expected 6,236 verses, found {len(verses)}"

    def test_corpus_verse_structure(self, complete_corpus):
        """TEST: Verify verse structure with required fields"""
        verses = complete_corpus.get('verses', [])
        assert len(verses) > 0, "No verses in corpus"

        required_fields = ['surah', 'ayah', 'verse_key', 'arabic_text', 'translation']
        for verse in verses[:50]:  # Check first 50
            for field in required_fields:
                assert field in verse, f"Missing '{field}' in verse {verse.get('verse_key')}"
                assert verse[field] is not None, f"'{field}' is None in verse {verse.get('verse_key')}"

    def test_scientific_concepts_loaded_with_400_concepts(self, scientific_concepts):
        """TEST: Verify scientific concepts contain all 400 concepts"""
        concepts = scientific_concepts.get('concepts', [])
        assert len(concepts) == 400, f"Expected 400 concepts, found {len(concepts)}"

    def test_scientific_concepts_structure(self, scientific_concepts):
        """TEST: Verify concept structure with required fields"""
        concepts = scientific_concepts.get('concepts', [])
        assert len(concepts) > 0, "No concepts in ontology"

        required_fields = ['id', 'name', 'domain', 'tier', 'definition']
        for concept in concepts[:50]:  # Check first 50
            for field in required_fields:
                assert field in concept, f"Missing '{field}' in concept {concept.get('id')}"
                assert concept[field] is not None, f"'{field}' is None in concept {concept.get('id')}"

    def test_concepts_by_domain(self, scientific_concepts):
        """TEST: Verify concepts distributed across 5 domains"""
        concepts = scientific_concepts.get('concepts', [])
        expected_domains = {'physics', 'biology', 'medicine', 'engineering', 'agriculture'}

        actual_domains = set(c.get('domain') for c in concepts if 'domain' in c)
        assert actual_domains == expected_domains, f"Expected domains {expected_domains}, got {actual_domains}"

    def test_concept_ids_unique(self, scientific_concepts):
        """TEST: Verify all concept IDs are unique"""
        concepts = scientific_concepts.get('concepts', [])
        concept_ids = [c.get('id') for c in concepts]

        assert len(concept_ids) == len(set(concept_ids)), "Duplicate concept IDs found"

    def test_verse_concept_mapper_instantiation(self, verse_concept_mapper):
        """TEST: Verify VerseConcept Mapper can be instantiated"""
        assert verse_concept_mapper is not None
        assert hasattr(verse_concept_mapper, 'verse_count')
        assert hasattr(verse_concept_mapper, 'concept_count')

    def test_verse_concept_mapper_verse_count(self, verse_concept_mapper):
        """TEST: Verify mapper has correct verse count (6,236)"""
        assert verse_concept_mapper.verse_count == 6236, \
            f"Expected 6,236 verses in mapper, got {verse_concept_mapper.verse_count}"

    def test_verse_concept_mapper_concept_count(self, verse_concept_mapper):
        """TEST: Verify mapper has correct concept count (400)"""
        assert verse_concept_mapper.concept_count == 400, \
            f"Expected 400 concepts in mapper, got {verse_concept_mapper.concept_count}"


class TestVerseConceptMappingLogic:
    """Tests for verse-concept matching and confidence scoring"""

    @pytest.fixture(scope="module")
    def complete_corpus(self):
        """Load complete corpus"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/output/complete_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def scientific_concepts(self):
        """Load scientific concepts"""
        concepts_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/ontology/scientific_concepts.json")
        with open(concepts_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def verse_concept_mapper(self, complete_corpus, scientific_concepts):
        """Instantiate mapper"""
        from verse_concept_mapper import VerseConceptMapper
        return VerseConceptMapper(complete_corpus, scientific_concepts)

    def test_map_single_verse_to_concepts(self, verse_concept_mapper):
        """TEST: Map a single verse (e.g., 1:1) to relevant concepts"""
        result = verse_concept_mapper.map_verse("1:1")

        assert result is not None, "Failed to map verse 1:1"
        assert 'verse_id' in result
        assert 'verse_text' in result
        assert 'concepts' in result
        assert isinstance(result['concepts'], list)

    def test_concept_confidence_scoring(self, verse_concept_mapper):
        """TEST: Verify confidence scores are in valid range [0.6, 1.0]"""
        result = verse_concept_mapper.map_verse("2:164")

        if result['concepts']:  # If verse has mapped concepts
            for concept_mapping in result['concepts']:
                confidence = concept_mapping.get('mapping_confidence')
                assert confidence is not None, "Missing confidence score"
                assert 0.6 <= confidence <= 1.0, \
                    f"Confidence {confidence} out of range [0.6, 1.0]"

    def test_concept_mapping_structure(self, verse_concept_mapper):
        """TEST: Verify concept mapping has all required fields"""
        result = verse_concept_mapper.map_verse("2:164")

        required_concept_fields = ['concept_id', 'concept_name', 'domain', 'tier', 'mapping_confidence']

        if result['concepts']:  # If verse has mappings
            for concept in result['concepts']:
                for field in required_concept_fields:
                    assert field in concept, f"Missing '{field}' in concept mapping"
                    assert concept[field] is not None, f"'{field}' is None in concept mapping"

    def test_confidence_threshold_filtering(self, verse_concept_mapper):
        """TEST: Verify only concepts with confidence >= 0.6 are included"""
        # Map all verses and check all concepts meet threshold
        for verse_key in ["1:1", "2:1", "5:1"]:  # Sample verses
            result = verse_concept_mapper.map_verse(verse_key)

            if result['concepts']:
                for concept in result['concepts']:
                    confidence = concept.get('mapping_confidence')
                    assert confidence >= 0.6, \
                        f"Concept with confidence {confidence} below threshold in {verse_key}"

    def test_concept_references_are_valid(self, verse_concept_mapper, scientific_concepts):
        """TEST: Verify all concept references point to valid concepts"""
        valid_concept_ids = {c['id'] for c in scientific_concepts['concepts']}

        # Sample some verses
        sample_verses = ["1:1", "2:164", "21:30", "51:47", "80:31"]

        for verse_key in sample_verses:
            result = verse_concept_mapper.map_verse(verse_key)

            if result['concepts']:
                for concept in result['concepts']:
                    concept_id = concept.get('concept_id')
                    assert concept_id in valid_concept_ids, \
                        f"Invalid concept_id '{concept_id}' in verse {verse_key}"

    def test_domain_coverage_in_mappings(self, verse_concept_mapper):
        """TEST: Verify mappings include concepts from multiple domains"""
        # Map several verses and check domain diversity
        domains_found = set()

        sample_verses = ["2:164", "21:30", "36:33", "80:31"]
        for verse_key in sample_verses:
            result = verse_concept_mapper.map_verse(verse_key)
            for concept in result.get('concepts', []):
                domains_found.add(concept.get('domain'))

        # Should find at least 2-3 different domains across these verses
        assert len(domains_found) >= 2, \
            f"Expected multiple domains, found {domains_found}"


class TestVerseConceptMappingCompletion:
    """Tests for complete verse-concept mapping across all verses"""

    @pytest.fixture(scope="module")
    def complete_corpus(self):
        """Load complete corpus"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/output/complete_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def scientific_concepts(self):
        """Load scientific concepts"""
        concepts_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/ontology/scientific_concepts.json")
        with open(concepts_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def verse_concept_mapper(self, complete_corpus, scientific_concepts):
        """Instantiate mapper"""
        from verse_concept_mapper import VerseConceptMapper
        return VerseConceptMapper(complete_corpus, scientific_concepts)

    @pytest.fixture(scope="module")
    def complete_mappings(self, verse_concept_mapper):
        """Generate complete mappings for all 6,236 verses"""
        return verse_concept_mapper.map_all_verses()

    def test_all_verses_mapped(self, complete_mappings):
        """TEST: All 6,236 verses are in the mapping results"""
        assert len(complete_mappings) == 6236, \
            f"Expected 6,236 mappings, got {len(complete_mappings)}"

    def test_no_duplicate_verses_in_mappings(self, complete_mappings):
        """TEST: No duplicate verses in the mappings"""
        verse_ids = [m['verse_id'] for m in complete_mappings]
        assert len(verse_ids) == len(set(verse_ids)), "Duplicate verses found in mappings"

    def test_all_verses_have_required_structure(self, complete_mappings):
        """TEST: All mapped verses have required fields"""
        required_fields = ['verse_id', 'verse_text_ar', 'concepts']

        for mapping in complete_mappings[:100]:  # Check first 100
            for field in required_fields:
                assert field in mapping, f"Missing '{field}' in mapping {mapping.get('verse_id')}"

    def test_no_orphaned_verses(self, complete_mappings):
        """TEST: No verse in corpus is missing from mappings"""
        mapped_verse_ids = {m['verse_id'] for m in complete_mappings}
        assert len(mapped_verse_ids) == 6236, \
            f"Found orphaned verses. Mapped: {len(mapped_verse_ids)}, Expected: 6236"

    def test_concept_references_in_complete_mappings_are_valid(self, complete_mappings, scientific_concepts):
        """TEST: All concept references in complete mappings are valid"""
        valid_concept_ids = {c['id'] for c in scientific_concepts['concepts']}

        invalid_refs = []
        for mapping in complete_mappings:
            for concept in mapping.get('concepts', []):
                concept_id = concept.get('concept_id')
                if concept_id not in valid_concept_ids:
                    invalid_refs.append((mapping['verse_id'], concept_id))

        assert len(invalid_refs) == 0, \
            f"Found {len(invalid_refs)} invalid concept references: {invalid_refs[:5]}"

    def test_confidence_scores_in_valid_range(self, complete_mappings):
        """TEST: All confidence scores are in range [0.6, 1.0]"""
        invalid_scores = []

        for mapping in complete_mappings:
            for concept in mapping.get('concepts', []):
                score = concept.get('mapping_confidence')
                if not (0.6 <= score <= 1.0):
                    invalid_scores.append((mapping['verse_id'], concept['concept_id'], score))

        assert len(invalid_scores) == 0, \
            f"Found {len(invalid_scores)} invalid confidence scores: {invalid_scores[:5]}"

    def test_output_format_valid_json(self, verse_concept_mapper):
        """TEST: Output can be serialized to valid JSON"""
        mappings = verse_concept_mapper.map_all_verses()
        output = {
            'metadata': {
                'version': '1.0',
                'created': verse_concept_mapper.creation_timestamp,
                'total_verses': 6236,
                'total_concepts': 400,
                'threshold_confidence': 0.6
            },
            'verse_concept_mappings': mappings
        }

        # Should not raise exception
        json_str = json.dumps(output)
        assert len(json_str) > 0

        # Should be able to reload
        reloaded = json.loads(json_str)
        assert len(reloaded['verse_concept_mappings']) == 6236


class TestVerseConceptMappingStatistics:
    """Tests for statistical analysis of verse-concept mappings"""

    @pytest.fixture(scope="module")
    def complete_corpus(self):
        """Load complete corpus"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/output/complete_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def scientific_concepts(self):
        """Load scientific concepts"""
        concepts_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/ontology/scientific_concepts.json")
        with open(concepts_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def verse_concept_mapper(self, complete_corpus, scientific_concepts):
        """Instantiate mapper"""
        from verse_concept_mapper import VerseConceptMapper
        return VerseConceptMapper(complete_corpus, scientific_concepts)

    @pytest.fixture(scope="module")
    def complete_mappings(self, verse_concept_mapper):
        """Generate complete mappings"""
        return verse_concept_mapper.map_all_verses()

    def test_coverage_percentage(self, complete_mappings):
        """TEST: At least 25% of verses have at least 1 concept"""
        verses_with_concepts = sum(1 for m in complete_mappings if len(m.get('concepts', [])) > 0)
        coverage_pct = (verses_with_concepts / len(complete_mappings)) * 100

        assert coverage_pct >= 25, \
            f"Coverage {coverage_pct:.1f}% below target of 25%"

    def test_average_concepts_per_mapped_verse(self, complete_mappings):
        """TEST: Average 2-4 concepts per mapped verse"""
        concept_counts = [len(m.get('concepts', [])) for m in complete_mappings if len(m.get('concepts', [])) > 0]

        if concept_counts:
            avg_concepts = statistics.mean(concept_counts)
            assert 2 <= avg_concepts <= 4, \
                f"Average concepts per verse {avg_concepts:.2f} outside target 2-4"

    def test_domain_coverage_physics(self, complete_mappings):
        """TEST: Physics domain covers 15-20% of verses"""
        verses_with_physics = sum(
            1 for m in complete_mappings
            if any(c.get('domain') == 'physics' for c in m.get('concepts', []))
        )
        coverage_pct = (verses_with_physics / len(complete_mappings)) * 100

        assert 15 <= coverage_pct <= 20, \
            f"Physics coverage {coverage_pct:.1f}% outside target 15-20%"

    def test_domain_coverage_biology(self, complete_mappings):
        """TEST: Biology domain covers 10-15% of verses"""
        verses_with_biology = sum(
            1 for m in complete_mappings
            if any(c.get('domain') == 'biology' for c in m.get('concepts', []))
        )
        coverage_pct = (verses_with_biology / len(complete_mappings)) * 100

        assert 10 <= coverage_pct <= 15, \
            f"Biology coverage {coverage_pct:.1f}% outside target 10-15%"

    def test_domain_coverage_medicine(self, complete_mappings):
        """TEST: Medicine domain covers 8-12% of verses"""
        verses_with_medicine = sum(
            1 for m in complete_mappings
            if any(c.get('domain') == 'medicine' for c in m.get('concepts', []))
        )
        coverage_pct = (verses_with_medicine / len(complete_mappings)) * 100

        assert 8 <= coverage_pct <= 12, \
            f"Medicine coverage {coverage_pct:.1f}% outside target 8-12%"

    def test_domain_coverage_engineering(self, complete_mappings):
        """TEST: Engineering domain covers 3-5% of verses"""
        verses_with_engineering = sum(
            1 for m in complete_mappings
            if any(c.get('domain') == 'engineering' for c in m.get('concepts', []))
        )
        coverage_pct = (verses_with_engineering / len(complete_mappings)) * 100

        assert 3 <= coverage_pct <= 5, \
            f"Engineering coverage {coverage_pct:.1f}% outside target 3-5%"

    def test_domain_coverage_agriculture(self, complete_mappings):
        """TEST: Agriculture domain covers 5-8% of verses"""
        verses_with_agriculture = sum(
            1 for m in complete_mappings
            if any(c.get('domain') == 'agriculture' for c in m.get('concepts', []))
        )
        coverage_pct = (verses_with_agriculture / len(complete_mappings)) * 100

        assert 5 <= coverage_pct <= 8, \
            f"Agriculture coverage {coverage_pct:.1f}% outside target 5-8%"

    def test_statistics_report_generation(self, verse_concept_mapper):
        """TEST: Mapper can generate statistics report"""
        stats = verse_concept_mapper.get_statistics()

        assert stats is not None
        assert 'total_verses_mapped' in stats
        assert 'verses_with_concepts' in stats
        assert 'coverage_percentage' in stats
        assert 'average_concepts_per_verse' in stats
        assert 'domain_distribution' in stats
        assert all(domain in stats['domain_distribution']
                   for domain in ['physics', 'biology', 'medicine', 'engineering', 'agriculture'])

    def test_concept_usage_distribution(self, verse_concept_mapper):
        """TEST: Different concepts have varying usage frequencies"""
        distribution = verse_concept_mapper.get_concept_usage_distribution()

        assert distribution is not None
        assert isinstance(distribution, dict)
        # Should have usage data for multiple concepts
        assert len(distribution) > 0


class TestVerseConceptOutputFile:
    """Tests for verse-to-concepts.json output file"""

    @pytest.fixture(scope="module")
    def complete_corpus(self):
        """Load complete corpus"""
        corpus_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/output/complete_corpus.json")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def scientific_concepts(self):
        """Load scientific concepts"""
        concepts_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/ontology/scientific_concepts.json")
        with open(concepts_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture(scope="module")
    def verse_concept_mapper(self, complete_corpus, scientific_concepts):
        """Instantiate mapper"""
        from verse_concept_mapper import VerseConceptMapper
        return VerseConceptMapper(complete_corpus, scientific_concepts)

    @pytest.fixture(scope="module")
    def output_file(self, verse_concept_mapper):
        """Generate and save output file"""
        output_path = Path("/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday/quran/corpus_extraction/ontology/verse_to_concepts.json")
        verse_concept_mapper.save_mappings(output_path)
        return output_path

    def test_output_file_created(self, output_file):
        """TEST: verse_to_concepts.json file is created"""
        assert output_file.exists(), f"Output file not created at {output_file}"

    def test_output_file_is_valid_json(self, output_file):
        """TEST: Output file contains valid JSON"""
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data is not None
        assert isinstance(data, dict)

    def test_output_file_has_metadata(self, output_file):
        """TEST: Output file has metadata section"""
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'metadata' in data
        metadata = data['metadata']

        required_metadata = ['version', 'created', 'total_verses', 'total_concepts', 'threshold_confidence']
        for field in required_metadata:
            assert field in metadata, f"Missing '{field}' in metadata"

    def test_output_file_has_verse_mappings(self, output_file):
        """TEST: Output file has verse_concept_mappings section"""
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'verse_concept_mappings' in data
        assert isinstance(data['verse_concept_mappings'], list)
        assert len(data['verse_concept_mappings']) == 6236

    def test_output_file_size_reasonable(self, output_file):
        """TEST: Output file size is reasonable (should be 5-15 MB)"""
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        assert 5 <= file_size_mb <= 15, \
            f"Output file size {file_size_mb:.1f} MB seems unreasonable"

    def test_output_can_be_reloaded(self, output_file):
        """TEST: Output file can be reloaded and parsed"""
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data['verse_concept_mappings']) == 6236

        # Spot check some verses
        verse_ids = {m['verse_id'] for m in data['verse_concept_mappings']}
        expected_verses = {'1:1', '2:164', '21:33', '51:47', '114:6'}
        assert expected_verses.issubset(verse_ids), \
            f"Missing expected verses in output"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
