"""
تشخیص الگوهای کلاسیک Price Action برای تایید نقطه‌ی ورود:
  - Bullish / Bearish Engulfing
  - Pin Bar (Hammer / Shooting Star)
  - Inside Bar
"""

import pandas as pd


def detect_price_action(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["bullish_engulfing"] = False
    df["bearish_engulfing"] = False
    df["bullish_pinbar"] = False
    df["bearish_pinbar"] = False
    df["inside_bar"] = False

    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    body = (c - o).abs()
    candle_range = (h - l).replace(0, 1e-9)
    upper_wick = h - df[["open", "close"]].max(axis=1)
    lower_wick = df[["open", "close"]].min(axis=1) - l

    for i in range(1, len(df)):
        # --- Engulfing ---
        prev_bear = c.iloc[i - 1] < o.iloc[i - 1]
        prev_bull = c.iloc[i - 1] > o.iloc[i - 1]
        curr_bull = c.iloc[i] > o.iloc[i]
        curr_bear = c.iloc[i] < o.iloc[i]

        if prev_bear and curr_bull and c.iloc[i] > o.iloc[i - 1] and o.iloc[i] < c.iloc[i - 1]:
            df.iloc[i, df.columns.get_loc("bullish_engulfing")] = True
        if prev_bull and curr_bear and o.iloc[i] > c.iloc[i - 1] and c.iloc[i] < o.iloc[i - 1]:
            df.iloc[i, df.columns.get_loc("bearish_engulfing")] = True

        # --- Pin Bar (بدنه کوچک + سایه بلند در یک طرف) ---
        if body.iloc[i] / candle_range.iloc[i] < 0.3:
            if lower_wick.iloc[i] / candle_range.iloc[i] > 0.55:
                df.iloc[i, df.columns.get_loc("bullish_pinbar")] = True
            if upper_wick.iloc[i] / candle_range.iloc[i] > 0.55:
                df.iloc[i, df.columns.get_loc("bearish_pinbar")] = True

        # --- Inside Bar ---
        if h.iloc[i] < h.iloc[i - 1] and l.iloc[i] > l.iloc[i - 1]:
            df.iloc[i, df.columns.get_loc("inside_bar")] = True

    return df
