"""Classic candle patterns: engulfing, inside bar."""

from __future__ import annotations

import pandas as pd

from app.strategy.price_action.rejection import RejectionDetector


class PatternDetector:
    def detect(self, candles: pd.DataFrame) -> pd.DataFrame:
        df = RejectionDetector().detect(candles)
        df["bullish_engulfing"] = False
        df["bearish_engulfing"] = False
        df["inside_bar"] = False

        o, h, l, c = df["open"], df["high"], df["low"], df["close"]

        for i in range(1, len(df)):
            prev_bear = c.iloc[i - 1] < o.iloc[i - 1]
            prev_bull = c.iloc[i - 1] > o.iloc[i - 1]
            curr_bull = c.iloc[i] > o.iloc[i]
            curr_bear = c.iloc[i] < o.iloc[i]

            if prev_bear and curr_bull and c.iloc[i] > o.iloc[i - 1] and o.iloc[i] < c.iloc[i - 1]:
                df.iloc[i, df.columns.get_loc("bullish_engulfing")] = True
            if prev_bull and curr_bear and o.iloc[i] > c.iloc[i - 1] and c.iloc[i] < o.iloc[i - 1]:
                df.iloc[i, df.columns.get_loc("bearish_engulfing")] = True
            if h.iloc[i] < h.iloc[i - 1] and l.iloc[i] > l.iloc[i - 1]:
                df.iloc[i, df.columns.get_loc("inside_bar")] = True

        return df
