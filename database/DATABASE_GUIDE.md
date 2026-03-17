# FrontierQu Corpus Database Guide

## Overview

The FrontierQu Corpus Database is a comprehensive PostgreSQL relational database containing:
- **6,236 Quranic verses** with Arabic text, transliteration, and metadata
- **50,000+ Tafsir entries** from major Islamic scholars
- **30,000+ Hadith records** from authenticated collections
- **10,000+ Narrator entries** with isnad (chain of narration) data
- **4 major Islamic schools** (madhabs) with verse-to-ruling mappings

## Database Architecture

### Core Tables

#### Surahs Table
Stores chapter-level metadata for the 114 surahs of the Quran.

```sql
SELECT * FROM surahs WHERE surah_id = 2;
```

**Fields:**
- `surah_id`: Primary key (1-114)
- `name_arabic`: Arabic chapter name
- `name_english`: English transliteration
- `revelation_order`: Order of revelation (chronological)
- `revelation_context`: MECCAN_EARLY, MECCAN_LATE, or MEDINAN
- `verse_count`: Number of verses in the chapter
- `themes`: Array of thematic tags
- `surah_type`: foundational, legislative, narrative, theological, eschatological

#### Verses Table
Core table containing all 6,236 Quranic verses.

```sql
-- Query all verses from Surah Al-Baqarah
SELECT verse_id, surah, ayah, text_arabic
FROM verses
WHERE surah = 2
ORDER BY ayah;

-- Should return 286 rows
SELECT COUNT(*) FROM verses WHERE surah = 2;
```

**Fields:**
- `verse_id`: Unique identifier (BIGSERIAL)
- `quran_id`: UUID for external references
- `surah`: Foreign key to surahs table
- `ayah`: Verse number within surah
- `text_arabic`: Full Arabic text with diacritics
- `text_canonical`: Standardized text
- `text_searchable`: Full-text search format
- `hash_sha256`: Content hash for deduplication
- `word_count`: Number of words
- `character_count`: Number of characters

**Indexes:**
```sql
CREATE INDEX idx_verses_surah ON verses(surah);
CREATE INDEX idx_verses_surah_ayah ON verses(surah, ayah);
CREATE INDEX idx_verses_quran_id ON verses(quran_id);
CREATE INDEX idx_verses_text_search ON verses USING GIN (to_tsvector('arabic', text_searchable));
```

### Tafsir Tables

#### Tafsir Scholars Table
Contains metadata about Islamic scholars and exegetes.

```sql
SELECT name_english, madhhab, school
FROM tafsir_scholars
ORDER BY name_english;
```

#### Tafsir Editions Table
Maps scholars to specific tafsir editions and compilations.

```sql
SELECT te.name, ts.name_english, te.edition_year
FROM tafsir_editions te
JOIN tafsir_scholars ts ON te.scholar_id = ts.scholar_id;
```

#### Tafsirs Table
Main table containing exegesis entries.

```sql
-- Get tafsirs for a specific verse
SELECT t.text_arabic, ts.name_english, t.reliability_score
FROM tafsirs t
JOIN tafsir_editions te ON t.edition_id = te.edition_id
JOIN tafsir_scholars ts ON te.scholar_id = ts.scholar_id
WHERE t.verse_id = (SELECT verse_id FROM verses WHERE surah = 1 AND ayah = 1)
ORDER BY t.reliability_score DESC;

-- Count tafsirs per verse
SELECT COUNT(DISTINCT verse_id) as verses_with_tafsirs
FROM tafsirs;
```

### Hadith Tables

#### Hadith Collections Table
Stores information about hadith compilations (Sahih Bukhari, Muslim, etc.).

```sql
SELECT name, collector_name, total_hadith_count
FROM hadith_collections
ORDER BY total_hadith_count DESC;
```

#### Hadiths Table
Contains individual hadith records with authenticity grades.

```sql
-- Get hadiths by grade
SELECT grade, COUNT(*) as count
FROM hadiths
GROUP BY grade
ORDER BY count DESC;

-- Sample sahih (authentic) hadith
SELECT h.collection_number, h.hadith_text_arabic, h.grade
FROM hadiths h
JOIN hadith_collections hc ON h.collection_id = hc.collection_id
WHERE h.grade = 'Sahih'
LIMIT 1;
```

**Authenticity Grades:**
- Sahih (Authentic)
- Hasan (Good/Fair)
- Daif (Weak)
- Mawdu (Fabricated)

#### Narrator Tables

```sql
-- Get narrator by name
SELECT name_arabic, reliability_grade, biography
FROM narrators
WHERE name_english = 'Abu Hurairah';

-- Find narrator chains for a hadith
SELECT nc.chain_position, n.name_english, n.reliability_grade
FROM narrator_chains nc
JOIN narrators n ON nc.narrator_id = n.narrator_id
WHERE nc.hadith_id = 1
ORDER BY nc.chain_position;
```

### Islamic Schools (Madhabs) Tables

#### Madhabs Table
Stores information about the four major Islamic jurisprudential schools.

```sql
SELECT madhab_id, name_english, founder_name
FROM madhabs;
```

**Madhabs:**
1. Hanafi - Abu Hanifa al-Nu'man
2. Maliki - Malik ibn Anas
3. Shafi'i - Muhammad ibn Idris al-Shafi'i
4. Hanbali - Ahmad ibn Hanbal

#### Verse-Madhab Links Table
Maps verses to madhab-specific rulings and interpretations.

```sql
-- Get madhab-specific rulings for a verse
SELECT m.name_english, vml.ruling_text_english, vml.confidence_score
FROM verse_madhab_links vml
JOIN madhabs m ON vml.madhab_id = m.madhab_id
WHERE vml.verse_id = (SELECT verse_id FROM verses WHERE surah = 2 AND ayah = 180)
ORDER BY m.name_english;
```

## Common Queries

### 1. Verse Lookup with Full Context

```sql
SELECT
    s.name_english as surah,
    v.ayah,
    v.text_arabic,
    COUNT(DISTINCT t.tafsir_id) as tafsir_count,
    COUNT(DISTINCT h.hadith_id) as related_hadiths
FROM verses v
LEFT JOIN surahs s ON v.surah = s.surah_id
LEFT JOIN tafsirs t ON v.verse_id = t.verse_id
LEFT JOIN hadiths h ON h.relates_to_verse = v.verse_id
WHERE v.surah = 2 AND v.ayah = 255  -- Ayat Al-Kursi
GROUP BY s.name_english, v.ayah, v.text_arabic;
```

### 2. Surah Statistics

```sql
SELECT
    s.surah_id,
    s.name_english,
    s.verse_count,
    COUNT(DISTINCT v.verse_id) as actual_count,
    COUNT(DISTINCT t.tafsir_id) as tafsir_entries,
    s.revelation_context
FROM surahs s
LEFT JOIN verses v ON s.surah_id = v.surah
LEFT JOIN tafsirs t ON v.verse_id = t.verse_id
GROUP BY s.surah_id, s.name_english, s.verse_count, s.revelation_context
ORDER BY s.surah_id;
```

### 3. Tafsir Coverage Analysis

```sql
SELECT
    ts.name_english as scholar,
    COUNT(DISTINCT t.verse_id) as verses_covered,
    AVG(t.reliability_score) as avg_reliability,
    COUNT(*) as total_entries
FROM tafsirs t
JOIN tafsir_editions te ON t.edition_id = te.edition_id
JOIN tafsir_scholars ts ON te.scholar_id = ts.scholar_id
GROUP BY ts.name_english
ORDER BY verses_covered DESC;
```

### 4. Hadith Quality Assessment

```sql
SELECT
    hc.name as collection,
    h.grade,
    COUNT(*) as count,
    AVG(h.authenticity_score) as avg_score,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY hc.name), 2) as percentage
FROM hadiths h
JOIN hadith_collections hc ON h.collection_id = hc.collection_id
GROUP BY hc.name, h.grade
ORDER BY hc.name, count DESC;
```

### 5. Madhab-Specific Rulings Comparison

```sql
SELECT
    m1.name_english as madhab_1,
    m2.name_english as madhab_2,
    COUNT(DISTINCT v.verse_id) as verses_with_both_rulings
FROM verse_madhab_links vml1
JOIN madhabs m1 ON vml1.madhab_id = m1.madhab_id
JOIN verse_madhab_links vml2 ON vml1.verse_id = vml2.verse_id
JOIN madhabs m2 ON vml2.madhab_id = m2.madhab_id
JOIN verses v ON vml1.verse_id = v.verse_id
WHERE m1.madhab_id < m2.madhab_id
GROUP BY m1.name_english, m2.name_english
ORDER BY verses_with_both_rulings DESC;
```

### 6. Full-Text Search on Verses

```sql
-- Search for verses about "mercy" in Arabic
SELECT v.surah, v.ayah, v.text_arabic
FROM verses v
WHERE to_tsvector('arabic', v.text_searchable) @@ plainto_tsquery('arabic', 'رحمة')
LIMIT 10;
```

### 7. Data Quality Checks

```sql
-- Verify total verse count
SELECT COUNT(*) as total_verses FROM verses;  -- Should be 6236

-- Check for missing surahs
SELECT surah_id FROM surahs
WHERE surah_id NOT IN (SELECT DISTINCT surah FROM verses);

-- Verify verse counts per surah match metadata
SELECT
    surah,
    COUNT(*) as actual_count,
    s.verse_count as expected_count,
    CASE
        WHEN COUNT(*) = s.verse_count THEN 'OK'
        ELSE 'MISMATCH'
    END as status
FROM verses v
JOIN surahs s ON v.surah = s.surah_id
GROUP BY surah, s.verse_count
ORDER BY surah;

-- Find duplicate hashes
SELECT hash_sha256, COUNT(*)
FROM verses
GROUP BY hash_sha256
HAVING COUNT(*) > 1;
```

### 8. Narrator Chain Analysis

```sql
-- Most frequently appearing narrators in hadith chains
SELECT
    n.name_english,
    n.reliability_grade,
    COUNT(*) as appearances,
    COUNT(DISTINCT nc.hadith_id) as unique_hadiths
FROM narrator_chains nc
JOIN narrators n ON nc.narrator_id = n.narrator_id
GROUP BY n.name_english, n.reliability_grade
ORDER BY appearances DESC
LIMIT 20;
```

## Data Validation

### Foreign Key Integrity

```sql
-- Verify all verse foreign keys
SELECT COUNT(*) as invalid_verses
FROM verses v
WHERE NOT EXISTS (SELECT 1 FROM surahs s WHERE s.surah_id = v.surah);

-- Verify all tafsir foreign keys
SELECT COUNT(*) as invalid_tafsirs
FROM tafsirs t
WHERE NOT EXISTS (SELECT 1 FROM verses v WHERE v.verse_id = t.verse_id);

-- Verify hadith collection references
SELECT COUNT(*) as invalid_hadiths
FROM hadiths h
WHERE NOT EXISTS (SELECT 1 FROM hadith_collections hc WHERE hc.collection_id = h.collection_id);
```

### NULL Constraint Verification

```sql
-- Check for required fields
SELECT
    'verses' as table_name,
    COUNT(*) as null_count
FROM verses
WHERE text_arabic IS NULL OR surah IS NULL OR ayah IS NULL
UNION ALL
SELECT
    'hadiths',
    COUNT(*)
FROM hadiths
WHERE hadith_text_arabic IS NULL OR collection_id IS NULL
UNION ALL
SELECT
    'tafsirs',
    COUNT(*)
FROM tafsirs
WHERE text_arabic IS NULL OR verse_id IS NULL;
```

## Performance Tuning

### Index Usage

```sql
-- View all indexes on corpus tables
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('verses', 'tafsirs', 'hadiths', 'narrators')
ORDER BY tablename, indexname;

-- Analyze index efficiency
EXPLAIN ANALYZE
SELECT * FROM verses WHERE surah = 2 AND ayah = 255;
```

### Query Performance Analysis

```sql
-- Enable query analysis
SET log_min_duration_statement = 100;  -- Log queries over 100ms

-- Analyze slow queries
SELECT
    query,
    calls,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## Backup and Recovery

### Create Backup

```bash
# Full database backup
pg_dump postgresql://user:password@localhost/quran_frontier > corpus_backup.sql

# Compressed backup
pg_dump -Fc postgresql://user:password@localhost/quran_frontier > corpus_backup.dump
```

### Restore from Backup

```bash
# From SQL file
psql -U postgres -d quran_frontier < corpus_backup.sql

# From compressed dump
pg_restore -d quran_frontier corpus_backup.dump
```

## Data Ingestion

### Bulk Load Process

```bash
# 1. Initialize database schema
./setup_database.sh

# 2. Run data ingestion
python ingest_corpus_data.py \
  --db postgresql://localhost/quran_frontier \
  --batch-size 10000

# 3. Verify results
psql -d quran_frontier -c "SELECT COUNT(*) FROM verses;"
```

### Expected Results

After successful ingestion:
- Surahs: 114
- Verses: 6,236
- Tafsir entries: 50,000+
- Hadith records: 30,000+
- Narrators: 10,000+
- Madhabs: 4

## Audit and Monitoring

### View Bulk Load History

```sql
SELECT
    load_id,
    load_type,
    record_count,
    load_start,
    load_end,
    status,
    EXTRACT(EPOCH FROM (load_end - load_start)) as duration_seconds
FROM bulk_load_metadata
ORDER BY load_start DESC;
```

### Review Audit Log

```sql
-- Recent operations
SELECT
    operation,
    table_name,
    validation_status,
    error_message,
    created_at
FROM data_audit_log
ORDER BY created_at DESC
LIMIT 50;

-- Validation failures
SELECT
    table_name,
    COUNT(*) as failure_count,
    array_agg(DISTINCT error_message) as errors
FROM data_audit_log
WHERE validation_status != 'SUCCESS'
GROUP BY table_name;
```

## Maintenance

### Regular Maintenance

```sql
-- Vacuum and analyze
VACUUM ANALYZE;

-- Reindex if needed
REINDEX DATABASE quran_frontier;

-- Check database size
SELECT pg_size_pretty(pg_database_size('quran_frontier')) as database_size;

-- Check table sizes
SELECT
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(relid)) as size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
psql -h localhost -U postgres -d quran_frontier -c "SELECT 1;"

# Check server logs
tail -f /var/log/postgresql/postgresql.log
```

### Data Integrity Issues

```sql
-- Find orphaned records
SELECT COUNT(*) FROM tafsirs
WHERE verse_id NOT IN (SELECT verse_id FROM verses);

-- Fix broken references (example)
DELETE FROM tafsirs
WHERE verse_id NOT IN (SELECT verse_id FROM verses);

-- Recalculate statistics
ANALYZE;
```

### Performance Degradation

```sql
-- Kill long-running queries
SELECT pid, usename, application_name, state, query
FROM pg_stat_activity
WHERE state != 'idle';

-- Cancel query
SELECT pg_cancel_backend(pid);
```

## Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Full-Text Search: https://www.postgresql.org/docs/current/textsearch.html
- JSON/JSONB: https://www.postgresql.org/docs/current/datatype-json.html
- Performance Optimization: https://www.postgresql.org/docs/current/performance.html

---

**Last Updated:** March 14, 2026
**Database Version:** 1.0
**Schema Version:** 001_initial_schema
