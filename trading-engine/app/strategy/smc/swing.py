"""Swing High / Swing Low detection."""

from __future__ import annotations

import pandas as pd


class SwingDetector:
    def __init__(self, lookback: int = 5) -> None:
        self.lookback = lookback

    def detect(self, candles: pd.DataFrame) -> pd.DataFrame:
        df = candles.copy()
        df["swing_high"] = False
        df["swing_low"] = False

        highs = df["high"].values
        lows = df["low"].values
        n = len(df)
        lb = self.lookback

        for i in range(lb, n - lb):
            window_high = highs[i - lb : i + lb + 1]
            window_low = lows[i - lb : i + lb + 1]
            if highs[i] == window_high.max():
                df.iloc[i, df.columns.get_loc("swing_high")] = True
            if lows[i] == window_low.min():
                df.iloc[i, df.columns.get_loc("swing_low")] = True

        return df
