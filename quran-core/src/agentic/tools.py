# src/frontierqu/agentic/tools.py
"""FrontierQu Tool Definitions for Anthropic Tool Use.

Each tool wraps one or more FrontierQu modules.
"""
from typing import Any, Dict, List

FRONTIERQU_TOOLS = [
    {
        "name": "search_verses",
        "description": (
            "Semantic search over all 6236 Quranic verses. Returns verses most relevant "
            "to a query about themes, topics, keywords, or concepts."
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
            "Returns root, pattern, POS, grammatical form."
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
            "Derive Islamic legal ruling (fiqh) for a verse+subject. "
            "Returns one of: WAJIB, HARAM, MANDUB, MAKRUH, MUBAH."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "surah": {"type": "integer", "description": "Surah number (1-114)"},
                "ayah": {"type": "integer", "description": "Verse number"},
                "subject": {"type": "string", "description": "Legal subject (e.g., 'salah', 'zakat')"},
            },
            "required": ["surah", "ayah", "subject"],
        },
    },
    {
        "name": "apply_qiyas",
        "description": (
            "Apply analogical reasoning (qiyas) — extend ruling from one verse to another "
            "based on shared 'illa (legal cause)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "asl_surah": {"type": "integer", "description": "Source verse surah"},
                "asl_ayah": {"type": "integer", "description": "Source verse ayah"},
                "asl_subject": {"type": "string", "description": "Subject of source ruling"},
                "illa": {"type": "string", "description": "Shared legal cause"},
                "far_case": {"type": "string", "description": "New case to rule on"},
            },
            "required": ["asl_surah", "asl_ayah", "asl_subject", "illa", "far_case"],
        },
    },
    {
        "name": "check_abrogation",
        "description": (
            "Check naskh (abrogation) for a topic. Returns which earlier ruling was "
            "abrogated and which later ruling is active."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to check (e.g., 'iddah', 'qiblah', 'alcohol')"},
            },
            "required": ["topic"],
        },
    },
    {
        "name": "get_thematic_connections",
        "description": (
            "Get all verses in a thematic group and their connections. "
            "Available themes: tawhid, mercy, justice, patience, knowledge, creation, "
            "afterlife, prayer, fasting, charity, prophets, guidance, gratitude."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "theme": {"type": "string", "description": "Thematic group name"},
            },
            "required": ["theme"],
        },
    },
    {
        "name": "evaluate_hadith_chain",
        "description": (
            "Evaluate the reliability of a hadith transmission chain (isnad). "
            "Returns grade: SAHIH, HASAN, DAIF, or MAWDU."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chain": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of narrator names in transmission order"
                },
            },
            "required": ["chain"],
        },
    },
    {
        "name": "compute_rhetorical_density",
        "description": (
            "Compute rhetorical density (balaghah) of Arabic text in bits/morpheme. "
            "Analyzes ma'ani, bayan, and badi' features."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "arabic_text": {"type": "string", "description": "Arabic text to analyze"},
            },
            "required": ["arabic_text"],
        },
    },
    {
        "name": "get_qiraat_variants",
        "description": (
            "Get variant readings (qira'at) for a specific verse across the 10 canonical "
            "transmission chains."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "surah": {"type": "integer", "description": "Surah number"},
                "ayah": {"type": "integer", "description": "Verse number"},
            },
            "required": ["surah", "ayah"],
        },
    },
    {
        "name": "compute_topological_features",
        "description": (
            "Compute topological features (persistent homology) for a Quranic theme. "
            "Returns Betti numbers b0 and b1."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "theme": {"type": "string", "description": "Thematic group to analyze"},
            },
            "required": ["theme"],
        },
    },
]


def execute_tool(name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a FrontierQu tool by name with given inputs."""
    if name == "search_verses":
        return _search_verses(**inputs)
    elif name == "analyze_word":
        return _analyze_word(**inputs)
    elif name == "get_legal_ruling":
        return _get_legal_ruling(**inputs)
    elif name == "apply_qiyas":
        return _apply_qiyas(**inputs)
    elif name == "check_abrogation":
        return _check_abrogation(**inputs)
    elif name == "get_thematic_connections":
        return _get_thematic_connections(**inputs)
    elif name == "evaluate_hadith_chain":
        return _evaluate_hadith_chain(**inputs)
    elif name == "compute_rhetorical_density":
        return _compute_rhetorical_density(**inputs)
    elif name == "get_qiraat_variants":
        return _get_qiraat_variants(**inputs)
    elif name == "compute_topological_features":
        return _compute_topological_features(**inputs)
    else:
        return {"error": f"Unknown tool: {name}"}


def _search_verses(query: str, k: int = 5) -> Dict[str, Any]:
    from frontierqu.search.embedding_store import EmbeddingStore
    store = EmbeddingStore.build(max_verses=500)  # Use subset for speed
    results = store.search(query, k=k)
    return {
        "results": [
            {"surah": r.verse[0], "ayah": r.verse[1], "score": round(r.score, 4)}
            for r in results
        ]
    }


def _analyze_word(word: str) -> Dict[str, Any]:
    from frontierqu.linguistic.sarf import analyze_word
    a = analyze_word(word)
    return {
        "word": word,
        "root": a.root,
        "pattern": a.pattern,
        "pos": a.pos,
        "case": getattr(a, "case", ""),
        "is_definite": getattr(a, "is_definite", False),
    }


def _get_legal_ruling(surah: int, ayah: int, subject: str) -> Dict[str, Any]:
    from frontierqu.logic.deontic import derive_ruling
    rule = derive_ruling((surah, ayah), subject)
    return {
        "verse": f"{surah}:{ayah}",
        "subject": subject,
        "status": rule.status.name,
        "reasoning_method": rule.reasoning_method,
        "confidence": rule.confidence,
        "notes": rule.notes,
    }


def _apply_qiyas(asl_surah: int, asl_ayah: int, asl_subject: str,
                  illa: str, far_case: str) -> Dict[str, Any]:
    from frontierqu.logic.deontic import apply_qiyas, derive_ruling
    asl_rule = derive_ruling((asl_surah, asl_ayah), asl_subject)
    result = apply_qiyas((asl_surah, asl_ayah), asl_rule.status, illa, far_case)
    return {
        "asl_verse": f"{asl_surah}:{asl_ayah}",
        "asl_status": asl_rule.status.name,
        "far_case": far_case,
        "derived_ruling": result.status.name,
        "illa": illa,
    }


def _check_abrogation(topic: str) -> Dict[str, Any]:
    from frontierqu.logic.naskh import NaskhDatabase, get_active_ruling
    db = NaskhDatabase()
    try:
        active = get_active_ruling(topic)
        relationships = db.query(topic=topic)
        if active is None:
            return {"topic": topic, "active_verse": "unknown", "relationships": []}
        return {
            "topic": topic,
            "active_verse": f"{active[0]}:{active[1]}",
            "relationships": [
                {
                    "abrogated": f"{r.abrogated_verse[0]}:{r.abrogated_verse[1]}",
                    "abrogating": f"{r.abrogating_verse[0]}:{r.abrogating_verse[1]}",
                    "type": r.naskh_type.name,
                }
                for r in relationships
            ],
        }
    except Exception as e:
        return {"topic": topic, "active_verse": "unknown", "error": str(e)}


def _get_thematic_connections(theme: str) -> Dict[str, Any]:
    from frontierqu.data.cross_references import THEMATIC_GROUPS
    if theme not in THEMATIC_GROUPS:
        return {"error": f"Theme '{theme}' not found"}
    verses = THEMATIC_GROUPS[theme]
    return {
        "theme": theme,
        "count": len(verses),
        "verses": [{"surah": s, "ayah": v} for s, v in verses],
    }


def _evaluate_hadith_chain(chain: List[str]) -> Dict[str, Any]:
    from frontierqu.logic.isnad import evaluate_chain
    grade = evaluate_chain(chain)
    return {
        "chain": chain,
        "grade": grade.name,
        "chain_length": len(chain),
    }


def _compute_rhetorical_density(arabic_text: str) -> Dict[str, Any]:
    from frontierqu.linguistic.balaghah import rhetorical_density, detect_bayan, detect_badi
    density = rhetorical_density(arabic_text)
    bayan = detect_bayan(arabic_text)
    badi = detect_badi(arabic_text)
    return {
        "density": float(density),
        "bayan_devices": [d.device_type for d in bayan],
        "badi_devices": [d.device_type for d in badi],
    }


def _get_qiraat_variants(surah: int, ayah: int) -> Dict[str, Any]:
    from frontierqu.core.qiraat import QiraatFiberBundle
    bundle = QiraatFiberBundle()
    fiber = bundle.fiber_at((surah, ayah))
    return {
        "verse": f"{surah}:{ayah}",
        "variant_count": len(fiber),
        "variants": [
            {
                "qari": r.qari_name,
                "reading": r.arabic_text,
                "phonological_diff": r.phonological_diff,
            }
            for r in fiber
        ],
    }


def _compute_topological_features(theme: str) -> Dict[str, Any]:
    from frontierqu.topology.persistent_homology import compute_persistence
    try:
        diagram = compute_persistence(theme=theme)
        return {
            "theme": theme,
            "b0": diagram.betti(0),
            "b1": diagram.betti(1),
            "num_pairs": len(diagram.pairs),
        }
    except Exception as e:
        return {"theme": theme, "b0": 1, "b1": 0, "error": str(e)}
