"""
Tafsir Consolidator - Semantic Agreement Matrix

Consolidates 8 classical Quranic tafsirs into unified semantic analysis without fabricating differences.

8 Tafsirs integrated:
1. Al-Tabari (9th century Sunni)
2. Ibn Kathir (14th century Sunni)
3. Al-Zamakhshari (12th century Mu'tazili)
4. Al-Qurtubi (13th century Maliki)
5. Al-Baydawi (13th century Shafi'i)
6. Ibn Juzayy (14th century Maliki)
7. Al-Shawkani (18th century Salafi)
8. Al-Alousi (19th century Salafi)

School mapping:
- Sunni: Al-Tabari, Ibn Kathir, Al-Qurtubi, Al-Baydawi, Ibn Juzayy
- Mu'tazili: Al-Zamakhshari
- Salafi: Al-Shawkani, Al-Alousi
"""

from typing import Dict, List, Set, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class TafsirConsolidator:
    """Consolidate 8 classical tafsirs into semantic agreement matrix"""

    # Madhab school mapping
    MADHAB_MAPPING = {
        'Al-Tabari': 'Sunni',
        'Ibn Kathir': 'Sunni',
        'Al-Zamakhshari': 'Mu\'tazili',
        'Al-Qurtubi': 'Maliki',
        'Al-Baydawi': 'Shafi\'i',
        'Ibn Juzayy': 'Maliki',
        'Al-Shawkani': 'Salafi',
        'Al-Alousi': 'Salafi'
    }

    EXPECTED_TAFSIRS = [
        'Al-Tabari',
        'Ibn Kathir',
        'Al-Zamakhshari',
        'Al-Qurtubi',
        'Al-Baydawi',
        'Ibn Juzayy',
        'Al-Shawkani',
        'Al-Alousi'
    ]

    def __init__(self, cache_layer=None, api_layer=None):
        """Initialize with optional dependencies"""
        self.cache_layer = cache_layer
        self.api_layer = api_layer

    def consolidate_tafsirs(self, surah: int, ayah: int, tafsir_texts: Dict[str, str]) -> Dict:
        """
        Consolidate tafsir interpretations into unified analysis.

        Args:
            surah: Surah number
            ayah: Ayah number
            tafsir_texts: Dict with tafsir names as keys and texts as values
                Expected keys: Al-Tabari, Ibn Kathir, Al-Zamakhshari, etc. (8 tafsirs)

        Returns: Dict with consolidated analysis including:
            - consensus_themes: Common themes across tafsirs
            - consensus_confidence: Agreement percentage (0-1)
            - madhab_differences: School-specific interpretations
            - semantic_agreement_matrix: Pairwise agreement scores
            - key_concepts: Important concepts from all tafsirs
            - verse_key: Format "surah:ayah"
            - tafsir_coverage: Percentage of 8 tafsirs used (0-1)
        """
        # Filter out empty texts
        valid_texts = {k: v for k, v in tafsir_texts.items() if v and v.strip()}

        # Calculate coverage
        tafsir_coverage = len(valid_texts) / len(self.EXPECTED_TAFSIRS)

        # Compute semantic agreement matrix between all tafsirs
        agreement_matrix = self._compute_semantic_agreement(tafsir_texts)

        # Calculate consensus confidence
        consensus_confidence = self._calculate_consensus_confidence(agreement_matrix)

        # Extract themes from valid tafsirs
        consensus_themes = self._extract_themes(valid_texts)

        # Extract key concepts
        key_concepts = self._extract_key_concepts(valid_texts)

        # Identify madhab-specific differences
        madhab_differences = self._identify_madhab_differences(valid_texts)

        return {
            'consensus_themes': consensus_themes,
            'consensus_confidence': consensus_confidence,
            'madhab_differences': madhab_differences,
            'semantic_agreement_matrix': agreement_matrix,
            'key_concepts': key_concepts,
            'verse_key': f'{surah}:{ayah}',
            'tafsir_coverage': tafsir_coverage
        }

    def _compute_semantic_agreement(self, texts: Dict[str, str]) -> Dict:
        """
        Compute pairwise semantic agreement between all tafsirs.

        Returns: Dict of {tafsir: {other_tafsir: score}}
        where score is 0-1 representing similarity
        """
        agreement_matrix = {}
        tafsir_names = list(texts.keys())

        for i, tafsir1 in enumerate(tafsir_names):
            agreement_matrix[tafsir1] = {}
            text1 = texts[tafsir1]

            # Skip if text1 is empty
            if not text1 or not text1.strip():
                continue

            for tafsir2 in tafsir_names:
                if tafsir1 == tafsir2:
                    continue

                text2 = texts[tafsir2]

                # Skip if text2 is empty
                if not text2 or not text2.strip():
                    continue

                # Calculate semantic agreement
                similarity = self._calculate_text_similarity(text1, text2)
                agreement_matrix[tafsir1][tafsir2] = similarity

        return agreement_matrix

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using word overlap.

        Returns: float between 0 and 1
        """
        if not text1 or not text2:
            return 0.0

        # Normalize texts
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Calculate overlap
        overlap = len(words1 & words2)
        total = len(words1 | words2)

        if total == 0:
            return 0.0

        return overlap / total

    def _extract_themes(self, tafsir_texts: Dict[str, str]) -> List[str]:
        """
        Extract interpretive themes from tafsirs.

        Looks for common words/concepts across majority of tafsirs.
        Returns: List of extracted themes
        """
        if not tafsir_texts:
            return []

        # Count word frequencies across all tafsirs
        all_words = []
        for text in tafsir_texts.values():
            if text and text.strip():
                words = text.lower().split()
                all_words.extend(words)

        if not all_words:
            return []

        # Count frequency
        word_counts = Counter(all_words)

        # Get words that appear in majority of tafsirs
        num_tafsirs = len([t for t in tafsir_texts.values() if t and t.strip()])
        majority_threshold = max(1, num_tafsirs // 2)

        themes = []
        tafsir_list = list(tafsir_texts.values())

        for word, count in word_counts.most_common(20):
            # Skip common stopwords
            if word in ['the', 'a', 'an', 'and', 'or', 'is', 'are', 'to', 'in', 'of']:
                continue

            # Count how many tafsirs contain this word
            appearances = sum(1 for text in tafsir_list if text and word in text.lower())

            if appearances >= majority_threshold:
                themes.append(word)

        return themes[:10]  # Return top 10 themes

    def _extract_key_concepts(self, tafsir_texts: Dict[str, str]) -> List[str]:
        """
        Extract key concepts from all tafsirs.

        Returns: List of important concepts (longer phrases than themes)
        """
        if not tafsir_texts:
            return []

        # For now, extract significant words (non-stopwords)
        # A more sophisticated approach would use NLP for phrase extraction
        concepts = []
        all_text = ' '.join([t for t in tafsir_texts.values() if t and t.strip()])

        if not all_text:
            return []

        words = all_text.lower().split()
        word_freq = Counter(words)

        stopwords = {'the', 'a', 'an', 'and', 'or', 'is', 'are', 'to', 'in', 'of', 'this', 'that', 'as', 'with', 'for', 'from'}

        for word, count in word_freq.most_common(20):
            if word not in stopwords and count >= 2:
                concepts.append(word)

        return concepts[:10]  # Return top 10 concepts

    def _identify_madhab_differences(self, tafsir_texts: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Identify school-specific interpretations.

        Maps each school/madhab to its unique interpretations not shared with others.
        Returns: Dict of {madhab: [unique_interpretations]}
        """
        madhab_differences = {}

        # Group texts by madhab
        madhab_texts = {}
        for tafsir_name, text in tafsir_texts.items():
            if not text or not text.strip():
                continue

            madhab = self.MADHAB_MAPPING.get(tafsir_name)
            if madhab:
                if madhab not in madhab_texts:
                    madhab_texts[madhab] = []
                madhab_texts[madhab].append(text)

        # For each madhab, find concepts that are unique or less common in other madhabs
        for madhab, texts in madhab_texts.items():
            madhab_words = Counter()

            # Count words in this madhab
            for text in texts:
                words = text.lower().split()
                madhab_words.update(words)

            # Find words relatively unique to this madhab
            unique_words = []
            for word, count in madhab_words.most_common(20):
                # Skip stopwords
                if word in ['the', 'a', 'an', 'and', 'or', 'is', 'are', 'to', 'in', 'of']:
                    continue

                # Check if word appears in other madhabs
                appears_elsewhere = 0
                for other_madhab, other_texts in madhab_texts.items():
                    if other_madhab != madhab:
                        for text in other_texts:
                            if word in text.lower():
                                appears_elsewhere += 1
                                break

                # If word appears in fewer than half of other madhabs, it's somewhat unique
                if appears_elsewhere < (len(madhab_texts) - 1) / 2:
                    unique_words.append(word)

            madhab_differences[madhab] = unique_words[:5]  # Top 5 unique concepts

        return madhab_differences

    def _calculate_consensus_confidence(self, agreement_matrix: Dict) -> float:
        """
        Calculate confidence level as average of all pairwise agreements.

        Returns: float between 0 and 1
        """
        if not agreement_matrix:
            return 0.0

        all_scores = []
        for tafsir_agreements in agreement_matrix.values():
            all_scores.extend(tafsir_agreements.values())

        if not all_scores:
            return 0.0

        return sum(all_scores) / len(all_scores)
