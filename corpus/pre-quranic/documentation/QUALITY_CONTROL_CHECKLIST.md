# Quality Control Checklist
## Pre-Quranic Sacred Texts Verification Workflow

**Purpose:** Ensure systematic verification of all content  
**Version:** 1.0  
**Date:** 2026-03-15

---

## PHASE 1: Initial File Check

### For Each JSON File:

- [ ] File is valid JSON (run `verify_corpus.py`)
- [ ] Has `metadata` section
- [ ] Has `accuracy_notice` in metadata
- [ ] Has `texts` section (if applicable)
- [ ] UTF-8 encoding verified
- [ ] No broken Unicode characters
- [ ] File size is reasonable (< 1 MB typically)

**Reviewer:** _________________ **Date:** _________

---

## PHASE 2: Content Verification

### Metadata Verification

- [ ] Tradition name is accurate
- [ ] Language identification is correct
- [ ] Script identification is correct
- [ ] Date range is scholarly accurate
- [ ] Source citations are provided
- [ ] Critical edition references are current

**Reviewer:** _________________ **Date:** _________

### Text Content Verification

- [ ] Original script text verified against source
- [ ] Transliteration follows scholarly standard
- [ ] Translation is accurate
- [ ] Verse/passage numbering is correct
- [ ] No content missing
- [ ] No content added that isn't in source

**Reviewer:** _________________ **Date:** _________

### Unicode/Script Verification

- [ ] All characters are valid Unicode
- [ ] Script matches claimed writing system
- [ ] No placeholder characters remaining
- [ ] Font rendering tested
- [ ] Directionality correct (LTR/RTL)

**Reviewer:** _________________ **Date:** _________

---

## PHASE 3: Scholarly Review

### Expert Consultation

- [ ] Subject matter expert identified
- [ ] Expert credentials verified
- [ ] Files sent for review
- [ ] Review deadline set
- [ ] Feedback received
- [ ] All corrections implemented
- [ ] Expert approval obtained

**Expert Name:** _________________  
**Affiliation:** _________________  
**Date Consulted:** _________

### Source Verification

- [ ] Critical edition identified
- [ ] Edition is scholarly standard
- [ ] Page/line references checked
- [ ] Variant readings noted
- [ ] Translation compared with edition

**Source:** _________________  
**Edition:** _________________  
**Year:** _________

---

## PHASE 4: Community Consultation (Living Traditions Only)

### Community Identification

- [ ] Living tradition status confirmed
- [ ] Community representatives identified
- [ ] Contact information verified
- [ ] Cultural protocols researched

**Community:** _________________  
**Representatives:** _________________

### Consultation Process

- [ ] Initial contact made
- [ ] Project explained
- [ ] Content presented for review
- [ ] Community feedback received
- [ ] Restrictions identified
- [ ] Access agreements negotiated
- [ ] Community approval obtained

**Date Contacted:** _________  
**Date Approved:** _________  
**Agreement Type:** _________________

### Content Modifications

- [ ] Restricted content identified
- [ ] Content removed (if requested)
- [ ] Access controls implemented
- [ ] Acknowledgment text approved
- [ ] Benefits agreement signed

**Modifications Made:** _________________

---

## PHASE 5: Technical Quality

### File Structure

- [ ] Follows JSON schema
- [ ] All required fields present
- [ ] Field types are correct
- [ ] No trailing commas
- [ ] Proper escaping of special characters

### Data Integrity

- [ ] Hash values calculated
- [ ] No duplicate entries
- [ ] Cross-references work
- [ ] Internal links valid
- [ ] External links verified

### Accessibility

- [ ] Screen reader compatible
- [ ] High contrast mode works
- [ ] Keyboard navigation works
- [ ] Mobile responsive (if web)
- [ ] Font sizes adjustable

**Technical Reviewer:** _________________ **Date:** _________

---

## PHASE 6: Documentation

### Required Documentation

- [ ] README.md present and accurate
- [ ] VERIFICATION_STATUS.md updated
- [ ] Change log maintained
- [ ] Citation information complete
- [ ] License clearly stated

### User Documentation

- [ ] Usage instructions clear
- [ ] Examples provided
- [ ] Known issues documented
- [ ] Contact information provided
- [ ] Attribution guidelines clear

**Documentation Reviewer:** _________________ **Date:** _________

---

## PHASE 7: Final Approval

### Pre-Publication Check

- [ ] All verification phases complete
- [ ] All corrections implemented
- [ ] All approvals obtained
- [ ] Documentation complete
- [ ] Technical checks passed
- [ ] Legal review complete (if needed)

### Publication Decision

- [ ] Approved for public release
- [ ] Approved with restrictions
- [ ] Approved for limited access only
- [ ] Not approved (revise and resubmit)

**Approval Type:** _________________

### Sign-offs Required

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Manager | | | |
| Lead Scholar | | | |
| Community Rep (if applicable) | | | |
| Technical Lead | | | |

---

## PHASE 8: Post-Publication

### Monitoring

- [ ] Usage statistics tracked
- [ ] User feedback collected
- [ ] Error reports logged
- [ ] Correction requests processed

### Maintenance

- [ ] Regular backups confirmed
- [ ] Link rot checked quarterly
- [ ] New scholarship monitored
- [ ] Updates planned

### Version Control

- [ ] Version number assigned
- [ ] Change log updated
- [ ] Old versions archived
- [ ] DOI minted (if applicable)

**Current Version:** _________  
**Last Updated:** _________

---

## Issue Tracking Log

| Issue ID | File | Description | Severity | Status | Resolution |
|----------|------|-------------|----------|--------|------------|
| 001 | | | High/Med/Low | Open/Resolved | |
| 002 | | | | | |
| 003 | | | | | |

**Severity Definitions:**
- **High:** Incorrect content, cultural sensitivity issues
- **Medium:** Formatting errors, missing metadata
- **Low:** Typos, minor improvements

---

## Verification Status Codes

| Code | Meaning |
|------|---------|
| ✅ VERIFIED | Expert verified, community approved |
| ⚠️ PENDING | Under review, not yet verified |
| ❌ UNVERIFIED | Not yet reviewed by expert |
| 🚫 RESTRICTED | Community restrictions apply |
| ⏸️ ON HOLD | Awaiting expert/community response |

---

## Quick Reference

### Critical Issues (Stop Publication)

- ❌ Incorrect sacred content
- ❌ Community objection
- ❌ Copyright violation
- ❌ Cultural appropriation concerns

### Medium Issues (Fix Before Publication)

- ⚠️ Missing metadata
- ⚠️ Unverified Unicode
- ⚠️ Broken links
- ⚠️ Incomplete documentation

### Minor Issues (Can Publish, Fix Later)

- ✅ Typos in documentation
- ✅ Formatting inconsistencies
- ✅ Missing optional fields

---

**Status:** READY TO USE - Customize for your workflow
