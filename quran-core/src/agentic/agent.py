# src/frontierqu/agentic/agent.py
"""QuranicResearchAgent — Autonomous Multi-Domain Quranic Scholar.

Uses Claude claude-sonnet-4-6 with tool-use to answer scholarly questions
about the Quran, calling FrontierQu tools across all 7 domains.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import os

from frontierqu.agentic.tools import FRONTIERQU_TOOLS, execute_tool


SYSTEM_PROMPT = """You are an autonomous Quranic research agent combining the precision of
a computational linguist with the depth of a classical Islamic scholar.

You have access to FrontierQu — a holistic algorithmic framework covering 7 domains:
1. Structural analysis (surah/verse position, normalization)
2. Thematic connections (13 thematic groups across 6236 verses)
3. Linguistic analysis (morphology/sarf, syntax/nahw, rhetoric/balaghah)
4. Topological features (persistent homology, Betti numbers)
5. Information geometry (Fisher-Rao metric, geodesic distances)
6. Deontic logic (al-ahkam al-khamsa, qiyas, naskh)
7. Qira'at (10 canonical readings, fiber bundle structure)

When answering questions:
- Use search_verses first to find relevant verses
- Combine multiple domains for richer analysis
- Cite specific verse references (surah:ayah)
- Apply the appropriate Islamic legal framework when relevant
- Be precise about what the computational analysis shows vs. traditional scholarship
- Synthesize across domains: a verse's rhetorical density, legal status, thematic connections,
  and topological position all contribute to holistic understanding

The Quran is treated as a single irreducible whole — every verse's meaning emerges from
its position within the entire structure, not in isolation.
"""


@dataclass
class AgentResponse:
    answer: str
    tools_used: List[str] = field(default_factory=list)
    iterations: int = 0
    tool_results: List[Dict[str, Any]] = field(default_factory=list)


class QuranicResearchAgent:
    """Autonomous research agent for Quranic scholarship using Claude tool-use."""

    SYSTEM_PROMPT = SYSTEM_PROMPT

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.tools = FRONTIERQU_TOOLS
        self.max_iterations = 5

    def ask(self, question: str, verbose: bool = False) -> AgentResponse:
        """Ask the agent a question. Uses Claude API with tool-use.

        Falls back to local answer if no API key is available.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            local_answer = self.answer_locally(question)
            return AgentResponse(
                answer=local_answer,
                tools_used=["local_fallback"],
                iterations=0
            )

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            return self._run_agentic_loop(client, question, verbose)
        except Exception as e:
            return AgentResponse(
                answer=f"Error: {e}. Using local fallback.",
                tools_used=["error_fallback"],
                iterations=0
            )

    def answer_locally(self, question: str) -> str:
        """Answer a question using only local FrontierQu tools (no API)."""
        question_lower = question.lower()
        results = []

        # Search for relevant verses
        try:
            search_result = execute_tool("search_verses", {"query": question, "k": 3})
            if "results" in search_result:
                verses = search_result["results"]
                refs = [f"{v['surah']}:{v['ayah']}" for v in verses]
                results.append(f"Most relevant verses: {refs}")
        except Exception:
            pass

        # Rhetorical analysis if text is mentioned
        arabic_words = [w for w in question.split() if any('\u0600' <= c <= '\u06FF' for c in w)]
        if arabic_words:
            try:
                text = " ".join(arabic_words)
                rhet = execute_tool("compute_rhetorical_density", {"arabic_text": text})
                results.append(f"Rhetorical density: {rhet.get('density', 0):.3f} bits/morpheme")
            except Exception:
                pass

        # Legal analysis if ruling keywords present
        if any(w in question_lower for w in ["ruling", "halal", "haram", "wajib", "permissible", "forbidden"]):
            results.append("For specific legal rulings, use get_legal_ruling with a verse reference.")

        if results:
            return f"Analysis of '{question}':\n" + "\n".join(f"• {r}" for r in results)
        return f"Query: '{question}' — use the FrontierQu tools for full analysis."

    def _run_agentic_loop(self, client, question: str, verbose: bool) -> AgentResponse:
        """Run the agentic tool-use loop with Claude."""
        import anthropic

        messages = [{"role": "user", "content": question}]
        tools_used = []
        tool_results = []
        iterations = 0

        while iterations < self.max_iterations:
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=self.tools,
                messages=messages,
            )
            iterations += 1

            if response.stop_reason == "end_turn":
                # Extract text answer
                answer = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        answer += block.text
                return AgentResponse(
                    answer=answer,
                    tools_used=tools_used,
                    iterations=iterations,
                    tool_results=tool_results
                )

            if response.stop_reason == "tool_use":
                # Execute tools
                tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
                tool_results_content = []

                for tool_call in tool_use_blocks:
                    tool_name = tool_call.name
                    tool_input = tool_call.input
                    tools_used.append(tool_name)

                    if verbose:
                        print(f"  → Calling tool: {tool_name}({tool_input})")

                    result = execute_tool(tool_name, tool_input)
                    tool_results.append({"tool": tool_name, "result": result})

                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": str(result),
                    })

                # Add assistant response and tool results to messages
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results_content})

            else:
                break

        # If we hit max iterations, return what we have
        answer = ""
        for block in response.content:
            if hasattr(block, "text"):
                answer += block.text
        return AgentResponse(
            answer=answer or "Max iterations reached.",
            tools_used=tools_used,
            iterations=iterations,
            tool_results=tool_results
        )
