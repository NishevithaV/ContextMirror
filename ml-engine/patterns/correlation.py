"""
Cross-source correlation analysis.

Detects meaningful statistical relationships between health metrics,
calendar behaviour, and messaging patterns — the core "mirror" signal.

Examples of correlations we look for:
  - High step count → fewer calendar cancellations the next day
  - Poor sleep → slower WhatsApp response times
  - Dense calendar weeks → reduced active minutes

Implementation
--------------
We compute Pearson (linear) and Spearman (rank) correlations on daily
feature vectors extracted from DayRecord lists.  Only correlations that
pass a significance threshold (p < 0.05 by default) are returned.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

# Significance threshold for reporting a correlation
DEFAULT_ALPHA = 0.05
# Minimum absolute correlation to report (filter noise)
MIN_ABS_CORRELATION = 0.25


@dataclass
class CorrelationResult:
    """A single statistically significant correlation between two features."""
    feature_a: str
    feature_b: str
    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float
    n_samples: int
    # Human-readable direction: "positive" | "negative"
    direction: str
    # Strength label: "weak" | "moderate" | "strong"
    strength: str


def _extract_features(day_records: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Flatten DayRecord dicts into a daily feature matrix.

    Columns produced:
      Health:     steps, sleep_hours, heart_rate_avg, active_minutes, calories_burned
      Calendar:   event_count, cancelled_count, cancellation_rate, total_event_hours
      Messaging:  total_messages_sent, total_messages_received, avg_response_time_s,
                  unique_chats, avg_sentiment
    """
    rows = []
    for r in day_records:
        health = r.get("health") or {}
        events = r.get("calendar_events") or []
        messaging = r.get("messaging") or []

        # --- Calendar features ---
        confirmed = [e for e in events if e.get("status") == "confirmed"]
        cancelled = [e for e in events if e.get("status") == "cancelled"]
        event_hours = sum(
            (
                (
                    pd.to_datetime(e["end_time"]) - pd.to_datetime(e["start_time"])
                ).total_seconds() / 3600
            )
            for e in confirmed
            if e.get("start_time") and e.get("end_time")
        )

        # --- Messaging features ---
        sent = sum(m.get("message_count_sent", 0) for m in messaging)
        received = sum(m.get("message_count_received", 0) for m in messaging)
        response_times = [
            m["response_time_avg_seconds"]
            for m in messaging
            if m.get("response_time_avg_seconds") is not None
        ]
        sentiments = [
            m["sentiment_score"]
            for m in messaging
            if m.get("sentiment_score") is not None
        ]

        rows.append(
            {
                "date": pd.to_datetime(r["date"]),
                # health
                "steps": health.get("steps"),
                "sleep_hours": health.get("sleep_hours"),
                "heart_rate_avg": health.get("heart_rate_avg"),
                "active_minutes": health.get("active_minutes"),
                "calories_burned": health.get("calories_burned"),
                # calendar
                "event_count": len(events),
                "cancelled_count": len(cancelled),
                "cancellation_rate": (
                    len(cancelled) / len(events) if events else 0.0
                ),
                "total_event_hours": event_hours,
                # messaging
                "messages_sent": sent,
                "messages_received": received,
                "avg_response_time_s": (
                    float(np.mean(response_times)) if response_times else None
                ),
                "unique_chats": len(messaging),
                "avg_sentiment": (
                    float(np.mean(sentiments)) if sentiments else None
                ),
            }
        )

    return pd.DataFrame(rows).set_index("date").sort_index()


def _strength_label(r: float) -> str:
    abs_r = abs(r)
    if abs_r >= 0.6:
        return "strong"
    if abs_r >= 0.4:
        return "moderate"
    return "weak"


def cross_source_correlations(
    day_records: list[dict[str, Any]],
    alpha: float = DEFAULT_ALPHA,
    min_abs_r: float = MIN_ABS_CORRELATION,
    lag_days: int = 0,
) -> list[CorrelationResult]:
    """
    Compute pairwise Pearson + Spearman correlations across all feature pairs.

    Parameters
    ----------
    day_records:
        List of DayRecord dicts (30+ days recommended for reliable p-values).
    alpha:
        Maximum p-value to include a result. Default 0.05.
    min_abs_r:
        Minimum |r| to include a result. Default 0.25 (filters noise).
    lag_days:
        Shift health metrics forward by this many days before correlating,
        to detect lagged effects (e.g. bad sleep TODAY → fewer steps TOMORROW).
        Default 0 (same-day).

    Returns
    -------
    List of CorrelationResult sorted by |pearson_r| descending.
    """
    df = _extract_features(day_records)

    if lag_days > 0:
        health_cols = [
            "steps", "sleep_hours", "heart_rate_avg",
            "active_minutes", "calories_burned",
        ]
        non_health = [c for c in df.columns if c not in health_cols]
        df_health = df[health_cols].shift(lag_days)
        df = pd.concat([df_health, df[non_health]], axis=1)

    # Drop all-NaN columns
    df = df.dropna(axis=1, how="all")
    columns = list(df.columns)

    results: list[CorrelationResult] = []

    for i, col_a in enumerate(columns):
        for col_b in columns[i + 1 :]:
            pair = df[[col_a, col_b]].dropna()
            n = len(pair)
            if n < 10:
                continue

            a_vals = pair[col_a].values
            b_vals = pair[col_b].values

            try:
                p_r, p_p = stats.pearsonr(a_vals, b_vals)
                s_r, s_p = stats.spearmanr(a_vals, b_vals)
            except Exception:
                continue

            # Only report if both methods agree on significance
            if p_p > alpha and s_p > alpha:
                continue
            if abs(p_r) < min_abs_r and abs(s_r) < min_abs_r:
                continue

            results.append(
                CorrelationResult(
                    feature_a=col_a,
                    feature_b=col_b,
                    pearson_r=round(float(p_r), 4),
                    pearson_p=round(float(p_p), 4),
                    spearman_r=round(float(s_r), 4),
                    spearman_p=round(float(s_p), 4),
                    n_samples=n,
                    direction="positive" if p_r >= 0 else "negative",
                    strength=_strength_label(p_r),
                )
            )

    results.sort(key=lambda c: abs(c.pearson_r), reverse=True)
    return results
