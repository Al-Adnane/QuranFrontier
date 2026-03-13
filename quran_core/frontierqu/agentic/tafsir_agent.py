# src/frontierqu/agentic/tafsir_agent.py
"""TafsirAgent — Multi-Domain Verse Analysis and Synthesis.

Synthesizes interpretations of Quranic verses by combining all 7 FrontierQu
domains into a coherent narrative.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import os

from frontierqu.agentic.tools import execute_tool


@dataclass
class TafsirEntry:
    """Complete multi-domain analysis of a single verse."""
    verse: Tuple[int, int]
    arabic_text: str = ""
    thematic_analysis: Dict[str, Any] = field(default_factory=dict)
    linguistic_analysis: Dict[str, Any] = field(default_factory=dict)
    legal_context: Dict[str, Any] = field(default_factory=dict)
    topological_position: Dict[str, Any] = field(default_factory=dict)
    qiraat_variants: List[Dict] = field(default_factory=list)
    geometric_features: Dict[str, Any] = field(default_factory=dict)
    synthesis: str = ""


class TafsirAgent:
    """Agent that synthesizes multi-domain tafsir for Quranic verses."""

    def synthesize_local(self, verse: Tuple[int, int]) -> TafsirEntry:
        """Synthesize tafsir without API calls using local FrontierQu tools."""
        surah, ayah = verse

        # 1. Get Arabic text
        arabic_text = self._get_arabic_text(verse)

        # 2. Thematic analysis
        thematic = self._get_thematic(verse)

        # 3. Linguistic analysis
        linguistic = self._get_linguistic(verse, arabic_text)

        # 4. Legal context
        legal = self._get_legal(verse)

        # 5. Topological position
        topo = self._get_topological(thematic)

        # 6. Qira'at variants
        qiraat = self._get_qiraat(verse)

        # 7. Synthesize narrative
        synthesis = self._build_synthesis(
            verse, arabic_text, thematic, linguistic, legal, topo, qiraat
        )

        return TafsirEntry(
            verse=verse,
            arabic_text=arabic_text,
            thematic_analysis=thematic,
            linguistic_analysis=linguistic,
            legal_context=legal,
            topological_position=topo,
            qiraat_variants=qiraat,
            synthesis=synthesis,
        )

    def synthesize(self, verse: Tuple[int, int]) -> TafsirEntry:
        """Synthesize tafsir with AI narrative if API key available."""
        entry = self.synthesize_local(verse)

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return entry

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            enhanced = self._enhance_with_ai(client, entry)
            entry.synthesis = enhanced
        except Exception:
            pass  # Keep local synthesis on failure

        return entry

    def _get_arabic_text(self, verse: Tuple[int, int]) -> str:
        from frontierqu.data.quran_text import load_quran_corpus
        corpus = load_quran_corpus()
        entry = corpus.get(verse, {})
        return entry.get("text_ar", f"{verse[0]}:{verse[1]}")

    def _get_thematic(self, verse: Tuple[int, int]) -> Dict[str, Any]:
        from frontierqu.data.cross_references import THEMATIC_GROUPS
        themes = []
        for theme, verses in THEMATIC_GROUPS.items():
            if verse in verses:
                themes.append(theme)
        return {"themes": themes, "primary_theme": themes[0] if themes else "unclassified"}

    def _get_linguistic(self, verse: Tuple[int, int], arabic_text: str) -> Dict[str, Any]:
        try:
            rhet = execute_tool("compute_rhetorical_density", {"arabic_text": arabic_text})
            density = rhet.get("density", 0.0)
            bayan = rhet.get("bayan_devices", [])
            badi = rhet.get("badi_devices", [])
        except Exception:
            density, bayan, badi = 0.0, [], []

        # Morphological analysis of first word
        first_word_analysis = {}
        words = arabic_text.split()
        if words:
            try:
                result = execute_tool("analyze_word", {"word": words[0]})
                first_word_analysis = result
            except Exception:
                pass

        return {
            "density": density,
            "bayan_devices": bayan,
            "badi_devices": badi,
            "word_count": len(words),
            "first_word": first_word_analysis,
        }

    def _get_legal(self, verse: Tuple[int, int]) -> Dict[str, Any]:
        try:
            result = execute_tool("get_legal_ruling", {
                "surah": verse[0], "ayah": verse[1], "subject": "general"
            })
            return result
        except Exception:
            return {"status": "MUBAH", "reasoning_method": "default"}

    def _get_topological(self, thematic: Dict[str, Any]) -> Dict[str, Any]:
        primary = thematic.get("primary_theme", "")
        if primary and primary != "unclassified":
            try:
                result = execute_tool("compute_topological_features", {"theme": primary})
                return result
            except Exception:
                pass
        return {"b0": 1, "b1": 0, "note": "no theme"}

    def _get_qiraat(self, verse: Tuple[int, int]) -> List[Dict]:
        try:
            result = execute_tool("get_qiraat_variants", {
                "surah": verse[0], "ayah": verse[1]
            })
            return result.get("variants", [])
        except Exception:
            return []

    def _build_synthesis(
        self,
        verse: Tuple[int, int],
        arabic_text: str,
        thematic: Dict,
        linguistic: Dict,
        legal: Dict,
        topo: Dict,
        qiraat: List,
    ) -> str:
        surah, ayah = verse
        themes = thematic.get("themes", [])
        density = linguistic.get("density", 0.0)
        status = legal.get("status", "MUBAH")
        b0, b1 = topo.get("b0", 1), topo.get("b1", 0)
        variants = len(qiraat)

        parts = [
            f"Verse {surah}:{ayah} analysis:",
            f"• Thematic: {', '.join(themes) if themes else 'unclassified'}",
            f"• Rhetorical density: {density:.3f} bits/morpheme",
            f"• Legal status: {status}",
            f"• Topological: b0={b0}, b1={b1} (connectivity={b0}, cycles={b1})",
            f"• Qira'at variants: {variants}",
        ]

        if linguistic.get("bayan_devices"):
            parts.append(f"• Rhetorical devices (bayan): {', '.join(linguistic['bayan_devices'])}")

        return "\n".join(parts)

    def _enhance_with_ai(self, client, entry: TafsirEntry) -> str:
        """Use Claude to generate a narrative synthesis."""
        prompt = f"""Based on this computational analysis of Quranic verse {entry.verse[0]}:{entry.verse[1]},
write a concise scholarly synthesis (2-3 paragraphs):

Arabic text: {entry.arabic_text}
Themes: {entry.thematic_analysis}
Linguistic: {entry.linguistic_analysis}
Legal context: {entry.legal_context}
Topological: {entry.topological_position}
Qira'at: {len(entry.qiraat_variants)} variant readings

Write a synthesis that integrates these computational findings with traditional Islamic scholarship."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
