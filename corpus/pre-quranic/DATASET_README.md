# Pre-Quranic Sacred Texts Corpus

**Version:** 1.0.0  
**Date:** 2026-03-15  
**Status:** REQUIRES VERIFICATION BEFORE ACADEMIC USE

---

## Quick Start

```bash
# Download/Clone this repository
git clone [YOUR_REPOSITORY_URL]

# Navigate to corpus
cd corpus/pre-quranic/

# View documentation
cat README_ACCURACY.md
cat VERIFICATION_STATUS.md
```

---

## Collection Contents

| Metric | Count |
|--------|-------|
| **Traditions** | 36+ |
| **Languages** | 40+ |
| **Scripts** | 20+ |
| **JSON Files** | 40 |
| **Documentation Files** | 10+ |
| **Mathematical Models** | 6 |
| **Total Size** | ~400 KB |

---

## Directory Structure

```
pre-quranic/
├── README.md
├── README_ACCURACY.md          ⚠️ READ FIRST
├── VERIFICATION_STATUS.md      ⚠️ IMPORTANT
├── COMPLETE_INDEX.md
├── FONTS_GUIDE.md
├── RESCAN_REPORT_2026-03-15.md
├── metadata/
│   ├── schema.json
│   ├── validation_report.json
│   ├── MATHEMATICAL_EXTRACTION_FRAMEWORK.md
│   └── mathematical_models/    (6 JSON files)
└── [36 tradition directories]/
    └── *.json
```

---

## ⚠️ CRITICAL ACCURACY NOTICE

**BEFORE USING THIS DATASET:**

1. **Read** `README_ACCURACY.md` for accuracy warnings
2. **Read** `VERIFICATION_STATUS.md` for known issues
3. **Verify** all content against scholarly sources
4. **Consult** experts for each tradition
5. **Obtain** permission from living tradition communities

**This dataset is NOT ready for academic use without verification.**

---

## File Format

All text files use consistent JSON schema:

```json
{
  "metadata": {
    "collection": "pre-quranic",
    "tradition": "[Tradition Name]",
    "language": "[Language]",
    "script": "[Script]",
    "date_range": "[Date Range]",
    "accuracy_notice": {
      "status": "UNVERIFIED",
      "warning": "[Specific warning]",
      "recommendation": "[What to do]"
    }
  },
  "texts": [...],
  "verification_required": {...}
}
```

---

## Mathematical Models

Located in `metadata/mathematical_models/`:

| File | Tradition | Model Type |
|------|-----------|------------|
| `yoruba_ifa_math.json` | Yoruba/Ifá | Binary Combinatorics |
| `taoist_iching_math.json` | Taoism/I Ching | Binary Algebra |
| `buddhism_abhidharma_math.json` | Buddhism | Graph Theory |
| `maya_calendar_math.json` | Maya | Modular Arithmetic |
| `hinduism_vedic_math.json` | Hinduism | Geometry/Combinatorics |
| `aztec_calendar_math.json` | Aztec | Modular Arithmetic |

---

## Usage Guidelines

### For Researchers:
1. Verify against scholarly critical editions
2. Consult subject experts
3. Do not cite without verification
4. Report errors to maintainers

### For Developers:
1. All files are UTF-8 encoded JSON
2. Follow schema in `metadata/schema.json`
3. Respect accuracy notices
4. Contribute corrections via pull requests

### For Community Members:
1. Review representation of your tradition
2. Request restrictions on sacred content
3. Provide corrections/guidance
4. Contact maintainers for concerns

---

## License

**Important:** This dataset contains:
- Public domain texts (ancient sources)
- Original translations (various licenses)
- Community knowledge (requires permission)

**Users must:**
- Verify licensing for their use case
- Obtain permissions for living traditions
- Attribute scholarly sources appropriately

---

## Citation

**If you must cite before verification:**

```
QuranFrontier Project. (2026). Pre-Quranic Sacred Texts 
Collection [Dataset]. STATUS: UNVERIFIED. 
Verify against scholarly sources before use.
```

**Better:** Cite the scholarly sources directly, not this dataset.

---

## Known Issues

| Issue | Status | Files Affected |
|-------|--------|----------------|
| Egyptian Hieroglyphs | ❌ Placeholder | `egyptian/*.json` |
| Avestan Script | ⚠️ Unverified | `avestan/*.json` |
| Cuneiform Signs | ⚠️ Unverified | `akkadian/*.json` |
| Yoruba Tonal Marks | ⚠️ Unverified | `african/yoruba/*.json` |
| Nahuatl Orthography | ⚠️ Unverified | `americas/aztec/*.json` |
| Quechua Spelling | ⚠️ Unverified | `americas/inca/*.json` |
| Tibetan Wylie | ⚠️ Unverified | `asian/bon/*.json` |

See `VERIFICATION_STATUS.md` for complete list.

---

## Contact & Contribution

**For corrections:**
1. Open issue on GitHub
2. Provide scholarly source
3. Submit pull request with verification

**For living traditions:**
1. Contact maintainers directly
2. Request content restrictions if needed
3. Provide community guidance

---

## Acknowledgments

This dataset acknowledges the living traditions and communities who maintain these sacred texts. Users are encouraged to:

- Support preservation efforts for endangered languages
- Respect cultural protocols for sacred knowledge
- Consult with tradition bearers before use
- Contribute to ethical scholarship

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-15 | Initial release |
| | | - 40 JSON text files |
| | | - 36+ traditions |
| | | - 6 mathematical models |
| | | - Full documentation |

---

**⚠️ READ README_ACCURACY.md BEFORE USE ⚠️**
