"""Liquidity zones: Equal Highs / Equal Lows + Premium/Discount."""

from __future__ import annotations

import pandas as pd


class LiquidityDetector:
    def __init__(self, tolerance: float = 0.0005, lookback: int = 50, level: float = 0.5) -> None:
        self.tolerance = tolerance
        self.lookback = lookback
        self.level = level

    def detect(self, candles: pd.DataFrame, structure: pd.DataFrame | None = None) -> pd.DataFrame:
        """structure is accepted for pipeline compatibility; swings come from candles."""
        df = candles.copy() if structure is None else structure.copy()
        df["equal_high"] = False
        df["equal_low"] = False
        df["zone"] = None

        swing_highs = df[df["swing_high"]]["high"]
        swing_lows = df[df["swing_low"]]["low"]

        sh_list = list(zip(swing_highs.index, swing_highs.values))
        for idx in range(1, len(sh_list)):
            _, h1 = sh_list[idx - 1]
            i2, h2 = sh_list[idx]
            if abs(h1 - h2) / h1 < self.tolerance:
                df.loc[i2, "equal_high"] = True

        sl_list = list(zip(swing_lows.index, swing_lows.values))
        for idx in range(1, len(sl_list)):
            _, l1 = sl_list[idx - 1]
            i2, l2 = sl_list[idx]
            if abs(l1 - l2) / l1 < self.tolerance:
                df.loc[i2, "equal_low"] = True

        for i in range(self.lookback, len(df)):
            window = df.iloc[i - self.lookback : i]
            high, low = window["high"].max(), window["low"].min()
            mid = low + (high - low) * self.level
            df.iloc[i, df.columns.get_loc("zone")] = (
                "premium" if df["close"].iloc[i] > mid else "discount"
            )

        return df
