"""Fair Value Gap (imbalance) detection."""

from __future__ import annotations

import pandas as pd


class FVGDetector:
    def __init__(self, min_gap_pct: float = 0.0002) -> None:
        self.min_gap_pct = min_gap_pct

    def detect(self, candles: pd.DataFrame) -> pd.DataFrame:
        df = candles.copy()
        df["bullish_fvg"] = False
        df["bearish_fvg"] = False

        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values

        for i in range(2, len(df)):
            ref_price = closes[i]
            gap_up = lows[i] - highs[i - 2]
            gap_down = lows[i - 2] - highs[i]

            if gap_up > 0 and (gap_up / ref_price) > self.min_gap_pct:
                df.iloc[i - 1, df.columns.get_loc("bullish_fvg")] = True
            if gap_down > 0 and (gap_down / ref_price) > self.min_gap_pct:
                df.iloc[i - 1, df.columns.get_loc("bearish_fvg")] = True

        return df
