# Arabic Morphological Analysis and Root-Pattern System Algorithm

## Source
- **Source Material**: The Study Quran (linguistic commentary), Classical Arabic grammar texts (Sibawayh), Quranic word studies
- **Methodology**: Root-and-pattern morphology system (tri/quadri-literal roots with diacritic patterns)
- **Framework**: Quranic linguistic analysis, word-family semantic relationships

## Principle
Arabic morphology operates on a tri-consonantal (or quadri-consonantal) root system combined with diacritic vowel patterns. This mathematical structure can be formalized to identify semantic relationships, morphological families, and word evolution. Understanding these patterns unlocks Quranic vocabulary interconnections.

## Mathematical Formulation

### 1. Morphological Structure
```
Arabic_Word = Root × Pattern

where:
  Root = {C₁, C₂, C₃} or {C₁, C₂, C₃, C₄} (consonants)
  Pattern = Template {V₁C₁V₂C₂V₃C₃V₄C₄...} or CvCvC (canonical forms)

Example:
  k-t-b (root: "write")
  kutiba (passive past) = k[u]t[i]b[a]
  yaktubu (present active) = y[a]kt[u]b[u]
  maktab (desk/office) = m[a]k[t]ab

```

### 2. Morphological Pattern Classification
```
MorphologicalPatterns = {
  Verb_Patterns: {
    FaCaLa: perfective active (root form)
    YaFCuLu: imperfective active
    FuCiLa: perfective passive
    YuFCaLu: imperfective passive
    AFCaLa: causative
    TaFaCCaLa: reflexive/intensive
  },
  Noun_Patterns: {
    FaCL: agent noun (writer = katib)
    FiCL: patient noun (written = maktub)
    FaCiLa: quality noun
    FuCuL: plurals
    MaFCaL: place noun (office = maktab)
    FaCCaL: intensive adjective
  },
  Derivational_Patterns: {...}
}

Pattern_Formula(root, pattern) = interpolate(root_consonants, pattern_template)
```

### 3. Semantic Field by Root
```
SemanticField(root) = {
  primary_meaning: core concept,
  derived_meanings: {
    word₁: meaning₁ via pattern_a,
    word₂: meaning₂ via pattern_b,
    ...
  },
  metaphorical_extensions: [extension₁, extension₂, ...],
  antonyms: [opposite_root₁, opposite_root₂, ...],
  cognates: [related_root₁, related_root₂, ...]
}

Example:
  r-h-m (mercy):
    rahma (mercy), rahmah (womb), rahman (merciful)
    metaphorical: "mercy encompasses all things" (Quran 7:156)
```

### 4. Morphological Complexity Metric
```
Complexity(word) = base_score + pattern_complexity + affixation_complexity

where:
  base_score = 1 (minimal word)
  pattern_complexity = number of vowel/consonant modifications from root
  affixation_complexity = Σ affixes (prefix + suffix + infix)

Simple: CvCv (e.g., nama)
Complex: CCaCCaCa with affixes (e.g., wal-muhaqqaqun)
```

### 5. Word Family Graph
```
WordFamily = (Nodes, Edges)
  Nodes = {all words sharing same root}
  Edges = {(w₁, w₂) | morphologically derived or semantically cognate}
  Edge_Type ∈ {pattern_derivation, semantic_extension, metaphorical, antonym}
  Edge_Weight = semantic_distance ∈ [0, 1]
    0 = direct pattern application
    1 = remote metaphorical extension
```

## Algorithm: Morphological Analysis

### Pseudocode
```
function MORPHOLOGICAL_ANALYZE(arabic_word):
  INPUT: arabic_word (with diacritics)
  OUTPUT: morphological_analysis (dict with root, pattern, components)

  // Step 1: Normalize word (remove diacritics for matching)
  normalized = REMOVE_DIACRITICS(arabic_word)
  fully_vocalized = arabic_word  // Keep for pattern analysis

  // Step 2: Extract affixes
  affixes = {}

  // Check prefixes (definite article al-, prepositions wa-, li-, bi-)
  if STARTS_WITH(normalized, "al"):
    affixes['definite_article'] = "al"
    normalized = REMOVE_PREFIX(normalized, "al")

  for each preposition in {wa, li, bi, ka}:
    if STARTS_WITH(normalized, preposition):
      affixes['preposition'] = preposition
      normalized = REMOVE_PREFIX(normalized, preposition)
      break

  // Check suffixes (pronouns: -ha, -hu, -hum, -na; case endings: -un, -an, -in)
  for each suffix in SUFFIX_LIST:
    if ENDS_WITH(normalized, suffix):
      affixes['suffix'] = suffix
      normalized = REMOVE_SUFFIX(normalized, suffix)
      break

  // Step 3: Identify root
  root_candidates = []

  // Try to extract tri-consonantal root
  for i in 0 to len(normalized)-3:
    potential_root = EXTRACT_CONSONANTS(normalized, positions={i, i+1, i+2})
    if IS_VALID_ROOT(potential_root):  // Check against root database
      root_candidates.append(potential_root)

  if len(root_candidates) > 1:
    // Disambiguate using context/frequency
    best_root = RANK_ROOTS(root_candidates)[0]
  else:
    best_root = root_candidates[0]

  // Step 4: Identify pattern
  root_positions = LOCATE_ROOT_CONSONANTS(normalized, best_root)
  pattern = EXTRACT_PATTERN_TEMPLATE(normalized, fully_vocalized, root_positions)

  // Step 5: Classify morphological type
  morph_type = CLASSIFY_TYPE(pattern)
    // Returns: verb_active, verb_passive, agent_noun, patient_noun, etc.

  // Step 6: Derive word meaning from root + pattern
  root_meaning = LOOKUP_ROOT_MEANING(best_root)
  pattern_modification = LOOKUP_PATTERN_MODIFICATION(pattern, morph_type)
  derived_meaning = COMPOSE_MEANING(root_meaning, pattern_modification)

  // Step 7: Find word family
  word_family = FIND_WORD_FAMILY(best_root)
  cognates = FIND_COGNATE_FORMS(best_root)

  return {
    original_word: arabic_word,
    root: best_root,
    pattern: pattern,
    pattern_name: morph_type,
    meaning: derived_meaning,
    affixes: affixes,
    word_family: word_family,
    cognates: cognates,
    confidence: CALCULATE_CONFIDENCE(root_candidates, pattern),
    morphological_derivation: {
      root_meaning: root_meaning,
      pattern_contribution: pattern_modification,
      overall_derivation: f"{root_meaning} + {pattern_modification}"
    }
  }
```

### Sub-algorithm: Pattern Identification
```
function IDENTIFY_PATTERN(normalized_word, vocalized_word, root_consonants):
  INPUT: normalized_word, vocalized_word, root_consonants
  OUTPUT: pattern (canonical form), vowel_sequence

  // Consonant positions in word
  consonant_positions = FIND_CONSONANT_POSITIONS(normalized_word)
  root_positions = LOCATE_ROOT_CONSONANTS(consonant_positions, root_consonants)

  // Extract vowels between root consonants
  vowel_pattern = []
  for i in 0 to len(root_positions)-1:
    pos_before = root_positions[i]
    pos_after = root_positions[i+1]
    vowels_between = EXTRACT_VOWELS(vocalized_word, pos_before, pos_after)
    vowel_pattern.append(vowels_between)

  // Construct canonical pattern template
  canonical_pattern = "C" + vowel_pattern[0] + "C" + vowel_pattern[1] + "C"

  // Match against known patterns
  pattern_name = MATCH_PATTERN_TEMPLATE(canonical_pattern)

  return (canonical_pattern, pattern_name, vowel_pattern)
```

## Implementation Approach

### Python Skeleton
```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

class MorphologicalType(Enum):
    VERB_ACTIVE = "Perfective Active"
    VERB_PASSIVE = "Perfective Passive"
    AGENT_NOUN = "One who does"
    PATIENT_NOUN = "That which is done to"
    INTENSIVE = "Intensive"
    CAUSATIVE = "Causative"
    PLACE_NOUN = "Place where action occurs"
    ABSTRACT_NOUN = "Abstract quality"

@dataclass
class ArabicRoot:
    root: str  # e.g., "k-t-b"
    primary_meaning: str
    semantic_field: List[str]
    frequency_in_quran: int
    related_roots: List[str]

@dataclass
class MorphologicalPattern:
    pattern_template: str  # e.g., "FaCaLa"
    vowel_sequence: Tuple[str, str, str]
    grammatical_function: MorphologicalType
    name: str
    example_word: str

@dataclass
class WordAnalysis:
    word: str
    root: ArabicRoot
    pattern: MorphologicalPattern
    affixes: Dict[str, str]
    meaning: str
    word_family: List[str]
    cognates: List[str]
    confidence: float

class ArabicMorphologicalAnalyzer:
    def __init__(self):
        self.root_database = {}  # Load root dictionary
        self.pattern_database = {}  # Load pattern templates
        self.word_family_db = {}  # Load word families

    def extract_affixes(self, word: str) -> Tuple[str, Dict[str, str]]:
        """Extract prefixes and suffixes from word"""
        affixes = {}
        normalized = word

        # Check for definite article
        if normalized.startswith('ال'):
            affixes['definite_article'] = 'ال'
            normalized = normalized[2:]

        # Check for prepositions
        for prep in ['و', 'ل', 'ب', 'ك']:
            if normalized.startswith(prep):
                affixes['preposition'] = prep
                normalized = normalized[1:]
                break

        # Check for suffixes
        suffix_patterns = [
            ('ها', 'feminine_possessive'),
            ('هم', 'masculine_plural_possessive'),
            ('ن', 'nominative_plural'),
            ('وا', 'verb_subject_marker'),
        ]

        for suffix, type_name in suffix_patterns:
            if normalized.endswith(suffix):
                affixes['suffix'] = (suffix, type_name)
                normalized = normalized[:-len(suffix)]
                break

        return normalized, affixes

    def find_root(self, word: str) -> Tuple[str, float]:
        """Identify tri-consonantal root"""
        # Extract consonants only
        consonants = [c for c in word if self._is_consonant(c)]

        if len(consonants) < 3:
            return None, 0.0

        # Try tri-consonantal combinations
        candidates = []
        for i in range(len(consonants) - 2):
            potential_root = f"{consonants[i]}-{consonants[i+1]}-{consonants[i+2]}"
            if potential_root in self.root_database:
                frequency = self.root_database[potential_root].frequency_in_quran
                candidates.append((potential_root, frequency))

        if candidates:
            # Pick most frequent
            best = max(candidates, key=lambda x: x[1])
            confidence = best[1] / 1000  # Normalize
            return best[0], min(1.0, confidence)
        return None, 0.0

    def identify_pattern(self, word: str, root: str) -> Tuple[str, MorphologicalType]:
        """Identify morphological pattern"""
        # Implementation: template matching
        # Extract vowels between root consonants
        # Match against known pattern templates
        pass

    def derive_meaning(self, root: ArabicRoot,
                      pattern: MorphologicalPattern) -> str:
        """Derive word meaning from root + pattern"""
        base_meaning = root.primary_meaning
        pattern_modification = self._get_pattern_modification(pattern.grammatical_function)

        return f"{base_meaning} ({pattern_modification})"

    def find_word_family(self, root: str) -> List[str]:
        """Find all words sharing same root"""
        return self.word_family_db.get(root, [])

    def analyze(self, word: str) -> WordAnalysis:
        """Complete morphological analysis"""
        normalized, affixes = self.extract_affixes(word)

        root_str, root_conf = self.find_root(normalized)
        if not root_str:
            return None

        root = self.root_database[root_str]
        pattern_name, morph_type = self.identify_pattern(normalized, root_str)
        pattern = self.pattern_database.get(pattern_name)

        meaning = self.derive_meaning(root, pattern)
        word_family = self.find_word_family(root_str)

        return WordAnalysis(
            word=word,
            root=root,
            pattern=pattern,
            affixes=affixes,
            meaning=meaning,
            word_family=word_family,
            cognates=root.related_roots,
            confidence=root_conf
        )

    @staticmethod
    def _is_consonant(char: str) -> bool:
        """Check if character is Arabic consonant"""
        vowels = {'َ', 'ِ', 'ُ', 'ً', 'ٍ', 'ٌ', 'ْ'}
        return char not in vowels and char.isalpha()
```

## Validation Method

### Test Cases
1. **Simple Verb**: Analyze "kataba" (he wrote)
   - Expected: Root = k-t-b, Pattern = FaCaLa, Meaning derived correctly

2. **Derived Noun**: Analyze "maktab" (office/desk)
   - Expected: Root = k-t-b, Pattern = MaFCaL, Cognate to "kataba"

3. **Complex Word with Affixes**: Analyze "walladhina" (and those who)
   - Expected: Affix extraction works, core word identified

4. **Word Family**: For root k-t-b
   - Expected: {kataba, maktab, kitab, kaatib, muktab, taktib}

### Quality Metrics
- Root identification accuracy vs. dictionary
- Pattern classification accuracy
- Semantic relationship discovery
- Word family completeness

## Applications

1. **Quranic Concordance**: Finding all variations of word families
2. **Semantic Relationships**: Understanding word connections through roots
3. **Translation Accuracy**: Mapping Arabic morphology to target languages
4. **Lexical Analysis**: Building semantic networks of Quranic vocabulary
5. **Language Learning**: Teaching Arabic structure systematically
6. **Textual Analysis**: Identifying author style through morphological patterns
7. **Hadith Word Studies**: Analyzing prophetic vocabulary usage

## Related Algorithms
- Semantic Field Extraction Algorithm (uses this for word families)
- Quranic Vocabulary Frequency Algorithm
- Tafsir Cross-Reference Algorithm
- Word Similarity Algorithm
