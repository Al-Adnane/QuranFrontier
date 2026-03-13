# tests/agentic/test_agent.py
import pytest
from frontierqu.agentic.agent import QuranicResearchAgent, AgentResponse

def test_agent_can_be_instantiated():
    """Agent can be created without errors"""
    agent = QuranicResearchAgent()
    assert agent is not None

def test_agent_has_system_prompt():
    """Agent has a meaningful system prompt"""
    agent = QuranicResearchAgent()
    assert len(agent.SYSTEM_PROMPT) > 100
    assert "Quran" in agent.SYSTEM_PROMPT or "Islamic" in agent.SYSTEM_PROMPT

def test_agent_response_structure():
    """AgentResponse has required fields"""
    response = AgentResponse(
        answer="test answer",
        tools_used=["search_verses"],
        iterations=1
    )
    assert response.answer == "test answer"
    assert "search_verses" in response.tools_used
    assert response.iterations == 1

def test_agent_has_tools():
    """Agent has all FrontierQu tools configured"""
    agent = QuranicResearchAgent()
    tool_names = [t["name"] for t in agent.tools]
    assert "search_verses" in tool_names
    assert "get_legal_ruling" in tool_names
    assert len(agent.tools) >= 10

def test_agent_local_answer():
    """Agent can answer without API using local knowledge"""
    agent = QuranicResearchAgent()
    # Test the local path - no API call needed
    result = agent.answer_locally("What is the rhetorical density of Bismillah?")
    assert isinstance(result, str)
    assert len(result) > 0
