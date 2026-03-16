# Sources Layer: Academic Paper Discovery

The sources layer discovers peer-reviewed papers and preprints for each of the 400 scientific concepts extracted from the Quranic corpus in Tasks 4-8.

## Architecture

### Core Components

1. **SemanticScholarClient** (`semantic_scholar_client.py`)
   - Queries Semantic Scholar API v1
   - Rate limiting: 1-2 requests/second
   - Extracts: title, year, authors, DOI
   - Handles error responses gracefully

2. **CrossRefClient** (`crossref_client.py`)
   - Queries CrossRef API for peer-reviewed papers
   - Rate limiting: 1 request/second
   - Extracts: title, publication date, authors, DOI
   - Prioritizes DOI-indexed papers

3. **SourceDiscovery** (`source_discovery.py`)
   - Orchestrates discovery across both APIs
   - Merges and deduplicates results by DOI
   - Validates source integrity
   - Caches results to avoid re-queries
   - Generates statistics and metadata

## Workflow

```
Scientific Concepts (400)
    ↓
For each concept:
  1. Build optimized search query
  2. Query Semantic Scholar API
  3. Query CrossRef API
  4. Merge and deduplicate by DOI
  5. Validate source integrity
  6. Cache results
    ↓
Result: 800+ unique peer-reviewed papers
Output: source_cache.json
```

## API Response Structures

### Semantic Scholar Response
```json
{
  "data": [
    {
      "paperId": "string",
      "title": "string",
      "year": 2023,
      "authors": [{"name": "Author Name"}],
      "externalIds": {"DOI": "10.xxxx/xxxxx"},
      "venue": "Journal Name"
    }
  ]
}
```

### CrossRef Response
```json
{
  "message": {
    "items": [
      {
        "title": ["Paper Title"],
        "DOI": "10.xxxx/xxxxx",
        "published-online": {"date-parts": [[2023, 3, 15]]},
        "author": [
          {"given": "First", "family": "Last"}
        ],
        "container-title": "Journal Name"
      }
    ]
  }
}
```

### Unified Source Format
```json
{
  "doi": "10.xxxx/xxxxx",
  "title": "Paper Title",
  "year": 2023,
  "authors": ["Author Name 1", "Author Name 2"],
  "source": "semantic_scholar" | "crossref"
}
```

## Cache File Structure

```json
{
  "metadata": {
    "total_concepts": 400,
    "covered_concepts": 387,
    "total_papers": 847,
    "discovery_date": "2026-03-16T14:30:00",
    "avg_sources_per_concept": 2.19
  },
  "concept_sources": {
    "physics_001": [
      {
        "doi": "10.1038/nature12345",
        "title": "Gravitational Waves in Cosmology",
        "year": 2023,
        "authors": ["John Doe", "Jane Smith"],
        "source": "semantic_scholar"
      }
    ]
  }
}
```

## Usage Examples

### Single Concept Discovery
```python
from quran.corpus_extraction.sources import SourceDiscovery

discovery = SourceDiscovery()
sources = discovery.discover_sources_for_concept(
    concept_id="physics_001",
    concept_name="gravitation",
    domain="physics",
    limit=10
)

for source in sources:
    print(f"{source['title']} ({source['year']})")
    print(f"  DOI: {source['doi']}")
    print(f"  Authors: {', '.join(source['authors'])}")
```

### Batch Discovery for All Concepts
```python
discovery = SourceDiscovery()

# Process all 400 concepts
results = discovery.discover_sources_for_all_concepts(
    "quran/corpus_extraction/ontology/scientific_concepts.json"
)

print(f"Discovered {results['papers']} papers for {results['discovered']} concepts")

# Save to cache
discovery.save_cache("source_cache.json")

# Get statistics
stats = discovery.get_statistics()
print(f"Total unique papers: {stats['metadata']['total_papers']}")
print(f"Papers by API: {stats['sources_by_api']}")
```

### Load Cached Results
```python
discovery = SourceDiscovery(cache_file="source_cache.json")

# Retrieve cached sources for a concept
sources = discovery.get_sources_by_concept("physics_001")
```

## Rate Limiting

Both API clients implement respectful rate limiting:

- **Semantic Scholar**: 1-2 requests/second (API limit)
- **CrossRef**: 1 request/second (API recommendation)

Rate limiting is automatic and transparent to the user.

## Error Handling

The module handles various failure scenarios gracefully:

- **API timeouts**: Returns empty list, logs error
- **Invalid responses**: Skips malformed items, continues processing
- **File not found**: Raises FileNotFoundError with context
- **Network errors**: Logs and returns empty results

## Statistics and Metadata

After discovery, analyze results:

```python
metadata = discovery.get_metadata()
# Returns: total_concepts, covered_concepts, total_papers, avg_sources_per_concept

stats = discovery.get_statistics()
# Returns: unique_sources, sources_by_api, publication_years distribution
```

## Testing

All functionality is tested with mocked API responses:

```bash
python -m pytest tests/corpus-extraction/test_source_discovery.py -v
```

Test coverage includes:
- API client initialization and configuration
- Single concept discovery with mocked responses
- Batch discovery for all concepts
- Source validation and deduplication
- Caching and persistence
- Error handling
- End-to-end integration

## Performance Targets

- **Coverage**: All 400 concepts should have sources
- **Average per concept**: 10+ papers
- **Total papers**: 800+ unique papers
- **Duplicate rate**: <2% (same paper from multiple APIs)
- **Quality**: All sources have DOI or URL

## Implementation Notes

1. **No Real API Calls in Tests**: All tests use mocked responses
2. **Idempotent Caching**: Can safely re-run without duplicate data
3. **Deduplication by DOI**: Ensures unique papers across API sources
4. **Respectful Rate Limiting**: Never exceeds API rate limits
5. **Graceful Degradation**: Partial failures don't stop processing

## Future Enhancements

- Additional API sources (PubMed, IEEE Xplore)
- Domain-specific search strategies
- Citation graph analysis
- Author co-occurrence patterns
- Journal impact factor filtering
- Semantic similarity clustering
