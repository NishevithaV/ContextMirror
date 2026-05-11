"""
ML Engine entry point.

This module is called by the orchestrator (via direct import or subprocess)
to run the full pattern pipeline over a window of DayRecord dicts and
return a structured result ready for the frontend.

Usage (from orchestrator):
    from ml_engine import run_pipeline, PipelineResult
    result = run_pipeline(day_records)

CLI usage (for local testing):
    python -m ml_engine --input records.json --out result.json
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from typing import Any

from patterns import (
    ClusterResult,
    CorrelationResult,
    ForecastResult,
    cluster_day_types,
    cross_source_correlations,
    decompose_and_forecast,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """
    Full output from the ML engine for one analysis window.

    Consumed by the orchestrator's /insights route, which converts this
    into PatternInsight objects and attaches them to InsightResponse.
    """
    forecasts: list[ForecastResult]
    correlations: list[CorrelationResult]
    clusters: ClusterResult


def run_pipeline(
    day_records: list[dict[str, Any]],
    forecast_metrics: list[str] | None = None,
    forecast_horizon: int = 7,
    n_clusters: int | None = None,
    correlation_alpha: float = 0.05,
    lag_days: int = 0,
) -> PipelineResult:
    """
    Run the full pattern analysis pipeline.

    Parameters
    ----------
    day_records:
        List of DayRecord dicts (from the orchestrator's /day-records endpoint
        or directly from MCPClient.fetch_day_records).
    forecast_metrics:
        Health metrics to forecast. Default: all available.
    forecast_horizon:
        Days ahead to forecast. Default 7.
    n_clusters:
        Number of day-type clusters. None = auto (elbow method).
    correlation_alpha:
        p-value cutoff for reporting correlations. Default 0.05.
    lag_days:
        Lag offset for correlation analysis. 0 = same-day, 1 = next-day effect.

    Returns
    -------
    PipelineResult containing forecasts, correlations, and clusters.
    """
    n = len(day_records)
    logger.info("Running ML pipeline over %d days", n)

    if n < 7:
        logger.warning("Only %d days of data — results will be unreliable", n)

    forecasts = decompose_and_forecast(
        day_records,
        metrics=forecast_metrics,
        horizon=forecast_horizon,
    )
    logger.info("Forecasts computed: %d metrics", len(forecasts))

    correlations = cross_source_correlations(
        day_records,
        alpha=correlation_alpha,
        lag_days=lag_days,
    )
    logger.info("Correlations found: %d significant pairs", len(correlations))

    clusters = cluster_day_types(day_records, n_clusters=n_clusters)
    logger.info(
        "Clustering complete: %d clusters over %d days",
        clusters.n_clusters,
        len(clusters.dates),
    )

    return PipelineResult(
        forecasts=forecasts,
        correlations=correlations,
        clusters=clusters,
    )


def _serialise(result: PipelineResult) -> dict[str, Any]:
    """Convert PipelineResult to a JSON-safe dict."""
    return {
        "forecasts": [asdict(f) for f in result.forecasts],
        "correlations": [asdict(c) for c in result.correlations],
        "clusters": asdict(result.clusters),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the ContextMirror ML pipeline")
    parser.add_argument("--input", required=True, help="Path to JSON file with DayRecord list")
    parser.add_argument("--out", default="-", help="Output path (default: stdout)")
    parser.add_argument("--horizon", type=int, default=7, help="Forecast horizon in days")
    parser.add_argument("--clusters", type=int, default=None, help="Number of clusters")
    parser.add_argument("--lag", type=int, default=0, help="Correlation lag in days")
    args = parser.parse_args()

    with open(args.input) as fh:
        records = json.load(fh)

    result = run_pipeline(
        records,
        forecast_horizon=args.horizon,
        n_clusters=args.clusters,
        lag_days=args.lag,
    )

    output = json.dumps(_serialise(result), indent=2)
    if args.out == "-":
        sys.stdout.write(output + "\n")
    else:
        with open(args.out, "w") as fh:
            fh.write(output)
        logger.info("Results written to %s", args.out)
