# Pre-Quranic Sacred Texts - User Tutorial

**Version:** 1.0  
**Last Updated:** 2026-03-15  
**Level:** Beginner to Advanced

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Structure](#understanding-the-structure)
3. [Reading the Texts](#reading-the-texts)
4. [Using Mathematical Models](#using-mathematical-models)
5. [Verification Workflow](#verification-workflow)
6. [Contributing Corrections](#contributing-corrections)
7. [Citing This Dataset](#citing-this-dataset)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Basic understanding of JSON format
- Text editor or IDE (VS Code, Sublime Text, etc.)
- Font installation (see FONTS_GUIDE.md)
- **Important:** Read README_ACCURACY.md before use

### Download the Dataset

```bash
# Clone from GitHub
git clone [REPOSITORY_URL]

# Or download ZIP
# Extract to your working directory
```

### Navigate the Structure

```
pre-quranic/
├── README.md              ← Start here
├── README_ACCURACY.md     ← ⚠️ READ THIS FIRST
├── metadata/              ← Schema and models
├── [tradition folders]/   ← Text files
└── scripts/               ← Utility scripts
```

---

## Understanding the Structure

### JSON File Format

Each tradition file follows this structure:

```json
{
  "metadata": {
    "collection": "pre-quranic",
    "tradition": "Tradition Name",
    "language": "Language",
    "script": "Script",
    "date_range": "Date Range",
    "accuracy_notice": {
      "status": "UNVERIFIED",
      "warning": "Specific warning",
      "recommendation": "What to do"
    }
  },
  "texts": [
    {
      "text_id": "unique_id",
      "text_name_en": "Name in English",
      "verses": [...]
    }
  ]
}
```

### Key Fields Explained

| Field | Description |
|-------|-------------|
| `metadata.tradition` | Religious tradition name |
| `metadata.language` | Original language |
| `metadata.script` | Writing system used |
| `metadata.date_range` | When text was composed |
| `accuracy_notice.status` | Verification status |
| `texts` | Array of text passages |

---

## Reading the Texts

### Using a Text Editor

1. **Open any JSON file**
   ```
   # Example: Open Hebrew texts
   code hebrew/torah_psalms.json
   ```

2. **Enable JSON syntax highlighting**
   - Most editors do this automatically
   - Helps identify structure

3. **Search for specific content**
   ```
   # Search for specific verse
   Ctrl+F → "verse_id": "gen_1_1"
   ```

### Using Python

```python
import json

# Load a file
with open('hebrew/torah_psalms.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Access metadata
print(data['metadata']['tradition'])

# Access texts
for text in data['texts']:
    print(text['text_name_en'])
```

### Using Command Line (jq)

```bash
# Install jq first
# macOS: brew install jq
# Linux: apt-get install jq

# View metadata
jq '.metadata' hebrew/torah_psalms.json

# Count texts
jq '.texts | length' hebrew/torah_psalms.json

# Find specific verse
jq '.texts[] | select(.verse_id == "gen_1_1")' hebrew/torah_psalms.json
```

---

## Using Mathematical Models

### Location

Mathematical models are in:
```
metadata/mathematical_models/
```

### Available Models

| File | Tradition | Model Type |
|------|-----------|------------|
| `yoruba_ifa_math.json` | Ifá | Binary combinatorics |
| `taoist_iching_math.json` | I Ching | Binary algebra |
| `buddhism_abhidharma_math.json` | Buddhism | Graph theory |
| `maya_calendar_math.json` | Maya | Modular arithmetic |
| `hinduism_vedic_math.json` | Hinduism | Geometry |
| `aztec_calendar_math.json` | Aztec | Calendar math |

### Example: Analyzing Ifá Binary System

```python
import json

# Load model
with open('metadata/mathematical_models/yoruba_ifa_math.json') as f:
    model = json.load(f)

# Access Odu list
odu_list = model['principal_odu']['odu_list']

# Print all Odu with binary
for odu in odu_list:
    print(f"{odu['name']}: {odu['binary']}")
```

### Visualizing Graph Models

```python
import networkx as nx
import matplotlib.pyplot as plt

# Load Buddhist model
with open('metadata/mathematical_models/buddhism_abhidharma_math.json') as f:
    model = json.load(f)

# Create graph from dependent origination
G = nx.DiGraph()
nidanas = model['dependent_origination']['nidanas']

for nidana in nidanas:
    G.add_node(nidana['index'], label=nidana['name'])
    for edge_to in nidana['edges_to']:
        G.add_edge(nidana['index'], edge_to)

# Draw
nx.draw(G, with_labels=True)
plt.show()
```

---

## Verification Workflow

### Step 1: Check Verification Status

```bash
# Read known issues
cat VERIFICATION_STATUS.md
```

### Step 2: Run Verification Script

```bash
# Navigate to corpus
cd corpus/pre-quranic/

# Run verification
python scripts/verify_corpus.py .
```

### Step 3: Compare with Sources

```
For each tradition:
1. Identify critical edition (see file metadata)
2. Compare text against edition
3. Note any discrepancies
4. Report issues (see Contributing section)
```

### Step 4: Document Findings

Create a verification report:

```markdown
## Verification Report: [Tradition]

**File:** [filename.json]
**Reviewer:** [Your name]
**Date:** [Date]

### Findings:
- [ ] Text accuracy: Correct/Incorrect
- [ ] Transliteration: Verified/Needs correction
- [ ] Translation: Accurate/Needs revision

### Corrections Needed:
1. [Specific correction]
2. [Specific correction]

### Sources Used:
- [Critical edition 1]
- [Critical edition 2]
```

---

## Contributing Corrections

### Via GitHub (Preferred)

1. **Fork the repository**
2. **Create a branch**
   ```bash
   git checkout -b fix/tradition-name
   ```
3. **Make corrections**
4. **Commit with clear message**
   ```bash
   git commit -m "Fix: Correct [specific issue] in [file]"
   ```
5. **Submit pull request**

### Via Email

1. **Document the issue**
   ```
   File: [filename.json]
   Line/Field: [specific location]
   Current: [what it says]
   Correct: [what it should be]
   Source: [critical edition reference]
   ```

2. **Send to:** [project email]

### Via Issue Tracker

1. **Create new issue**
2. **Use template:**
   ```
   **Type:** Correction/Verification
   **File:** [filename]
   **Issue:** [description]
   **Source:** [reference]
   **Suggested Fix:** [correction]
   ```

---

## Citing This Dataset

### Basic Citation

```
QuranFrontier Project. (2026). Pre-Quranic Sacred Texts 
Corpus [Dataset]. Version 1.0. 
[URL or DOI]
```

### With Specific File

```
QuranFrontier Project. (2026). Yoruba/Ifá Texts. 
In Pre-Quranic Sacred Texts Corpus [Dataset]. 
[URL or DOI]
```

### BibTeX

```bibtex
@dataset{quranfrontier2026,
  author = {{QuranFrontier Project}},
  title = {Pre-Quranic Sacred Texts Corpus},
  year = {2026},
  version = {1.0},
  publisher = {[Repository Name]},
  url = {[URL]},
  doi = {[DOI]},
  note = {STATUS: UNVERIFIED. Verify against scholarly sources.}
}
```

---

## Troubleshooting

### Problem: Unicode Characters Display as Boxes

**Solution:**
1. Install required fonts (see FONTS_GUIDE.md)
2. Ensure your editor supports Unicode
3. Check file encoding is UTF-8

### Problem: JSON Won't Load

**Solution:**
```bash
# Validate JSON
python -m json.tool filename.json > /dev/null

# If error, check for:
# - Trailing commas
# - Missing quotes
# - Unclosed braces
```

### Problem: Can't Find Specific Text

**Solution:**
```bash
# Search all files
grep -r "search term" .

# Or use Python
import glob
for f in glob.glob('**/*.json', recursive=True):
    if 'search term' in open(f).read():
        print(f)
```

### Problem: Mathematical Model Won't Load

**Solution:**
1. Check file is valid JSON
2. Verify you have correct Python libraries
3. Check model documentation

---

## Best Practices

### Do:
- ✅ Read accuracy notices before use
- ✅ Verify against scholarly sources
- ✅ Cite properly
- ✅ Report errors you find
- ✅ Respect living tradition protocols

### Don't:
- ❌ Cite without verification
- ❌ Use for commercial purposes without permission
- ❌ Ignore community restrictions
- ❌ Assume content is authoritative

---

## Getting Help

### Documentation

- `README_ACCURACY.md` - Accuracy warnings
- `VERIFICATION_STATUS.md` - Known issues
- `FONTS_GUIDE.md` - Font installation
- `UPLOAD_GUIDE.md` - How to share

### Contact

- **Email:** [project email]
- **GitHub:** [repository issues]
- **Website:** [project website]

### Community

- Join discussion forum
- Attend virtual office hours
- Participate in verification sprints

---

## Next Steps

### For Beginners:
1. Read README_ACCURACY.md
2. Browse a few tradition files
3. Install required fonts
4. Try loading a file in Python

### For Scholars:
1. Identify your area of expertise
2. Review relevant files
3. Verify against your sources
4. Submit corrections

### For Developers:
1. Review JSON schema
2. Build tools for analysis
3. Create visualizations
4. Contribute to repository

---

**Tutorial Status:** ✅ COMPLETE  
**Last Reviewed:** 2026-03-15
