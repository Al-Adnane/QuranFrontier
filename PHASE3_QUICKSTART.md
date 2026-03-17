# Phase 3 Quick Start Guide

## Files Created

All Phase 3 components are in `/quran/corpus_extraction/`:

### Core Files
```
extraction/
├── verse_mapping.py          # Global verse → (surah, ayah) mapping
├── verse_extractor.py        # Single verse extraction using Phase 2
├── agent_1.py through agent_32.py  # 32 parallel extraction agents
└── __init__.py

output/                        # Output directory (created at runtime)
├── corpus_1.json through corpus_32.json
└── phase3_results.json

phase3_coordinator.py         # Main coordinator script
```

## Quick Test

To verify the verse mapping works correctly:

```bash
cd /Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday

# Run verse mapping tests
python3 -m pytest tests/corpus-extraction/test_verse_mapping.py -v
```

Expected output: **12 passed**

## Full Execution

To run the complete Phase 3 extraction:

```bash
cd /Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday

# Execute all 32 agents in parallel
python3 quran/corpus_extraction/phase3_coordinator.py
```

## What Happens

1. **Coordinator starts** (1-2 seconds)
2. **32 agents spawn** in parallel
3. **Each agent processes** ~195 verses
4. **Checkpoints saved** every 50 verses
5. **Results output** to corpus_<N>.json
6. **Report generated** when all agents complete

## Monitoring Progress

### In Real-Time
- Agent logs appear in console
- Each agent shows progress: "Agent N completed (X/32)"

### Check Output Files
```bash
# While agents are running
ls -lah quran/corpus_extraction/output/corpus_*.json

# Count verses extracted so far
for f in quran/corpus_extraction/output/corpus_*.json; do
  jq 'length' "$f"
done | awk '{sum+=$1} END {print sum}'
```

### Final Report
```bash
# After completion
jq . quran/corpus_extraction/output/phase3_results.json | head -50
```

## Key Files Summary

### 1. verse_mapping.py (290 lines)
- Maps verse numbers bidirectionally
- All 114 surahs with correct ayah counts
- O(log n) lookup performance
- Fully tested with 12 unit tests

**Key Methods**:
- `get_surah_ayah(verse_num)` → (surah, ayah)
- `get_global_verse(surah, ayah)` → verse_num

### 2. verse_extractor.py (160 lines)
- Extracts single verses using Phase 2 framework
- Handles caching and API integration
- Returns VerseExtraction dataclass
- Error handling and logging

**Key Method**:
- `extract_verse_complete(surah, ayah)` → VerseExtraction

### 3. agent_1.py through agent_32.py (240 lines each)
- Each processes ~195 verses
- Checkpointing for recovery
- Independent JSON output
- Statistics tracking

**Verse Ranges**:
- Agent 1: Verses 1-195
- Agent 2: Verses 196-390
- ...
- Agent 32: Verses 6,046-6,236+

### 4. phase3_coordinator.py (330 lines)
- Spawns all 32 agents with ThreadPoolExecutor
- Monitors execution
- Collects and aggregates results
- Generates final report
- Verifies output integrity

## Output Format

Each `corpus_<N>.json` contains array of VerseExtraction objects:

```json
[
  {
    "surah": 1,
    "ayah": 1,
    "verse_key": "1:1",
    "arabic_text": "الحمد لله رب العالمين",
    "translation": "All the praises and thanks be to Allah...",
    "physics_content": null,
    "biology_content": null,
    "medicine_content": null,
    "engineering_content": null,
    "agriculture_content": null,
    "tafsirs": {},
    "tafsir_agreement": 0.0,
    "asbab_nuzul": null,
    "semantic_analysis": null,
    "verification_layers": {},
    "confidence_score": 0.0,
    "source_citations": []
  },
  ...
]
```

## Expected Completion Time

- **With 32 parallel agents**: 30-60 minutes
  - Bottleneck: API rate limiting (100 req/hour per agent)
  - 32 agents × 195 verses = 6,240 total extractions
  - Actual time depends on API responsiveness

- **Sequential extraction**: 6+ hours (for reference)

## Architecture Diagram

```
Phase 3 Coordinator
    ├─ Agent 1 (Verses 1-195) → corpus_1.json
    ├─ Agent 2 (Verses 196-390) → corpus_2.json
    ├─ Agent 3 (Verses 391-585) → corpus_3.json
    │  ...
    └─ Agent 32 (Verses 6046-6236) → corpus_32.json
         ↓
    Aggregator
         ↓
    phase3_results.json (with statistics)
```

## Database Checkpointing

Checkpoints stored in Redis:
- Key: `checkpoint:agent_<N>`
- Contents:
  - Last completed verse
  - Verses processed
  - Timestamp
  - Status (in_progress/completed)

If agent crashes:
1. Coordinator detects timeout
2. Agent can be restarted
3. Agent checks checkpoint
4. Agent resumes from next verse

## Verification

After completion, verify extraction:

```bash
# 1. Check all files created
ls quran/corpus_extraction/output/corpus_*.json | wc -l
# Expected: 32

# 2. Check verse counts
for i in {1..32}; do
  count=$(jq 'length' quran/corpus_extraction/output/corpus_$i.json)
  echo "Agent $i: $count verses"
done

# 3. Sum total verses
python3 << 'EOF'
import json
import os
from pathlib import Path

output_dir = Path("quran/corpus_extraction/output")
total = 0

for corpus_file in sorted(output_dir.glob("corpus_*.json")):
    with open(corpus_file) as f:
        data = json.load(f)
        total += len(data)

print(f"Total verses extracted: {total}")
print(f"Expected: 6236+ (actual count from API)")
EOF

# 4. Spot check a verse
jq '.[0]' quran/corpus_extraction/output/corpus_1.json
```

## Troubleshooting

### Agent Timeout
- Check Redis connection: `redis-cli ping`
- Check network/API: Try manual API call
- Check logs for specific errors

### Missing Output Files
- Check agent exit codes in coordinator output
- Check agent logs for errors
- Verify Redis checkpoint status

### Low Verse Count
- Check API rate limiting
- Verify API access
- Check for extraction errors in logs

### Memory Issues
- Reduce parallel workers (not recommended)
- Clear cache between agents
- Process in smaller batches

## Next Steps

1. **Run tests first**: `pytest tests/corpus-extraction/test_verse_mapping.py -v`
2. **Execute coordinator**: `python3 quran/corpus_extraction/phase3_coordinator.py`
3. **Monitor progress**: Check output directory
4. **Verify results**: Use verification commands above
5. **Analyze corpus**: Process corpus_*.json files for downstream tasks

## Integration Points

Phase 3 integrates with:
- **Phase 2 Framework**: Uses VerseExtractorCoordinator
- **quran.com API**: Fetches verse data
- **Redis**: Checkpoint storage
- **Cache Layer**: Multi-level caching
- **Verification Pipeline**: 5-layer checks

All components from Phase 2 are reused and enhanced for parallel execution.
