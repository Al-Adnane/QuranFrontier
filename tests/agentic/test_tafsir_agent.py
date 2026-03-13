# tests/agentic/test_tafsir_agent.py
import pytest
from frontierqu.agentic.tafsir_agent import TafsirAgent, TafsirEntry

def test_tafsir_entry_structure():
    """TafsirEntry has required fields"""
    entry = TafsirEntry(
        verse=(1, 1),
        arabic_text="بِسْمِ اللَّهِ",
        thematic_analysis={"theme": "tawhid"},
        linguistic_analysis={"density": 1.5},
        legal_context={"status": "MUBAH"},
        topological_position={"b0": 1, "b1": 0},
        qiraat_variants=[],
        synthesis="Test synthesis"
    )
    assert entry.verse == (1, 1)
    assert entry.synthesis == "Test synthesis"

def test_tafsir_agent_instantiates():
    """TafsirAgent can be created"""
    agent = TafsirAgent()
    assert agent is not None

def test_synthesize_local_returns_entry():
    """synthesize_local returns TafsirEntry without API"""
    agent = TafsirAgent()
    entry = agent.synthesize_local((1, 1))
    assert isinstance(entry, TafsirEntry)
    assert entry.verse == (1, 1)
    assert len(entry.synthesis) > 0

def test_synthesize_local_all_domains():
    """synthesize_local populates all analysis domains"""
    agent = TafsirAgent()
    entry = agent.synthesize_local((2, 255))  # Ayat al-Kursi
    assert entry.thematic_analysis is not None
    assert entry.linguistic_analysis is not None
    assert entry.legal_context is not None

def test_multi_verse_synthesis():
    """Can synthesize multiple verses"""
    agent = TafsirAgent()
    verses = [(1, 1), (1, 2), (112, 1)]
    entries = [agent.synthesize_local(v) for v in verses]
    assert len(entries) == 3
    assert all(isinstance(e, TafsirEntry) for e in entries)

def test_synthesis_narrative_mentions_verse():
    """Synthesis narrative references the verse"""
    agent = TafsirAgent()
    entry = agent.synthesize_local((112, 1))
    # Should mention surah 112 or Al-Ikhlas
    assert "112" in entry.synthesis or "Ikhlas" in entry.synthesis or "verse" in entry.synthesis.lower()
