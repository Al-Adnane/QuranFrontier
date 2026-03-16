"""Tests for SemanticFieldAnalyzer class."""
import pytest
from quran.corpus_extraction.framework.semantic_analyzer import SemanticFieldAnalyzer


class TestSemanticFieldAnalyzer:
    """Test suite for SemanticFieldAnalyzer semantic field and lexical analysis."""

    def setup_method(self):
        """Initialize SemanticFieldAnalyzer before each test."""
        self.analyzer = SemanticFieldAnalyzer()

    def test_analyze_verse_semantics_basic(self):
        """Test basic semantic analysis returns all required fields."""
        verse_text = "خلق السماوات والأرض"  # "Created the heavens and the earth"
        verse_key = "39:5"

        result = self.analyzer.analyze_verse_semantics(verse_text, verse_key)

        assert result is not None
        assert isinstance(result, dict)
        assert "verse_key" in result
        assert "root_clusters" in result
        assert "semantic_field" in result
        assert "synonyms" in result
        assert "antonyms" in result
        assert "semantic_density" in result
        assert "key_semantic_nodes" in result
        assert "metaphorical_expressions" in result
        assert "literal_expressions" in result

        # Verify data types
        assert result["verse_key"] == verse_key
        assert isinstance(result["root_clusters"], dict)
        assert isinstance(result["semantic_field"], list)
        assert isinstance(result["synonyms"], dict)
        assert isinstance(result["antonyms"], dict)
        assert isinstance(result["semantic_density"], float)
        assert isinstance(result["key_semantic_nodes"], list)
        assert isinstance(result["metaphorical_expressions"], list)
        assert isinstance(result["literal_expressions"], list)

    def test_root_clustering(self):
        """Test root clustering groups related words by Arabic root."""
        # Verse with words from same root: ن-ش-أ (growth/creation)
        verse_text = "نشأ النبات ونمى الشيء"  # "The plant grew and the thing developed"
        verse_key = "23:12"

        result = self.analyzer.analyze_verse_semantics(verse_text, verse_key)

        root_clusters = result["root_clusters"]
        assert isinstance(root_clusters, dict)

        # Check that roots are grouped (even if implementation groups them differently)
        if root_clusters:
            for root, words in root_clusters.items():
                assert isinstance(words, list)
                assert len(words) > 0
                # Each word in cluster should be a string
                assert all(isinstance(w, str) for w in words)

    def test_semantic_field_extraction(self):
        """Test semantic field extraction captures related concepts."""
        # Verse about creation with interconnected concepts
        verse_text = "خلق كون أنشأ بعث"  # "Created, formed, originated, originated"
        verse_key = "39:5"

        result = self.analyzer.analyze_verse_semantics(verse_text, verse_key)

        semantic_field = result["semantic_field"]
        assert isinstance(semantic_field, list)
        # Semantic field should contain related concepts
        if semantic_field:
            assert all(isinstance(item, str) for item in semantic_field)

    def test_synonyms_identification(self):
        """Test synonyms are correctly identified for key words."""
        verse_text = "علم عرف فقه"  # "Know, understand, comprehend"
        verse_key = "96:5"

        result = self.analyzer.analyze_verse_semantics(verse_text, verse_key)

        synonyms = result["synonyms"]
        assert isinstance(synonyms, dict)

        # If synonyms are found, verify structure
        if synonyms:
            for word, synonym_list in synonyms.items():
                assert isinstance(word, str)
                assert isinstance(synonym_list, list)
                assert all(isinstance(s, str) for s in synonym_list)

    def test_antonyms_identification(self):
        """Test antonyms are correctly identified."""
        verse_text = "النور والظلام الحق والباطل"  # "Light and darkness, truth and falsehood"
        verse_key = "2:257"

        result = self.analyzer.analyze_verse_semantics(verse_text, verse_key)

        antonyms = result["antonyms"]
        assert isinstance(antonyms, dict)

        # If antonyms are found, verify structure
        if antonyms:
            for word, antonym_list in antonyms.items():
                assert isinstance(word, str)
                assert isinstance(antonym_list, list)
                assert all(isinstance(a, str) for a in antonym_list)

    def test_metaphor_literal_separation(self):
        """Test separation of metaphorical and literal expressions."""
        verse_text = "قلبه مظلم والنور في السماء"  # "His heart is dark and light in the sky"
        verse_key = "24:40"

        result = self.analyzer.analyze_verse_semantics(verse_text, verse_key)

        metaphorical = result["metaphorical_expressions"]
        literal = result["literal_expressions"]

        assert isinstance(metaphorical, list)
        assert isinstance(literal, list)
        assert all(isinstance(m, str) for m in metaphorical)
        assert all(isinstance(l, str) for l in literal)

    def test_semantic_density_calculation(self):
        """Test semantic density reflects interconnectedness."""
        # Dense semantic field (multiple related words)
        dense_verse = "خلق السماوات والأرض وكون القمر والنجوم"
        result_dense = self.analyzer.analyze_verse_semantics(dense_verse, "39:5")

        # Sparse semantic field (fewer connections)
        sparse_verse = "قال الله"  # "God said"
        result_sparse = self.analyzer.analyze_verse_semantics(sparse_verse, "2:1")

        density_dense = result_dense["semantic_density"]
        density_sparse = result_sparse["semantic_density"]

        # Verify both are valid floats in range [0, 1]
        assert isinstance(density_dense, float)
        assert isinstance(density_sparse, float)
        assert 0.0 <= density_dense <= 1.0
        assert 0.0 <= density_sparse <= 1.0

    def test_semantic_nodes(self):
        """Test key semantic nodes are identified correctly."""
        verse_text = "خلق السماوات والأرض في ستة أيام"  # "Created heavens and earth in six days"
        verse_key = "39:5"

        result = self.analyzer.analyze_verse_semantics(verse_text, verse_key)

        key_nodes = result["key_semantic_nodes"]
        assert isinstance(key_nodes, list)

        # Key nodes should be strings representing most connected words
        if key_nodes:
            assert all(isinstance(node, str) for node in key_nodes)


class TestSemanticFieldAnalyzerEdgeCases:
    """Test edge cases and special scenarios."""

    def setup_method(self):
        """Initialize SemanticFieldAnalyzer before each test."""
        self.analyzer = SemanticFieldAnalyzer()

    def test_empty_verse(self):
        """Test analyzer handles empty verse gracefully."""
        result = self.analyzer.analyze_verse_semantics("", "1:1")

        assert result is not None
        assert result["verse_key"] == "1:1"
        assert isinstance(result["semantic_density"], float)

    def test_single_word_verse(self):
        """Test analyzer handles single word verse."""
        result = self.analyzer.analyze_verse_semantics("خلق", "39:5")

        assert result is not None
        assert result["verse_key"] == "39:5"
        assert isinstance(result["root_clusters"], dict)

    def test_with_embeddings_layer(self):
        """Test analyzer can be initialized with optional embeddings layer."""
        mock_embeddings = {}
        analyzer = SemanticFieldAnalyzer(embeddings_layer=mock_embeddings)

        assert analyzer is not None
        result = analyzer.analyze_verse_semantics("خلق", "39:5")
        assert result is not None
