/**
 * Neo4j Schema for Quranic Knowledge Graph
 * Defines all constraints, indexes, and node/relationship types
 */

// ============================================================================
// CONSTRAINTS
// ============================================================================

// Unique constraint on verse_key - ensures no duplicate verses
CREATE CONSTRAINT verse_key_unique IF NOT EXISTS ON (v:Verse) ASSERT v.verse_key IS UNIQUE;

// Tafsir uniqueness - source + verse combination
CREATE CONSTRAINT tafsir_unique IF NOT EXISTS ON (t:Tafsir) ASSERT (t.source, t.verse_key) IS UNIQUE;


// ============================================================================
// INDEXES - VERSE NODES
// ============================================================================

// Index for fast surah lookup
CREATE INDEX verse_surah IF NOT EXISTS ON (v:Verse) FOR (v.surah);

// Index for ayah (verse number within surah)
CREATE INDEX verse_ayah IF NOT EXISTS ON (v:Verse) FOR (v.ayah);

// Index for confidence scores - useful for ranking queries
CREATE INDEX verse_confidence IF NOT EXISTS ON (v:Verse) FOR (v.confidence_score);

// Full-text index on translations for semantic search
CREATE TEXT INDEX verse_translation IF NOT EXISTS ON (v:Verse) FOR (v.translation);

// Full-text index on Arabic text for linguistic analysis
CREATE TEXT INDEX verse_arabic IF NOT EXISTS ON (v:Verse) FOR (v.arabic_text);


// ============================================================================
// INDEXES - DOMAIN CONCEPT NODES
// ============================================================================

// Physics concepts
CREATE INDEX physics_concept IF NOT EXISTS ON (p:PhysicsConcept) FOR (p.name);
CREATE INDEX physics_confidence IF NOT EXISTS ON (p:PhysicsConcept) FOR (p.confidence);
CREATE INDEX physics_verse IF NOT EXISTS ON (p:PhysicsConcept) FOR (p.verse_key);

// Biology concepts
CREATE INDEX biology_concept IF NOT EXISTS ON (b:BiologyConcept) FOR (b.name);
CREATE INDEX biology_confidence IF NOT EXISTS ON (b:BiologyConcept) FOR (b.confidence);
CREATE INDEX biology_verse IF NOT EXISTS ON (b:BiologyConcept) FOR (b.verse_key);

// Medicine concepts
CREATE INDEX medicine_concept IF NOT EXISTS ON (m:MedicineConcept) FOR (m.name);
CREATE INDEX medicine_confidence IF NOT EXISTS ON (m:MedicineConcept) FOR (m.confidence);
CREATE INDEX medicine_verse IF NOT EXISTS ON (m:MedicineConcept) FOR (m.verse_key);

// Engineering concepts
CREATE INDEX engineering_concept IF NOT EXISTS ON (e:EngineeringConcept) FOR (e.name);
CREATE INDEX engineering_confidence IF NOT EXISTS ON (e:EngineeringConcept) FOR (e.confidence);
CREATE INDEX engineering_verse IF NOT EXISTS ON (e:EngineeringConcept) FOR (e.verse_key);

// Agriculture concepts
CREATE INDEX agriculture_concept IF NOT EXISTS ON (a:AgricultureConcept) FOR (a.name);
CREATE INDEX agriculture_confidence IF NOT EXISTS ON (a:AgricultureConcept) FOR (a.confidence);
CREATE INDEX agriculture_verse IF NOT EXISTS ON (a:AgricultureConcept) FOR (a.verse_key);


// ============================================================================
// INDEXES - TAFSIR NODES
// ============================================================================

// Tafsir source indexing for interpretation lookup
CREATE INDEX tafsir_source IF NOT EXISTS ON (t:Tafsir) FOR (t.source);

// Tafsir verse key for fast retrieval
CREATE INDEX tafsir_verse IF NOT EXISTS ON (t:Tafsir) FOR (t.verse_key);

// Tafsir category for classification
CREATE INDEX tafsir_category IF NOT EXISTS ON (t:Tafsir) FOR (t.category);

// Full-text index on tafsir text
CREATE TEXT INDEX tafsir_text IF NOT EXISTS ON (t:Tafsir) FOR (t.text);


// ============================================================================
// INDEXES - SCIENTIFIC PRINCIPLE NODES
// ============================================================================

// Scientific principle name lookup
CREATE INDEX principle_name IF NOT EXISTS ON (s:ScientificPrinciple) FOR (s.name);

// Scientific principle domain classification
CREATE INDEX principle_domain IF NOT EXISTS ON (s:ScientificPrinciple) FOR (s.domain);


// ============================================================================
// NODE STRUCTURES
// ============================================================================

/**
 * (:Verse) - Represents a single Quranic verse
 *
 * Properties:
 *   - surah: int - Chapter number (1-114)
 *   - ayah: int - Verse number within surah
 *   - verse_key: string - Unique identifier like "1:1" (indexed, unique)
 *   - arabic_text: string - Original Arabic text of verse
 *   - translation: string - English translation
 *   - transliteration: string - Transliteration
 *   - physics_concepts: string - List of physics concepts (stringified)
 *   - biology_concepts: string - List of biology concepts (stringified)
 *   - medicine_concepts: string - List of medicine concepts (stringified)
 *   - engineering_concepts: string - List of engineering concepts (stringified)
 *   - agriculture_concepts: string - List of agriculture concepts (stringified)
 *   - confidence_score: float - Overall confidence in extraction (0.0-1.0)
 *   - created_at: string - ISO timestamp of ingestion
 */

/**
 * (:PhysicsConcept) - Physics domain concept extracted from verse
 * (:BiologyConcept) - Biology domain concept extracted from verse
 * (:MedicineConcept) - Medicine domain concept extracted from verse
 * (:EngineeringConcept) - Engineering domain concept extracted from verse
 * (:AgricultureConcept) - Agriculture domain concept extracted from verse
 *
 * Properties:
 *   - name: string - Concept name/label (indexed)
 *   - verse_key: string - Reference to verse containing concept
 *   - confidence: float - Confidence in extraction (0.0-1.0)
 *   - domain: string - Domain identifier
 *   - created_at: string - ISO timestamp
 */

/**
 * (:Tafsir) - Classical tafsir interpretation of a verse
 *
 * Properties:
 *   - source: string - Source scholar (e.g., "Ibn Kathir", "Al-Tabari")
 *   - name: string - Tafsir name
 *   - verse_key: string - Verse being interpreted
 *   - text: string - Interpretation text
 *   - category: string - Category (e.g., "classical", "contemporary")
 *   - created_at: string - ISO timestamp
 */

/**
 * (:ScientificPrinciple) - General scientific principle
 *
 * Properties:
 *   - name: string - Principle name
 *   - domain: string - Scientific domain
 *   - description: string - Description
 *   - created_at: string - ISO timestamp
 */


// ============================================================================
// RELATIONSHIP TYPES
// ============================================================================

/**
 * (Verse)-[:NEXT_VERSE]->(Verse)
 * Sequential relationship between consecutive verses
 * Used for navigating surah order
 */

/**
 * (Verse)-[:SAME_SURAH]->(Verse)
 * Relationship between verses in same chapter
 * Used for finding related verses within chapter
 */

/**
 * (Verse)-[:CONTAINS_CONCEPT]->(Concept)
 * Verse contains a specific scientific concept
 * Direction: Verse → Concept (what does verse contain?)
 */

/**
 * (Concept)-[:APPEARS_IN]->(Verse)
 * Concept appears in a specific verse
 * Direction: Concept → Verse (where does concept appear?)
 */

/**
 * (Tafsir)-[:INTERPRETS]->(Verse)
 * Tafsir provides interpretation of verse
 * Direction: Tafsir → Verse
 */

/**
 * (Tafsir)-[:SIMILAR_TO]->(Tafsir)
 * Two tafsirs provide similar interpretations
 * Suggests semantic agreement between scholars
 */

/**
 * (ScientificPrinciple)-[:REFERENCED_IN]->(Verse)
 * Scientific principle is referenced/discussed in verse
 * Direction: Principle → Verse
 */

/**
 * (PhysicsConcept)-[:RELATED_TO]->(BiologyConcept)
 * Cross-domain relationships (e.g., physics of cellular processes)
 * Enables cross-domain semantic queries
 */


// ============================================================================
// QUERY TEMPLATES FOR COMMON OPERATIONS
// ============================================================================

// Find all verses in a surah
// MATCH (v:Verse {surah: 1}) RETURN v ORDER BY v.ayah;

// Find verses containing specific concept
// MATCH (c:PhysicsConcept {name: "light"})-[:APPEARS_IN]->(v:Verse) RETURN v;

// Find tafsirs for a verse
// MATCH (t:Tafsir)-[:INTERPRETS]->(v:Verse {verse_key: "1:1"}) RETURN t;

// Find related verses (same concepts)
// MATCH (v1:Verse {verse_key: "1:1"})-[:CONTAINS_CONCEPT]->(c)-[:APPEARS_IN]->(v2:Verse)
// WHERE v1 <> v2 RETURN v2, count(c) as shared_concepts ORDER BY shared_concepts DESC;

// Find verses by confidence threshold
// MATCH (v:Verse) WHERE v.confidence_score >= 0.85 RETURN v;

// Cross-domain semantic analysis
// MATCH (p:PhysicsConcept)-[:APPEARS_IN]->(v:Verse)<-[:APPEARS_IN]-(b:BiologyConcept)
// RETURN v, p, b;
