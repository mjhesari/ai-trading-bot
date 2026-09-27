"""Candle body / wick classification helpers."""

from __future__ import annotations

import pandas as pd


def annotate_candle_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["body"] = (out["close"] - out["open"]).abs()
    out["candle_range"] = (out["high"] - out["low"]).replace(0, 1e-9)
    out["upper_wick"] = out["high"] - out[["open", "close"]].max(axis=1)
    out["lower_wick"] = out[["open", "close"]].min(axis=1) - out["low"]
    return out
