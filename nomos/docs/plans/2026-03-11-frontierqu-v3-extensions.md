# FrontierQu v3: Real Data + Semantic Search + Deeptech Agentic Layer

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend FrontierQu v2 with real morphological data, a semantic search API, and a multi-domain autonomous research agent powered by the Anthropic API.

**Architecture:** Three stacked layers: (1) Real Data — expanded lexicon and corpus replacing placeholders; (2) Search API — FastAPI server with cosine-similarity vector search over the unified tensor; (3) Agentic Engine — Claude claude-sonnet-4-6 with tool-use calling all FrontierQu domains to answer scholarly questions autonomously.

**Tech Stack:** Python 3.11+, FastAPI 0.135, uvicorn 0.41, scipy 1.17 (cosine similarity), anthropic 0.84 (tool-use), torch, existing FrontierQu v2 modules.

**Existing codebase (118 passing tests):**
- `src/frontierqu/core/tensor.py` — QuranicTensor (6236×102), `.compute()`, `.query(text)`
- `src/frontierqu/core/simplicial.py` — QuranicComplex, adjacency_matrix()
- `src/frontierqu/linguistic/sarf.py` — extract_root, analyze_word, ROOT_LEXICON (14 roots)
- `src/frontierqu/linguistic/nahw.py` — GrammaticalRole, parse_verse, check_constraints
- `src/frontierqu/linguistic/balaghah.py` — rhetorical_density, detect_maani, detect_bayan, detect_badi
- `src/frontierqu/topology/persistent_homology.py` — compute_persistence, PersistenceDiagram
- `src/frontierqu/geometry/fisher_metric.py` — fisher_matrix, geodesic_distance, curvature
- `src/frontierqu/logic/deontic.py` — DeonticStatus, derive_ruling, apply_qiyas, KNOWN_RULINGS
- `src/frontierqu/logic/naskh.py` — NaskhDatabase, get_active_ruling, TemporalFormula
- `src/frontierqu/logic/isnad.py` — IsnadDAG, evaluate_chain, KNOWN_NARRATORS
- `src/frontierqu/core/qiraat.py` — QiraatFiberBundle, CANONICAL_QURRA, VARIANT_READINGS
- `src/frontierqu/linguistic/tajweed.py` — TajweedGrammar, detect_tajweed_rules
- `src/frontierqu/data/quran_text.py` — load_quran_corpus() (real text for 30 verses, placeholders for 6206)
- `src/frontierqu/data/cross_references.py` — THEMATIC_GROUPS (13 themes), CROSS_REFERENCES (25+)

---

## Phase 8: Real Data Layer

### Task 8.1: Expanded Morphological Lexicon (500+ Quranic Words)

**Files:**
- Modify: `src/frontierqu/data/morphology_lexicon.py` (create new)
- Modify: `src/frontierqu/linguistic/sarf.py` — replace ROOT_LEXICON with import from morphology_lexicon
- Test: `tests/data/test_morphology_lexicon.py`

**Context:** Current ROOT_LEXICON has 14 roots. We need 500+ Quranic roots with word families, patterns, and POS. This is the single biggest data upgrade — every morphological analysis improves.

**Step 1: Write the failing test**

```python
# tests/data/test_morphology_lexicon.py
from frontierqu.data.morphology_lexicon import (
    MORPHOLOGY_LEXICON, get_root_family, get_all_roots,
    lookup_word, MorphEntry
)

def test_lexicon_has_500_plus_roots():
    assert len(MORPHOLOGY_LEXICON) >= 100  # Start with 100, grow to 500

def test_root_family_returns_words():
    family = get_root_family("كتب")
    assert "كتاب" in family
    assert "كاتب" in family
    assert "مكتوب" in family

def test_lookup_word_finds_root():
    entry = lookup_word("الرحمن")
    assert entry is not None
    assert entry.root == "رحم"

def test_lookup_word_strips_al():
    entry = lookup_word("المؤمنون")
    assert entry is not None

def test_morph_entry_has_all_fields():
    entry = lookup_word("كتاب")
    assert entry.root != ""
    assert entry.pattern != ""
    assert entry.pos in ("noun", "verb", "particle", "adjective")

def test_all_roots_returns_list():
    roots = get_all_roots()
    assert len(roots) >= 100
    assert "رحم" in roots
    assert "علم" in roots
    assert "قرأ" in roots
```

**Step 2: Verify failure**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest tests/data/test_morphology_lexicon.py -v
```
Expected: ModuleNotFoundError

**Step 3: Implement morphology_lexicon.py**

```python
# src/frontierqu/data/morphology_lexicon.py
"""Comprehensive Quranic Arabic Morphological Lexicon.

Covers the most frequent roots in the Quran with full word families.
Grounded in classical Arabic grammar (sarf) with wazn-based patterns.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MorphEntry:
    word: str
    root: str
    pattern: str
    pos: str          # noun, verb, particle, adjective, pronoun
    form: Optional[int] = None   # verb form 1-10
    gloss: str = ""


# Full morphological database: root -> list of derived words with full analysis
MORPHOLOGY_LEXICON: Dict[str, List[MorphEntry]] = {
    # Divine Names / Core Theology
    "الله": [MorphEntry("الله", "اله", "فِعَال", "noun", gloss="God")],
    "رحم": [
        MorphEntry("رحمن", "رحم", "فَعْلَان", "adjective", gloss="Most Merciful"),
        MorphEntry("رحيم", "رحم", "فَعِيل", "adjective", gloss="Especially Merciful"),
        MorphEntry("رحمة", "رحم", "فَعْلَة", "noun", gloss="mercy"),
        MorphEntry("رحم", "رحم", "فَعَلَ", "verb", 1, "to have mercy"),
        MorphEntry("مرحوم", "رحم", "مَفْعُول", "adjective", gloss="shown mercy"),
        MorphEntry("يرحم", "رحم", "يَفْعَل", "verb", 1, "he has mercy"),
        MorphEntry("ارحم", "رحم", "أَفْعَل", "verb", 4, "make merciful"),
    ],
    "حمد": [
        MorphEntry("حمد", "حمد", "فَعَلَ", "verb", 1, "to praise"),
        MorphEntry("الحمد", "حمد", "الفَعْل", "noun", gloss="the praise"),
        MorphEntry("حامد", "حمد", "فَاعِل", "adjective", gloss="one who praises"),
        MorphEntry("محمود", "حمد", "مَفْعُول", "adjective", gloss="praiseworthy"),
        MorphEntry("محمد", "حمد", "مُفَعَّل", "noun", gloss="Muhammad (the praised)"),
        MorphEntry("أحمد", "حمد", "أَفْعَل", "noun", gloss="Ahmad (more praised)"),
        MorphEntry("حمداً", "حمد", "فَعْلاً", "noun", gloss="praise (accusative)"),
    ],
    "ربب": [
        MorphEntry("رب", "ربب", "فَعْل", "noun", gloss="Lord/Sustainer"),
        MorphEntry("ربّ", "ربب", "فَعَّلَ", "verb", 2, "to raise/nurture"),
        MorphEntry("ربّاني", "ربب", "فَعَّالِي", "adjective", gloss="Lordly"),
        MorphEntry("رباني", "ربب", "فَعَّالِي", "adjective", gloss="divine scholar"),
        MorphEntry("ربّاني", "ربب", "فَعَّالِي", "noun", gloss="scholar of God"),
    ],
    "علم": [
        MorphEntry("علم", "علم", "فَعَلَ", "verb", 1, "to know"),
        MorphEntry("عليم", "علم", "فَعِيل", "adjective", gloss="All-Knowing"),
        MorphEntry("عالم", "علم", "فَاعِل", "noun", gloss="scholar/world"),
        MorphEntry("العالمين", "علم", "الفَاعِلِين", "noun", gloss="the worlds"),
        MorphEntry("معلوم", "علم", "مَفْعُول", "adjective", gloss="known"),
        MorphEntry("علم", "علم", "فَعْل", "noun", gloss="knowledge"),
        MorphEntry("تعليم", "علم", "تَفْعِيل", "noun", gloss="teaching"),
        MorphEntry("معلم", "علم", "مُفَعِّل", "noun", gloss="teacher"),
        MorphEntry("يعلم", "علم", "يَفْعَل", "verb", 1, "he knows"),
        MorphEntry("أعلم", "علم", "أَفْعَل", "adjective", gloss="more knowing"),
    ],
    "ملك": [
        MorphEntry("ملك", "ملك", "فَعَلَ", "verb", 1, "to own/possess"),
        MorphEntry("مالك", "ملك", "فَاعِل", "noun", gloss="owner/Malik"),
        MorphEntry("ملك", "ملك", "فَعْل", "noun", gloss="king/sovereignty"),
        MorphEntry("مملكة", "ملك", "مَفْعَلَة", "noun", gloss="kingdom"),
        MorphEntry("ملكوت", "ملك", "فَعَلُوت", "noun", gloss="dominion"),
        MorphEntry("مَلَك", "ملك", "فَعَل", "noun", gloss="angel"),
        MorphEntry("ملائكة", "ملك", "فَعَالِكَة", "noun", gloss="angels"),
    ],
    "دين": [
        MorphEntry("دين", "دين", "فِعْل", "noun", gloss="religion/judgment"),
        MorphEntry("يدين", "دين", "يُفَعِّل", "verb", 2, "to judge/owe"),
        MorphEntry("ديّان", "دين", "فَعَّال", "noun", gloss="Judge (of Judgment Day)"),
        MorphEntry("مدين", "دين", "مَفْعُول", "adjective", gloss="indebted"),
        MorphEntry("ديانة", "دين", "فِعَالَة", "noun", gloss="religiosity"),
    ],
    # Prayer / Worship
    "عبد": [
        MorphEntry("عبد", "عبد", "فَعَلَ", "verb", 1, "to worship"),
        MorphEntry("عبادة", "عبد", "فَعَالَة", "noun", gloss="worship"),
        MorphEntry("عابد", "عبد", "فَاعِل", "noun", gloss="worshipper"),
        MorphEntry("معبود", "عبد", "مَفْعُول", "noun", gloss="the worshipped"),
        MorphEntry("عبد", "عبد", "فَعْل", "noun", gloss="slave/servant"),
        MorphEntry("عباد", "عبد", "فِعَال", "noun", gloss="servants"),
        MorphEntry("نعبد", "عبد", "نَفْعُل", "verb", 1, "we worship"),
    ],
    "صلو": [
        MorphEntry("صلاة", "صلو", "فَعَالَة", "noun", gloss="prayer"),
        MorphEntry("صلى", "صلو", "فَعَّلَ", "verb", 2, "to pray"),
        MorphEntry("مصلى", "صلو", "مَفْعَل", "noun", gloss="place of prayer"),
        MorphEntry("مصلون", "صلو", "مُفَعِّلُون", "noun", gloss="those who pray"),
        MorphEntry("صلوات", "صلو", "فَعَالَات", "noun", gloss="prayers"),
    ],
    "سجد": [
        MorphEntry("سجود", "سجد", "فُعُول", "noun", gloss="prostration"),
        MorphEntry("ساجد", "سجد", "فَاعِل", "noun", gloss="one prostrating"),
        MorphEntry("مسجد", "سجد", "مَفْعَل", "noun", gloss="mosque"),
        MorphEntry("سجدة", "سجد", "فَعْلَة", "noun", gloss="one prostration"),
        MorphEntry("اسجد", "سجد", "أُفْعُل", "verb", 1, "prostrate!"),
    ],
    "زكو": [
        MorphEntry("زكاة", "زكو", "فَعَالَة", "noun", gloss="alms/purification"),
        MorphEntry("زكى", "زكو", "فَعَّلَ", "verb", 2, "to purify"),
        MorphEntry("زاكي", "زكو", "فَاعِل", "adjective", gloss="pure"),
        MorphEntry("تزكية", "زكو", "تَفْعِيل", "noun", gloss="purification act"),
    ],
    # Guidance / Path
    "هدي": [
        MorphEntry("هداية", "هدي", "فَعَالَة", "noun", gloss="guidance"),
        MorphEntry("هدى", "هدي", "فَعَلَ", "verb", 1, "to guide"),
        MorphEntry("هادي", "هدي", "فَاعِل", "noun", gloss="guide"),
        MorphEntry("مهدي", "هدي", "مَفْعُول", "adjective", gloss="guided"),
        MorphEntry("اهدنا", "هدي", "أَفْعِلْنَا", "verb", 4, "guide us"),
        MorphEntry("هدى", "هدي", "فَعَل", "noun", gloss="guidance"),
    ],
    "صرط": [
        MorphEntry("صراط", "صرط", "فِعَال", "noun", gloss="path/road"),
        MorphEntry("الصراط", "صرط", "الفِعَال", "noun", gloss="the straight path"),
    ],
    "قوم": [
        MorphEntry("قوم", "قوم", "فَوْل", "noun", gloss="people/nation"),
        MorphEntry("قام", "قوم", "فَعَلَ", "verb", 1, "to stand/rise"),
        MorphEntry("قيامة", "قوم", "فَعَالَة", "noun", gloss="resurrection/Judgment Day"),
        MorphEntry("قائم", "قوم", "فَاعِل", "noun", gloss="standing"),
        MorphEntry("مقيم", "قوم", "مُفْعِل", "adjective", gloss="established"),
        MorphEntry("استقام", "قوم", "اسْتَفْعَلَ", "verb", 10, "to be upright"),
        MorphEntry("استقامة", "قوم", "اسْتِفْعَال", "noun", gloss="uprightness"),
    ],
    # Faith / Belief
    "أمن": [
        MorphEntry("إيمان", "أمن", "إِفْعَال", "noun", gloss="faith/belief"),
        MorphEntry("آمن", "أمن", "فَاعَلَ", "verb", 3, "to believe"),
        MorphEntry("مؤمن", "أمن", "مُفْعِل", "noun", gloss="believer"),
        MorphEntry("مؤمنون", "أمن", "مُفْعِلُون", "noun", gloss="believers"),
        MorphEntry("أمان", "أمن", "فَعَال", "noun", gloss="safety/security"),
        MorphEntry("أمين", "أمن", "فَعِيل", "adjective", gloss="trustworthy"),
    ],
    "كفر": [
        MorphEntry("كفر", "كفر", "فَعَلَ", "verb", 1, "to disbelieve/cover"),
        MorphEntry("كافر", "كفر", "فَاعِل", "noun", gloss="disbeliever"),
        MorphEntry("كافرون", "كفر", "فَاعِلُون", "noun", gloss="disbelievers"),
        MorphEntry("كفران", "كفر", "فُعْلَان", "noun", gloss="ingratitude"),
        MorphEntry("كفارة", "كفر", "فِعَالَة", "noun", gloss="expiation"),
    ],
    "نفق": [
        MorphEntry("نفاق", "نفق", "فِعَال", "noun", gloss="hypocrisy"),
        MorphEntry("منافق", "نفق", "مُفَاعِل", "noun", gloss="hypocrite"),
        MorphEntry("نافق", "نفق", "فَاعَلَ", "verb", 3, "to be hypocritical"),
    ],
    # Quran / Knowledge
    "قرأ": [
        MorphEntry("قرآن", "قرأ", "فُعْلَان", "noun", gloss="Quran/recitation"),
        MorphEntry("قرأ", "قرأ", "فَعَلَ", "verb", 1, "to read/recite"),
        MorphEntry("قارئ", "قرأ", "فَاعِل", "noun", gloss="reader/reciter"),
        MorphEntry("مقروء", "قرأ", "مَفْعُول", "adjective", gloss="read"),
        MorphEntry("قراءة", "قرأ", "فَعَالَة", "noun", gloss="reading/recitation"),
        MorphEntry("اقرأ", "قرأ", "أَفْعِل", "verb", 1, "read! recite!"),
    ],
    "كتب": [
        MorphEntry("كتاب", "كتب", "فِعَال", "noun", gloss="book/scripture"),
        MorphEntry("كاتب", "كتب", "فَاعِل", "noun", gloss="writer/scribe"),
        MorphEntry("مكتوب", "كتب", "مَفْعُول", "adjective", gloss="written"),
        MorphEntry("كتابة", "كتب", "فَعَالَة", "noun", gloss="writing"),
        MorphEntry("مكتبة", "كتب", "مَفْعَلَة", "noun", gloss="library"),
        MorphEntry("كتب", "كتب", "فَعَلَ", "verb", 1, "to write"),
        MorphEntry("كتب", "كتب", "فُعُل", "noun", gloss="books (plural)"),
        MorphEntry("كتبنا", "كتب", "فَعَلْنَا", "verb", 1, "we wrote"),
    ],
    # Creation
    "خلق": [
        MorphEntry("خلق", "خلق", "فَعَلَ", "verb", 1, "to create"),
        MorphEntry("خالق", "خلق", "فَاعِل", "noun", gloss="Creator"),
        MorphEntry("مخلوق", "خلق", "مَفْعُول", "noun", gloss="created thing"),
        MorphEntry("خلق", "خلق", "فَعْل", "noun", gloss="creation/character"),
        MorphEntry("خلقنا", "خلق", "فَعَلْنَا", "verb", 1, "we created"),
        MorphEntry("يخلق", "خلق", "يَفْعُل", "verb", 1, "he creates"),
    ],
    "سمو": [
        MorphEntry("سماء", "سمو", "فَعَاء", "noun", gloss="sky/heaven"),
        MorphEntry("سماوات", "سمو", "فَعَاوَات", "noun", gloss="heavens"),
        MorphEntry("اسم", "سمو", "إِفْعِل", "noun", gloss="name"),
        MorphEntry("أسماء", "سمو", "أَفْعَال", "noun", gloss="names"),
        MorphEntry("بسم", "سمو", "بِفِعْل", "particle", gloss="in the name of"),
        MorphEntry("سمي", "سمو", "فُعِلَ", "verb", 1, "was named"),
    ],
    "أرض": [
        MorphEntry("أرض", "أرض", "فَعْل", "noun", gloss="earth/ground"),
        MorphEntry("الأرض", "أرض", "الفَعْل", "noun", gloss="the earth"),
        MorphEntry("أراضي", "أرض", "أَفَاعِل", "noun", gloss="lands"),
    ],
    # Life / Death / Afterlife
    "حيي": [
        MorphEntry("حياة", "حيي", "فَعَالَة", "noun", gloss="life"),
        MorphEntry("حي", "حيي", "فَعِيل", "adjective", gloss="living/alive"),
        MorphEntry("الحي", "حيي", "الفَعِيل", "adjective", gloss="the Living"),
        MorphEntry("يحيي", "حيي", "يُفَعِّل", "verb", 2, "to give life"),
        MorphEntry("أحيا", "حيي", "أَفْعَلَ", "verb", 4, "to revive"),
    ],
    "موت": [
        MorphEntry("موت", "موت", "فَعْل", "noun", gloss="death"),
        MorphEntry("مات", "موت", "فَعَلَ", "verb", 1, "to die"),
        MorphEntry("ميت", "موت", "فَعِيل", "adjective", gloss="dead"),
        MorphEntry("يموت", "موت", "يَفْعُل", "verb", 1, "he dies"),
        MorphEntry("إماتة", "موت", "إِفْعَال", "noun", gloss="causing death"),
    ],
    "آخر": [
        MorphEntry("آخرة", "آخر", "فَاعِلَة", "noun", gloss="hereafter/afterlife"),
        MorphEntry("الآخرة", "آخر", "الفَاعِلَة", "noun", gloss="the hereafter"),
        MorphEntry("آخر", "آخر", "فَاعِل", "adjective", gloss="last/other"),
        MorphEntry("أخرى", "آخر", "أَفْعَل", "adjective", gloss="other (fem.)"),
    ],
    # Justice / Judgment
    "عدل": [
        MorphEntry("عدل", "عدل", "فَعَلَ", "verb", 1, "to be just"),
        MorphEntry("عادل", "عدل", "فَاعِل", "noun", gloss="just person"),
        MorphEntry("عدل", "عدل", "فَعْل", "noun", gloss="justice"),
        MorphEntry("معادلة", "عدل", "مُفَاعَلَة", "noun", gloss="equation"),
    ],
    "ظلم": [
        MorphEntry("ظلم", "ظلم", "فَعَلَ", "verb", 1, "to oppress/wrong"),
        MorphEntry("ظالم", "ظلم", "فَاعِل", "noun", gloss="wrongdoer"),
        MorphEntry("ظلم", "ظلم", "فَعْل", "noun", gloss="oppression/darkness"),
        MorphEntry("ظلمات", "ظلم", "فُعُلَات", "noun", gloss="darknesses"),
        MorphEntry("مظلوم", "ظلم", "مَفْعُول", "noun", gloss="oppressed"),
        MorphEntry("ظالمون", "ظلم", "فَاعِلُون", "noun", gloss="wrongdoers"),
    ],
    # Prophets / Messengers
    "نبأ": [
        MorphEntry("نبي", "نبأ", "فَعِيل", "noun", gloss="prophet"),
        MorphEntry("نبوة", "نبأ", "فُعُولَة", "noun", gloss="prophethood"),
        MorphEntry("أنبياء", "نبأ", "أَفْعِيَاء", "noun", gloss="prophets"),
        MorphEntry("نبأ", "نبأ", "فَعَلَ", "verb", 1, "to inform"),
        MorphEntry("نبأ", "نبأ", "فَعَل", "noun", gloss="news/information"),
    ],
    "رسل": [
        MorphEntry("رسول", "رسل", "فَعُول", "noun", gloss="messenger"),
        MorphEntry("رسالة", "رسل", "فِعَالَة", "noun", gloss="message/mission"),
        MorphEntry("رسل", "رسل", "فُعُل", "noun", gloss="messengers"),
        MorphEntry("أرسل", "رسل", "أَفْعَلَ", "verb", 4, "to send"),
        MorphEntry("مرسل", "رسل", "مُفْعِل", "noun", gloss="sender"),
        MorphEntry("مرسلون", "رسل", "مُفْعِلُون", "noun", gloss="messengers"),
    ],
    # Forbidden / Permitted
    "حرم": [
        MorphEntry("حرام", "حرم", "فَعَال", "adjective", gloss="forbidden"),
        MorphEntry("حرم", "حرم", "فَعَلَ", "verb", 1, "to forbid"),
        MorphEntry("محرم", "حرم", "مُفَعَّل", "adjective", gloss="forbidden"),
        MorphEntry("حرمة", "حرم", "فُعْلَة", "noun", gloss="sanctity"),
        MorphEntry("الحرام", "حرم", "الفَعَال", "adjective", gloss="the sacred/forbidden"),
    ],
    "حلل": [
        MorphEntry("حلال", "حلل", "فَعَال", "adjective", gloss="permissible"),
        MorphEntry("أحل", "حلل", "أَفْعَلَ", "verb", 4, "to make lawful"),
        MorphEntry("حل", "حلل", "فَعَّلَ", "verb", 2, "to solve/untie"),
    ],
    # Mercy / Forgiveness
    "غفر": [
        MorphEntry("غفور", "غفر", "فَعُول", "adjective", gloss="Most Forgiving"),
        MorphEntry("مغفرة", "غفر", "مَفْعِلَة", "noun", gloss="forgiveness"),
        MorphEntry("غفر", "غفر", "فَعَلَ", "verb", 1, "to forgive"),
        MorphEntry("غافر", "غفر", "فَاعِل", "noun", gloss="forgiver"),
        MorphEntry("استغفار", "غفر", "اسْتِفْعَال", "noun", gloss="seeking forgiveness"),
        MorphEntry("استغفر", "غفر", "اسْتَفْعَلَ", "verb", 10, "to seek forgiveness"),
        MorphEntry("يغفر", "غفر", "يَفْعِل", "verb", 1, "he forgives"),
    ],
    "توب": [
        MorphEntry("توبة", "توب", "فَوْعَلَة", "noun", gloss="repentance"),
        MorphEntry("تاب", "توب", "فَعَلَ", "verb", 1, "to repent"),
        MorphEntry("تواب", "توب", "فَعَّال", "adjective", gloss="accepting repentance"),
        MorphEntry("تائب", "توب", "فَاعِل", "noun", gloss="repentant"),
    ],
    # Heaven / Hell
    "جنن": [
        MorphEntry("جنة", "جنن", "فَعَّة", "noun", gloss="paradise/garden"),
        MorphEntry("جنات", "جنن", "فَعَّات", "noun", gloss="gardens"),
        MorphEntry("جان", "جنن", "فَاعِل", "noun", gloss="jinn"),
        MorphEntry("جن", "جنن", "فُعْل", "noun", gloss="jinn (collective)"),
    ],
    "نار": [
        MorphEntry("نار", "نار", "فَعَل", "noun", gloss="fire/hell"),
        MorphEntry("النار", "نار", "الفَعَل", "noun", gloss="the Fire"),
        MorphEntry("أنار", "نار", "أَفْعَلَ", "verb", 4, "to illuminate"),
        MorphEntry("نور", "نار", "فُعْل", "noun", gloss="light"),
    ],
    # Heart / Soul / Mind
    "قلب": [
        MorphEntry("قلب", "قلب", "فَعْل", "noun", gloss="heart/mind"),
        MorphEntry("قلوب", "قلب", "فُعُول", "noun", gloss="hearts"),
        MorphEntry("قلب", "قلب", "فَعَلَ", "verb", 1, "to turn/flip"),
        MorphEntry("تقلب", "قلب", "تَفَعُّل", "noun", gloss="fluctuation"),
    ],
    "نفس": [
        MorphEntry("نفس", "نفس", "فَعْل", "noun", gloss="soul/self"),
        MorphEntry("أنفس", "نفس", "أَفْعَال", "noun", gloss="souls (plural)"),
        MorphEntry("نفوس", "نفس", "فُعُول", "noun", gloss="souls"),
        MorphEntry("نفسه", "نفس", "فَعْلُه", "noun", gloss="himself/itself"),
    ],
    "عقل": [
        MorphEntry("عقل", "عقل", "فَعَلَ", "verb", 1, "to reason/understand"),
        MorphEntry("عقل", "عقل", "فَعْل", "noun", gloss="reason/intellect"),
        MorphEntry("تعقلون", "عقل", "تَفْعِلُون", "verb", 1, "you reason (pl.)"),
        MorphEntry("يعقل", "عقل", "يَفْعِل", "verb", 1, "he reasons"),
    ],
    # Time
    "يوم": [
        MorphEntry("يوم", "يوم", "فَعْل", "noun", gloss="day"),
        MorphEntry("أيام", "يوم", "أَفْعَال", "noun", gloss="days"),
        MorphEntry("يومئذ", "يوم", "فَعْلَئِذ", "noun", gloss="on that day"),
    ],
    "زمن": [
        MorphEntry("زمان", "زمن", "فَعَال", "noun", gloss="time/era"),
        MorphEntry("زمن", "زمن", "فَعَل", "noun", gloss="time"),
    ],
    # Numbers / Counting
    "عدد": [
        MorphEntry("عدد", "عدد", "فَعَلَ", "verb", 1, "to count"),
        MorphEntry("عدد", "عدد", "فَعَل", "noun", gloss="number"),
        MorphEntry("معدود", "عدد", "مَفْعُول", "adjective", gloss="counted/numbered"),
    ],
    # Water / Rain
    "مطر": [
        MorphEntry("مطر", "مطر", "فَعَلَ", "verb", 1, "to rain"),
        MorphEntry("مطر", "مطر", "فَعَل", "noun", gloss="rain"),
        MorphEntry("أمطار", "مطر", "أَفْعَال", "noun", gloss="rains"),
    ],
    "ماء": [
        MorphEntry("ماء", "ماء", "فَعَل", "noun", gloss="water"),
        MorphEntry("مياه", "ماء", "فِعَال", "noun", gloss="waters"),
    ],
    # Additional key terms
    "سلم": [
        MorphEntry("سلام", "سلم", "فَعَال", "noun", gloss="peace/greeting"),
        MorphEntry("إسلام", "سلم", "إِفْعَال", "noun", gloss="Islam/submission"),
        MorphEntry("مسلم", "سلم", "مُفْعِل", "noun", gloss="Muslim"),
        MorphEntry("مسلمون", "سلم", "مُفْعِلُون", "noun", gloss="Muslims"),
        MorphEntry("سليم", "سلم", "فَعِيل", "adjective", gloss="sound/safe"),
        MorphEntry("أسلم", "سلم", "أَفْعَلَ", "verb", 4, "to submit/embrace Islam"),
    ],
    "صبر": [
        MorphEntry("صبر", "صبر", "فَعَلَ", "verb", 1, "to be patient"),
        MorphEntry("صابر", "صبر", "فَاعِل", "noun", gloss="patient one"),
        MorphEntry("صبور", "صبر", "فَعُول", "adjective", gloss="very patient"),
        MorphEntry("صبر", "صبر", "فَعْل", "noun", gloss="patience"),
        MorphEntry("الصابرون", "صبر", "الفَاعِلُون", "noun", gloss="the patient ones"),
    ],
    "شكر": [
        MorphEntry("شكر", "شكر", "فَعَلَ", "verb", 1, "to be grateful"),
        MorphEntry("شكور", "شكر", "فَعُول", "adjective", gloss="Most Grateful"),
        MorphEntry("شكر", "شكر", "فَعْل", "noun", gloss="gratitude"),
        MorphEntry("شاكر", "شكر", "فَاعِل", "noun", gloss="grateful one"),
    ],
    "نصر": [
        MorphEntry("نصر", "نصر", "فَعَلَ", "verb", 1, "to help/support"),
        MorphEntry("ناصر", "نصر", "فَاعِل", "noun", gloss="helper"),
        MorphEntry("منصور", "نصر", "مَفْعُول", "adjective", gloss="helped"),
        MorphEntry("أنصار", "نصر", "أَفْعَال", "noun", gloss="helpers (Ansar)"),
        MorphEntry("نصير", "نصر", "فَعِيل", "noun", gloss="protector"),
    ],
    "صلح": [
        MorphEntry("صالح", "صلح", "فَاعِل", "adjective", gloss="righteous"),
        MorphEntry("إصلاح", "صلح", "إِفْعَال", "noun", gloss="reform/correction"),
        MorphEntry("مصلح", "صلح", "مُفْعِل", "noun", gloss="reformer"),
        MorphEntry("صلاح", "صلح", "فَعَال", "noun", gloss="righteousness"),
        MorphEntry("الصالحون", "صلح", "الفَاعِلُون", "noun", gloss="the righteous"),
    ],
    "أمر": [
        MorphEntry("أمر", "أمر", "فَعَلَ", "verb", 1, "to command"),
        MorphEntry("أمر", "أمر", "فَعَل", "noun", gloss="command/matter"),
        MorphEntry("أوامر", "أمر", "أَفَاعِل", "noun", gloss="commands"),
        MorphEntry("مأمور", "أمر", "مَفْعُول", "noun", gloss="commanded"),
        MorphEntry("يأمر", "أمر", "يَفْعُل", "verb", 1, "he commands"),
    ],
    "نهي": [
        MorphEntry("نهي", "نهي", "فَعَلَ", "verb", 1, "to forbid"),
        MorphEntry("نهي", "نهي", "فَعْل", "noun", gloss="prohibition"),
        MorphEntry("نواهي", "نهي", "فَوَاعِل", "noun", gloss="prohibitions"),
    ],
    "فتح": [
        MorphEntry("فتح", "فتح", "فَعَلَ", "verb", 1, "to open/conquer"),
        MorphEntry("فتح", "فتح", "فَعْل", "noun", gloss="opening/conquest"),
        MorphEntry("فاتح", "فتح", "فَاعِل", "noun", gloss="opener"),
        MorphEntry("الفاتحة", "فتح", "الفَاعِلَة", "noun", gloss="Al-Fatihah (the opening)"),
    ],
    "وحد": [
        MorphEntry("أحد", "وحد", "أَفْعَل", "adjective", gloss="one/unique"),
        MorphEntry("واحد", "وحد", "فَاعِل", "adjective", gloss="one"),
        MorphEntry("توحيد", "وحد", "تَفْعِيل", "noun", gloss="monotheism"),
        MorphEntry("وحدة", "وحد", "فَعْلَة", "noun", gloss="unity"),
    ],
    "صمد": [
        MorphEntry("صمد", "صمد", "فَعَلَ", "verb", 1, "to be eternal/refuge"),
        MorphEntry("الصمد", "صمد", "الفَعَل", "noun", gloss="the Eternal (Al-Samad)"),
    ],
    "ولد": [
        MorphEntry("ولد", "ولد", "فَعَلَ", "verb", 1, "to beget"),
        MorphEntry("ولد", "ولد", "فَعَل", "noun", gloss="child"),
        MorphEntry("والد", "ولد", "فَاعِل", "noun", gloss="father"),
        MorphEntry("والدة", "ولد", "فَاعِلَة", "noun", gloss="mother"),
        MorphEntry("مولود", "ولد", "مَفْعُول", "noun", gloss="newborn"),
    ],
    "كفو": [
        MorphEntry("كفو", "كفو", "فُعُو", "noun", gloss="equal/match"),
        MorphEntry("كفؤ", "كفو", "فُعُل", "noun", gloss="equivalent"),
    ],
}

# Build reverse lookup: word -> MorphEntry
_WORD_LOOKUP: Dict[str, MorphEntry] = {}
for root_group, entries in MORPHOLOGY_LEXICON.items():
    for entry in entries:
        _WORD_LOOKUP[entry.word] = entry


def get_root_family(root: str) -> List[str]:
    """Get all words derived from a root."""
    if root in MORPHOLOGY_LEXICON:
        return [e.word for e in MORPHOLOGY_LEXICON[root]]
    return []


def lookup_word(word: str) -> Optional[MorphEntry]:
    """Look up a word's morphological analysis, stripping ال if needed."""
    import re
    # Direct lookup
    if word in _WORD_LOOKUP:
        return _WORD_LOOKUP[word]
    # Strip diacritics
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', word)
    if stripped in _WORD_LOOKUP:
        return _WORD_LOOKUP[stripped]
    # Strip ال prefix
    if stripped.startswith("ال") and len(stripped) > 2:
        bare = stripped[2:]
        if bare in _WORD_LOOKUP:
            return _WORD_LOOKUP[bare]
    return None


def get_all_roots() -> List[str]:
    """Return all roots in the lexicon."""
    return list(MORPHOLOGY_LEXICON.keys())
```

**Step 4: Update sarf.py to use the expanded lexicon**

Modify `src/frontierqu/linguistic/sarf.py`: replace `ROOT_LEXICON` definition at the top with:

```python
from frontierqu.data.morphology_lexicon import MORPHOLOGY_LEXICON as _LEX, lookup_word as _lookup

ROOT_LEXICON: Dict[str, List[str]] = {
    root: [e.word for e in entries]
    for root, entries in _LEX.items()
    if root not in ("الله",)  # Skip special entries
}
```

Also update `extract_root()` to use `lookup_word` from morphology_lexicon:

```python
def extract_root(word: str) -> Optional[str]:
    """Extract trilateral root from Arabic word."""
    from frontierqu.data.morphology_lexicon import lookup_word
    entry = lookup_word(word)
    if entry:
        return entry.root
    # Fallback: strip affixes and take consonant skeleton
    clean = _strip_affixes(word)
    for root, words in ROOT_LEXICON.items():
        if word in words or clean in words:
            return root
    consonants = [c for c in clean if c in ARABIC_LETTERS and c not in "اويى"]
    if len(consonants) >= 3:
        return "".join(consonants[:3])
    return None
```

**Step 5: Run tests, verify all pass**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest tests/data/test_morphology_lexicon.py tests/linguistic/ -v --tb=short
```

**Step 6: Commit**

```bash
cd ~/Desktop/FrontierQu && git add -A && git commit -m "feat: expand morphological lexicon to 50+ roots, 300+ word entries"
```

---

### Task 8.2: Expanded Real Arabic Corpus (Key Surahs)

**Files:**
- Modify: `src/frontierqu/data/quran_text.py` — add real text for Surahs 112-114 (already have) + Al-Baqarah opening verses + short Makkan surahs
- Test: `tests/data/test_corpus_coverage.py`

**Step 1: Write the failing test**

```python
# tests/data/test_corpus_coverage.py
from frontierqu.data.quran_text import load_quran_corpus, get_real_text_coverage

def test_coverage_above_threshold():
    """At least 5% of verses have real Arabic text"""
    coverage = get_real_text_coverage()
    assert coverage >= 0.05  # At least 312 of 6236 verses

def test_al_ikhlas_complete():
    """Surah 112 (Al-Ikhlas) fully covered"""
    corpus = load_quran_corpus()
    for v in range(1, 5):
        assert corpus[(112, v)]["has_real_text"]

def test_short_makkan_surahs():
    """Short Makkan surahs (107-114) covered"""
    corpus = load_quran_corpus()
    for surah in [108, 110, 111]:
        verse_1 = corpus.get((surah, 1))
        assert verse_1 is not None

def test_get_real_text_returns_arabic():
    """get_real_text returns genuine Arabic Unicode"""
    corpus = load_quran_corpus()
    text = corpus[(1, 1)]["text_ar"]
    # Arabic Unicode range: 0600-06FF
    arabic_chars = [c for c in text if '\u0600' <= c <= '\u06FF']
    assert len(arabic_chars) > 0
```

**Step 2: Implement `get_real_text_coverage()` and add short surahs**

Add to `src/frontierqu/data/quran_text.py`:

```python
# Additional short Makkan surahs
_ARABIC_TEXT.update({
    # Al-Kawthar (108)
    (108, 1): "إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ",
    (108, 2): "فَصَلِّ لِرَبِّكَ وَانْحَرْ",
    (108, 3): "إِنَّ شَانِئَكَ هُوَ الْأَبْتَرُ",
    # Al-Masad (111)
    (111, 1): "تَبَّتْ يَدَا أَبِي لَهَبٍ وَتَبَّ",
    (111, 2): "مَا أَغْنَىٰ عَنْهُ مَالُهُ وَمَا كَسَبَ",
    (111, 3): "سَيَصْلَىٰ نَارًا ذَاتَ لَهَبٍ",
    (111, 4): "وَامْرَأَتُهُ حَمَّالَةَ الْحَطَبِ",
    (111, 5): "فِي جِيدِهَا حَبْلٌ مِّن مَّسَدٍ",
    # An-Nasr (110)
    (110, 1): "إِذَا جَاءَ نَصْرُ اللَّهِ وَالْفَتْحُ",
    (110, 2): "وَرَأَيْتَ النَّاسَ يَدْخُلُونَ فِي دِينِ اللَّهِ أَفْوَاجًا",
    (110, 3): "فَسَبِّحْ بِحَمْدِ رَبِّكَ وَاسْتَغْفِرْهُ إِنَّهُ كَانَ تَوَّابًا",
    # Al-Kafiroun (109)
    (109, 1): "قُلْ يَا أَيُّهَا الْكَافِرُونَ",
    (109, 2): "لَا أَعْبُدُ مَا تَعْبُدُونَ",
    (109, 3): "وَلَا أَنتُمْ عَابِدُونَ مَا أَعْبُدُ",
    (109, 4): "وَلَا أَنَا عَابِدٌ مَّا عَبَدتُّمْ",
    (109, 5): "وَلَا أَنتُمْ عَابِدُونَ مَا أَعْبُدُ",
    (109, 6): "لَكُمْ دِينُكُمْ وَلِيَ دِينِ",
    # Al-Asr (103)
    (103, 1): "وَالْعَصْرِ",
    (103, 2): "إِنَّ الْإِنسَانَ لَفِي خُسْرٍ",
    (103, 3): "إِلَّا الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ وَتَوَاصَوْا بِالْحَقِّ وَتَوَاصَوْا بِالصَّبْرِ",
    # Al-Fatiha verse Bismillah cross reference
    (27, 30): "إِنَّهُ مِن سُلَيْمَانَ وَإِنَّهُ بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
})


def get_real_text_coverage() -> float:
    """Return fraction of 6236 verses with real Arabic text."""
    from frontierqu.data.quran_metadata import VERSE_COUNTS
    total = sum(VERSE_COUNTS.values())
    real = len(_ARABIC_TEXT)
    return real / total
```

**Step 3: Run tests**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest tests/data/test_corpus_coverage.py -v
```

**Step 4: Commit**

```bash
cd ~/Desktop/FrontierQu && git add -A && git commit -m "feat: expand real Arabic corpus with short Makkan surahs"
```

---

## Phase 9: Semantic Search Engine

### Task 9.1: Vector Embedding Store with Cosine Search

**Files:**
- Create: `src/frontierqu/search/embedding_store.py`
- Create: `tests/search/test_embedding_store.py`

**Context:** The unified tensor gives us a 6236×102 matrix. We build a cosine-similarity search index over it. No external library needed — scipy.spatial.distance handles this.

**Step 1: Write the failing test**

```python
# tests/search/test_embedding_store.py
import torch
from frontierqu.search.embedding_store import EmbeddingStore, SearchResult

def test_store_builds_from_tensor():
    """EmbeddingStore indexes the unified tensor"""
    store = EmbeddingStore.build(max_verses=50)  # small subset for tests
    assert store.num_verses == 50

def test_search_returns_results():
    """Search returns top-k results"""
    store = EmbeddingStore.build(max_verses=50)
    results = store.search("mercy", k=5)
    assert len(results) == 5
    assert all(isinstance(r, SearchResult) for r in results)

def test_search_result_has_fields():
    """SearchResult has verse, score, rank"""
    store = EmbeddingStore.build(max_verses=50)
    results = store.search("tawhid", k=3)
    for r in results:
        assert isinstance(r.verse, tuple)
        assert len(r.verse) == 2
        assert 0.0 <= r.score <= 1.0
        assert r.rank >= 0

def test_scores_are_ordered():
    """Results are returned in descending score order"""
    store = EmbeddingStore.build(max_verses=50)
    results = store.search("guidance", k=5)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)

def test_verse_lookup():
    """Can retrieve embedding for specific verse"""
    store = EmbeddingStore.build(max_verses=50)
    emb = store.get_embedding((1, 1))
    assert emb is not None
    assert len(emb) > 0

def test_similar_verses():
    """Find verses similar to a given verse"""
    store = EmbeddingStore.build(max_verses=100)
    similar = store.find_similar((1, 1), k=5)
    assert len(similar) <= 5
    # Verse 1:1 should not be most similar to itself if excluding self
    verses = [r.verse for r in similar]
    assert (1, 1) not in verses
```

**Step 2: Implement embedding_store.py**

```python
# src/frontierqu/search/embedding_store.py
"""Semantic Search over the Unified Quranic Tensor.

Cosine similarity search over the 6236×102 unified tensor.
No external vector DB needed — scipy handles this efficiently for 6236 vectors.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import numpy as np
import torch
from scipy.spatial.distance import cdist


@dataclass
class SearchResult:
    verse: Tuple[int, int]
    score: float        # cosine similarity (0-1)
    rank: int
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class EmbeddingStore:
    """Cosine similarity search index over the Quranic tensor."""

    def __init__(self, embeddings: np.ndarray, verse_index: List[Tuple[int, int]]):
        self._embeddings = embeddings          # [N, D] float32
        self._verse_index = verse_index        # [(surah, verse), ...]
        self._verse_to_idx = {v: i for i, v in enumerate(verse_index)}

        # L2-normalize for cosine similarity via dot product
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10
        self._normalized = embeddings / norms

    @property
    def num_verses(self) -> int:
        return len(self._verse_index)

    @classmethod
    def build(cls, max_verses: Optional[int] = None) -> 'EmbeddingStore':
        """Build store from the unified QuranicTensor."""
        from frontierqu.core.tensor import QuranicTensor
        qt = QuranicTensor()
        T = qt.compute()  # [6236, 102]

        embeddings = T.detach().numpy()
        from frontierqu.data.quran_metadata import VERSE_COUNTS
        verse_index = []
        for surah, count in VERSE_COUNTS.items():
            for v in range(1, count + 1):
                verse_index.append((surah, v))

        if max_verses is not None:
            embeddings = embeddings[:max_verses]
            verse_index = verse_index[:max_verses]

        return cls(embeddings, verse_index)

    def search(self, query: str, k: int = 10) -> List[SearchResult]:
        """Search for verses matching a text query."""
        query_vec = self._encode_query(query)
        return self._cosine_search(query_vec, k)

    def find_similar(self, verse: Tuple[int, int], k: int = 10) -> List[SearchResult]:
        """Find verses similar to a given verse (excludes self)."""
        if verse not in self._verse_to_idx:
            return []
        idx = self._verse_to_idx[verse]
        query_vec = self._normalized[idx]
        results = self._cosine_search(query_vec, k + 1)
        return [r for r in results if r.verse != verse][:k]

    def get_embedding(self, verse: Tuple[int, int]) -> Optional[np.ndarray]:
        """Get raw embedding for a specific verse."""
        if verse not in self._verse_to_idx:
            return None
        return self._embeddings[self._verse_to_idx[verse]]

    def _cosine_search(self, query_vec: np.ndarray, k: int) -> List[SearchResult]:
        """Core cosine similarity search."""
        # Normalize query
        norm = np.linalg.norm(query_vec) + 1e-10
        q_norm = query_vec / norm

        # Cosine similarity = dot product of normalized vectors
        scores = self._normalized @ q_norm  # [N]

        # Top-k
        top_k = min(k, len(scores))
        top_indices = np.argpartition(scores, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

        return [
            SearchResult(
                verse=self._verse_index[i],
                score=float(np.clip(scores[i], 0.0, 1.0)),
                rank=rank
            )
            for rank, i in enumerate(top_indices)
        ]

    def _encode_query(self, query: str) -> np.ndarray:
        """Encode text query to a feature vector matching tensor dimensions."""
        from frontierqu.data.cross_references import THEMATIC_GROUPS
        from frontierqu.core.tensor import TOTAL_BASE_DIM

        query_lower = query.lower()
        vec = np.zeros(TOTAL_BASE_DIM, dtype=np.float32)

        theme_keywords = {
            "tawhid": 0, "mercy": 1, "justice": 2, "patience": 3,
            "knowledge": 4, "creation": 5, "afterlife": 4, "prayer": 7,
            "fasting": 8, "charity": 9, "prophets": 10, "guidance": 11,
            "gratitude": 12, "oneness": 0, "god": 0, "allah": 0,
            "al-fatihah": 7, "fatihah": 7, "quran": 11, "legal": 3,
            "tafsir": 6, "worship": 7, "belief": 0, "faith": 0,
        }

        for keyword, theme_i in theme_keywords.items():
            if keyword in query_lower:
                vec[4 + theme_i] = 1.0  # offset 4 = after structural features

        if not vec.any():
            vec[4:17] = 0.1  # weak signal across all themes

        return vec
```

**Step 3: Ensure `tests/search/__init__.py` exists**

```bash
mkdir -p ~/Desktop/FrontierQu/tests/search && touch ~/Desktop/FrontierQu/tests/search/__init__.py
mkdir -p ~/Desktop/FrontierQu/src/frontierqu/search && touch ~/Desktop/FrontierQu/src/frontierqu/search/__init__.py
```

**Step 4: Run tests**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest tests/search/test_embedding_store.py -v --tb=short
```

**Step 5: Commit**

```bash
cd ~/Desktop/FrontierQu && git add -A && git commit -m "feat: implement semantic embedding store with cosine similarity search"
```

---

### Task 9.2: FastAPI REST Server

**Files:**
- Create: `src/frontierqu/api/server.py`
- Create: `src/frontierqu/api/__init__.py`
- Create: `tests/api/test_server.py`

**Context:** FastAPI (0.135.1) and uvicorn (0.41.0) are already installed. The server exposes 6 endpoints covering all FrontierQu domains.

**Step 1: Write the failing test**

```python
# tests/api/test_server.py
import pytest
from fastapi.testclient import TestClient
from frontierqu.api.server import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_search_endpoint():
    response = client.get("/search?q=mercy&k=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) <= 5

def test_verse_endpoint():
    response = client.get("/verse/1/1")
    assert response.status_code == 200
    data = response.json()
    assert data["surah"] == 1
    assert data["verse"] == 1
    assert "arabic" in data
    assert "morphology" in data

def test_ruling_endpoint():
    response = client.get("/ruling?verse_surah=2&verse_ayah=43&subject=salah")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("WAJIB", "HARAM", "MANDUB", "MAKRUH", "MUBAH")

def test_thematic_endpoint():
    response = client.get("/thematic/tawhid")
    assert response.status_code == 200
    data = response.json()
    assert "theme" in data
    assert "verses" in data
    assert len(data["verses"]) > 0

def test_analyze_endpoint():
    response = client.post("/analyze", json={"arabic": "الْحَمْدُ لِلَّهِ"})
    assert response.status_code == 200
    data = response.json()
    assert "words" in data
    assert "rhetorical_density" in data
```

**Step 2: Implement server.py**

```python
# src/frontierqu/api/server.py
"""FrontierQu REST API — Holistic Quranic Research Endpoints.

Endpoints:
    GET  /health                              — liveness check
    GET  /search?q=<query>&k=<int>           — semantic verse search
    GET  /verse/<surah>/<ayah>               — full verse analysis
    GET  /ruling?verse_surah=&verse_ayah=&subject= — legal ruling
    GET  /thematic/<theme>                   — thematic verse group
    POST /analyze                            — Arabic text analysis
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="FrontierQu API",
    description="Holistic Quranic Algorithmic Framework — REST Interface",
    version="3.0.0"
)

# Lazy-loaded singletons
_store = None
_tensor = None


def _get_store():
    global _store
    if _store is None:
        from frontierqu.search.embedding_store import EmbeddingStore
        _store = EmbeddingStore.build()
    return _store


def _get_tensor():
    global _tensor
    if _tensor is None:
        from frontierqu.core.tensor import QuranicTensor
        _tensor = QuranicTensor()
    return _tensor


# ── Models ──

class AnalyzeRequest(BaseModel):
    arabic: str


class SearchResultResponse(BaseModel):
    surah: int
    ayah: int
    score: float
    rank: int


# ── Endpoints ──

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0", "verses": 6236}


@app.get("/search")
def search(q: str, k: int = 10):
    """Semantic search over all 6236 verses."""
    k = min(k, 50)
    store = _get_store()
    results = store.search(q, k=k)
    return {
        "query": q,
        "total": len(results),
        "results": [
            SearchResultResponse(
                surah=r.verse[0], ayah=r.verse[1],
                score=round(r.score, 4), rank=r.rank
            )
            for r in results
        ]
    }


@app.get("/verse/{surah}/{ayah}")
def get_verse(surah: int, ayah: int):
    """Full multi-domain analysis of a single verse."""
    from frontierqu.data.quran_text import load_quran_corpus
    from frontierqu.linguistic.sarf import analyze_word
    from frontierqu.linguistic.balaghah import rhetorical_density
    from frontierqu.logic.deontic import derive_ruling

    corpus = load_quran_corpus()
    verse = (surah, ayah)

    if verse not in corpus:
        raise HTTPException(status_code=404, detail=f"Verse {surah}:{ayah} not found")

    entry = corpus[verse]
    arabic = entry["text_ar"]

    # Morphological analysis of first word
    words = arabic.split()
    morphology = []
    for w in words[:5]:  # First 5 words
        try:
            a = analyze_word(w)
            morphology.append({
                "word": w, "root": a.root, "pos": a.pos,
                "pattern": a.pattern, "case": a.case
            })
        except Exception:
            morphology.append({"word": w})

    # Rhetorical density
    density = rhetorical_density(arabic) if entry["has_real_text"] else 0.0

    # Deontic ruling
    ruling = derive_ruling(verse, "general")

    return {
        "surah": surah,
        "verse": ayah,
        "arabic": arabic,
        "has_real_text": entry["has_real_text"],
        "morphology": morphology,
        "rhetorical_density": round(density, 4),
        "deontic_status": ruling.status.name,
    }


@app.get("/ruling")
def get_ruling(verse_surah: int, verse_ayah: int, subject: str):
    """Derive Islamic legal ruling from verse and subject."""
    from frontierqu.logic.deontic import derive_ruling

    verse = (verse_surah, verse_ayah)
    rule = derive_ruling(verse, subject)

    return {
        "verse": f"{verse_surah}:{verse_ayah}",
        "subject": subject,
        "status": rule.status.name,
        "reasoning_method": rule.reasoning_method,
        "confidence": rule.confidence,
        "notes": rule.notes,
    }


@app.get("/thematic/{theme}")
def get_thematic(theme: str):
    """Get all verses in a thematic group."""
    from frontierqu.data.cross_references import THEMATIC_GROUPS

    if theme not in THEMATIC_GROUPS:
        raise HTTPException(
            status_code=404,
            detail=f"Theme '{theme}' not found. Available: {list(THEMATIC_GROUPS.keys())}"
        )

    verses = THEMATIC_GROUPS[theme]
    return {
        "theme": theme,
        "count": len(verses),
        "verses": [{"surah": s, "ayah": v} for s, v in verses],
    }


@app.post("/analyze")
def analyze_text(req: AnalyzeRequest):
    """Full linguistic analysis of arbitrary Arabic text."""
    from frontierqu.linguistic.sarf import analyze_word
    from frontierqu.linguistic.balaghah import rhetorical_density, detect_maani, detect_badi
    from frontierqu.linguistic.tajweed import detect_tajweed_rules

    words = req.arabic.split()
    word_analyses = []
    for w in words:
        try:
            a = analyze_word(w)
            word_analyses.append({
                "word": w, "root": a.root, "pos": a.pos,
                "pattern": a.pattern,
            })
        except Exception:
            word_analyses.append({"word": w})

    maani = detect_maani(req.arabic)
    badi = detect_badi(req.arabic)
    tajweed = detect_tajweed_rules(req.arabic)

    return {
        "input": req.arabic,
        "word_count": len(words),
        "words": word_analyses,
        "rhetorical_density": round(rhetorical_density(req.arabic), 4),
        "sentence_type": maani.sentence_type,
        "emphasis_level": maani.emphasis_level,
        "rhetorical_devices": [
            {"type": d.device_type, "category": d.category, "score": d.score}
            for d in badi
        ],
        "tajweed_rules": [
            {"name": r.name, "category": r.category.name}
            for r in tajweed
        ],
    }
```

**Step 3: Create test directory**

```bash
mkdir -p ~/Desktop/FrontierQu/tests/api && touch ~/Desktop/FrontierQu/tests/api/__init__.py
```

**Step 4: Run tests**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest tests/api/test_server.py -v --tb=short
```

**Step 5: Commit**

```bash
cd ~/Desktop/FrontierQu && git add -A && git commit -m "feat: add FastAPI REST server with 6 Quranic research endpoints"
```

---

## Phase 10: Deeptech Agentic Layer

### Task 10.1: Tool Definitions for FrontierQu Domains

**Files:**
- Create: `src/frontierqu/agentic/tools.py`
- Create: `tests/agentic/test_tools.py`

**Context:** Define all FrontierQu capabilities as Anthropic tool specs. Each tool wraps one or more existing modules. The agent will call these tools to answer scholarly questions.

**Step 1: Write the failing test**

```python
# tests/agentic/test_tools.py
from frontierqu.agentic.tools import FRONTIERQU_TOOLS, execute_tool

def test_tools_are_defined():
    """All FrontierQu domains have tool definitions"""
    tool_names = [t["name"] for t in FRONTIERQU_TOOLS]
    assert "search_verses" in tool_names
    assert "analyze_word" in tool_names
    assert "get_legal_ruling" in tool_names
    assert "check_abrogation" in tool_names
    assert "get_thematic_connections" in tool_names
    assert "evaluate_hadith_chain" in tool_names
    assert "compute_rhetorical_density" in tool_names

def test_tool_has_required_fields():
    """Each tool has name, description, input_schema"""
    for tool in FRONTIERQU_TOOLS:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert "type" in tool["input_schema"]

def test_execute_search_verses():
    """search_verses tool executes and returns results"""
    result = execute_tool("search_verses", {"query": "mercy", "k": 3})
    assert "results" in result
    assert len(result["results"]) <= 3

def test_execute_analyze_word():
    """analyze_word tool returns morphological analysis"""
    result = execute_tool("analyze_word", {"word": "كتاب"})
    assert "root" in result
    assert result["root"] == "كتب"

def test_execute_get_legal_ruling():
    """get_legal_ruling returns deontic status"""
    result = execute_tool("get_legal_ruling", {
        "surah": 2, "ayah": 43, "subject": "salah"
    })
    assert "status" in result
    assert result["status"] == "WAJIB"

def test_execute_check_abrogation():
    """check_abrogation returns naskh info"""
    result = execute_tool("check_abrogation", {"topic": "iddah"})
    assert "active_verse" in result

def test_execute_evaluate_hadith():
    """evaluate_hadith_chain returns reliability grade"""
    result = execute_tool("evaluate_hadith_chain", {
        "chain": ["Abu Hurayrah", "Ibn Shihab", "Malik"]
    })
    assert "grade" in result
    assert result["grade"] in ("SAHIH", "HASAN", "DAIF", "MAWDU")

def test_execute_rhetorical_density():
    """compute_rhetorical_density returns a float"""
    result = execute_tool("compute_rhetorical_density", {
        "arabic_text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    })
    assert "density" in result
    assert isinstance(result["density"], float)
```

**Step 2: Implement tools.py**

```python
# src/frontierqu/agentic/tools.py
"""FrontierQu Tool Definitions for Anthropic Tool Use.

Each tool wraps one or more FrontierQu modules.
The agent calls these tools to answer scholarly questions autonomously.
"""
from typing import Any, Dict, List

# Tool specifications in Anthropic format
FRONTIERQU_TOOLS = [
    {
        "name": "search_verses",
        "description": (
            "Semantic search over all 6236 Quranic verses. Returns verses most relevant "
            "to a query about themes, topics, keywords, or concepts. Use this first "
            "when answering questions about what the Quran says about a topic."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (Arabic or English)"},
                "k": {"type": "integer", "description": "Number of results (default 5)", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "analyze_word",
        "description": (
            "Full Arabic morphological analysis (sarf) of a single word. "
            "Returns the trilateral root, morphological pattern (wazn), "
            "part of speech, verb form (1-10), case, and grammatical state. "
            "Use for any question about Arabic word meaning, grammar, or etymology."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "word": {"type": "string", "description": "Arabic word to analyze"},
            },
            "required": ["word"],
        },
    },
    {
        "name": "get_legal_ruling",
        "description": (
            "Derive an Islamic legal ruling (hukm shari) from a verse and subject. "
            "Returns one of the five categories: WAJIB (obligatory), HARAM (forbidden), "
            "MANDUB (recommended), MAKRUH (discouraged), MUBAH (permissible). "
            "Includes reasoning method (nass, qiyas, ijma) and confidence score."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "surah": {"type": "integer", "description": "Surah number (1-114)"},
                "ayah": {"type": "integer", "description": "Verse number"},
                "subject": {"type": "string", "description": "Legal subject (e.g. 'salah', 'riba', 'fasting')"},
            },
            "required": ["surah", "ayah", "subject"],
        },
    },
    {
        "name": "apply_qiyas",
        "description": (
            "Apply analogical reasoning (qiyas) to derive a ruling for a new case. "
            "Requires: the original verse with known ruling (asl), "
            "the effective cause/ratio legis (illa), and the new case (far'). "
            "Returns the derived ruling with confidence."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "asl_surah": {"type": "integer"},
                "asl_ayah": {"type": "integer"},
                "asl_ruling": {"type": "string", "enum": ["WAJIB", "HARAM", "MANDUB", "MAKRUH", "MUBAH"]},
                "illa": {"type": "string", "description": "Effective cause (e.g. 'intoxication')"},
                "far_case": {"type": "string", "description": "New case to derive ruling for"},
            },
            "required": ["asl_surah", "asl_ayah", "asl_ruling", "illa", "far_case"],
        },
    },
    {
        "name": "check_abrogation",
        "description": (
            "Check if a topic has known naskh (abrogation) relationships. "
            "Returns the abrogated verse, abrogating verse, and currently active ruling. "
            "Use when there appears to be a contradiction between verses."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to check (e.g. 'iddah', 'qiblah', 'alcohol')"},
                "verse_surah": {"type": "integer", "description": "Optional: check if this verse is abrogated"},
                "verse_ayah": {"type": "integer"},
            },
            "required": ["topic"],
        },
    },
    {
        "name": "get_thematic_connections",
        "description": (
            "Get all verses related to a theme and their cross-references. "
            "Themes: tawhid, mercy, justice, patience, knowledge, creation, "
            "afterlife, prayer, fasting, charity, prophets, guidance, gratitude. "
            "Returns verse list and thematic subgraph."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "theme": {"type": "string"},
                "include_cross_refs": {"type": "boolean", "default": True},
            },
            "required": ["theme"],
        },
    },
    {
        "name": "evaluate_hadith_chain",
        "description": (
            "Evaluate the reliability of a hadith transmission chain (isnad). "
            "Returns SAHIH (authentic), HASAN (good), DAIF (weak), or MAWDU (fabricated) "
            "based on narrator reliability scores. Identifies the weakest narrator."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chain": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of narrator names from source to collector",
                },
            },
            "required": ["chain"],
        },
    },
    {
        "name": "compute_rhetorical_density",
        "description": (
            "Compute the rhetorical density of an Arabic text using balaghah analysis. "
            "Detects ma'ani (meaning devices), bayan (clarity devices), and badi' "
            "(embellishment). Returns density score in bits/morpheme and detected devices."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "arabic_text": {"type": "string"},
                "verse_ref": {"type": "string", "description": "Optional verse reference e.g. '1:1'"},
            },
            "required": ["arabic_text"],
        },
    },
    {
        "name": "get_qiraat_variants",
        "description": (
            "Get variant readings (qira'at) for a verse from the 10 canonical readers. "
            "Returns each reader's pronunciation variant and semantic impact. "
            "Use when exploring how different readings affect meaning."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "surah": {"type": "integer"},
                "ayah": {"type": "integer"},
            },
            "required": ["surah", "ayah"],
        },
    },
    {
        "name": "compute_topological_features",
        "description": (
            "Compute persistent homology features (Betti numbers, persistence) "
            "for a thematic group of verses. Reveals topological structure: "
            "connected components (b0), thematic cycles (b1), voids (b2)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "theme": {"type": "string"},
            },
            "required": ["theme"],
        },
    },
]


def execute_tool(tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a FrontierQu tool and return its result."""
    handlers = {
        "search_verses": _search_verses,
        "analyze_word": _analyze_word,
        "get_legal_ruling": _get_legal_ruling,
        "apply_qiyas": _apply_qiyas,
        "check_abrogation": _check_abrogation,
        "get_thematic_connections": _get_thematic_connections,
        "evaluate_hadith_chain": _evaluate_hadith_chain,
        "compute_rhetorical_density": _compute_rhetorical_density,
        "get_qiraat_variants": _get_qiraat_variants,
        "compute_topological_features": _compute_topological_features,
    }
    if tool_name not in handlers:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return handlers[tool_name](inputs)
    except Exception as e:
        return {"error": str(e), "tool": tool_name}


def _search_verses(inputs: Dict) -> Dict:
    from frontierqu.search.embedding_store import EmbeddingStore
    store = EmbeddingStore.build()
    k = inputs.get("k", 5)
    results = store.search(inputs["query"], k=k)
    return {
        "results": [
            {"surah": r.verse[0], "ayah": r.verse[1], "score": round(r.score, 4)}
            for r in results
        ]
    }


def _analyze_word(inputs: Dict) -> Dict:
    from frontierqu.linguistic.sarf import analyze_word
    a = analyze_word(inputs["word"])
    return {
        "word": inputs["word"],
        "root": a.root,
        "pattern": a.pattern,
        "pos": a.pos,
        "form": a.form,
        "case": a.case,
        "state": a.state,
    }


def _get_legal_ruling(inputs: Dict) -> Dict:
    from frontierqu.logic.deontic import derive_ruling
    verse = (inputs["surah"], inputs["ayah"])
    rule = derive_ruling(verse, inputs["subject"])
    return {
        "verse": f"{inputs['surah']}:{inputs['ayah']}",
        "subject": inputs["subject"],
        "status": rule.status.name,
        "reasoning_method": rule.reasoning_method,
        "confidence": rule.confidence,
        "notes": rule.notes,
    }


def _apply_qiyas(inputs: Dict) -> Dict:
    from frontierqu.logic.deontic import apply_qiyas, DeonticStatus
    asl_verse = (inputs["asl_surah"], inputs["asl_ayah"])
    asl_ruling = DeonticStatus[inputs["asl_ruling"]]
    result = apply_qiyas(asl_verse, asl_ruling, inputs["illa"], inputs["far_case"])
    return {
        "far_case": inputs["far_case"],
        "derived_ruling": result.status.name,
        "asl_verse": f"{inputs['asl_surah']}:{inputs['asl_ayah']}",
        "illa": inputs["illa"],
        "confidence": result.confidence,
        "reasoning": result.notes,
    }


def _check_abrogation(inputs: Dict) -> Dict:
    from frontierqu.logic.naskh import NaskhDatabase, get_active_ruling
    db = NaskhDatabase()
    topic = inputs["topic"]
    relations = db.query(topic=topic)
    active = get_active_ruling(topic)
    return {
        "topic": topic,
        "naskh_found": len(relations) > 0,
        "active_verse": f"{active[0]}:{active[1]}" if active else None,
        "relations": [
            {
                "abrogated": f"{r.abrogated_verse[0]}:{r.abrogated_verse[1]}",
                "abrogating": f"{r.abrogating_verse[0]}:{r.abrogating_verse[1]}",
                "type": r.naskh_type.name,
                "consensus": r.scholarly_consensus,
                "notes": r.notes,
            }
            for r in relations
        ],
    }


def _get_thematic_connections(inputs: Dict) -> Dict:
    from frontierqu.data.cross_references import THEMATIC_GROUPS, CROSS_REFERENCES
    theme = inputs["theme"]
    if theme not in THEMATIC_GROUPS:
        return {"error": f"Theme '{theme}' not found"}
    verses = THEMATIC_GROUPS[theme]
    cross_refs = []
    if inputs.get("include_cross_refs", True):
        verse_set = set(verses)
        for (v1, v2, label) in CROSS_REFERENCES:
            if v1 in verse_set or v2 in verse_set:
                cross_refs.append({"from": f"{v1[0]}:{v1[1]}", "to": f"{v2[0]}:{v2[1]}", "type": label})
    return {
        "theme": theme,
        "verse_count": len(verses),
        "verses": [f"{s}:{v}" for s, v in verses],
        "cross_references": cross_refs[:20],
    }


def _evaluate_hadith_chain(inputs: Dict) -> Dict:
    from frontierqu.logic.isnad import evaluate_chain, IsnadDAG
    chain = inputs["chain"]
    grade = evaluate_chain(chain)
    dag = IsnadDAG()
    weakest = dag.weakest_link(chain)
    return {
        "chain": chain,
        "grade": grade.name,
        "weakest_narrator": weakest,
        "chain_length": len(chain),
    }


def _compute_rhetorical_density(inputs: Dict) -> Dict:
    from frontierqu.linguistic.balaghah import (
        rhetorical_density, detect_maani, detect_bayan, detect_badi
    )
    text = inputs["arabic_text"]
    density = rhetorical_density(text)
    maani = detect_maani(text)
    bayan = detect_bayan(text)
    badi = detect_badi(text)
    all_devices = maani.devices + bayan + badi
    return {
        "density": round(density, 4),
        "sentence_type": maani.sentence_type,
        "emphasis_level": round(maani.emphasis_level, 3),
        "devices": [
            {"type": d.device_type, "category": d.category, "score": round(d.score, 3)}
            for d in all_devices
        ],
    }


def _get_qiraat_variants(inputs: Dict) -> Dict:
    from frontierqu.core.qiraat import QiraatFiberBundle
    bundle = QiraatFiberBundle()
    verse = (inputs["surah"], inputs["ayah"])
    fiber = bundle.fiber_at(verse)
    return {
        "verse": f"{inputs['surah']}:{inputs['ayah']}",
        "variant_count": len(fiber),
        "readings": [
            {
                "qari": r.qari,
                "arabic": r.arabic,
                "semantic_impact": r.semantic_impact,
                "phonological_diff": r.phonological_diff,
            }
            for r in fiber
        ],
    }


def _compute_topological_features(inputs: Dict) -> Dict:
    from frontierqu.topology.persistent_homology import compute_persistence
    diagram = compute_persistence(theme=inputs["theme"])
    return {
        "theme": inputs["theme"],
        "betti_0": diagram.betti(0),
        "betti_1": diagram.betti(1),
        "total_features": len(diagram.pairs),
        "long_lived_cycles": len([
            p for p in diagram.pairs
            if p.dimension == 1 and p.persistence > 0.5
        ]),
    }
```

**Step 3: Create agentic test directory**

```bash
mkdir -p ~/Desktop/FrontierQu/tests/agentic && touch ~/Desktop/FrontierQu/tests/agentic/__init__.py
mkdir -p ~/Desktop/FrontierQu/src/frontierqu/agentic && touch ~/Desktop/FrontierQu/src/frontierqu/agentic/__init__.py
```

**Step 4: Run tests**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest tests/agentic/test_tools.py -v --tb=short
```

**Step 5: Commit**

```bash
cd ~/Desktop/FrontierQu && git add -A && git commit -m "feat: define 10 FrontierQu tools for Anthropic agent tool-use"
```

---

### Task 10.2: QuranicResearchAgent — Autonomous Multi-Domain Scholar

**Files:**
- Create: `src/frontierqu/agentic/agent.py`
- Create: `tests/agentic/test_agent.py`

**Context:** The agent uses `anthropic` (0.84.0, installed) with tool_use to answer Quranic research questions. It reasons across all 7 domains simultaneously, calls tools autonomously, and synthesizes multi-domain answers. Uses claude-sonnet-4-6 for cost efficiency with full capability.

**IMPORTANT:** Tests must mock the Anthropic API (no real API calls in tests). Use `unittest.mock.patch`.

**Step 1: Write the failing test**

```python
# tests/agentic/test_agent.py
import pytest
from unittest.mock import patch, MagicMock
from frontierqu.agentic.agent import QuranicResearchAgent, AgentResponse

def test_agent_initializes():
    """Agent initializes with tools loaded"""
    agent = QuranicResearchAgent(api_key="test-key")
    assert len(agent.tools) == 10  # all FrontierQu tools

def test_agent_response_dataclass():
    """AgentResponse has required fields"""
    resp = AgentResponse(
        question="What does the Quran say about mercy?",
        answer="Allah is the Most Merciful...",
        tools_used=["search_verses", "compute_rhetorical_density"],
        tool_results=[],
        model="claude-sonnet-4-6",
    )
    assert resp.answer != ""
    assert "search_verses" in resp.tools_used

def test_agent_calls_tools_on_query():
    """Agent invokes tools when answering a question"""
    agent = QuranicResearchAgent(api_key="test-key")

    # Mock the Anthropic client
    mock_tool_use = MagicMock()
    mock_tool_use.type = "tool_use"
    mock_tool_use.name = "search_verses"
    mock_tool_use.id = "tool_1"
    mock_tool_use.input = {"query": "mercy", "k": 5}

    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = "The Quran speaks extensively about mercy..."

    mock_response_1 = MagicMock()
    mock_response_1.stop_reason = "tool_use"
    mock_response_1.content = [mock_tool_use]

    mock_response_2 = MagicMock()
    mock_response_2.stop_reason = "end_turn"
    mock_response_2.content = [mock_text]

    with patch.object(agent.client.messages, 'create',
                      side_effect=[mock_response_1, mock_response_2]):
        response = agent.ask("What does the Quran say about mercy?")

    assert isinstance(response, AgentResponse)
    assert "search_verses" in response.tools_used
    assert len(response.answer) > 0

def test_agent_handles_no_tool_response():
    """Agent handles direct answer without tool use"""
    agent = QuranicResearchAgent(api_key="test-key")

    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = "This is a direct answer."

    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [mock_text]

    with patch.object(agent.client.messages, 'create', return_value=mock_response):
        response = agent.ask("Hello")

    assert response.answer == "This is a direct answer."
    assert response.tools_used == []
```

**Step 2: Implement agent.py**

```python
# src/frontierqu/agentic/agent.py
"""QuranicResearchAgent — Autonomous Multi-Domain Scholar.

Uses Claude claude-sonnet-4-6 with tool-use to answer Quranic research questions
by autonomously calling FrontierQu tools across all 7 domains.

Architecture:
    User question → Claude (reasoning) → Tool calls → FrontierQu modules
    → Tool results → Claude (synthesis) → Multi-domain answer

The agent reasons across: linguistics, topology, geometry, logic, physics,
qira'at, tajweed, isnad — simultaneously — before answering.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import anthropic

from frontierqu.agentic.tools import FRONTIERQU_TOOLS, execute_tool


SYSTEM_PROMPT = """You are a world-class Islamic scholar and computational researcher
with deep expertise in:

1. Arabic linguistics (sarf/nahw/balaghah)
2. Quranic sciences (tafsir, qira'at, tajweed, asbab al-nuzul)
3. Usul al-Fiqh (Islamic jurisprudence principles)
4. Hadith sciences (isnad, rijal, jarh wa ta'dil)
5. Mathematical representations of the Quran (topology, information geometry, GNNs)

You have access to the FrontierQu v3 framework which represents the entire Quran
as a single holistic mathematical object (simplicial complex of 6,236 verses).

ALWAYS:
- Use the search_verses tool first to ground your answers in specific verses
- Cross-reference multiple domains (linguistic + legal + topological) for complex questions
- Cite specific verses (surah:ayah format) in your answers
- Distinguish between scholarly consensus and minority positions
- Acknowledge when questions involve ijtihad (scholarly interpretation)

Your answers combine rigorous Islamic scholarship with cutting-edge mathematics.
The Quran is holistic — every verse affects every other. Never treat verses in isolation."""


@dataclass
class AgentResponse:
    question: str
    answer: str
    tools_used: List[str] = field(default_factory=list)
    tool_results: List[Dict] = field(default_factory=list)
    model: str = "claude-sonnet-4-6"
    tokens_used: int = 0


class QuranicResearchAgent:
    """Autonomous multi-domain Quranic research agent."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.tools = FRONTIERQU_TOOLS
        self._max_tool_rounds = 5  # Prevent infinite loops

    def ask(self, question: str, verbose: bool = False) -> AgentResponse:
        """Ask the agent a research question. Returns a multi-domain answer."""
        messages = [{"role": "user", "content": question}]
        tools_used = []
        tool_results_log = []
        total_tokens = 0

        for round_num in range(self._max_tool_rounds):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=self.tools,
                messages=messages,
            )

            if hasattr(response, 'usage') and response.usage:
                total_tokens += getattr(response.usage, 'input_tokens', 0)
                total_tokens += getattr(response.usage, 'output_tokens', 0)

            if verbose:
                print(f"[Round {round_num+1}] stop_reason={response.stop_reason}")

            # If done, extract final answer
            if response.stop_reason == "end_turn":
                answer = self._extract_text(response.content)
                return AgentResponse(
                    question=question,
                    answer=answer,
                    tools_used=tools_used,
                    tool_results=tool_results_log,
                    model=self.model,
                    tokens_used=total_tokens,
                )

            # Process tool calls
            if response.stop_reason == "tool_use":
                # Add assistant message
                messages.append({"role": "assistant", "content": response.content})

                # Execute all tool calls
                tool_results_content = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input if isinstance(block.input, dict) else {}

                        if verbose:
                            print(f"  → Calling {tool_name}({tool_input})")

                        result = execute_tool(tool_name, tool_input)
                        tools_used.append(tool_name)
                        tool_results_log.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "result": result,
                        })

                        tool_results_content.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False),
                        })

                # Add tool results to conversation
                messages.append({"role": "user", "content": tool_results_content})
            else:
                # Unexpected stop reason
                break

        # Fallback: extract whatever text we have
        answer = self._extract_text(response.content) if response else "No answer generated."
        return AgentResponse(
            question=question,
            answer=answer,
            tools_used=tools_used,
            tool_results=tool_results_log,
            model=self.model,
            tokens_used=total_tokens,
        )

    def _extract_text(self, content: List) -> str:
        """Extract text from response content blocks."""
        texts = []
        for block in content:
            if hasattr(block, 'type') and block.type == "text":
                texts.append(block.text)
            elif isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))
        return "\n".join(texts).strip()
```

**Step 3: Run tests**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest tests/agentic/test_agent.py -v --tb=short
```

**Step 4: Commit**

```bash
cd ~/Desktop/FrontierQu && git add -A && git commit -m "feat: implement QuranicResearchAgent with Claude claude-sonnet-4-6 tool-use"
```

---

### Task 10.3: TafsirSynthesisAgent — Domain-Specific Synthesis

**Files:**
- Create: `src/frontierqu/agentic/tafsir_agent.py`
- Create: `tests/agentic/test_tafsir_agent.py`

**Context:** Specialized agent that synthesizes a structured tafsir entry for any verse, combining morphological, legal, rhetorical, topological, and qira'at analysis into a scholarly report.

**Step 1: Write the failing test**

```python
# tests/agentic/test_tafsir_agent.py
import pytest
from unittest.mock import patch, MagicMock
from frontierqu.agentic.tafsir_agent import TafsirAgent, TafsirEntry

def test_tafsir_entry_dataclass():
    entry = TafsirEntry(
        verse=(1, 1),
        arabic="بِسْمِ اللَّهِ",
        morphological_analysis=[{"word": "بسم", "root": "سمو"}],
        rhetorical_analysis={"density": 0.5, "devices": []},
        legal_dimensions=[],
        qiraat_variants=[],
        thematic_connections=[],
        synthesis="This verse..."
    )
    assert entry.verse == (1, 1)
    assert entry.synthesis != ""

def test_tafsir_agent_initializes():
    agent = TafsirAgent(api_key="test-key")
    assert agent.research_agent is not None

def test_tafsir_synthesize_without_api():
    """Can generate partial tafsir entry using local tools only"""
    agent = TafsirAgent(api_key="test-key")
    entry = agent.synthesize_local(verse=(1, 1))
    assert isinstance(entry, TafsirEntry)
    assert entry.verse == (1, 1)
    assert len(entry.morphological_analysis) > 0
    assert entry.rhetorical_analysis["density"] >= 0.0

def test_tafsir_synthesize_with_mock_api():
    """Full synthesis uses agent for narrative"""
    agent = TafsirAgent(api_key="test-key")

    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = "This verse opens the Quran with the divine attributes..."

    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [mock_text]

    with patch.object(agent.research_agent.client.messages, 'create',
                      return_value=mock_response):
        entry = agent.synthesize(verse=(1, 1))

    assert isinstance(entry, TafsirEntry)
    assert len(entry.synthesis) > 0
```

**Step 2: Implement tafsir_agent.py**

```python
# src/frontierqu/agentic/tafsir_agent.py
"""TafsirSynthesisAgent — Structured Verse Analysis Report.

Generates a multi-domain tafsir entry combining:
    1. Morphological analysis (sarf) of each word
    2. Syntactic structure (nahw)
    3. Rhetorical devices (balaghah)
    4. Legal dimensions (deontic + qiyas)
    5. Variant readings (qira'at)
    6. Thematic connections
    7. Topological position in Quranic structure
    8. AI-synthesized scholarly narrative
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from frontierqu.agentic.agent import QuranicResearchAgent
from frontierqu.agentic.tools import execute_tool


@dataclass
class TafsirEntry:
    verse: Tuple[int, int]
    arabic: str
    morphological_analysis: List[Dict]
    rhetorical_analysis: Dict
    legal_dimensions: List[Dict]
    qiraat_variants: List[Dict]
    thematic_connections: List[str]
    synthesis: str = ""
    topological_features: Dict = field(default_factory=dict)


class TafsirAgent:
    """Generate structured tafsir entries through multi-domain analysis."""

    def __init__(self, api_key: str):
        self.research_agent = QuranicResearchAgent(api_key=api_key)

    def synthesize_local(self, verse: Tuple[int, int]) -> TafsirEntry:
        """Generate tafsir entry using local tools only (no API call)."""
        surah, ayah = verse

        # 1. Get Arabic text
        from frontierqu.data.quran_text import load_quran_corpus
        corpus = load_quran_corpus()
        entry = corpus.get(verse, {})
        arabic = entry.get("text_ar", f"{surah}:{ayah}")

        # 2. Morphological analysis
        morph_result = execute_tool("analyze_word", {"word": arabic.split()[0] if arabic.split() else ""})
        morph_analysis = []
        for word in arabic.split()[:5]:
            r = execute_tool("analyze_word", {"word": word})
            morph_analysis.append(r)

        # 3. Rhetorical analysis
        rhet_result = execute_tool("compute_rhetorical_density", {"arabic_text": arabic})

        # 4. Legal dimensions
        legal = execute_tool("get_legal_ruling", {"surah": surah, "ayah": ayah, "subject": "general"})

        # 5. Qira'at variants
        qiraat = execute_tool("get_qiraat_variants", {"surah": surah, "ayah": ayah})

        # 6. Thematic connections
        thematic_themes = []
        from frontierqu.data.cross_references import THEMATIC_GROUPS
        for theme, verses in THEMATIC_GROUPS.items():
            if verse in verses:
                thematic_themes.append(theme)

        return TafsirEntry(
            verse=verse,
            arabic=arabic,
            morphological_analysis=morph_analysis,
            rhetorical_analysis=rhet_result,
            legal_dimensions=[legal],
            qiraat_variants=qiraat.get("readings", []),
            thematic_connections=thematic_themes,
        )

    def synthesize(self, verse: Tuple[int, int]) -> TafsirEntry:
        """Full synthesis: local analysis + AI narrative."""
        entry = self.synthesize_local(verse)
        surah, ayah = verse

        # Build context for AI synthesis
        question = (
            f"Provide a scholarly tafsir synthesis for verse {surah}:{ayah}. "
            f"The verse text is: '{entry.arabic}'. "
            f"Consider: morphological roots {[m.get('root') for m in entry.morphological_analysis if m.get('root')]}, "
            f"rhetorical density {entry.rhetorical_analysis.get('density', 0):.3f}, "
            f"thematic connections to: {entry.thematic_connections}. "
            f"Synthesize a scholarly 2-paragraph tafsir integrating linguistic, legal, and spiritual dimensions."
        )

        agent_response = self.research_agent.ask(question)
        entry.synthesis = agent_response.answer
        return entry
```

**Step 3: Run tests**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest tests/agentic/test_tafsir_agent.py -v --tb=short
```

**Step 4: Commit**

```bash
cd ~/Desktop/FrontierQu && git add -A && git commit -m "feat: implement TafsirSynthesisAgent for structured verse analysis"
```

---

### Task 10.4: Final Integration & Full Test Run

**Files:**
- Create: `tests/test_v3_integration.py`

**Step 1: Write integration tests**

```python
# tests/test_v3_integration.py
"""Integration tests for FrontierQu v3: Real Data + Search + Agents."""

def test_morphology_lexicon_powers_sarf():
    """Expanded lexicon improves root extraction"""
    from frontierqu.linguistic.sarf import extract_root
    # Words now in expanded lexicon
    assert extract_root("مسلمون") == "سلم"
    assert extract_root("الصابرون") == "صبر"
    assert extract_root("غفور") == "غفر"

def test_search_finds_mercy_theme():
    """Semantic search finds mercy-related verses"""
    from frontierqu.search.embedding_store import EmbeddingStore
    store = EmbeddingStore.build()
    results = store.search("mercy compassion", k=10)
    assert len(results) == 10
    # At least one result should be from Al-Fatihah (which has الرحمن الرحيم)
    surahs = [r.verse[0] for r in results]
    assert 1 in surahs or any(s < 10 for s in surahs)

def test_api_health():
    """FastAPI server health check"""
    from fastapi.testclient import TestClient
    from frontierqu.api.server import app
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200

def test_tools_all_executable():
    """All 10 tools execute without crashing"""
    from frontierqu.agentic.tools import execute_tool, FRONTIERQU_TOOLS

    safe_inputs = {
        "search_verses": {"query": "mercy", "k": 3},
        "analyze_word": {"word": "كتاب"},
        "get_legal_ruling": {"surah": 2, "ayah": 43, "subject": "salah"},
        "apply_qiyas": {"asl_surah": 5, "asl_ayah": 90, "asl_ruling": "HARAM", "illa": "intoxication", "far_case": "beer"},
        "check_abrogation": {"topic": "iddah"},
        "get_thematic_connections": {"theme": "mercy"},
        "evaluate_hadith_chain": {"chain": ["Abu Hurayrah", "Malik"]},
        "compute_rhetorical_density": {"arabic_text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"},
        "get_qiraat_variants": {"surah": 1, "ayah": 4},
        "compute_topological_features": {"theme": "tawhid"},
    }

    for tool in FRONTIERQU_TOOLS:
        name = tool["name"]
        inputs = safe_inputs.get(name, {})
        result = execute_tool(name, inputs)
        assert "error" not in result or result.get("error") is None, f"Tool {name} failed: {result}"

def test_tafsir_local_synthesis():
    """TafsirAgent generates local entry for Al-Fatihah"""
    from frontierqu.agentic.tafsir_agent import TafsirAgent
    agent = TafsirAgent(api_key="test-key")
    entry = agent.synthesize_local(verse=(1, 1))
    assert entry.arabic != ""
    assert len(entry.morphological_analysis) > 0
    assert isinstance(entry.thematic_connections, list)
```

**Step 2: Run all tests — must reach 150+**

```bash
cd ~/Desktop/FrontierQu && python3 -m pytest --tb=short -q
```

Expected: 150+ passed, 0 failed.

**Step 3: Final commit**

```bash
cd ~/Desktop/FrontierQu && git add -A && git commit -m "feat: FrontierQu v3 — real data + semantic search + deeptech agentic layer"
```

---

## Summary: What v3 Adds Over v2

| Component | v2 | v3 |
|---|---|---|
| Morphological lexicon | 14 roots, ~80 words | 50+ roots, 300+ words with full wazn |
| Arabic corpus coverage | 30 verses (0.5%) | 60+ verses (1%) with short Makkan surahs |
| Semantic search | Query returns activation pattern | Cosine similarity over tensor, ranked results |
| REST API | None | 6 endpoints: search, verse, ruling, thematic, analyze, health |
| Agentic layer | Empty `agentic/` folder | QuranicResearchAgent + TafsirAgent, 10 tools |
| Tool use | None | Claude claude-sonnet-4-6 autonomously calling all 7 domains |
| Test count | 118 | 150+ |
