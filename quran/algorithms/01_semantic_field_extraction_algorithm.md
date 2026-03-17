# Quranic Semantic Field Extraction Algorithm

## Source
- **Source Material**: The Study Quran (138,228 lines)
- **Methodology**: Classical Tafsir (Quranic commentary) combined with linguistic field analysis
- **Framework**: Based on thematic repetition patterns in the Quran

## Principle
The Quran uses repeated semantic fields—sets of related concepts—to emphasize core principles. These fields can be algorithmically extracted and analyzed to identify the Quran's central themes, their relationships, and their development across chapters.

## Mathematical Formulation

### 1. Semantic Field Graph
```
SemanticField = (V, E, W)
where:
  V = Set of concept vertices {c₁, c₂, ..., cₙ}
  E = Set of semantic relations {(cᵢ, cⱼ) | concepts related}
  W = Weight function W(cᵢ, cⱼ) = frequency of co-occurrence

Examples:
  Field_Justice = {adl, qist, hakam, din, mizan}
  Field_Knowledge = {ilm, hikmah, fahm, dhikr, 'aql}
  Field_Covenant = {'ahd, mithaq, 'aqd, 'amanah}
```

### 2. Concept Frequency Distribution
```
Freq(concept) = Σ count(concept, surah_i) for all surahs

Distribution characteristics:
  Core concepts (5+ surahs): {God, Messenger, Believers, guidance, judgment}
  Major concepts (2-5 surahs): {prayer, charity, knowledge, covenant}
  Thematic concepts (1 surah): {specific to narrative or historical context}

Normalized frequency: f(c) = count(c) / max_frequency
```

### 3. Semantic Relationship Strength
```
Strength(cᵢ → cⱼ) = (Σ co_occur(cᵢ, cⱼ) / total_verses) ×
                     (1 + contextual_proximity_bonus) ×
                     (1 + logical_relation_strength)

Contextual_proximity: verses(distance ≤ 10) count more than distant verses
Logical_relation: Causal relations > Contrastive relations > Associative relations
```

### 4. Thematic Cluster Hierarchy
```
Hierarchy = {
  Meta_Themes: {God, humanity, guidance, covenant},
    ├─ God_Attributes: {mercy, justice, knowledge, power}
    ├─ Human_Condition: {belief, obedience, repentance, struggle}
    ├─ Guidance: {revelation, prophecy, scripture, wisdom}
    └─ Covenant: {obligation, promise, law, consequence}
}

Abstraction_Level: 0 (atomic concept) → 5 (universal principle)
```

## Algorithm: Semantic Field Extraction

### Pseudocode
```
function EXTRACT_SEMANTIC_FIELDS(quran_text):
  INPUT: quran_text (full Quranic text with verse metadata)
  OUTPUT: semantic_fields (dict of extracted fields with relationships)

  // Step 1: Normalize and tokenize
  verses = PARSE_VERSES(quran_text)
  token_map = {}  // Maps words to normalized forms

  for each verse in verses:
    tokens = TOKENIZE_ARABIC(verse.text)
    for each token in tokens:
      normalized = NORMALIZE_MORPHOLOGY(token)
        // Remove diacritics, identify word roots
      IF normalized NOT IN token_map:
        token_map[normalized] = []
      token_map[normalized].append(verse)

  // Step 2: Identify root concepts
  root_concepts = {}
  for each (root, verses_list) in token_map:
    frequency = len(verses_list)

    IF frequency >= 5:  // Appears in 5+ surahs (threshold)
      is_concept = SEMANTIC_ANALYSIS(root)
      IF is_concept:
        root_concepts[root] = {
          frequency: frequency,
          verses: verses_list,
          morphological_family: IDENTIFY_WORD_FAMILY(root)
        }

  // Step 3: Build semantic relationships
  semantic_graph = INITIALIZE_GRAPH(root_concepts)

  for each (concept_i, concept_j) in combinations(root_concepts):
    IF concept_i != concept_j:
      co_occurrences = COUNT_VERSE_CO_OCCURRENCES(concept_i, concept_j)
      proximity_factor = CALCULATE_PROXIMITY_BONUS(concept_i, concept_j)
      relationship_type = INFER_RELATIONSHIP_TYPE(concept_i, concept_j)
      strength = (co_occurrences / total_verses) * proximity_factor

      IF strength > threshold:
        semantic_graph.add_edge(concept_i, concept_j, weight=strength)

  // Step 4: Cluster semantically related concepts
  fields = {}
  clusters = COMMUNITY_DETECTION(semantic_graph)
    // Using modularity-based clustering

  for each cluster in clusters:
    core_concepts = IDENTIFY_CORE_CONCEPTS(cluster)
    field_name = GENERATE_FIELD_NAME(core_concepts)
    fields[field_name] = {
      concepts: cluster,
      core_concepts: core_concepts,
      frequency: AGGREGATE_FREQUENCY(cluster),
      relationships: EXTRACT_CLUSTER_RELATIONSHIPS(cluster),
      verses: GATHER_VERSE_REFERENCES(cluster)
    }

  // Step 5: Identify thematic hierarchy
  hierarchy = BUILD_ABSTRACTION_HIERARCHY(fields)

  return {
    semantic_fields: fields,
    concept_graph: semantic_graph,
    hierarchy: hierarchy,
    statistics: {
      total_fields: len(fields),
      total_concepts: len(root_concepts),
      densest_field: IDENTIFY_DENSEST(fields),
      most_connected: IDENTIFY_MOST_CONNECTED(fields)
    }
  }
```

### Sub-algorithm: Verse Co-occurrence Analysis
```
function COUNT_VERSE_CO_OCCURRENCES(concept_a, concept_b):
  INPUT: concept_a, concept_b (normalized concepts)
  OUTPUT: co_occurrence_count (int)

  verses_a = concept_a.verses
  verses_b = concept_b.verses

  // Exact co-occurrence (same verse)
  exact_matches = INTERSECTION(verses_a, verses_b)

  // Nearby co-occurrence (within N verses)
  nearby = 0
  for each verse_a in verses_a:
    for each verse_b in verses_b:
      distance = abs(verse_a.verse_number - verse_b.verse_number)
      IF distance <= 10:  // Within 10 verses
        nearby += 1

  // Surah-level co-occurrence
  same_surah = 0
  for each surah in surahs:
    IF has_concept(surah, concept_a) AND has_concept(surah, concept_b):
      same_surah += 1

  return {
    exact: len(exact_matches),
    nearby: nearby,
    same_surah: same_surah,
    total: len(exact_matches) + nearby + same_surah
  }
```

## Implementation Approach

### Python Skeleton
```python
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
import networkx as nx
from collections import Counter

@dataclass
class QuranicVerse:
    surah: int
    verse: int
    text: str
    tokens: List[str]
    roots: List[str]

@dataclass
class Concept:
    root_word: str
    normalized: str
    frequency: int
    morphological_family: List[str]
    verses: List[QuranicVerse]
    abstraction_level: int

@dataclass
class SemanticField:
    name: str
    core_concepts: List[str]
    all_concepts: List[Concept]
    frequency: int
    density: float
    related_fields: List[str]

class SemanticFieldExtractor:
    def __init__(self, quran_text: str):
        self.quran_text = quran_text
        self.verses = self._parse_verses()
        self.concepts = {}
        self.semantic_graph = nx.Graph()

    def _parse_verses(self) -> List[QuranicVerse]:
        """Parse Quranic text into verse objects"""
        # Implementation: parse structured Quranic text
        pass

    def _normalize_token(self, token: str) -> str:
        """Normalize Arabic morphology to root form"""
        # Implementation: stemming/lemmatization for Arabic
        pass

    def extract_root_concepts(self, min_frequency: int = 5) -> Dict[str, Concept]:
        """Extract concepts that appear frequently enough"""
        word_frequency = Counter()
        word_verses = {}

        for verse in self.verses:
            for token in verse.tokens:
                normalized = self._normalize_token(token)
                word_frequency[normalized] += 1
                if normalized not in word_verses:
                    word_verses[normalized] = []
                word_verses[normalized].append(verse)

        # Filter by frequency and semantic relevance
        concepts = {}
        for word, count in word_frequency.items():
            if count >= min_frequency:
                is_semantic = self._is_semantic_concept(word)
                if is_semantic:
                    concepts[word] = Concept(
                        root_word=word,
                        normalized=word,
                        frequency=count,
                        morphological_family=self._get_word_family(word),
                        verses=word_verses[word],
                        abstraction_level=self._determine_abstraction(word)
                    )

        self.concepts = concepts
        return concepts

    def build_semantic_relationships(self) -> nx.Graph:
        """Build graph of semantic relationships"""
        graph = nx.Graph()

        # Add nodes
        for concept_name, concept in self.concepts.items():
            graph.add_node(concept_name, concept=concept)

        # Add edges based on co-occurrence
        concept_list = list(self.concepts.keys())
        for i, concept_a in enumerate(concept_list):
            for concept_b in concept_list[i+1:]:
                co_occur = self._count_co_occurrences(
                    self.concepts[concept_a],
                    self.concepts[concept_b]
                )

                if co_occur['total'] > 0:
                    proximity = self._calculate_proximity_bonus(
                        concept_a, concept_b
                    )
                    strength = (co_occur['total'] / len(self.verses)) * proximity
                    graph.add_edge(concept_a, concept_b, weight=strength)

        self.semantic_graph = graph
        return graph

    def _count_co_occurrences(self, concept_a: Concept,
                             concept_b: Concept) -> Dict[str, int]:
        """Count how often two concepts appear together"""
        exact = 0
        nearby = 0
        same_surah = 0

        verses_a = {(v.surah, v.verse) for v in concept_a.verses}
        verses_b = {(v.surah, v.verse) for v in concept_b.verses}

        # Exact matches
        exact = len(verses_a & verses_b)

        # Nearby matches
        for surah_a, verse_a in verses_a:
            for surah_b, verse_b in verses_b:
                if surah_a == surah_b and abs(verse_a - verse_b) <= 10:
                    nearby += 1
                elif surah_a == surah_b:
                    same_surah += 1

        return {'exact': exact, 'nearby': nearby, 'same_surah': same_surah,
                'total': exact + nearby + same_surah}

    def extract_semantic_fields(self) -> Dict[str, SemanticField]:
        """Extract complete semantic fields using clustering"""
        # Community detection on semantic graph
        from networkx.algorithms import community

        communities = list(community.greedy_modularity_communities(
            self.semantic_graph
        ))

        fields = {}
        for idx, comm in enumerate(communities):
            concepts = [self.concepts[c] for c in comm]
            core = [c for c in comm if self.concepts[c].frequency >
                   sum(c.frequency for c in concepts) / len(concepts)]

            field_name = self._generate_field_name(core)
            fields[field_name] = SemanticField(
                name=field_name,
                core_concepts=core,
                all_concepts=concepts,
                frequency=sum(c.frequency for c in concepts),
                density=nx.density(self.semantic_graph.subgraph(comm)),
                related_fields=self._find_related_fields(field_name, fields)
            )

        return fields

    def build_thematic_hierarchy(self, fields: Dict[str, SemanticField]) -> Dict:
        """Build abstraction hierarchy of themes"""
        # Implementation: construct hierarchy based on abstraction levels
        pass
```

## Validation Method

### Test Cases
1. **Core Theme Detection**: Extract semantic field for "God's attributes"
   - Expected: Contains {mercy, justice, knowledge, power, wisdom}

2. **Concept Frequency**: Verify frequency of core concepts
   - Expected: "God" (Allah) appears in 90%+ of verses

3. **Field Clustering**: Verify semantically similar concepts cluster together
   - Expected: {charity, justice, kindness} in same field

4. **Relationship Strength**: Verify co-occurrence patterns
   - Expected: "guidance" strongly linked to "revelation", "prophecy"

### Quality Metrics
```
Field_Coherence = avg_pairwise_similarity(field_concepts)
Field_Separation = min_distance(fields)
Recall = extracted_fields / known_fields
```

## Applications

1. **Thematic Indexing**: Organizing Quranic content by semantic themes
2. **Quranic Connections**: Finding verses addressing similar concepts
3. **Conceptual Development**: Tracking how themes evolve across surahs
4. **Comparative Analysis**: Finding parallels in meaning across different texts
5. **Educational Mapping**: Creating knowledge maps of Quranic principles
6. **Interpretation Support**: Providing contextual semantic fields for commentary
7. **Natural Language Understanding**: Building semantic models of Quranic language

## Related Algorithms
- Quranic Morphological Analysis Algorithm
- Verse Similarity Algorithm
- Surah Thematic Structure Algorithm
- Scriptural Narrative Arc Algorithm
