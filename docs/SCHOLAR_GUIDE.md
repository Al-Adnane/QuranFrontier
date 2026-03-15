# FrontierQu Scholar Guide

**Version:** 1.0.0
**Last Updated:** March 14, 2026
**Audience:** Verified Islamic Scholars

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [System Overview](#system-overview)
4. [Corrections Workflow](#corrections-workflow)
5. [Conflict Resolution](#conflict-resolution)
6. [Audit Logs](#audit-logs)
7. [Scholar Board Responsibilities](#scholar-board-responsibilities)
8. [FAQs](#faqs)

---

## Introduction

Welcome to FrontierQu. This guide explains how to use the system as a verified scholar, submit corrections, participate in governance, and access audit trails.

### What is FrontierQu?

FrontierQu is a neuro-symbolic AI system that serves as a comprehensive index to Islamic knowledge. It does **not** generate fatwas or independent theological rulings. Instead, it:

- **Retrieves verified texts** from authenticated sources (Quran, authentic hadiths, classical tafsirs, madhab jurisprudence)
- **Displays scholarly disagreement** transparently when multiple schools hold different positions
- **Supports academic research** through advanced search and linguistic analysis
- **Maintains audit trails** so all information is traceable to verified sources

### Key Principle

**"AI as Librarian, Not Mufti"** — The system facilitates access to knowledge but cannot and does not make theological rulings.

---

## Getting Started

### Creating a Verified Scholar Account

To access scholar-level features, you must:

1. **Register** at frontierqu.ai with institutional email address
2. **Verify credentials** by providing:
   - Academic degree or certificate in Islamic studies
   - Institutional affiliation (university, center, or mosque)
   - Letter of recommendation from your institution's head
   - CV or publication record
3. **Approval process** (3-5 business days):
   - Documentation reviewed by board member
   - Verification call may be requested
   - Account activated upon approval

### Scholar Dashboard

Once approved, you access the **Scholar Dashboard**:

```
Scholar Dashboard
├─ My Profile & Credentials
├─ Active Corrections
│  ├─ Submitted by Me (Pending Review)
│  ├─ Assigned to Me (Awaiting My Vote)
│  └─ Resolved (Approved/Rejected)
├─ Corpus Search
├─ Audit Log Query
├─ Governance Calendar
│  ├─ Upcoming Votes
│  ├─ Board Meetings
│  └─ Important Announcements
└─ Resources
   ├─ Guidelines & Standards
   ├─ Evidence Templates
   └─ Documentation
```

---

## System Overview

### The Golden Corpus

FrontierQu operates on a curated "Golden Corpus" of verified Islamic texts:

**Included Sources:**
- **Quran:** Madani Mushaf (1924 printing), all authentic qira'at (Hafs, Warsh, etc.)
- **Hadith:** Kutub al-Sittah (six canonical hadith collections) + Musnad Ahmad
- **Grading References:** Al-Albani, Ibn Hajar, An-Nawawi, Al-Arna'ut
- **Tafsir:** Tabari, Qurtubi, Ibn Kathir, As-Sa'di
- **Fiqh:** Al-Umm (Shafi'i), Al-Muwatta (Maliki), Al-Hidayah (Hanafi), Kashshaf (Hanbali)
- **Linguistics:** Lisan al-Arab, Taj al-Arus, classical Arabic lexicons

**Excluded Sources:**
- Contemporary theological opinions not from established schools
- Hadiths graded as fabricated (Mawdu') by consensus of major scholars
- Texts that contradict authenticated sources
- Unverified digital editions

### Knowledge Graph Structure

The system stores relationships as a knowledge graph:

```
Verse 2:183
├─ Explained by: Tafsir Ibn Kathir (p. 45)
├─ Basis for: Hanafi Ruling on Fasting Obligation
├─ Narrated by: Hadith Bukhari 1904 (Sahih grade)
├─ Linguistic Analysis: Root ص-و-م (to fast)
└─ Madhab Applications:
   ├─ Hanafi: Obligatory (Wajib)
   ├─ Maliki: Obligatory (Wajib)
   ├─ Shafi: Obligatory (Wajib)
   └─ Hanbali: Obligatory (Wajib)
```

---

## Corrections Workflow

### Types of Corrections

You can submit corrections for several categories:

| Correction Type | Description | Examples |
|-----------------|-------------|----------|
| **Textual Error** | Typo or translation mistake | Misspelled Arabic word, incorrect Quranic punctuation |
| **Attribution Error** | Citation to wrong source | Verse attributed to wrong surah |
| **Grading Error** | Hadith grade is incorrect | Hadith marked as Sahih but should be Dhaif |
| **Translation Error** | English rendering incorrect | Mistranslation changing meaning |
| **Madhab Misclassification** | School ruling mislabeled | Hanafi position attributed to Shafi school |
| **Linguistic Error** | Morphological or grammatical mistake | Root derivation incorrect |
| **Evidence Gap** | Missing supporting hadith/verse | Ruling stated without referenced evidence |

### Submitting a Correction

**Step 1: Identify the Error**

Navigate to the affected content and click **"Report an Error"**.

**Step 2: Fill the Correction Form**

```
Correction Form
├─ Error Type: [Select from dropdown]
├─ Entity Details:
│  ├─ Text/Verse: [Auto-populated]
│  ├─ Source: [Auto-populated]
│  └─ Current Content: [Auto-populated]
├─ Correction Details:
│  ├─ Correct Information: [Your proposed correction]
│  ├─ Reasoning: [Why this is correct]
│  └─ Confidence Level: [High / Medium / Low]
├─ Evidence:
│  ├─ Primary Evidence: [Citation with page/edition]
│  ├─ Supporting Evidence: [Additional corroboration]
│  └─ Source Documents: [Upload PDF/images if available]
└─ Impact Assessment:
   ├─ Affects User Queries: [Yes / No]
   ├─ Theological Significance: [Low / Medium / High]
   └─ Affected Communities: [e.g., Hanafi students, Arabic linguists]
```

**Step 3: Submit and Receive ID**

After submission, you receive:
- **Correction ID:** (e.g., `CORR_2026_00123`)
- **Assigned Reviewers:** (typically 3 scholars with relevant expertise)
- **Timeline:** Standard review takes 5-7 business days
- **Status Tracking:** Real-time updates as reviewers vote

### Reviewing Assigned Corrections

If you are assigned as a reviewer on a correction:

**Step 1: Receive Notification**

You receive email with:
- Correction summary
- Submitter's evidence
- Deadline (typically 7 days)

**Step 2: Access Review Interface**

```
Correction Review
├─ Original Content: [Full context with highlights]
├─ Proposed Change: [Side-by-side comparison]
├─ Submitter Evidence:
│  ├─ Primary Source: [Citation + quote]
│  ├─ Supporting Sources: [Additional evidence]
│  └─ Submitter Reasoning: [Full explanation]
├─ Scholar Board Context:
│  ├─ Related Corrections: [Similar past cases]
│  └─ Relevant Policies: [Standards that apply]
├─ Your Review:
│  ├─ Decision: [Approve / Request Clarification / Reject]
│  ├─ Reasoning: [Explain your decision]
│  ├─ Confidence: [High / Medium / Low]
│  └─ Submit Vote
└─ Other Reviewers: [Their votes visible after you vote]
```

**Step 3: Vote on Correction**

**Vote Options:**

- **APPROVE:** Evidence is compelling; correction should be applied
  - *Reasoning required:* Why does this evidence convince you?
  - *Confidence:* Assess your certainty level (80-100% = High, 60-80% = Medium, <60% = Low)

- **REQUEST CLARIFICATION:** More information needed before deciding
  - *Questions:* What additional evidence or explanation would help?
  - *Deadline:* Submitter has 7 days to respond
  - *Automatic resolution:* If no clarification provided, vote counts as REJECT

- **REJECT:** Evidence is insufficient; status quo should remain
  - *Reasoning required:* Why is the evidence not convincing?
  - *Precedent:* Reference similar cases if applicable
  - *Appeal option:* Submitter may appeal with new evidence

**Step 4: Resolution**

Correction status is determined by:

```
APPROVAL RULES:
├─ Requires: 2/3 reviewers approve (e.g., 2 of 3)
├─ Timeline: Resolved when 2 votes are in OR 7 days pass
├─ Automatic Processing: Applied or rejected automatically
└─ Notification: All parties notified of decision
```

### Appealing a Rejected Correction

If your correction is rejected, you may appeal:

**Requirements:**
- Submit within 30 days of rejection
- Provide substantially new evidence
- Address specific reviewer concerns
- Cannot appeal the same evidence twice

**Process:**
1. **New evidence review** by different reviewer panel
2. **2-week timeline** for appeal resolution
3. **Final decision** is binding (no further appeals)

---

## Conflict Resolution

### Madhab Disagreements

When different Islamic schools hold different positions, the system displays all views transparently:

**Example: Hadith Grade Disagreement**

```
CORRECTION REVIEW: Hadith Grade Disagreement

Original Status: Sahih (Authentic)

Correction Proposes: Dhaif (Weak)

Madhab Perspectives:
├─ Al-Albani Classification: Dhaif (Weak)
│  └─ Reasoning: Chain contains weak narrator
│
├─ Ibn Hajar Classification: Sahih (Authentic)
│  └─ Reasoning: Weak narrator supported by other chains
│
└─ An-Nawawi Classification: Hasan (Good)
   └─ Reasoning: Weak narrator but corroborated by hadiths

DECISION FRAMEWORK:
- System shows ALL scholarly positions
- No single classification imposed
- Users see evidence for each position
- Recommendation: Display most conservative grading (Dhaif)
  when substantial disagreement exists
```

### Resolution Principles

When reviewers disagree on a correction:

1. **Consensus Preferred:** Seek common ground through discussion
2. **Transparent Disagreement:** If no consensus, record minority position
3. **Documentation:** Full reasoning from each reviewer preserved
4. **User Clarity:** Users see if scholars disagree on this point

---

## Audit Logs

### Accessing Audit Logs

As a verified scholar, you can access complete audit logs of:

- **User queries:** What questions were asked (anonymized unless scholar owns query)
- **System corrections:** All approved and rejected corrections
- **Decisions:** Board votes and reasoning
- **Error rates:** Percentage of hallucinations or incorrect citations
- **Temporal trends:** How accuracy changes over time

### Audit Log Query Interface

```
Audit Log Search
├─ Time Range: [Start date] to [End date]
├─ Query Type: [Query / Correction / Approval / Error]
├─ Filter by:
│  ├─ Entity Type: [Verse / Hadith / Tafsir / Madhab]
│  ├─ Entity ID: [Specific verse, hadith, etc.]
│  └─ Status: [Approved / Rejected / Pending]
├─ Sort by: [Timestamp / Relevance / Impact]
└─ Results:
   ├─ [Result 1] - [Timestamp] - [Details]
   ├─ [Result 2]
   └─ [Result N]
```

### Data Retention

Audit logs are retained:
- **Active logs:** 2 years online
- **Archive logs:** 7 years in cold storage
- **Regulatory hold:** Logs relevant to corrections retained indefinitely

---

## Scholar Board Responsibilities

### If You Are Appointed to the Scholar Board

Your role includes:

**Monthly:**
- Review corrections assigned to you (typically 10-15 per month)
- Vote within 7 days of assignment
- Attend monthly virtual board meeting
- Spot-check 5% of system interactions for compliance

**Quarterly:**
- Participate in strategic planning discussions
- Review system performance metrics
- Assess corpus completeness
- Identify emerging issues

**Annually:**
- Participate in annual audit preparation
- Review 100+ complex corrections or edge cases
- Contribute to annual transparency report
- Attend in-person board retreat

### Board Decision Portal

```
Board Decision Portal
├─ Active Votes: [Corrections, policy decisions, etc.]
├─ Decision Archive: [All past decisions with rationale]
├─ Governance Calendar: [Meetings, deadlines, events]
├─ Charter & Policies: [Current version + history]
├─ Voting Statistics: [Your voting record, patterns]
└─ Communication: [Secure messaging with other members]
```

### Conflict of Interest Management

Board members must disclose:
- Financial interests in entities using FrontierQu
- Academic rivalries or collaborations
- Personal relationships with other board members
- Scholarly positions that might bias decisions

**Recusal Protocol:**
If you cannot vote objectively, you **must** recuse yourself. System will:
1. Flag your recusal in the decision record
2. Exclude your vote from the decision
3. Note recusal reason (you decide disclosure level)
4. Document in public governance records

---

## FAQs

### General Questions

**Q: Can I use FrontierQu to issue fatwas to my congregation?**

A: No. FrontierQu is a research and indexing tool. You should only issue fatwas based on your own scholarly expertise. You may reference FrontierQu's sources to support your fatwa, but the responsibility for the ruling is entirely yours.

**Q: Is FrontierQu biased toward a particular madhab?**

A: FrontierQu treats all four madhabs (Hanafi, Maliki, Shafi, Hanbali) equally and displays their positions side-by-side. It also includes Salafi and Jafari perspectives (tagged clearly). When evidence differs across schools, all schools are shown with their evidence.

**Q: How do I report a theological error, not just a factual one?**

A: If you believe the system is making a theological claim it shouldn't (e.g., extrapolating a ruling beyond what evidence supports), please report this as a "Theological Overreach" issue. Board members will review and may restrict the query type or add explicit warnings.

### Technical Questions

**Q: How long does correction review take?**

A: Standard timeline is 5-7 business days. Emergency corrections (involving theology or security) are reviewed within 48 hours.

**Q: Can I remain anonymous when submitting a correction?**

A: No. All corrections are attributed to the submitter to maintain accountability. However, your correction details are only visible to assigned reviewers and board members (not public).

**Q: What if I disagree with the rejection of my correction?**

A: You have 30 days to appeal with new evidence. Appeals are reviewed by a different reviewer panel. If rejected again, that decision is final but documented in your profile.

### Governance Questions

**Q: How are board members selected?**

A: See GOVERNANCE_CHARTER.md for full selection process. Candidates are nominated by existing members and institutions, vetted by an independent committee, and approved by majority board vote.

**Q: Can I see the board's reasoning for decisions?**

A: Yes. All board decisions (including votes, rationale, and minority positions) are documented in the Decision Archive. Some sensitive details (e.g., personal conflicts) may be redacted.

**Q: What happens if a board member violates this charter?**

A: Violations trigger an investigation and potential enforcement actions, ranging from warning to removal. Whistleblower protections apply.

---

## Support and Resources

**Scholar Help Desk:** scholars@frontierqu.ai
**Governance Questions:** governance@frontierqu.ai
**Technical Support:** support@frontierqu.ai
**Emergency (Theological Issues):** emergency@frontierqu.ai

**Documentation:**
- API Specification: `/docs/API_SPECIFICATION.md`
- Correction Procedure: `/docs/CORRECTION_PROCEDURE.md`
- System Architecture: `/docs/SYSTEM_ARCHITECTURE.md`

---

**Last Updated:** March 14, 2026
**Next Review:** June 14, 2026

May Allah accept this effort in service of His Book. 🕌
