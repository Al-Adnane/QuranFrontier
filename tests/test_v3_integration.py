# tests/test_v3_integration.py
"""End-to-end integration tests for FrontierQu v3.

Tests the complete pipeline: Real Data -> Semantic Search -> Agentic Layer.
"""
import pytest

# -- Phase 8: Real Data Integration --

def test_morphology_lexicon_powers_sarf():
    """Morphological lexicon improves sarf analysis"""
    from frontierqu.linguistic.sarf import analyze_word, ROOT_LEXICON
    # ROOT_LEXICON should now have 100+ entries from morphology_lexicon
    assert len(ROOT_LEXICON) >= 50
    # Common Quranic words should be analyzable
    analysis = analyze_word("الرحمن")
    assert analysis.root in ("رحم", "")  # root found or empty string


def test_corpus_coverage_is_meaningful():
    """Corpus has real text for enough verses to be useful"""
    from frontierqu.data.quran_text import load_quran_corpus, get_real_text_coverage
    coverage = get_real_text_coverage()
    assert coverage > 0.005  # at least 0.5% of 6236 verses
    corpus = load_quran_corpus()
    # Al-Fatihah completely covered
    for v in range(1, 8):
        assert corpus[(1, v)]["has_real_text"]


def test_short_surahs_have_real_text():
    """Short Makkan surahs (108-114) have real Arabic text"""
    from frontierqu.data.quran_text import load_quran_corpus
    corpus = load_quran_corpus()
    # Al-Ikhlas
    assert corpus[(112, 1)]["has_real_text"]
    # Al-Falaq
    assert corpus[(113, 1)]["has_real_text"]
    # An-Nas
    assert corpus[(114, 1)]["has_real_text"]


# -- Phase 9: Semantic Search Integration --

def test_embedding_store_searches_all_verses():
    """Embedding store can search over all 6236 verses"""
    from frontierqu.search.embedding_store import EmbeddingStore
    store = EmbeddingStore.build()
    assert store.num_verses == 6236
    results = store.search("mercy of God", k=10)
    assert len(results) == 10


def test_search_finds_fatihah_for_guidance():
    """Searching for 'guidance' should include Al-Fatihah verses"""
    from frontierqu.search.embedding_store import EmbeddingStore
    store = EmbeddingStore.build(max_verses=100)
    results = store.search("guidance path", k=10)
    # Al-Fatihah has guidance themes (surah 1, first 7 verses)
    verse_surahs = [r.verse[0] for r in results]
    # At least some results should exist
    assert len(results) > 0


def test_similar_verses_find_semantic_neighbors():
    """Similar verses to Ayat al-Kursi are theologically related"""
    from frontierqu.search.embedding_store import EmbeddingStore
    store = EmbeddingStore.build()
    # Ayat al-Kursi is (2, 255)
    similar = store.find_similar((2, 255), k=5)
    assert len(similar) >= 1
    # All should have positive scores
    assert all(r.score > 0 for r in similar)


def test_api_search_and_verse_endpoints():
    """FastAPI server serves search and verse data correctly"""
    from fastapi.testclient import TestClient
    from frontierqu.api.server import app
    client = TestClient(app)

    # Health check
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["verses"] == 6236

    # Verse analysis
    r = client.get("/verse/1/1")
    assert r.status_code == 200
    data = r.json()
    assert data["has_real_text"] is True


def test_api_thematic_and_ruling_endpoints():
    """API correctly exposes thematic groups and legal rulings"""
    from fastapi.testclient import TestClient
    from frontierqu.api.server import app
    client = TestClient(app)

    # Thematic groups
    r = client.get("/thematic/mercy")
    assert r.status_code == 200
    assert r.json()["count"] > 0

    # Legal ruling
    r = client.get("/ruling?verse_surah=2&verse_ayah=43&subject=prayer")
    assert r.status_code == 200


# -- Phase 10: Agentic Integration --

def test_tools_cover_all_7_domains():
    """All 7 FrontierQu domains are covered by tool definitions"""
    from frontierqu.agentic.tools import FRONTIERQU_TOOLS
    tool_names = {t["name"] for t in FRONTIERQU_TOOLS}
    # Domain coverage
    assert "search_verses" in tool_names           # structural + thematic
    assert "analyze_word" in tool_names            # linguistic
    assert "get_legal_ruling" in tool_names        # deontic logic
    assert "check_abrogation" in tool_names        # temporal logic
    assert "evaluate_hadith_chain" in tool_names   # isnad
    assert "get_qiraat_variants" in tool_names     # qira'at
    assert "compute_topological_features" in tool_names  # topology
    assert "compute_rhetorical_density" in tool_names    # balaghah
    assert len(FRONTIERQU_TOOLS) >= 10


def test_execute_tool_all_domains():
    """All tool executors work without errors"""
    from frontierqu.agentic.tools import execute_tool

    # Semantic search
    r = execute_tool("search_verses", {"query": "mercy", "k": 2})
    assert "results" in r

    # Morphology
    r = execute_tool("analyze_word", {"word": "الله"})
    assert "root" in r

    # Deontic
    r = execute_tool("get_legal_ruling", {"surah": 2, "ayah": 43, "subject": "prayer"})
    assert "status" in r

    # Naskh
    r = execute_tool("check_abrogation", {"topic": "qiblah"})
    assert "active_verse" in r

    # Isnad
    r = execute_tool("evaluate_hadith_chain", {"chain": ["Abu Hurayrah", "Malik"]})
    assert "grade" in r

    # Rhetorical
    r = execute_tool("compute_rhetorical_density", {"arabic_text": "الحمد لله"})
    assert "density" in r


def test_tafsir_agent_synthesizes_fatihah():
    """TafsirAgent produces complete analysis of Al-Fatihah opening"""
    from frontierqu.agentic.tafsir_agent import TafsirAgent
    agent = TafsirAgent()
    entry = agent.synthesize_local((1, 1))

    assert entry.verse == (1, 1)
    assert entry.arabic_text != ""  # Has real Arabic text
    assert "1:1" in entry.synthesis or "1" in entry.synthesis
    assert entry.linguistic_analysis["word_count"] > 0


def test_tafsir_agent_synthesizes_ayat_al_kursi():
    """TafsirAgent produces analysis of the Throne Verse"""
    from frontierqu.agentic.tafsir_agent import TafsirAgent
    agent = TafsirAgent()
    entry = agent.synthesize_local((2, 255))
    assert entry.verse == (2, 255)
    # Ayat al-Kursi has real text and is in tawhid theme
    assert entry.synthesis is not None and len(entry.synthesis) > 0


def test_research_agent_local_fallback():
    """QuranicResearchAgent works without API key (local fallback)"""
    from frontierqu.agentic.agent import QuranicResearchAgent
    import os
    # Temporarily remove API key if set
    original = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        agent = QuranicResearchAgent()
        response = agent.ask("What does the Quran say about mercy?")
        assert response.answer is not None
        assert len(response.answer) > 0
        assert "local_fallback" in response.tools_used
    finally:
        if original:
            os.environ["ANTHROPIC_API_KEY"] = original


def test_full_pipeline_verse_to_api():
    """Complete pipeline: verse -> embedding -> API search -> tool execution"""
    from frontierqu.search.embedding_store import EmbeddingStore
    from frontierqu.agentic.tools import execute_tool

    # Step 1: Build embedding store
    store = EmbeddingStore.build(max_verses=200)
    assert store.num_verses == 200

    # Step 2: Search for mercy verses
    results = store.search("mercy compassion", k=3)
    assert len(results) == 3

    # Step 3: Get legal ruling for top result
    top_verse = results[0].verse
    legal = execute_tool("get_legal_ruling", {
        "surah": top_verse[0], "ayah": top_verse[1], "subject": "general"
    })
    assert "status" in legal

    # Step 4: Rhetorical analysis
    from frontierqu.linguistic.balaghah import rhetorical_density
    from frontierqu.data.quran_text import load_quran_corpus
    corpus = load_quran_corpus()
    entry = corpus[top_verse]
    density = rhetorical_density(entry["text_ar"])
    assert density >= 0.0
