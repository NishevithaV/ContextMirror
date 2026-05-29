"""
ML Engine HTTP server.

Wraps the run_pipeline() library function in a single FastAPI endpoint
so the orchestrator can call it over HTTP instead of importing it directly.

POST /analyze
  Body: { day_records: [...], forecast_horizon: 7, n_clusters: null,
          correlation_alpha: 0.05, lag_days: 0 }
  Returns: { forecasts, correlations, clusters }

Run locally:
    uvicorn server:app --reload --port 8001
"""

import logging
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from main import PipelineResult, run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="ContextMirror ML Engine",
    description="Pattern detection: forecasts, correlations, and day-type clusters.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    day_records: list[dict[str, Any]]
    forecast_horizon: int = Field(default=7, ge=1, le=30)
    n_clusters: int | None = None
    correlation_alpha: float = Field(default=0.05, gt=0, lt=1)
    lag_days: int = Field(default=0, ge=0, le=7)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(body: AnalyzeRequest):
    """
    Run the full pattern pipeline over a window of DayRecords.

    Returns forecasts (time series), correlations (cross-source), and
    clusters (day-type archetypes).
    """
    if len(body.day_records) < 7:
        raise HTTPException(
            status_code=422,
            detail=f"Need at least 7 days of data, got {len(body.day_records)}.",
        )

    try:
        result: PipelineResult = run_pipeline(
            body.day_records,
            forecast_horizon=body.forecast_horizon,
            n_clusters=body.n_clusters,
            correlation_alpha=body.correlation_alpha,
            lag_days=body.lag_days,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    return {
        "forecasts": [asdict(f) for f in result.forecasts],
        "correlations": [asdict(c) for c in result.correlations],
        "clusters": asdict(result.clusters),
    }
