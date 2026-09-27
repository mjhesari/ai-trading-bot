"""Rejection / pin-bar style price action."""

from __future__ import annotations

import pandas as pd

from app.strategy.price_action.candles import annotate_candle_metrics


class RejectionDetector:
    def detect(self, candles: pd.DataFrame) -> pd.DataFrame:
        df = annotate_candle_metrics(candles)
        df["bullish_pinbar"] = False
        df["bearish_pinbar"] = False

        for i in range(len(df)):
            if df["body"].iloc[i] / df["candle_range"].iloc[i] >= 0.3:
                continue
            if df["lower_wick"].iloc[i] / df["candle_range"].iloc[i] > 0.55:
                df.iloc[i, df.columns.get_loc("bullish_pinbar")] = True
            if df["upper_wick"].iloc[i] / df["candle_range"].iloc[i] > 0.55:
                df.iloc[i, df.columns.get_loc("bearish_pinbar")] = True

        return df
