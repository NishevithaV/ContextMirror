"""
Time series decomposition and forecasting for health metrics.

Pipeline per metric:
  1. Build a daily pandas Series from DayRecord list
  2. STL decomposition  → trend + seasonality + residual
  3. SARIMA on the trend component → 7-day forecast
  4. Return everything the frontend needs to render the chart

Why STL + SARIMA instead of Prophet?
  - No heavy fbprophet dependency (difficult to install on ARM / Linux)
  - statsmodels ships with pandas, so no extra install
  - STL handles the seasonal split cleanly; SARIMA handles the stochastic part
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.statespace.sarimax import SARIMAX

logger = logging.getLogger(__name__)

# HK type → HealthMetrics field name mapping
_HK_TO_FIELD: dict[str, str] = {
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierHeartRate": "heart_rate_avg",
    "HKQuantityTypeIdentifierActiveEnergyBurned": "calories_burned",
    "HKQuantityTypeIdentifierAppleExerciseTime": "active_minutes",
}

# Metrics that are directly on HealthMetrics
FORECASTABLE_METRICS: list[str] = [
    "steps",
    "heart_rate_avg",
    "sleep_hours",
    "active_minutes",
    "calories_burned",
]


@dataclass
class DecomposedMetric:
    """STL decomposition components for a single metric."""
    metric: str
    dates: list[str]          # ISO date strings, aligned with all arrays below
    observed: list[float]
    trend: list[float]
    seasonal: list[float]
    residual: list[float]


@dataclass
class ForecastResult:
    """
    Full output for one metric: decomposition + forward forecast.

    The frontend can render:
      - observed / trend / seasonal as a decomposition chart
      - forecast_values + forecast_dates as a future projection strip
      - forecast_lower / forecast_upper as a confidence band
    """
    metric: str
    decomposed: DecomposedMetric
    forecast_dates: list[str]    # next `horizon` days (ISO strings)
    forecast_values: list[float]
    forecast_lower: list[float]  # 80 % prediction interval
    forecast_upper: list[float]
    sarima_order: tuple[int, int, int]
    sarima_seasonal_order: tuple[int, int, int, int]


def _day_records_to_dataframe(day_records: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Convert the orchestrator's DayRecord dicts to a DataFrame indexed by date.

    Expected day_record shape (matches orchestrator/mcp_client/models.py):
      {
        "date": "2025-01-01",
        "health": {
          "steps": 8000,
          "sleep_hours": 7.5,
          "heart_rate_avg": 72,
          "active_minutes": 45,
          "calories_burned": 2100
        },
        ...
      }
    """
    rows = []
    for record in day_records:
        health = record.get("health") or {}
        rows.append(
            {
                "date": pd.to_datetime(record["date"]),
                "steps": health.get("steps"),
                "sleep_hours": health.get("sleep_hours"),
                "heart_rate_avg": health.get("heart_rate_avg"),
                "active_minutes": health.get("active_minutes"),
                "calories_burned": health.get("calories_burned"),
            }
        )
    df = pd.DataFrame(rows).set_index("date").sort_index()
    # Fill short gaps (≤ 3 days) linearly; leave longer gaps as NaN
    df = df.interpolate(method="linear", limit=3)
    return df


def _stl_decompose(series: pd.Series, period: int = 7) -> STL:
    """Run STL decomposition with a weekly seasonal period."""
    stl = STL(series.dropna(), period=period, robust=True)
    return stl.fit()


def _fit_sarima(
    series: pd.Series,
) -> tuple[SARIMAX, tuple[int, int, int], tuple[int, int, int, int]]:
    """
    Fit a SARIMA model with a simple auto-selection heuristic.

    We try a small grid of (p, d, q) orders and pick the lowest AIC.
    Seasonal period is fixed at 7 (weekly).  This keeps fitting time
    under a second for typical 90-day series.
    """
    best_aic = np.inf
    best_model = None
    best_order = (1, 1, 1)
    best_seasonal = (0, 1, 0, 7)

    candidate_orders = [
        (1, 1, 0),
        (0, 1, 1),
        (1, 1, 1),
        (2, 1, 0),
    ]

    clean = series.dropna()
    if len(clean) < 14:
        # Not enough data — fall back to a naive drift model
        order = (0, 1, 0)
        seasonal = (0, 0, 0, 0)
        model = SARIMAX(clean, order=order, seasonal_order=seasonal, trend="c")
        result = model.fit(disp=False)
        return result, order, seasonal

    for order in candidate_orders:
        try:
            model = SARIMAX(
                clean,
                order=order,
                seasonal_order=(0, 1, 0, 7),
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            fitted = model.fit(disp=False)
            if fitted.aic < best_aic:
                best_aic = fitted.aic
                best_model = fitted
                best_order = order
                best_seasonal = (0, 1, 0, 7)
        except Exception:
            continue

    if best_model is None:
        # Absolute fallback
        model = SARIMAX(clean, order=(1, 1, 0), seasonal_order=(0, 0, 0, 0))
        best_model = model.fit(disp=False)

    return best_model, best_order, best_seasonal


def decompose_and_forecast(
    day_records: list[dict[str, Any]],
    metrics: list[str] | None = None,
    horizon: int = 7,
) -> list[ForecastResult]:
    """
    Entry point: decompose health time series and produce a forward forecast.

    Parameters
    ----------
    day_records:
        List of DayRecord dicts from the orchestrator (at least 30 days
        recommended; 90 days gives better seasonal estimates).
    metrics:
        Which metrics to process. Defaults to all FORECASTABLE_METRICS.
        Pass a subset to speed things up: e.g. ["steps", "sleep_hours"].
    horizon:
        How many days ahead to forecast. Default 7.

    Returns
    -------
    List of ForecastResult, one per metric that had enough data.

    Example
    -------
    >>> results = decompose_and_forecast(day_records, metrics=["steps"])
    >>> results[0].forecast_values  # next 7 days of predicted steps
    """
    if metrics is None:
        metrics = FORECASTABLE_METRICS

    df = _day_records_to_dataframe(day_records)
    results: list[ForecastResult] = []

    for metric in metrics:
        if metric not in df.columns:
            logger.debug("Metric %s not in dataframe, skipping", metric)
            continue

        series = df[metric].dropna()
        if len(series) < 14:
            logger.info("Metric %s: only %d data points, skipping", metric, len(series))
            continue

        # --- STL Decomposition ---
        try:
            stl_result = _stl_decompose(series)
        except Exception as exc:
            logger.warning("STL failed for %s: %s", metric, exc)
            continue

        decomposed = DecomposedMetric(
            metric=metric,
            dates=[d.date().isoformat() for d in series.index],
            observed=series.tolist(),
            trend=stl_result.trend.tolist(),
            seasonal=stl_result.seasonal.tolist(),
            residual=stl_result.resid.tolist(),
        )

        # --- SARIMA Forecast ---
        try:
            fitted_model, order, seasonal_order = _fit_sarima(series)
            forecast = fitted_model.get_forecast(steps=horizon)
            pred_mean = forecast.predicted_mean
            pred_ci = forecast.conf_int(alpha=0.2)  # 80 % interval

            last_date = series.index[-1]
            future_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D"
            )

            results.append(
                ForecastResult(
                    metric=metric,
                    decomposed=decomposed,
                    forecast_dates=[d.date().isoformat() for d in future_dates],
                    forecast_values=pred_mean.tolist(),
                    forecast_lower=pred_ci.iloc[:, 0].tolist(),
                    forecast_upper=pred_ci.iloc[:, 1].tolist(),
                    sarima_order=order,
                    sarima_seasonal_order=seasonal_order,
                )
            )
        except Exception as exc:
            logger.warning("SARIMA forecast failed for %s: %s", metric, exc)
            # Still include the decomposition even without forecast
            results.append(
                ForecastResult(
                    metric=metric,
                    decomposed=decomposed,
                    forecast_dates=[],
                    forecast_values=[],
                    forecast_lower=[],
                    forecast_upper=[],
                    sarima_order=(0, 0, 0),
                    sarima_seasonal_order=(0, 0, 0, 0),
                )
            )

    return results
