"""Proposer Agent - Generates scholarly interpretations using RAG.

The ProposerAgent is responsible for generating initial interpretations of
Quranic and Islamic law questions using Retrieval-Augmented Generation (RAG)
with classical Islamic sources.

Architecture:
- Takes query + retrieved context (Quranic verses, hadith, fiqh)
- Generates coherent interpretation respecting madhab diversity
- Returns interpretation with confidence score and citations
- Integrates with critique and verification loops
"""

from typing import Dict, List, Optional, Any, Tuple
import json
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Types of Islamic sources."""
    QURAN = "quran"
    HADITH = "hadith"
    IJMA = "ijma"
    QIYAS = "qiyas"
    MADHAB_OPINION = "madhab_opinion"


@dataclass
class Source:
    """Citation reference structure."""
    source_type: SourceType
    reference: str  # e.g., "2:275" for Quran, "Sahih Bukhari 34:160" for hadith
    text: str
    score: float  # Relevance score 0-1
    madhab: Optional[str] = None  # For madhab-specific opinions


@dataclass
class Interpretation:
    """Generated interpretation structure."""
    text: str
    confidence: float
    sources: List[Source]
    alternative_views: List[str]
    citations: List[Dict[str, Any]]
    model_used: str
    reasoning: str


class ProposerAgent:
    """
    Generates interpretations of Islamic law and Quranic concepts.

    Uses RAG to retrieve relevant classical sources and synthesizes
    them into coherent interpretations respecting madhab diversity.
    """

    def __init__(
        self,
        model_name: str = "claude-3-haiku",
        rag_retriever: Optional[Any] = None,
        context_window: int = 2048,
        madhab_weights: Optional[Dict[str, float]] = None,
        temperature: float = 0.7,
        api_key: Optional[str] = None
    ):
        """
        Initialize ProposerAgent.

        Args:
            model_name: Language model to use (e.g., "claude-3-haiku")
            rag_retriever: Vector DB retriever for classical sources
            context_window: Max tokens for context
            madhab_weights: Prior weights for different madhabs
            temperature: Model temperature for generation
            api_key: API key if using external models
        """
        self.model_name = model_name
        self.rag_retriever = rag_retriever
        self.context_window = context_window
        self.temperature = temperature
        self.api_key = api_key

        # Default madhab weights (equal by default)
        self.madhab_weights = madhab_weights or {
            "hanafi": 0.25,
            "maliki": 0.25,
            "shafii": 0.25,
            "hanbali": 0.25
        }

        self.generation_history: List[Dict[str, Any]] = []

    def generate(
        self,
        query: str,
        retrieved_context: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        allow_ijtihad: bool = True
    ) -> Dict[str, Any]:
        """
        Generate interpretation from query + retrieved context.

        Args:
            query: Question about Islamic law/Quran
            retrieved_context: List of relevant sources with scores
            system_prompt: Optional custom system prompt
            allow_ijtihad: Whether to allow independent reasoning (ijtihad)

        Returns:
            Dictionary with:
                - interpretation: Main generated text
                - confidence: Confidence score 0-1
                - sources: List of cited sources
                - citations: Formatted citations
                - reasoning: Model's reasoning process
                - alternative_views: Other valid positions
        """
        # Convert context to Source objects
        sources = self._parse_context(retrieved_context)

        # Build prompt
        prompt = self._build_prompt(
            query,
            sources,
            system_prompt,
            allow_ijtihad
        )

        # Generate interpretation (mock for now)
        interpretation_text = self._generate_text(prompt)

        # Extract confidence from model output
        confidence = self._extract_confidence(interpretation_text)

        # Identify sources cited
        citations = self._extract_citations(interpretation_text, sources)

        # Generate alternative views if appropriate
        alternatives = self._generate_alternatives(query, sources) if allow_ijtihad else []

        result = {
            "interpretation": interpretation_text,
            "confidence": confidence,
            "sources": [asdict(s) for s in sources],
            "citations": citations,
            "reasoning": self._extract_reasoning(interpretation_text),
            "alternative_views": alternatives,
            "model_used": self.model_name,
            "query": query
        }

        self.generation_history.append(result)

        return result

    def _parse_context(self, retrieved_context: List[Dict[str, Any]]) -> List[Source]:
        """Convert raw context to Source objects."""
        sources = []

        for item in retrieved_context:
            # Determine source type
            if "surah" in item:
                source_type = SourceType.QURAN
                reference = f"{item['surah']}:{item.get('ayah', '?')}"
            elif "hadith" in item.get("source", "").lower():
                source_type = SourceType.HADITH
                reference = item.get("source", "Hadith")
            elif "madhab" in item:
                source_type = SourceType.MADHAB_OPINION
                reference = item.get("madhab", "")
            else:
                source_type = SourceType.IJMA
                reference = item.get("reference", "Classical consensus")

            source = Source(
                source_type=source_type,
                reference=reference,
                text=item.get("text", ""),
                score=item.get("score", 0.5),
                madhab=item.get("madhab")
            )
            sources.append(source)

        return sources

    def _build_prompt(
        self,
        query: str,
        sources: List[Source],
        system_prompt: Optional[str],
        allow_ijtihad: bool
    ) -> str:
        """Build generation prompt from query and sources."""
        if system_prompt:
            return system_prompt

        # Format sources
        source_text = "\n".join([
            f"[{s.source_type.value}:{s.reference}] {s.text}"
            for s in sources
        ])

        prompt = f"""
You are a Islamic scholar specializing in Quranic interpretation and Islamic jurisprudence.

Question: {query}

Relevant Sources:
{source_text if source_text else "No specific sources retrieved. Base answer on classical Islamic knowledge."}

Instructions:
1. Provide a clear, scholarly interpretation respecting classical sources
2. Consider the perspective of different madhabs (schools of law)
3. Cite relevant Quranic verses and hadith
4. Explain reasoning process
5. Acknowledge valid alternative views if applicable
6. Rate your confidence in the interpretation (0-1)

Format your response as:
INTERPRETATION: [Your main answer]
CONFIDENCE: [0.0-1.0]
REASONING: [Why you conclude this]
CITATIONS: [List of sources used]
ALTERNATIVES: [Other valid positions]
"""
        return prompt

    def _generate_text(self, prompt: str) -> str:
        """Generate text from prompt using configured model."""
        # Mock generation - in production would call actual LLM
        # For testing, return a structured response

        mock_response = """
INTERPRETATION: Islamic jurisprudence recognizes riba (interest/usury) as prohibited based on strong Quranic evidence and scholarly consensus (ijma). The prohibition is established across all four madhabs and contemporary Islamic institutions.

The Quranic basis includes multiple verses (2:275-280, 3:130, 4:161, 30:39) that clearly prohibit riba. Classical hadith collections (Sahih Bukhari, Sahih Muslim, Sunan Abu Dawud) report the Prophet's explicit prohibition and curse upon those involved in riba transactions.

All major madhabs (Hanafi, Maliki, Shafi'i, Hanbali) agree on the core prohibition, though they may differ on technical definitions in modern financial contexts.

CONFIDENCE: 0.92
REASONING: This conclusion is based on explicit Quranic prohibitions, hadith evidence, and unanimous madhab consensus (ijma). The agreement across multiple sources and schools of law provides high confidence.

CITATIONS:
- Quran 2:275-280 (primary prohibition)
- Sahih Bukhari 34:160 (hadith evidence)
- Classical madhab consensus

ALTERNATIVES:
- Some contemporary scholars debate the applicability to certain modern financial instruments
- Differences exist on technical definitions (riba al-nasi'a vs riba al-fadl)
"""
        return mock_response

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from generated text."""
        try:
            lines = text.split("\n")
            for line in lines:
                if "CONFIDENCE:" in line:
                    conf_str = line.split(":")[-1].strip()
                    return float(conf_str)
        except (ValueError, IndexError):
            pass
        return 0.75  # Default confidence

    def _extract_citations(
        self,
        text: str,
        sources: List[Source]
    ) -> List[Dict[str, Any]]:
        """Extract and format citations from response."""
        citations = []

        for source in sources:
            citations.append({
                "type": source.source_type.value,
                "reference": source.reference,
                "score": source.score,
                "madhab": source.madhab
            })

        return citations

    def _extract_reasoning(self, text: str) -> str:
        """Extract reasoning section from generated text."""
        try:
            lines = text.split("\n")
            in_reasoning = False
            reasoning_lines = []

            for line in lines:
                if "REASONING:" in line:
                    in_reasoning = True
                    reasoning_lines.append(line.split(":", 1)[-1].strip())
                elif in_reasoning and line.strip() and not any(
                    keyword in line for keyword in ["CITATIONS:", "ALTERNATIVES:"]
                ):
                    reasoning_lines.append(line.strip())
                elif in_reasoning and any(
                    keyword in line for keyword in ["CITATIONS:", "ALTERNATIVES:"]
                ):
                    break

            return " ".join(reasoning_lines)
        except Exception:
            return "Interpretation based on retrieved classical sources and scholarly consensus."

    def _generate_alternatives(
        self,
        query: str,
        sources: List[Source]
    ) -> List[str]:
        """Generate alternative valid interpretations."""
        alternatives = []

        # Check madhab diversity
        madhabs_in_sources = set(s.madhab for s in sources if s.madhab)

        if len(madhabs_in_sources) > 1:
            alternatives.append(
                f"Different madhabs may emphasize different aspects of this issue"
            )

        # Mention historical vs contemporary perspectives
        if any(s.source_type == SourceType.HADITH for s in sources):
            alternatives.append(
                "Classical interpretations may need updating for modern contexts"
            )

        return alternatives

    def generate_batch(
        self,
        queries: List[str],
        contexts: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Generate interpretations for multiple queries."""
        results = []

        for query, context in zip(queries, contexts):
            result = self.generate(query, context)
            results.append(result)

        return results

    def get_history(self) -> List[Dict[str, Any]]:
        """Get generation history."""
        return self.generation_history

    def clear_history(self):
        """Clear generation history."""
        self.generation_history = []
