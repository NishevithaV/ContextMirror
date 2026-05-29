"""
Day-type clustering using KMeans on daily feature vectors.

The goal is to discover recurring "modes" of behaviour — e.g.:
  Cluster 0 → "high-output day": lots of steps, many meetings, fast replies
  Cluster 1 → "rest day": low steps, few events, slow or no messages
  Cluster 2 → "social day": low steps, high messaging, average health
  ...

We use KMeans rather than DBSCAN here because:
  - KMeans is faster and more predictable on small (30–180 day) datasets
  - The cluster count can be chosen by the user / elbow method
  - DBSCAN works well for larger datasets; switch by setting method="dbscan"

The returned ClusterResult includes per-cluster centroid statistics so the
frontend can label clusters meaningfully.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

ClusterMethod = Literal["kmeans", "dbscan"]

# Features used for clustering (all normalised before fitting)
_CLUSTER_FEATURES = [
    "steps",
    "sleep_hours",
    "heart_rate_avg",
    "active_minutes",
    "event_count",
    "total_event_hours",
    "cancellation_rate",
    "messages_sent",
    "messages_received",
    "unique_chats",
]


@dataclass
class ClusterResult:
    """
    Clustering output for the full date range.

    Attributes
    ----------
    labels:
        Cluster label per day, in the same order as `dates`.
        DBSCAN may produce -1 (noise) labels.
    dates:
        ISO date strings corresponding to each label.
    n_clusters:
        Number of distinct clusters found (excluding DBSCAN noise).
    cluster_profiles:
        Dict mapping cluster_id → {feature: mean_value, ...}.
        Use this to label each cluster (e.g. "high-activity", "rest").
    inertia:
        KMeans within-cluster sum of squares. None for DBSCAN.
    """
    labels: list[int]
    dates: list[str]
    n_clusters: int
    cluster_profiles: dict[int, dict[str, float]]
    inertia: float | None = None


def _build_feature_matrix(day_records: list[dict[str, Any]]) -> pd.DataFrame:
    """Build the feature matrix — same logic as correlation._extract_features."""
    rows = []
    for r in day_records:
        health = r.get("health") or {}
        events = r.get("calendar_events") or []
        messaging = r.get("messaging") or []

        confirmed = [e for e in events if e.get("status") == "confirmed"]
        cancelled = [e for e in events if e.get("status") == "cancelled"]
        event_hours = sum(
            (
                pd.to_datetime(e["end_time"]) - pd.to_datetime(e["start_time"])
            ).total_seconds() / 3600
            for e in confirmed
            if e.get("start_time") and e.get("end_time")
        )

        rows.append(
            {
                "date": pd.to_datetime(r["date"]),
                "steps": health.get("steps"),
                "sleep_hours": health.get("sleep_hours"),
                "heart_rate_avg": health.get("heart_rate_avg"),
                "active_minutes": health.get("active_minutes"),
                "event_count": len(events),
                "cancelled_count": len(cancelled),
                "cancellation_rate": len(cancelled) / len(events) if events else 0.0,
                "total_event_hours": event_hours,
                "messages_sent": sum(m.get("message_count_sent", 0) for m in messaging),
                "messages_received": sum(
                    m.get("message_count_received", 0) for m in messaging
                ),
                "unique_chats": len(messaging),
            }
        )

    df = pd.DataFrame(rows).set_index("date").sort_index()
    # Keep only the features we cluster on
    available = [f for f in _CLUSTER_FEATURES if f in df.columns]
    return df[available]


def _elbow_k(X: np.ndarray, max_k: int = 8) -> int:
    """
    Pick k using the elbow method (largest second-derivative of inertia curve).
    Falls back to k=3 if the curve is flat.
    """
    inertias = []
    k_range = range(2, min(max_k + 1, len(X)))
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        km.fit(X)
        inertias.append(km.inertia_)

    if len(inertias) < 3:
        return 3

    diffs = np.diff(inertias)
    second_diffs = np.diff(diffs)
    best_idx = int(np.argmax(second_diffs)) + 2  # offset for double diff
    return max(2, min(best_idx, max_k))


def cluster_day_types(
    day_records: list[dict[str, Any]],
    n_clusters: int | None = None,
    method: ClusterMethod = "kmeans",
    dbscan_eps: float = 0.5,
    dbscan_min_samples: int = 5,
) -> ClusterResult:
    """
    Cluster days into behavioural archetypes.

    Parameters
    ----------
    day_records:
        List of DayRecord dicts. 30+ days recommended.
    n_clusters:
        Number of KMeans clusters. If None, auto-selected via elbow method.
        Ignored when method="dbscan".
    method:
        "kmeans" (default) or "dbscan".
    dbscan_eps:
        Neighbourhood radius for DBSCAN (in normalised feature space).
    dbscan_min_samples:
        Minimum points to form a dense region in DBSCAN.

    Returns
    -------
    ClusterResult with per-day labels and per-cluster centroid profiles.

    Example
    -------
    >>> result = cluster_day_types(day_records, n_clusters=4)
    >>> result.cluster_profiles
    {0: {"steps": 12000, "sleep_hours": 7.2, ...}, 1: {...}, ...}
    """
    df = _build_feature_matrix(day_records)

    # Impute missing values with column medians so NaN doesn't lose the day
    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(df.values)

    # Standardise so all features are on the same scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    dates = [d.date().isoformat() for d in df.index]

    if method == "dbscan":
        model = DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_samples)
        labels = model.fit_predict(X_scaled).tolist()
        unique_labels = [l for l in set(labels) if l != -1]
        n_found = len(unique_labels)
        inertia = None
    else:
        k = n_clusters if n_clusters is not None else _elbow_k(X_scaled)
        model = KMeans(n_clusters=k, n_init=10, random_state=42)
        labels = model.fit_predict(X_scaled).tolist()
        unique_labels = list(range(k))
        n_found = k
        inertia = float(model.inertia_)

    # Build cluster profiles in original (unscaled) units
    feature_names = df.columns.tolist()
    cluster_profiles: dict[int, dict[str, float]] = {}
    df_with_labels = df.copy()
    df_with_labels["_label"] = labels

    for label_id in unique_labels:
        mask = df_with_labels["_label"] == label_id
        profile = df_with_labels.loc[mask, feature_names].mean().round(2).to_dict()
        cluster_profiles[label_id] = {k: float(v) for k, v in profile.items()}

    return ClusterResult(
        labels=labels,
        dates=dates,
        n_clusters=n_found,
        cluster_profiles=cluster_profiles,
        inertia=inertia,
    )
