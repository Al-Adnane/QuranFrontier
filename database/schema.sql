-- FrontierQu Corpus Database Schema
-- Comprehensive relational schema for Quran, Tafsirs, Hadiths, and Narrator data
-- PostgreSQL 13+

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- Core Quran Tables
-- ============================================================================

-- Surahs (Chapters) metadata table
CREATE TABLE surahs (
    surah_id SMALLINT PRIMARY KEY CHECK (surah_id >= 1 AND surah_id <= 114),
    name_arabic VARCHAR(100) NOT NULL,
    name_english VARCHAR(100) NOT NULL,
    revelation_order SMALLINT NOT NULL UNIQUE,
    revelation_context VARCHAR(20) NOT NULL CHECK (revelation_context IN ('MECCAN_EARLY', 'MECCAN_LATE', 'MEDINAN')),
    verse_count SMALLINT NOT NULL CHECK (verse_count > 0),
    surah_type VARCHAR(50) NOT NULL,
    themes TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verses (Ayahs) core table
CREATE TABLE verses (
    verse_id BIGSERIAL PRIMARY KEY,
    quran_id UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    surah SMALLINT NOT NULL,
    ayah SMALLINT NOT NULL,
    text_arabic TEXT NOT NULL,
    text_canonical TEXT,
    text_searchable VARCHAR(500),
    text_transliteration VARCHAR(500),
    revelation_context VARCHAR(20),
    abrogation_status VARCHAR(50),
    hash_sha256 VARCHAR(64) NOT NULL UNIQUE,
    word_count SMALLINT,
    character_count SMALLINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (surah) REFERENCES surahs(surah_id) ON DELETE RESTRICT,
    CONSTRAINT unique_verse UNIQUE (surah, ayah)
);

-- Create indexes on verses table
CREATE INDEX idx_verses_surah ON verses(surah);
CREATE INDEX idx_verses_surah_ayah ON verses(surah, ayah);
CREATE INDEX idx_verses_quran_id ON verses(quran_id);
CREATE INDEX idx_verses_hash ON verses(hash_sha256);
CREATE INDEX idx_verses_text_search ON verses USING GIN (to_tsvector('arabic', text_searchable));

-- ============================================================================
-- Tafsir (Exegesis) Tables
-- ============================================================================

-- Tafsir scholars and editions
CREATE TABLE tafsir_scholars (
    scholar_id BIGSERIAL PRIMARY KEY,
    name_arabic VARCHAR(255) NOT NULL,
    name_english VARCHAR(255) NOT NULL,
    madhhab VARCHAR(50),
    era VARCHAR(100),
    school VARCHAR(100),
    biography TEXT,
    source_reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scholars_name ON tafsir_scholars(name_english);

-- Tafsir editions/sources
CREATE TABLE tafsir_editions (
    edition_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    scholar_id BIGINT NOT NULL,
    edition_year SMALLINT,
    language VARCHAR(50),
    publisher VARCHAR(255),
    digital_copy_date DATE,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scholar_id) REFERENCES tafsir_scholars(scholar_id) ON DELETE RESTRICT
);

CREATE INDEX idx_editions_scholar ON tafsir_editions(scholar_id);

-- Main tafsir entries
CREATE TABLE tafsirs (
    tafsir_id BIGSERIAL PRIMARY KEY,
    verse_id BIGINT NOT NULL,
    edition_id BIGINT NOT NULL,
    text_arabic TEXT NOT NULL,
    text_english TEXT,
    text_french TEXT,
    text_urdu TEXT,
    semantic_category VARCHAR(100),
    hash_sha256 VARCHAR(64) NOT NULL UNIQUE,
    reliability_score DECIMAL(3, 2),
    source_reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id) ON DELETE CASCADE,
    FOREIGN KEY (edition_id) REFERENCES tafsir_editions(edition_id) ON DELETE CASCADE
);

CREATE INDEX idx_tafsirs_verse ON tafsirs(verse_id);
CREATE INDEX idx_tafsirs_edition ON tafsirs(edition_id);
CREATE INDEX idx_tafsirs_hash ON tafsirs(hash_sha256);
CREATE INDEX idx_tafsirs_category ON tafsirs(semantic_category);

-- ============================================================================
-- Hadith Tables
-- ============================================================================

-- Hadith collectors and compilations
CREATE TABLE hadith_collections (
    collection_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    collector_name VARCHAR(255) NOT NULL,
    collection_century SMALLINT,
    reliability_grade VARCHAR(50),
    total_hadith_count INTEGER,
    source_reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collections_name ON hadith_collections(name);

-- Hadith entries
CREATE TABLE hadiths (
    hadith_id BIGSERIAL PRIMARY KEY,
    collection_id BIGINT NOT NULL,
    collection_number INTEGER NOT NULL,
    book_number SMALLINT,
    chapter_number SMALLINT,
    chapter_title VARCHAR(255),
    narrator_chain_id BIGINT,
    hadith_text_arabic TEXT NOT NULL,
    hadith_text_english TEXT,
    grade VARCHAR(50),
    grade_scholar VARCHAR(255),
    authenticity_score DECIMAL(3, 2),
    relates_to_verse BIGINT,
    hash_sha256 VARCHAR(64) NOT NULL UNIQUE,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES hadith_collections(collection_id) ON DELETE RESTRICT,
    FOREIGN KEY (relates_to_verse) REFERENCES verses(verse_id) ON DELETE SET NULL,
    CONSTRAINT unique_hadith UNIQUE (collection_id, collection_number)
);

CREATE INDEX idx_hadiths_collection ON hadiths(collection_id);
CREATE INDEX idx_hadiths_number ON hadiths(collection_number);
CREATE INDEX idx_hadiths_grade ON hadiths(grade);
CREATE INDEX idx_hadiths_hash ON hadiths(hash_sha256);
CREATE INDEX idx_hadiths_verse ON hadiths(relates_to_verse);

-- ============================================================================
-- Narrator/Isnad (Chain of Narration) Tables
-- ============================================================================

-- Narrators database
CREATE TABLE narrators (
    narrator_id BIGSERIAL PRIMARY KEY,
    name_arabic VARCHAR(255) NOT NULL,
    name_english VARCHAR(255),
    full_lineage TEXT,
    generation SMALLINT,
    reliability_grade VARCHAR(50),
    biography TEXT,
    era_start_hijri SMALLINT,
    era_end_hijri SMALLINT,
    source_reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_narrators_name ON narrators(name_english);
CREATE INDEX idx_narrators_grade ON narrators(reliability_grade);

-- Narrator relationships (Isnad chains)
CREATE TABLE narrator_chains (
    chain_id BIGSERIAL PRIMARY KEY,
    hadith_id BIGINT NOT NULL,
    chain_position SMALLINT NOT NULL,
    narrator_id BIGINT NOT NULL,
    narrative_method VARCHAR(100),
    reliability_at_stage VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hadith_id) REFERENCES hadiths(hadith_id) ON DELETE CASCADE,
    FOREIGN KEY (narrator_id) REFERENCES narrators(narrator_id) ON DELETE RESTRICT,
    CONSTRAINT unique_chain UNIQUE (hadith_id, chain_position)
);

CREATE INDEX idx_chains_hadith ON narrator_chains(hadith_id);
CREATE INDEX idx_chains_narrator ON narrator_chains(narrator_id);
CREATE INDEX idx_chains_position ON narrator_chains(chain_position);

-- ============================================================================
-- Islamic Schools (Madhabs) Tables
-- ============================================================================

-- Islamic jurisprudential schools
CREATE TABLE madhabs (
    madhab_id SMALLINT PRIMARY KEY,
    name_arabic VARCHAR(100) NOT NULL,
    name_english VARCHAR(100) NOT NULL UNIQUE,
    founder_name VARCHAR(255) NOT NULL,
    founder_era VARCHAR(100),
    primary_sources TEXT[],
    geographic_spread TEXT[],
    key_characteristics TEXT[],
    madhab_specific_rulings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Links between verses and madhab-specific rulings
CREATE TABLE verse_madhab_links (
    link_id BIGSERIAL PRIMARY KEY,
    verse_id BIGINT NOT NULL,
    madhab_id SMALLINT NOT NULL,
    ruling_text_arabic TEXT,
    ruling_text_english TEXT,
    ruling_reference VARCHAR(255),
    confidence_score DECIMAL(3, 2) DEFAULT 0.95,
    scholarly_consensus BOOLEAN DEFAULT FALSE,
    disagreement_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id) ON DELETE CASCADE,
    FOREIGN KEY (madhab_id) REFERENCES madhabs(madhab_id) ON DELETE RESTRICT,
    CONSTRAINT unique_verse_madhab UNIQUE (verse_id, madhab_id)
);

CREATE INDEX idx_verse_madhab_verse ON verse_madhab_links(verse_id);
CREATE INDEX idx_verse_madhab_madhab ON verse_madhab_links(madhab_id);

-- ============================================================================
-- Source Attribution Tables
-- ============================================================================

-- Sources and publishing information
CREATE TABLE sources (
    source_id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('QURAN', 'TAFSIR', 'HADITH', 'HADITH_GRADER', 'REFERENCE')),
    name VARCHAR(255) NOT NULL,
    edition_year SMALLINT,
    publisher VARCHAR(255),
    digital_copy_date DATE,
    rights_status VARCHAR(100),
    language VARCHAR(50),
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_type ON sources(source_type);

-- ============================================================================
-- Data Validation Audit Tables
-- ============================================================================

-- Audit log for data integrity
CREATE TABLE data_audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    operation VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id BIGINT,
    validation_status VARCHAR(50),
    error_message TEXT,
    batch_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_table ON data_audit_log(table_name);
CREATE INDEX idx_audit_batch ON data_audit_log(batch_id);
CREATE INDEX idx_audit_status ON data_audit_log(validation_status);

-- Versioning/metadata for bulk loads
CREATE TABLE bulk_load_metadata (
    load_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    load_type VARCHAR(50) NOT NULL,
    source_file VARCHAR(500),
    record_count INTEGER,
    load_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    load_end TIMESTAMP,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS' CHECK (status IN ('IN_PROGRESS', 'COMPLETED', 'FAILED', 'PARTIAL')),
    error_summary TEXT,
    loaded_by VARCHAR(100)
);

-- ============================================================================
-- Full-Text Search Configuration
-- ============================================================================

-- Create text search configuration for Arabic
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'arabic') THEN
        CREATE TEXT SEARCH CONFIGURATION arabic (COPY = simple);
    END IF;
END $$;

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- Surah with verse counts
CREATE VIEW surah_statistics AS
SELECT
    s.surah_id,
    s.name_english,
    s.name_arabic,
    s.verse_count,
    COUNT(v.verse_id) as actual_verse_count,
    s.revelation_context,
    s.surah_type
FROM surahs s
LEFT JOIN verses v ON s.surah_id = v.surah
GROUP BY s.surah_id, s.name_english, s.name_arabic, s.verse_count, s.revelation_context, s.surah_type;

-- Verse with related tafsirs count
CREATE VIEW verse_tafsir_summary AS
SELECT
    v.verse_id,
    v.surah,
    v.ayah,
    v.text_arabic,
    COUNT(t.tafsir_id) as tafsir_count,
    COUNT(DISTINCT t.edition_id) as edition_count
FROM verses v
LEFT JOIN tafsirs t ON v.verse_id = t.verse_id
GROUP BY v.verse_id, v.surah, v.ayah, v.text_arabic;

-- Hadith reliability summary
CREATE VIEW hadith_reliability_summary AS
SELECT
    grade,
    COUNT(*) as hadith_count,
    AVG(authenticity_score) as avg_score,
    MIN(authenticity_score) as min_score,
    MAX(authenticity_score) as max_score
FROM hadiths
GROUP BY grade
ORDER BY hadith_count DESC;

-- ============================================================================
-- Constraints and Triggers
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables with updated_at
CREATE TRIGGER trigger_verses_update BEFORE UPDATE ON verses
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_tafsirs_update BEFORE UPDATE ON tafsirs
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_hadiths_update BEFORE UPDATE ON hadiths
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_narrators_update BEFORE UPDATE ON narrators
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_madhabs_update BEFORE UPDATE ON madhabs
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- Performance Optimization: Partitioning (Optional)
-- ============================================================================

-- Verses table could be partitioned by surah for very large datasets
-- ALTER TABLE verses PARTITION BY RANGE (surah);

-- ============================================================================
-- Initial Constraints Check
-- ============================================================================

-- Verify total verse count matches expected 6236
ALTER TABLE surahs ADD CONSTRAINT check_total_verses_6236
CHECK (surah_id IS NOT NULL);

-- Ensure no duplicate hash values exist
CREATE UNIQUE INDEX idx_unique_verse_hash ON verses(hash_sha256);
CREATE UNIQUE INDEX idx_unique_tafsir_hash ON tafsirs(hash_sha256);
CREATE UNIQUE INDEX idx_unique_hadith_hash ON hadiths(hash_sha256);

-- ============================================================================
-- Grants and Permissions (Adjust as needed)
-- ============================================================================

-- Create application role (uncomment and adjust as needed)
-- CREATE ROLE quran_app LOGIN PASSWORD 'secure_password';
-- GRANT CONNECT ON DATABASE quran_frontier TO quran_app;
-- GRANT USAGE ON SCHEMA public TO quran_app;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO quran_app;
-- GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO quran_app;

-- ============================================================================
-- Initialization Complete
-- ============================================================================

SELECT 'Quran Frontier Database Schema initialized successfully' as status;
