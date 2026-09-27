"""Candle helpers and OHLC normalization."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ("open", "high", "low", "close", "volume")


def normalize_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure standard OHLC columns and a DatetimeIndex named time."""
    out = df.copy()
    rename_map = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    out = out.rename(columns={k: v for k, v in rename_map.items() if k in out.columns})
    missing = [c for c in REQUIRED_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError(f"Missing OHLC columns: {missing}")
    if out.index.name != "time":
        out.index.name = "time"
    return out[list(REQUIRED_COLUMNS)]


def body_size(open_: float, close: float) -> float:
    return abs(close - open_)


def candle_range(high: float, low: float) -> float:
    return max(high - low, 1e-9)
