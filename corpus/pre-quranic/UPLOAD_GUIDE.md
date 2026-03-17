# DATASET UPLOAD GUIDE

**For:** Researchers wanting to upload Pre-Quranic Sacred Texts Corpus  
**Date:** 2026-03-15

---

## ⚠️ BEFORE UPLOADING

### Required Checks:

1. **Read** `README_ACCURACY.md` - Understand accuracy limitations
2. **Read** `VERIFICATION_STATUS.md` - Know all known issues
3. **Verify** you have rights to share this content
4. **Consider** living tradition restrictions
5. **Prepare** appropriate disclaimers

---

## UPLOAD OPTIONS

### Option 1: GitHub/GitLab

```bash
# Navigate to project
cd /Users/mac/Desktop/QuranFrontier

# Check git status
git status

# Add pre-quranic corpus
git add corpus/pre-quranic/

# Commit
git commit -m "Add pre-Quranic sacred texts corpus (UNVERIFIED)"

# Push
git push origin main
```

**GitHub Repository Settings:**
- Add `DATASET_README.md` as main documentation
- Include `CITATION.cff` for proper citation
- Add topic tags: `religious-studies`, `digital-humanities`, `ancient-texts`
- Set license: CC-BY-NC-SA-4.0 (or appropriate)

**Required Repository Files:**
```
QuranFrontier/
├── corpus/pre-quranic/          # Main dataset
├── DATASET_README.md            # Upload this
├── CITATION.cff                 # Upload this
├── LICENSE                      # Add license file
└── .gitignore                   # Exclude cache files
```

---

### Option 2: Zenodo (Academic Repository)

**Steps:**

1. **Create Zenodo Account**
   - Go to https://zenodo.org/
   - Login with ORCID or institutional account

2. **Prepare Upload Package**
   ```bash
   # Create upload directory
   mkdir zenodo-upload
   cd zenodo-upload
   
   # Copy dataset
   cp -r ../pre-quranic/ ./
   
   # Add metadata
   cp ../DATASET_README.md ./README.md
   cp ../CITATION.cff ./
   
   # Create metadata.json
   # (see template below)
   
   # Compress
   zip -r pre-quranic-corpus.zip ./
   ```

3. **Create Metadata (metadata.json)**
   ```json
   {
     "metadata": {
       "title": "Pre-Quranic Sacred Texts Corpus",
       "description": "Collection of sacred texts from 36+ pre-Quranic religious traditions",
       "publication_date": "2026-03-15",
       "creators": [
         {
           "name": "QuranFrontier Project"
         }
       ],
       "keywords": [
         "pre-quranic",
         "sacred texts",
         "religious studies",
         "digital humanities"
       ],
       "license": "cc-by-nc-sa-4.0",
       "resource_type": "dataset",
       "notes": "STATUS: UNVERIFIED. Requires scholarly verification before academic use."
     }
   }
   ```

4. **Upload to Zenodo**
   - Click "New Upload"
   - Fill in metadata
   - Upload zip file
   - Add disclaimer in description
   - Publish (gets DOI)

---

### Option 3: Figshare

**Steps:**

1. Go to https://figshare.com/
2. Click "Upload"
3. Drag and drop files
4. Fill in metadata:
   - Title: Pre-Quranic Sacred Texts Corpus
   - Description: Include accuracy disclaimer
   - Tags: religious-studies, ancient-texts, etc.
5. Set license
6. Publish

---

### Option 4: Academic Data Repository

**Examples:**
- Harvard Dataverse
- UC3 Merritt
- Dryad
- Institutional repository

**Requirements:**
- Dataset description
- Metadata (Dublin Core or domain-specific)
- License information
- Verification disclaimer

---

## Required Disclaimer (Include Everywhere)

```
⚠️ ACCURACY NOTICE ⚠️

This dataset contains UNVERIFIED content. Before academic use:

1. Read VERIFICATION_STATUS.md for known issues
2. Verify against scholarly critical editions
3. Consult subject experts for each tradition
4. Obtain permission from living tradition communities

DO NOT CITE without independent verification.

Some content (Egyptian hieroglyphs, cuneiform, Avestan) 
is acknowledged as potentially inaccurate and requires 
specialist verification.
```

---

## License Recommendations

### Recommended: CC-BY-NC-SA-4.0

```
Attribution-NonCommercial-ShareAlike 4.0 International

Users must:
- Attribute the source
- Use only for non-commercial purposes
- Share derivatives under same license
```

### For Living Traditions:

Add traditional knowledge labels:
- TK Traditional Knowledge Attribution
- TK Traditional Knowledge Non-Commercial
- TK Traditional Knowledge Share-Alike

See: https://localcontexts.org/labels/

---

## File Checklist for Upload

```
□ DATASET_README.md
□ README_ACCURACY.md
□ VERIFICATION_STATUS.md
□ CITATION.cff
□ LICENSE
□ All JSON text files (40)
□ All documentation files (10+)
□ Mathematical models (6)
□ Metadata files (schema, validation)
□ .gitignore (exclude cache files)
```

---

## Size Information

| Component | Size |
|-----------|------|
| JSON text files | ~300 KB |
| Documentation | ~100 KB |
| Mathematical models | ~50 KB |
| **Total** | **~450 KB** |

**Compressed (zip):** ~200 KB

---

## Post-Upload Actions

### 1. Share DOI/URL
- Add to project documentation
- Update README files
- Share with collaborators

### 2. Request Verification
- Contact subject experts
- Reach out to living tradition communities
- Request peer review

### 3. Track Usage
- Monitor citations
- Collect verification reports
- Update dataset with corrections

---

## Ethical Considerations

### Living Traditions:

For these traditions, EXTRA care is needed:

| Tradition | Action Required |
|-----------|----------------|
| Yoruba/Ifá | Consult Babalawo |
| Buddhism | Consult Buddhist scholars |
| Hinduism | Consult Hindu organizations |
| Native American | Consult tribal authorities |
| Aboriginal | Consult Land Councils |
| Bon | Consult FPBT |

### Restricted Content:

Some content may need to be:
- Removed (sacred/restricted)
- Access-controlled (community only)
- Modified (per community request)

---

## Contact Template for Experts

```
Subject: Request for Verification - Pre-Quranic Sacred Texts Dataset

Dear [Expert Name],

I am writing to request your expertise in verifying a dataset of 
pre-quranic sacred texts, specifically [Tradition Name] content.

The dataset is available at: [URL/DOI]

We acknowledge that the [specific content] requires verification 
against scholarly critical editions. Would you be willing to:

1. Review the [specific files]
2. Provide corrections where needed
3. Advise on appropriate use guidelines

We understand this requires your time and expertise, and we are 
happy to discuss appropriate acknowledgment or collaboration.

Thank you for your consideration.

Best regards,
[Your Name]
```

---

## Version Control

### When to Create New Version:

- Content corrections received
- New traditions added
- Verification reports incorporated
- Community feedback implemented

### Version Naming:

```
v1.0.0 - Initial release (2026-03-15)
v1.1.0 - Minor corrections (TBD)
v2.0.0 - Major verification update (TBD)
```

---

## Summary

**To Upload:**

1. Choose platform (GitHub, Zenodo, etc.)
2. Prepare files (see checklist)
3. Add disclaimers (required)
4. Set appropriate license
5. Upload
6. Share DOI/URL
7. Request verification

**Remember:** This dataset requires scholarly verification before academic use. Make this clear in all descriptions.

---

**Status:** READY FOR UPLOAD (with disclaimers)
