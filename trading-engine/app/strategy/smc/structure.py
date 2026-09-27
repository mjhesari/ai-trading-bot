"""Market structure: trend + BOS + CHoCH over swings."""

from __future__ import annotations

import pandas as pd

from app.strategy.smc.bos import is_bearish_bos, is_bullish_bos
from app.strategy.smc.choch import is_bearish_choch, is_bullish_choch


class MarketStructure:
    def detect(self, candles: pd.DataFrame) -> pd.DataFrame:
        """Requires swing_high / swing_low columns from SwingDetector."""
        df = candles.copy()
        df["trend"] = None
        df["bos"] = False
        df["choch"] = False

        last_swing_high = None
        last_swing_low = None
        trend = None

        for i in range(len(df)):
            close = float(df["close"].iloc[i])

            if bool(df["swing_high"].iloc[i]):
                last_swing_high = float(df["high"].iloc[i])
            if bool(df["swing_low"].iloc[i]):
                last_swing_low = float(df["low"].iloc[i])

            if is_bullish_choch(trend, close, last_swing_high):
                df.iloc[i, df.columns.get_loc("choch")] = True
                trend = "up"
                last_swing_high = None
            elif is_bullish_bos(trend, close, last_swing_high):
                df.iloc[i, df.columns.get_loc("bos")] = True
                trend = "up"
                last_swing_high = None
            elif is_bearish_choch(trend, close, last_swing_low):
                df.iloc[i, df.columns.get_loc("choch")] = True
                trend = "down"
                last_swing_low = None
            elif is_bearish_bos(trend, close, last_swing_low):
                df.iloc[i, df.columns.get_loc("bos")] = True
                trend = "down"
                last_swing_low = None

            df.iloc[i, df.columns.get_loc("trend")] = trend

        return df
