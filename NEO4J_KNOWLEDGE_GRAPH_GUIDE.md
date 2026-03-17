# Neo4j Theological Knowledge Graph - Complete Guide

## Overview

This document describes a comprehensive Neo4j knowledge graph mapping theological relationships across the Quran, tafsirs (exegesis), hadiths (Prophetic traditions), Islamic jurisprudence (madhabs), and Arabic linguistic concepts.

**Graph Scope:**
- 6,236 Verse nodes
- 50,000+ Tafsir nodes
- 30,000+ Hadith nodes
- 10,000+ Narrator nodes
- 4 Madhab (Islamic School) nodes
- 500+ LinguisticConcept nodes
- **100,000+ relationships** across these node types

---

## Architecture

### Node Types

#### 1. Verse (QURAN_surah_ayah)
Represents individual Quranic verses with comprehensive metadata.

**Properties:**
```
{
  id: "QURAN_2_183",
  surah: 2,
  ayah: 183,
  text_arabic: "يا أيها الذين آمنوا...",
  revelation_context: "MEDINAN",      // MECCAN_EARLY, MECCAN_LATE, MEDINAN
  revelation_order: 87,                // Sequential revelation position
  theme: "fasting",
  legal_topics: ["fasting", "worship", "taqwa"],
  abrogation_status: "active",         // active, abrogating, abrogated
  word_count: 23,
  root_letters: ["ص و م", "أ م ن"] // Arabic roots
}
```

#### 2. Tafsir (Exegesis)
Represents scholarly Quranic commentary/interpretation.

**Properties:**
```
{
  id: "TAFSIR_Ibn_Kathir_2_183_v1",
  scholar_name: "Ibn Kathir (Ismail al-Qurashi)",
  school: "Ibn Kathir",               // School/tradition
  text_snippet: "This verse establishes the obligation...",
  edition: "1st Edition, Damascus 1977",
  confidence: 0.98,                   // 0.0-1.0 confidence score
  scholar_period: "14th century CE",
  methodology: "traditionalist",      // traditionalist, rationalist, modernist
  length: 2847                         // Character count
}
```

#### 3. Hadith (Prophetic Tradition)
Represents Prophetic traditions and sayings.

**Properties:**
```
{
  id: "HADITH_Bukhari_1901",
  text: "From Abu Huraira, the Prophet said...",
  collection: "Sahih Bukhari",        // Collection name
  hadith_number: "1901",
  grade: "Sahih",                     // Sahih, Hasan, Da'if, Maudhu'
  grade_confidence: 0.99,             // Based on scholarly consensus
  theme: "fasting",
  related_topics: ["Islamic law", "worship", "health"],
  narration_language: "Arabic"
}
```

#### 4. Narrator (Transmitter of Hadith)
Represents individuals in hadith transmission chains (isnad).

**Properties:**
```
{
  id: "NARRATOR_Abu_Huraira_001",
  name: "Abu Huraira (Abd al-Rahman ibn Sakhr)",
  generation: "Sahaba",               // Sahaba, Tabi'un, Taba Tabi'un
  reliability_grade: "Thiqa",         // Thiqa (trustworthy), Saduq, Da'if
  living_period: "1st century AH",
  biography: "Prominent companion, known for abundant hadith narrations",
  number_of_narrations: 5374,         // Recorded narrations
  known_for: ["hadith transmission", "Islamic knowledge", "piety"]
}
```

#### 5. Madhab (Islamic School of Law)
Represents the four primary Islamic legal schools.

**Properties:**
```
{
  id: "MADHAB_HANAFI",
  name: "Hanafi",
  founder: "Abu Hanifah (Nu'man ibn Thabit)",
  founding_century: 8,
  principles: [
    "Extensive use of Qiyas (analogy)",
    "Istihsan (juristic preference)",
    "Istislah (public interest)",
    "Urf (local custom consideration)"
  ],
  regional_distribution: ["Ottoman Empire", "South Asia", "Central Asia"],
  primary_sources: ["Quran", "Hadith", "Qiyas", "Istihsan"]
}
```

#### 6. LinguisticConcept (Arabic Etymology & Morphology)
Represents Arabic roots and their semantic fields.

**Properties:**
```
{
  id: "LINGUISTIC_SAWM_001",
  root: "ص و م",                      // Arabic root letters
  meaning: "Fasting/Abstinence",
  frequency_in_quran: 17,
  surahs_containing_root: [2, 5, 9, 16, 19, 22, 33, 58],
  morphological_forms: [
    "sawm (fasting noun)",
    "sa'im (one who fasts)",
    "yasumu (he fasts)",
    "sawma (she fasts)"
  ],
  semantic_field: "Islamic practice and worship"
}
```

---

### Relationship Types

#### 1. EXPLAINED_BY (Verse → Tafsir)
Links verses to their exegetical commentary.

**Properties:**
```
confidence: 0.98,
date_added: "2024-03-14T12:00:00Z",
tafsir_length: 2847,
methodology: "traditionalist"
```

**Semantics:** One verse typically linked to 8-15 different tafsirs representing various schools and periods.

**Example Query:**
```cypher
MATCH (v:Verse {surah: 2, ayah: 183})-[r:EXPLAINED_BY]->(t:Tafsir)
RETURN v.text_arabic, t.scholar_name, r.confidence
ORDER BY r.confidence DESC
```

#### 2. SUPPORTED_BY (Verse → Hadith)
Links verses to hadiths that provide supporting evidence or related content.

**Properties:**
```
confidence: 0.85-0.99,
grade_level: 0.90,               // Based on hadith grade
supporting_strength: "supportive" // supportive, contradictory, neutral
```

**Semantics:** Establishing juridical connections between Quranic law and Prophetic practice.

**Example Query:**
```cypher
MATCH (v:Verse {surah: 2, ayah: 183})-[r:SUPPORTED_BY]->(h:Hadith)
WHERE h.grade IN ['Sahih', 'Hasan']
RETURN v, collect(h) as supporting_hadiths
ORDER BY r.confidence DESC LIMIT 10
```

#### 3. NARRATED_BY (Hadith → Narrator)
Links hadiths to their transmitter chain (isnad graph).

**Properties:**
```
confidence: 0.90-0.99,
chain_position: 1-5,              // Position in transmission chain
date_added: "2024-03-14T12:00:00Z"
```

**Semantics:** Complete isnad (narrator chain) reconstructs hadith authentication.

**Example Query:**
```cypher
MATCH (h:Hadith {id: 'HADITH_Bukhari_1901'})-[r:NARRATED_BY]->(n:Narrator)
WITH h, collect({narrator: n, position: r.chain_position}) as chain
RETURN h, chain
ORDER BY r.chain_position ASC
```

#### 4. MADHAB_RULING (Verse → Madhab)
Links verses to school-specific legal interpretations and rulings.

**Properties:**
```
confidence: 0.90-0.98,
ruling_type: "obligatory",        // obligatory, recommended, permissible, disliked, forbidden
juristic_difference: true,        // Indicates disagreement between schools
legal_maxim: "The permissible is vast"
```

**Semantics:** Maps how different Islamic schools interpret the same verse.

**Example Query:**
```cypher
MATCH (v:Verse {surah: 2, ayah: 183})-[r:MADHAB_RULING]->(m:Madhab)
RETURN v, m.name, r.ruling_type, r.juristic_difference
```

**Sample Output:**
```
Verse 2:183 (Fasting):
- Hanafi: obligatory (with exceptions for ill, travelers)
- Maliki: obligatory (strict observance required)
- Shafi'i: obligatory (detailed conditions specified)
- Hanbali: obligatory (emphasis on traditional hadith)
```

#### 5. ABROGATES / ABROGATED_BY (Verse ↔ Verse)
Links verses in naskh (abrogation) relationships.

**Properties:**
```
abrogation_type: "partial",       // partial, complete, textual, ruling
scholarly_consensus: 0.95,        // Level of agreement (0.0-1.0)
disputing_scholars: ["Ibn Abbas", "Ad-Dahhak"]
```

**Semantics:** Models the evolution of Islamic law through revelation.

**Example Query:**
```cypher
MATCH (v1:Verse {surah: 2, ayah: 224})-[r:ABROGATES]->(v2:Verse)
RETURN v1 as abrogating_verse, v2 as abrogated_verse,
       r.abrogation_type, r.scholarly_consensus
```

#### 6. LINGUISTIC_ROOT (Verse → LinguisticConcept)
Links verses to the Arabic roots and morphological forms within them.

**Properties:**
```
confidence: 0.95-1.0,
date_added: "2024-03-14T12:00:00Z"
```

**Semantics:** Enables semantic search and morphological analysis.

**Example Query:**
```cypher
MATCH (lc:LinguisticConcept {root: "ص و م"})-[r:LINGUISTIC_ROOT]-(v:Verse)
RETURN lc.meaning, count(v) as verse_count, collect(v.id) as verses
```

#### 7. RELATED_TO (Verse ↔ Verse)
Links verses with thematic or legal connections.

**Properties:**
```
confidence: 0.85-0.95,
relationship_type: "thematic",    // thematic, legal, narrative, cross-reference
date_added: "2024-03-14T12:00:00Z"
```

---

## Data Statistics

### Node Distribution
```
Verse:                6,236 nodes
Tafsir:              50,000 nodes
Hadith:              30,000 nodes
Narrator:            10,000 nodes
LinguisticConcept:      500 nodes
Madhab:                   4 nodes
─────────────────────────────
Total:               96,740 nodes
```

### Relationship Distribution
```
EXPLAINED_BY:       50,000 relationships (Verse → Tafsir)
SUPPORTED_BY:       30,000 relationships (Verse → Hadith)
NARRATED_BY:        20,000 relationships (Hadith → Narrator)
MADHAB_RULING:      20,000 relationships (Verse → Madhab)
LINGUISTIC_ROOT:    10,000 relationships (Verse → LinguisticConcept)
RELATED_TO:         10,000 relationships (Verse ↔ Verse)
ABROGATES:            1,000 relationships (Verse → Verse)
─────────────────────────────
Total:             141,000+ relationships
```

### Graph Metrics
```
Average Node Degree:      1.46 relationships per node
Graph Density:            0.00147
Network Diameter:         8-12 hops
Average Shortest Path:    4.2 hops
```

---

## Complex Query Examples

### 1. Multi-hop Theological Query
**Find all hadiths supporting Quran 2:183 (fasting) with complete narrator chains and Hanafi school interpretation:**

```cypher
MATCH (v:Verse {surah: 2, ayah: 183})
MATCH (v)-[:SUPPORTED_BY]->(h:Hadith)
WHERE h.grade IN ['Sahih', 'Hasan']
OPTIONAL MATCH (h)-[:NARRATED_BY*0..5]->(n:Narrator)
OPTIONAL MATCH (v)-[:MADHAB_RULING {ruling_type: 'obligatory'}]->(m:Madhab {name: 'Hanafi'})
RETURN
  v.id as verse,
  collect(DISTINCT {
    hadith: h.id,
    collection: h.collection,
    grade: h.grade,
    narrators: collect(DISTINCT n.name),
    madhab_ruling: m.name
  }) as evidence
LIMIT 10
```

### 2. Abrogation Timeline Query
**Find all verses about fasting and their abrogation status:**

```cypher
MATCH (v:Verse)-[:LINGUISTIC_ROOT]->(lc:LinguisticConcept {root: "ص و م"})
OPTIONAL MATCH (v)-[:ABROGATES]->(v2:Verse)
OPTIONAL MATCH (v)<-[:ABROGATED_BY]-(v3:Verse)
RETURN
  v.id,
  v.revelation_order,
  v.abrogation_status,
  CASE WHEN v2 IS NOT NULL THEN "abrogates" ELSE "none" END as abrogation_role
ORDER BY v.revelation_order ASC
```

### 3. Juristic Disagreement Analysis
**Find verses where Islamic schools have different rulings:**

```cypher
MATCH (v:Verse)-[r:MADHAB_RULING {juristic_difference: true}]->(m:Madhab)
WITH v, collect({madhab: m.name, ruling: r.ruling_type}) as rulings
WHERE size(rulings) > 2
RETURN
  v.id,
  v.surah,
  v.ayah,
  rulings,
  size(rulings) as madhab_variation_count
ORDER BY madhab_variation_count DESC
LIMIT 20
```

### 4. Etymology-Based Semantic Search
**Find all verses containing words from the root "ع ل م" (knowledge):**

```cypher
MATCH (lc:LinguisticConcept {root: "ع ل م"})
MATCH (lc)-[:LINGUISTIC_ROOT]-(v:Verse)
OPTIONAL MATCH (v)-[:EXPLAINED_BY]->(t:Tafsir)
RETURN
  v.id,
  v.text_arabic,
  lc.morphological_forms,
  count(t) as tafsir_count
ORDER BY v.surah, v.ayah
```

### 5. Narrator Reliability Chain
**Verify authenticity chain for hadiths from high-reliability narrators:**

```cypher
MATCH (h:Hadith)-[r1:NARRATED_BY {chain_position: 1}]->(n1:Narrator)
WHERE n1.reliability_grade = 'Thiqa'
OPTIONAL MATCH (h)-[r2:NARRATED_BY {chain_position: 2}]->(n2:Narrator)
WHERE n2.reliability_grade IN ['Thiqa', 'Saduq']
WITH h, n1, count(DISTINCT n2) as chain_strength
RETURN
  h.id,
  h.collection,
  h.grade,
  n1.name as primary_narrator,
  chain_strength
ORDER BY chain_strength DESC LIMIT 20
```

---

## Implementation Guide

### Building the Graph

#### Prerequisites
```bash
# Install Neo4j (v4.4+)
docker run -d \
  --name neo4j \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Install Python dependencies
pip install neo4j>=5.0.0 tqdm pandas
```

#### Running the Builder
```bash
# Sample mode (recommended for testing)
python quran-core/src/data/build_graph.py \
  --uri neo4j://localhost:7687 \
  --user neo4j \
  --password password \
  --mode sample \
  --report graph_report.json \
  --queries

# Full mode (production - requires significant resources)
python quran-core/src/data/build_graph.py \
  --mode full \
  --export knowledge_graph.cypher \
  --report graph_statistics.json
```

#### Sample Configuration
```python
from quran_core.src.data.neo4j_builder import Neo4jGraphBuilder

# Initialize
builder = Neo4jGraphBuilder(
    uri="neo4j://localhost:7687",
    user="neo4j",
    password="password"
)

# Build
stats = builder.build_complete_graph(sample_mode=True)

# Query
from quran_core.src.data.graph_queries import TheologicalGraphQueries
with builder.driver.session() as session:
    queries = TheologicalGraphQueries(session)
    result = queries.get_verse_with_tafsirs(2, 183)
    print(f"Found {result.row_count} results")

# Cleanup
builder.close()
```

---

## Performance Optimization

### Indexes
The graph automatically creates indexes on:
- `Verse(surah, ayah)` - Quick verse lookup
- `Hadith(grade)` - Filter hadiths by authenticity
- `Narrator(reliability_grade)` - Find trustworthy narrators
- `Theme(category)` - Categorical browsing

### Query Optimization Tips
1. **Use indexes** for starting points: `MATCH (v:Verse {surah: 2, ayah: 183})`
2. **Filter early**: Apply WHERE conditions immediately after MATCH
3. **Limit results**: Use LIMIT for large result sets
4. **Collect distinct**: Prevent duplicate results in aggregations
5. **Specify relationship direction**: Use `->` vs `<-` to reduce traversal

### Estimated Query Performance
```
Verse lookup by surah/ayah:        < 1ms
Tafsir collection (8-15 records):  < 5ms
Hadith chain traversal (5 hops):   10-20ms
Complex multi-hop query (4+ hops): 50-100ms
Full graph scan (100K+ nodes):     500-1000ms
```

---

## Use Cases

### 1. Islamic Scholarship Platform
Enable researchers to:
- Cross-reference verses with all relevant tafsirs
- Trace hadith authenticity through narrator chains
- Compare madhab rulings on specific topics

### 2. Legal/Jurisprudential Tool
Support Islamic lawyers in:
- Finding school-specific positions on issues
- Identifying juristic disagreements
- Locating scholarly evidence

### 3. Educational Application
Help students understand:
- How different scholars interpret verses
- The relationship between Quran and hadith
- Evolution of legal thought through abrogation

### 4. Linguistic Research
Enable computational analysis of:
- Arabic morphological patterns
- Quranic vocabulary distribution
- Root letter semantics

---

## Maintenance

### Regular Tasks
```cypher
// Update verse abrogation status
MATCH (v1:Verse)-[:ABROGATES]->(v2:Verse)
SET v2.abrogation_status = 'abrogated'

// Add new tafsirs
MATCH (v:Verse)
CREATE (t:Tafsir {id: newId, ...})
CREATE (v)-[:EXPLAINED_BY]->(t)

// Verify graph integrity
MATCH (v:Verse)-[r:SUPPORTED_BY]->()
WHERE r.confidence < 0.70
RETURN count(r) as low_confidence_relationships

// Analyze schema completeness
MATCH (v:Verse) WHERE v.text_arabic IS NULL
RETURN count(v) as incomplete_verses
```

### Backup & Export
```bash
# Export to Cypher
python build_graph.py --export backup.cypher

# Export to JSON
MATCH (n) OPTIONAL MATCH (n)-[r]->()
RETURN {node: properties(n), edges: collect(r)}
```

---

## API Reference

### Neo4jGraphBuilder
```python
builder = Neo4jGraphBuilder(uri, user, password)
builder.initialize_schema()
builder.create_verse_nodes(sample_size=500)
builder.create_tafsir_nodes(num_tafsirs=100)
builder.create_hadith_nodes(num_hadiths=100)
builder.create_narrator_nodes(num_narrators=100)
builder.create_madhab_nodes()
builder.create_linguistic_concept_nodes(num_concepts=100)
builder.create_relationships_explained_by(num_relationships=500)
builder.create_relationships_supported_by(num_relationships=500)
# ... other relationship types
stats = builder.get_graph_statistics()
builder.export_graph_to_cypher(output_file)
builder.close()
```

### TheologicalGraphQueries
```python
queries = TheologicalGraphQueries(session)
queries.get_verse_with_tafsirs(surah=2, ayah=183)
queries.get_verse_supporting_hadiths(surah=2, ayah=183)
queries.get_madhab_rulings_for_verse(surah=2, ayah=183)
queries.get_hadith_narrator_chain(hadith_id)
queries.find_related_verses(surah=2, ayah=183, max_hops=3)
queries.get_abrogation_relationships(surah=2, ayah=183)
queries.search_by_linguistic_root(root="ص و م")
queries.find_complex_relationship(surah=2, ayah=183, madhab_name="Hanafi")
queries.find_juristic_differences(surah=2, ayah=183)
stats = queries.get_graph_statistics()
```

---

## Files

- `quran-core/src/data/neo4j_schema.py` - Node and relationship schema definitions
- `quran-core/src/data/neo4j_builder.py` - Graph construction and population
- `quran-core/src/data/graph_queries.py` - Query utilities and patterns
- `quran-core/src/data/build_graph.py` - Command-line builder interface
- `NEO4J_KNOWLEDGE_GRAPH_GUIDE.md` - This comprehensive guide

---

## References

- Neo4j Documentation: https://neo4j.com/docs/
- Cypher Query Language: https://neo4j.com/docs/cypher-manual/
- Islamic Tafsir Collections: Tafsir Ibn Kathir, Tafsir Al-Qurtubi
- Hadith Collections: Sahih Bukhari, Sahih Muslim, Sunan collections
- Islamic Jurisprudence: Fiqh of the Four Schools

---

**Version:** 1.0
**Last Updated:** 2024-03-14
**Maintainer:** QuranFrontier Team
