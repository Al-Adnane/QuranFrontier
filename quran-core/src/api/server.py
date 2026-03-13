# src/frontierqu/api/server.py
"""FrontierQu REST API — Holistic Quranic Research Endpoints."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="FrontierQu API",
    description="Holistic Quranic Algorithmic Framework — REST Interface",
    version="3.0.0"
)

# Lazy-loaded singleton
_store = None


def _get_store():
    global _store
    if _store is None:
        from frontierqu.search.embedding_store import EmbeddingStore
        _store = EmbeddingStore.build()
    return _store


class AnalyzeRequest(BaseModel):
    arabic: str


class SearchResultResponse(BaseModel):
    surah: int
    ayah: int
    score: float
    rank: int


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

    words = arabic.split()
    morphology = []
    for w in words[:5]:
        try:
            a = analyze_word(w)
            morphology.append({
                "word": w, "root": a.root, "pos": a.pos,
                "pattern": a.pattern, "case": getattr(a, 'case', '')
            })
        except Exception:
            morphology.append({"word": w})

    density = rhetorical_density(arabic) if entry["has_real_text"] else 0.0
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
