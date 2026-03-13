"""
TextProfiler — FastAPI Router
===============================
Mount this router in any FastAPI app:

    from nomos.products.text_profiler.api import router
    app.include_router(router, prefix="/text")

Endpoints:
    POST /text/profile  — profile a text input
    GET  /text/health   — health check
"""

from __future__ import annotations

from typing import Optional, List
import time

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field

    _FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FASTAPI_AVAILABLE = False

from . import TextProfiler, ProfileReport


# ── Singleton profiler instance ──────────────────────────────────────────────
_profiler_instance: Optional[TextProfiler] = None


def _get_profiler() -> TextProfiler:
    global _profiler_instance
    if _profiler_instance is None:
        _profiler_instance = TextProfiler()
    return _profiler_instance


# ── Only define router if FastAPI is available ───────────────────────────────

if _FASTAPI_AVAILABLE:

    router = APIRouter(tags=["text-profiler"])

    # ── Request / Response models ────────────────────────────────────────

    class ProfileRequest(BaseModel):
        text: str = Field(..., description="Text to profile")
        context: Optional[str] = Field(
            default=None,
            description="Optional context to inform the analysis",
        )

    class ProfileResponse(BaseModel):
        emotional_category: str
        valence: float
        arousal: float
        complexity_score: float
        confidence: float
        attention_salience: float
        themes: List[str]
        secondary_category: str
        attention_active: bool
        information_flow: float
        duration_ms: float

    class HealthResponse(BaseModel):
        status: str
        service: str
        timestamp: float

    # ── Endpoints ────────────────────────────────────────────────────────

    @router.post("/profile", response_model=ProfileResponse)
    def profile_text(request: ProfileRequest) -> ProfileResponse:
        """
        Profile a text input across emotional, complexity, confidence,
        and thematic dimensions using Quranic emotional categories.
        """
        profiler = _get_profiler()
        try:
            report: ProfileReport = profiler.profile(
                text=request.text,
                context=request.context,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return ProfileResponse(**report.to_dict())

    @router.get("/health", response_model=HealthResponse)
    def health_check() -> HealthResponse:
        """Return service health status."""
        return HealthResponse(
            status="ok",
            service="text-profiler",
            timestamp=time.time(),
        )

else:  # pragma: no cover
    router = None  # type: ignore[assignment]
