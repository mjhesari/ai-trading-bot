"""Timeframe helpers."""

from __future__ import annotations

SUPPORTED_TIMEFRAMES = {"1m", "5m", "15m", "30m", "1h", "4h", "1d"}


def normalize_timeframe(timeframe: str) -> str:
    tf = timeframe.strip().lower()
    aliases = {"60m": "1h", "240m": "4h", "d": "1d", "h1": "1h", "h4": "4h"}
    tf = aliases.get(tf, tf)
    if tf not in SUPPORTED_TIMEFRAMES:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    return tf
