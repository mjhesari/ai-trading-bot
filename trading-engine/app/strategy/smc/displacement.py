"""Displacement detection (strong impulsive candles after structure breaks)."""

from __future__ import annotations

import pandas as pd


class DisplacementDetector:
    def __init__(self, body_ratio: float = 0.6, range_mult: float = 1.5) -> None:
        self.body_ratio = body_ratio
        self.range_mult = range_mult

    def detect(self, candles: pd.DataFrame) -> pd.DataFrame:
        df = candles.copy()
        df["bullish_displacement"] = False
        df["bearish_displacement"] = False

        body = (df["close"] - df["open"]).abs()
        rng = (df["high"] - df["low"]).replace(0, 1e-9)
        avg_range = rng.rolling(20, min_periods=5).mean()

        for i in range(1, len(df)):
            if avg_range.iloc[i] != avg_range.iloc[i] or avg_range.iloc[i] == 0:
                continue
            strong = body.iloc[i] / rng.iloc[i] >= self.body_ratio
            expansive = rng.iloc[i] >= avg_range.iloc[i] * self.range_mult
            if not (strong and expansive):
                continue
            if df["close"].iloc[i] > df["open"].iloc[i]:
                df.iloc[i, df.columns.get_loc("bullish_displacement")] = True
            else:
                df.iloc[i, df.columns.get_loc("bearish_displacement")] = True

        return df
