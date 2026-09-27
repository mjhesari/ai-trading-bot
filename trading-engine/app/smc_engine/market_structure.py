"""
تشخیص ساختار بازار (Market Structure) - پایه‌ی تحلیل Smart Money

شامل:
  - تشخیص Swing High / Swing Low (فرکتال ساده)
  - تشخیص روند بر اساس توالی HH/HL (صعودی) یا LH/LL (نزولی)
  - تشخیص BOS (Break of Structure) و CHoCH (Change of Character)
"""

import pandas as pd


def find_swings(df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
    """
    یک کندل Swing High است اگر high آن از `lookback` کندل قبل و بعد بیشتر باشد.
    مشابه برای Swing Low.
    ستون‌های خروجی: swing_high (bool), swing_low (bool)
    """
    df = df.copy()
    df["swing_high"] = False
    df["swing_low"] = False

    highs = df["high"].values
    lows = df["low"].values
    n = len(df)

    for i in range(lookback, n - lookback):
        window_high = highs[i - lookback:i + lookback + 1]
        window_low = lows[i - lookback:i + lookback + 1]
        if highs[i] == window_high.max():
            df.iloc[i, df.columns.get_loc("swing_high")] = True
        if lows[i] == window_low.min():
            df.iloc[i, df.columns.get_loc("swing_low")] = True

    return df


def detect_structure(df: pd.DataFrame) -> pd.DataFrame:
    """
    بر اساس سوئینگ‌های شناسایی‌شده، روند فعلی و رویدادهای BOS/CHoCH را تعیین می‌کند.

    منطق:
      - trend: 'up' / 'down' / None  -> روند فعلی بر اساس آخرین سوئینگ‌ها
      - bos: True در کندلی که قیمت close، آخرین Swing High/Low هم‌جهت با روند را می‌شکند (ادامه‌ی روند)
      - choch: True وقتی روند برخلاف جهت قبلی خودش شکسته می‌شود (تغییر احتمالی روند)
    """
    df = df.copy()
    df["trend"] = None
    df["bos"] = False
    df["choch"] = False

    last_swing_high = None
    last_swing_low = None
    prev_swing_high = None
    prev_swing_low = None
    trend = None

    for i in range(len(df)):
        close = df["close"].iloc[i]

        # آپدیت کردن آخرین سوئینگ‌های ثبت‌شده تا این کندل
        if df["swing_high"].iloc[i]:
            prev_swing_high = last_swing_high
            last_swing_high = df["high"].iloc[i]
        if df["swing_low"].iloc[i]:
            prev_swing_low = last_swing_low
            last_swing_low = df["low"].iloc[i]

        # شکست سقف قبلی => فشار خرید (BOS صعودی یا CHoCH اگر روند نزولی بود)
        if last_swing_high is not None and close > last_swing_high:
            if trend == "down":
                df.iloc[i, df.columns.get_loc("choch")] = True
                trend = "up"
            elif trend != "up":
                df.iloc[i, df.columns.get_loc("bos")] = True
                trend = "up"
            else:
                df.iloc[i, df.columns.get_loc("bos")] = True
            last_swing_high = None  # این سطح شکسته شد، تا سوئینگ بعدی صبر کن

        # شکست کف قبلی => فشار فروش (BOS نزولی یا CHoCH اگر روند صعودی بود)
        elif last_swing_low is not None and close < last_swing_low:
            if trend == "up":
                df.iloc[i, df.columns.get_loc("choch")] = True
                trend = "down"
            elif trend != "down":
                df.iloc[i, df.columns.get_loc("bos")] = True
                trend = "down"
            else:
                df.iloc[i, df.columns.get_loc("bos")] = True
            last_swing_low = None

        df.iloc[i, df.columns.get_loc("trend")] = trend

    return df
