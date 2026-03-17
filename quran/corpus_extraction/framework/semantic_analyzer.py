"""Semantic field analyzer for Arabic lexical relationships in Quranic verses."""
from typing import Dict, List, Tuple, Optional
import re


class SemanticFieldAnalyzer:
    """Analyze semantic fields and lexical relationships in Quranic verses."""

    # Arabic root patterns - maps 3-letter roots to their meanings
    ARABIC_ROOTS = {
        'خ-ل-ق': ['creation', 'creator', 'create', 'creature', 'nature'],
        'ن-ش-أ': ['develop', 'originate', 'growth', 'development'],
        'ع-ل-م': ['knowledge', 'know', 'knowing', 'learned'],
        'ف-ق-ه': ['understand', 'comprehension', 'fiqh', 'understanding'],
        'ن-و-ر': ['light', 'illuminate', 'illumination'],
        'ظ-ل-م': ['darkness', 'dark', 'oppress', 'oppression'],
        'ح-ق-ق': ['truth', 'true', 'reality', 'right'],
        'ب-ط-ل': ['falsehood', 'vain', 'void', 'false'],
        'ع-د-ل': ['justice', 'equity', 'fair', 'just'],
        'ق-س-ط': ['equity', 'justice', 'equitable'],
        'ك-و-ن': ['form', 'create', 'form', 'being'],
        'ب-ع-د': ['distance', 'far', 'remoteness'],
        'ط-ب-ق': ['layer', 'layers', 'stratified'],
        'ع-رض': ['width', 'presented', 'display'],
        'ع-ل-و': ['high', 'highest', 'elevation', 'exaltation'],
    }

    # Synonym mappings
    SYNONYMS_MAP = {
        'خلق': ['كون', 'أنشأ', 'بعث'],
        'علم': ['عرف', 'فقه', 'درى'],
        'نور': ['ضياء', 'إضاءة'],
        'ظلام': ['ظلمة'],
        'حق': ['صدق', 'حقيقة'],
        'باطل': ['كذب', 'زور'],
        'عدل': ['قسط', 'حق'],
        'قلب': ['فؤاد', 'صدر'],
        'سمع': ['استمع'],
        'بصر': ['رأى', 'نظر'],
        'نشأ': ['نمى', 'نبت'],
        'ذاق': ['ذوق', 'طعم'],
    }

    # Antonym mappings
    ANTONYMS_MAP = {
        'نور': ['ظلام', 'ظلمة'],
        'حق': ['باطل', 'كذب'],
        'عدل': ['ظلم', 'جور'],
        'حياة': ['موت'],
        'علم': ['جهل'],
        'قوة': ['ضعف'],
        'سماء': ['أرض'],
        'علو': ['سفل'],
    }

    # Metaphorical indicator words
    METAPHORICAL_INDICATORS = {
        'مثل', 'كأن', 'كان', 'يشبه', 'شبه', 'أشبه',
        'غرى', 'تراه', 'قلب', 'رؤية', 'بصر'
    }

    # Literal indicator words and patterns
    LITERAL_KEYWORDS = {
        'سماء', 'أرض', 'ماء', 'نار', 'شمس', 'قمر',
        'نجم', 'جبل', 'بحر', 'بيت', 'يوم', 'ليل'
    }

    def __init__(self, embeddings_layer=None):
        """Initialize with optional embeddings support.

        Args:
            embeddings_layer: Optional embeddings layer for semantic similarity.
        """
        self.embeddings_layer = embeddings_layer

    def analyze_verse_semantics(self, verse_text: str, verse_key: str) -> Dict:
        """Analyze semantic field of verse.

        Args:
            verse_text: The Arabic text of the verse.
            verse_key: The verse reference key (e.g., "39:5").

        Returns:
            Dictionary with semantic analysis including:
            - verse_key: str
            - root_clusters: Dict of roots to words
            - semantic_field: List of related concepts
            - synonyms: Dict of word -> synonyms
            - antonyms: Dict of word -> antonyms
            - semantic_density: float (0-1)
            - key_semantic_nodes: List of most connected words
            - metaphorical_expressions: List of metaphorical parts
            - literal_expressions: List of literal parts
        """
        # Extract roots and cluster them
        root_clusters = self._extract_roots(verse_text)

        # Identify semantic field
        words = self._extract_words(verse_text)
        semantic_field = self._identify_semantic_field(words, verse_text)

        # Extract synonyms and antonyms
        synonyms, antonyms = self._extract_synonyms_antonyms(verse_text)

        # Identify metaphors and literal expressions
        metaphorical_expr, literal_expr = self._identify_metaphors(verse_text)

        # Calculate semantic density
        semantic_density = self._calculate_semantic_density(root_clusters)

        # Identify key semantic nodes
        key_nodes = self._identify_key_nodes(
            root_clusters, semantic_field, words
        )

        return {
            'verse_key': verse_key,
            'root_clusters': root_clusters,
            'semantic_field': semantic_field,
            'synonyms': synonyms,
            'antonyms': antonyms,
            'semantic_density': semantic_density,
            'key_semantic_nodes': key_nodes,
            'metaphorical_expressions': metaphorical_expr,
            'literal_expressions': literal_expr,
        }

    def _extract_words(self, verse_text: str) -> List[str]:
        """Extract individual words from verse text.

        Args:
            verse_text: The verse text.

        Returns:
            List of words (with diacritics removed).
        """
        # Remove diacritics (tashkeel)
        diacritics = re.compile(r'[\u064B-\u0652]')
        clean_text = diacritics.sub('', verse_text)

        # Split into words
        words = clean_text.split()
        return [w.strip() for w in words if w.strip()]

    def _extract_roots(self, verse_text: str) -> Dict[str, List[str]]:
        """Extract Arabic 3-letter roots and group related words.

        Args:
            verse_text: The verse text.

        Returns:
            Dictionary mapping roots to lists of words that share them.
        """
        words = self._extract_words(verse_text)
        root_clusters = {}

        # For each known root, find matching words
        for root, concepts in self.ARABIC_ROOTS.items():
            # Extract the three letters from the root (e.g., 'خ-ل-ق' -> ['خ', 'ل', 'ق'])
            letters = root.split('-')

            matching_words = []
            for word in words:
                # Check if word contains all three root letters in order
                if self._contains_root_letters(word, letters):
                    matching_words.append(word)

            if matching_words:
                root_clusters[root] = matching_words

        return root_clusters

    def _contains_root_letters(self, word: str, letters: List[str]) -> bool:
        """Check if word contains all root letters in sequence.

        Args:
            word: The word to check.
            letters: List of 3 root letters to find.

        Returns:
            True if word contains all letters in order.
        """
        pos = 0
        for letter in letters:
            idx = word.find(letter, pos)
            if idx == -1:
                return False
            pos = idx + 1
        return True

    def _identify_semantic_field(self, words: List[str], verse_text: str) -> List[str]:
        """Identify related concepts beyond direct matches.

        Args:
            words: List of words in the verse.
            verse_text: The full verse text.

        Returns:
            List of semantic field concepts.
        """
        semantic_field = []

        # Add meanings from all roots present in verse
        for root, concepts in self.ARABIC_ROOTS.items():
            letters = root.split('-')
            for word in words:
                if self._contains_root_letters(word, letters):
                    # Add the associated concepts
                    semantic_field.extend(concepts)
                    break

        # Remove duplicates while preserving order
        seen = set()
        unique_field = []
        for item in semantic_field:
            if item not in seen:
                unique_field.append(item)
                seen.add(item)

        return unique_field

    def _extract_synonyms_antonyms(
        self, verse_text: str
    ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """Map synonyms and antonyms for key words.

        Args:
            verse_text: The verse text.

        Returns:
            Tuple of (synonyms_dict, antonyms_dict).
        """
        words = self._extract_words(verse_text)
        synonyms = {}
        antonyms = {}

        for word in words:
            # Check synonyms
            if word in self.SYNONYMS_MAP:
                synonyms[word] = self.SYNONYMS_MAP[word]

            # Check antonyms
            if word in self.ANTONYMS_MAP:
                antonyms[word] = self.ANTONYMS_MAP[word]

        return synonyms, antonyms

    def _identify_metaphors(
        self, verse_text: str
    ) -> Tuple[List[str], List[str]]:
        """Separate metaphorical from literal expressions.

        Args:
            verse_text: The verse text.

        Returns:
            Tuple of (metaphorical_expressions, literal_expressions).
        """
        words = self._extract_words(verse_text)
        metaphorical = []
        literal = []

        for word in words:
            # Check if word is a metaphorical indicator
            if word in self.METAPHORICAL_INDICATORS:
                metaphorical.append(word)
            # Check if word is a literal keyword
            elif word in self.LITERAL_KEYWORDS:
                literal.append(word)

        # If no explicit markers, use heuristic:
        # Words like 'قلب', 'عين', 'سمع' in abstract contexts are metaphorical
        abstract_body_parts = {'قلب', 'عين', 'سمع', 'بصر', 'لسان'}
        for word in words:
            if word in abstract_body_parts and word not in metaphorical:
                metaphorical.append(word)

        return metaphorical, literal

    def _calculate_semantic_density(self, root_clusters: Dict) -> float:
        """Calculate interconnectedness of semantic field (0-1).

        Args:
            root_clusters: Dictionary of root clusters.

        Returns:
            Density score between 0 and 1.
        """
        if not root_clusters:
            return 0.0

        # Count total words across all clusters
        total_words = sum(len(words) for words in root_clusters.values())

        if total_words == 0:
            return 0.0

        # Density = (number of clusters with multiple words) / (total clusters)
        # This reflects how interconnected the semantic field is
        multi_word_clusters = sum(
            1 for words in root_clusters.values() if len(words) > 1
        )

        density = multi_word_clusters / len(root_clusters)

        # Also factor in word density: ratio of total words to possible positions
        # Assuming max density when we have many words from few roots
        if total_words > 0:
            word_ratio = min(total_words / 10.0, 1.0)  # Normalize to max 10 words
            density = (density + word_ratio) / 2.0

        return min(density, 1.0)

    def _identify_key_nodes(
        self,
        root_clusters: Dict,
        semantic_field: List[str],
        words: List[str],
    ) -> List[str]:
        """Identify key semantic nodes (most connected words).

        Args:
            root_clusters: Dictionary of root clusters.
            semantic_field: List of semantic field concepts.
            words: List of words in verse.

        Returns:
            List of key semantic nodes.
        """
        key_nodes = []

        # Add words that appear in multiple contexts
        for cluster_words in root_clusters.values():
            if len(cluster_words) > 1:
                # Most common word from each multi-word cluster
                key_nodes.append(cluster_words[0])

        # Add semantic field concepts that are most general
        if semantic_field:
            # Take the first 2-3 most general concepts
            key_nodes.extend(semantic_field[:3])

        # Remove duplicates
        seen = set()
        unique_nodes = []
        for node in key_nodes:
            if node not in seen:
                unique_nodes.append(node)
                seen.add(node)

        return unique_nodes
