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
