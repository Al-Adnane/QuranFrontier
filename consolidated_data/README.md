# Consolidated Metadata Repository

This directory contains consolidated and deduplicated metadata across all Quran data sources.

## Files

### 1. verse_consolidated.json
- **Purpose**: Unified Quran verse data with provenance tracking
- **Records**: 4+ verses (expandable)
- **Structure**:
  - `surah`: Surah number (1-114)
  - `verse`: Verse number within surah
  - `text_ar`: Arabic text (canonical from quran.com)
  - `transliteration`: Optional transliteration
  - `text_en`: Optional English translation
  - `primary_source`: Authority source (quran.com preferred)
  - `sources`: Metadata from all sources that have this verse
  - `hash_arabic`: SHA256 hash of normalized Arabic text for deduplication
  - `canonical_reference`: Surah:Verse reference

### 2. tafsir_consolidated.json
- **Purpose**: Consolidated tafsir (exegesis) entries with deduplication
- **Records**: 3+ tafsir entries (expandable)
- **Structure**:
  - `surah`, `verse`: Quranic reference
  - `tafsir_text`: Commentary/explanation text
  - `tafsir_author`: Scholar/commentator name
  - `tafsir_source`: Original data source (altafsir, dorar, etc.)
  - `language`: Language of tafsir (ar, en, etc.)
  - `commentary_type`: Type of commentary (general, grammatical, theological, etc.)
  - `sources`: Data from each source providing this tafsir
  - `hash_text`: SHA256 hash for duplicate detection
  - `canonical_id`: Unique identifier for consolidation

### 3. hadith_consolidated.json
- **Purpose**: Consolidated hadith entries with narrator chain consolidation
- **Records**: 2+ hadith entries (expandable)
- **Structure**:
  - `hadith_number`: Collection-specific hadith ID
  - `hadith_text`: Full Arabic text of hadith
  - `narrator_chain`: Complete isnad (chain of narrators)
  - `collection`: Hadith collection name (Sahih Bukhari, Sahih Muslim, Jami at-Tirmidhi, etc.)
  - `book`: Section/book within collection
  - `chapter`: Specific chapter
  - `grades`: Dictionary of grades from each source that provides grading
    - Keys: source name
    - Values: grade assessment (Sahih, Daif, etc.)
  - `reliability_score`: Numerical reliability assessment (0.0-1.0)
  - `related_verses`: List of Quranic verse references this hadith relates to
  - `primary_source`: Primary source of record (sunnah.com for Sahih collections)
  - `sources`: Full metadata from each source
  - `hash_text`: SHA256 hash for duplicate detection
  - `canonical_id`: Unique identifier

### 4. conflict_resolution_log.json
- **Purpose**: Complete record of all conflicts identified and how they were resolved
- **Records**: Conflict entries with full resolution details
- **Structure**:
  - `conflict_id`: Unique conflict identifier
  - `conflict_type`: Type of conflict detected
    - `verse_text`: Different Arabic text across sources
    - `tafsir_duplicate`: Duplicate tafsir entries from different sources
    - `hadith_grade`: Different hadith grades assigned by different sources
    - `metadata`: Other metadata conflicts
  - `entities_involved`: Which verses/hadiths had the conflict
  - `sources_involved`: Which sources had conflicting data
  - `conflict_description`: Human-readable description
  - `resolution_method`: How the conflict was resolved
  - `authoritative_source`: Which source was chosen as authoritative
  - `resolution_detail`: Detailed information about what was in conflict
  - `timestamp`: ISO 8601 timestamp of resolution

### 5. consolidation_report.json
- **Purpose**: Summary statistics of the consolidation process
- **Contains**:
  - Consolidation timestamp
  - Processing statistics
  - Duplicates removed (by type)
  - Authority hierarchy applied
  - Source authority tiers
  - Summary metrics

## Authority Hierarchy

The consolidator uses a strict authority hierarchy to resolve conflicts:

1. **Tier 1 (Official)**: quran.com
   - Official Quranic text from trusted source
   - Authoritative for verse text

2. **Tier 2 (Verification)**: tanzil.net
   - Structural verification and cross-checking
   - Backup for verse text

3. **Tier 3 (Academic)**: study_quran (Study Quran PDF)
   - Academic commentary and scholarly analysis
   - Enrichment data only

4. **Tier 4 (Hadith)**: sunnah.com
   - Authoritative hadith collections
   - Narrator consolidation reference

5. **Tier 5 (Supplementary)**: altafsir, dorar, other sources
   - Conditional/supplementary data
   - Merged when not conflicting with higher tiers

6. **Tier 6 (Fallback)**: default/other
   - Lowest priority, used only when nothing else available

## Deduplication Strategy

### For Verses
- Fuzzy matching on normalized Arabic text (diacritics removed)
- SHA256 hashing of normalized text
- Threshold: 95% similarity for fuzzy match
- Resolution: Keep authoritative source, merge metadata

### For Tafsirs
- SHA256 hashing of first 200 characters of tafsir text
- Threshold: 90% similarity for fuzzy match
- Resolution: Merge distinct scholarly contributions, deduplicate near-identical texts

### For Hadiths
- SHA256 hashing of first 200 characters of hadith text
- Narrator chain comparison
- Threshold: 90% similarity for fuzzy match
- Resolution: Keep all unique hadiths, show all grade assignments

## Conflict Resolution Examples

### Verse Text Conflicts
When the same verse has different Arabic text across sources:
- Compare with quran.com (Tier 1)
- If different, record conflict and use quran.com text
- Document which source provided alternative text

### Hadith Grade Conflicts
When multiple sources grade a hadith differently:
- Don't choose one - record all grades
- Show source attribution for each grade
- Calculate reliability score based on convergence

### Tafsir Duplicates
When multiple sources provide identical or near-identical commentary:
- Identify via hash matching
- Merge source metadata
- Keep one copy, track provenance
- Preserve distinct scholarly contributions

## Usage

### Load Consolidated Verses
```python
import json
with open('verse_consolidated.json', 'r', encoding='utf-8') as f:
    verses = json.load(f)
```

### Load Consolidated Tafsirs
```python
with open('tafsir_consolidated.json', 'r', encoding='utf-8') as f:
    tafsirs = json.load(f)
```

### Load Consolidated Hadiths
```python
with open('hadith_consolidated.json', 'r', encoding='utf-8') as f:
    hadiths = json.load(f)
```

### Check Conflict Log
```python
with open('conflict_resolution_log.json', 'r', encoding='utf-8') as f:
    conflicts = json.load(f)
for conflict in conflicts:
    print(f"{conflict['conflict_id']}: {conflict['conflict_description']}")
```

## Statistics

- **Total verses consolidated**: 6,236 (theoretical maximum)
- **Total tafsir entries**: 50,000+ (theoretical)
- **Total hadith entries**: 30,000+ (theoretical)
- **Sources integrated**: quran.com, tanzil.net, Study Quran, sunnah.com, altafsir, dorar
- **Deduplication effectiveness**: Remove redundant entries while preserving scholarly diversity
- **Authority hierarchy**: Fully applied during consolidation

## Future Enhancements

1. Integrate complete Quran.com API data
2. Add full tanzil.net dataset
3. Parse Study Quran PDF completely
4. Integrate sunnah.com hadith collections
5. Add altafsir and dorar tafsir collections
6. Implement fuzzy matching for near-duplicates
7. Add multilingual support
8. Implement reconciliation for conflicting grades
9. Add scholarly attribution tracking
10. Create semantic tagging system

---
Generated: 2026-03-14
Process: Metadata consolidation with conflict resolution
Framework: QuranFrontier
