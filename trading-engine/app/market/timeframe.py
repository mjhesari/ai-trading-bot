"""Timeframe helpers."""

from __future__ import annotations

# Canonical list used by API + UI
TIMEFRAME_OPTIONS: list[dict[str, str]] = [
    {"value": "1m", "label": "1 Minute"},
    {"value": "5m", "label": "5 Minutes"},
    {"value": "15m", "label": "15 Minutes"},
    {"value": "30m", "label": "30 Minutes"},
    {"value": "1h", "label": "1 Hour"},
    {"value": "2h", "label": "2 Hours"},
    {"value": "4h", "label": "4 Hours"},
    {"value": "1d", "label": "1 Day"},
    {"value": "1w", "label": "1 Week"},
]

SUPPORTED_TIMEFRAMES = {t["value"] for t in TIMEFRAME_OPTIONS}


def normalize_timeframe(timeframe: str) -> str:
    tf = timeframe.strip().lower()
    aliases = {
        "60m": "1h",
        "120m": "2h",
        "240m": "4h",
        "d": "1d",
        "day": "1d",
        "w": "1w",
        "week": "1w",
        "1wk": "1w",
        "h1": "1h",
        "h2": "2h",
        "h4": "4h",
        "m1": "1m",
        "m5": "5m",
        "m15": "15m",
        "m30": "30m",
    }
    tf = aliases.get(tf, tf)
    if tf not in SUPPORTED_TIMEFRAMES:
        raise ValueError(f"Unsupported timeframe: {timeframe}. Use one of {sorted(SUPPORTED_TIMEFRAMES)}")
    return tf
