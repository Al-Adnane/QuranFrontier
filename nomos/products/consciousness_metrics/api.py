"""
ConsciousnessMetrics — FastAPI Router
======================================
Mount this router in any FastAPI app:

    from nomos.products.consciousness_metrics.api import router
    app.include_router(router, prefix="/consciousness")

Endpoints:
    POST /consciousness/measure    — measure a single input
    GET  /consciousness/health     — health check
    GET  /consciousness/thresholds — current GWT thresholds
"""

from __future__ import annotations

from typing import Optional
import time

import numpy as np

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field

    _FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FASTAPI_AVAILABLE = False

from . import ConsciousnessMetrics, ConsciousnessReport

# ── Singleton metrics instance (shared across requests) ──────────────────────
_metrics_instance: Optional[ConsciousnessMetrics] = None


def _get_metrics() -> ConsciousnessMetrics:
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = ConsciousnessMetrics()
    return _metrics_instance


# ── Only define router if FastAPI is available ────────────────────────────────

if _FASTAPI_AVAILABLE:

    router = APIRouter(tags=["consciousness"])

    # ── Request / Response models ────────────────────────────────────────────

    class MeasureRequest(BaseModel):
        text: str = Field(..., description="Text to measure")
        model_id: str = Field(default="", description="Model identifier")

    class ConsciousnessReportResponse(BaseModel):
        phi_score: float
        gwt_active: bool
        ignition_threshold: float
        information_flow: float
        safety_grade: str
        broadcast_count: int
        ignition_rate: float
        workspace_stability: float
        model_id: str
        duration_ms: float

    class HealthResponse(BaseModel):
        status: str
        workspace_active: bool
        timestamp: float

    class ThresholdsResponse(BaseModel):
        ignition_threshold: float
        decay_rate: float
        workspace_dim: int
        safety_grades: dict

    # ── Endpoints ────────────────────────────────────────────────────────────

    @router.post("/measure", response_model=ConsciousnessReportResponse)
    def measure_consciousness(request: MeasureRequest) -> ConsciousnessReportResponse:
        """
        Measure consciousness metrics for a text input.

        Returns phi_score (IIT Φ approximation), GWT ignition state,
        information flow, and a safety grade.
        """
        cm = _get_metrics()
        try:
            report: ConsciousnessReport = cm.measure(
                input_data=request.text,
                model_id=request.model_id,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return ConsciousnessReportResponse(**report.to_dict())

    @router.get("/health", response_model=HealthResponse)
    def health_check() -> HealthResponse:
        """Return service health status."""
        cm = _get_metrics()
        ws = cm._gw.get_workspace_state()
        return HealthResponse(
            status="ok",
            workspace_active=ws is not None,
            timestamp=time.time(),
        )

    @router.get("/thresholds", response_model=ThresholdsResponse)
    def get_thresholds() -> ThresholdsResponse:
        """Return current GWT ignition thresholds and safety grade boundaries."""
        cm = _get_metrics()
        t = cm.get_thresholds()
        return ThresholdsResponse(**t)

else:  # pragma: no cover
    # Provide a stub so the module can be imported without FastAPI
    router = None  # type: ignore[assignment]
