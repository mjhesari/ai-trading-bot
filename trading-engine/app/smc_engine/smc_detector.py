"""
تشخیص مفاهیم Smart Money Concepts (SMC):
  - Order Block (بولیش/بریش)
  - Fair Value Gap / Imbalance (FVG)
  - Liquidity Zones (Equal Highs / Equal Lows)
  - Premium / Discount Zone (بر اساس فیبوناچی ۵۰٪ سوئینگ اخیر)
"""

import pandas as pd


def detect_order_blocks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Order Block ساده:
      - Bullish OB: آخرین کندل نزولی (قرمز) قبل از یک BOS صعودی
      - Bearish OB: آخرین کندل صعودی (سبز) قبل از یک BOS نزولی
    نیازمند ستون‌های 'bos' و 'trend' که در market_structure ساخته می‌شن.
    """
    df = df.copy()
    df["bullish_ob"] = False
    df["bearish_ob"] = False

    for i in range(1, len(df)):
        if df["bos"].iloc[i] and df["trend"].iloc[i] == "up":
            # به عقب برگرد و آخرین کندل نزولی را پیدا کن
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


def detect_fvg(df: pd.DataFrame, min_gap_pct: float = 0.0002) -> pd.DataFrame:
    """
    Fair Value Gap (سه‌کندلی):
      - Bullish FVG: high کندل اول < low کندل سوم  (گپ خالی صعودی)
      - Bearish FVG: low کندل اول > high کندل سوم   (گپ خالی نزولی)
    """
    df = df.copy()
    df["bullish_fvg"] = False
    df["bearish_fvg"] = False

    highs = df["high"].values
    lows = df["low"].values
    closes = df["close"].values

    for i in range(2, len(df)):
        ref_price = closes[i]
        gap_up = lows[i] - highs[i - 2]
        gap_down = lows[i - 2] - highs[i]

        if gap_up > 0 and (gap_up / ref_price) > min_gap_pct:
            df.iloc[i - 1, df.columns.get_loc("bullish_fvg")] = True
        if gap_down > 0 and (gap_down / ref_price) > min_gap_pct:
            df.iloc[i - 1, df.columns.get_loc("bearish_fvg")] = True

    return df


def detect_liquidity_zones(df: pd.DataFrame, tolerance: float = 0.0005) -> pd.DataFrame:
    """
    Equal Highs / Equal Lows: نواحی که چند سوئینگ تقریبا در یک سطح شکل گرفتن
    (جایی که لیکوییدیتی/استاپ‌لاس معامله‌گران خرد جمع شده).
    """
    df = df.copy()
    df["equal_high"] = False
    df["equal_low"] = False

    swing_highs = df[df["swing_high"]]["high"]
    swing_lows = df[df["swing_low"]]["low"]

    sh_list = list(zip(swing_highs.index, swing_highs.values))
    for idx in range(1, len(sh_list)):
        _, h1 = sh_list[idx - 1]
        i2, h2 = sh_list[idx]
        if abs(h1 - h2) / h1 < tolerance:
            df.loc[i2, "equal_high"] = True

    sl_list = list(zip(swing_lows.index, swing_lows.values))
    for idx in range(1, len(sl_list)):
        _, l1 = sl_list[idx - 1]
        i2, l2 = sl_list[idx]
        if abs(l1 - l2) / l1 < tolerance:
            df.loc[i2, "equal_low"] = True

    return df


def detect_premium_discount(df: pd.DataFrame, lookback: int = 50, level: float = 0.5) -> pd.DataFrame:
    """
    بر اساس بالاترین/پایین‌ترین قیمت در `lookback` کندل اخیر، ناحیه‌ی فعلی را
    Premium (بالای ۵۰٪ رنج -> ناحیه فروش) یا Discount (پایین ۵۰٪ رنج -> ناحیه خرید) می‌کند.
    """
    df = df.copy()
    df["zone"] = None

    for i in range(lookback, len(df)):
        window = df.iloc[i - lookback:i]
        high, low = window["high"].max(), window["low"].min()
        mid = low + (high - low) * level
        df.iloc[i, df.columns.get_loc("zone")] = "premium" if df["close"].iloc[i] > mid else "discount"

    return df
