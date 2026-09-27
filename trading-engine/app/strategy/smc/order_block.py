"""Order Block detection based on BOS events."""

from __future__ import annotations

import pandas as pd


class OrderBlockDetector:
    def detect(self, candles: pd.DataFrame) -> pd.DataFrame:
        """Requires bos and trend columns."""
        df = candles.copy()
        df["bullish_ob"] = False
        df["bearish_ob"] = False

        for i in range(1, len(df)):
            if df["bos"].iloc[i] and df["trend"].iloc[i] == "up":
                for j in range(i - 1, max(i - 15, -1), -1):
                    if df["close"].iloc[j] < df["open"].iloc[j]:
                        df.iloc[j, df.columns.get_loc("bullish_ob")] = True
                        break

            if df["bos"].iloc[i] and df["trend"].iloc[i] == "down":
                for j in range(i - 1, max(i - 15, -1), -1):
                    if df["close"].iloc[j] > df["open"].iloc[j]:
                        df.iloc[j, df.columns.get_loc("bearish_ob")] = True
                        break

        return df
