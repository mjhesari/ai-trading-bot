"""
موتور سیگنال: ترکیب کانتکست Smart Money با تریگر Price Action

منطق سیگنال خرید (BUY):
  1) روند/ساختار بازار به تازگی BOS یا CHoCH صعودی داده (trend == 'up')
  2) قیمت در ناحیه Discount قرار داره (zone == 'discount') یا روی Order Block/FVG بولیش نشسته
  3) یک الگوی Price Action تاییدکننده (Bullish Engulfing یا Bullish Pin Bar) شکل گرفته

منطق سیگنال فروش (SELL): برعکس حالت بالا.

خروجی هر سیگنال شامل نقطه ورود، حد ضرر (زیر/بالای Order Block) و حد سود
بر اساس نسبت ریسک به ریوارد تنظیم‌شده در config است.
"""

import pandas as pd


def generate_signals(df: pd.DataFrame, rr_ratio: float = 2.0, sl_buffer_pct: float = 0.0005) -> pd.DataFrame:
    df = df.copy()
    df["signal"] = None       # 'BUY' / 'SELL'
    df["entry"] = None
    df["stop_loss"] = None
    df["take_profit"] = None
    df["reason"] = None

    # آخرین Order Block فعال هر نوع را دنبال می‌کنیم (ساده‌سازی: نزدیک‌ترین OB قبل از کندل فعلی)
    last_bull_ob_low = None
    last_bear_ob_high = None

    for i in range(len(df)):
        if df["bullish_ob"].iloc[i]:
            last_bull_ob_low = df["low"].iloc[i]
        if df["bearish_ob"].iloc[i]:
            last_bear_ob_high = df["high"].iloc[i]

        trend = df["trend"].iloc[i]
        zone = df["zone"].iloc[i]
        pa_bull = df["bullish_engulfing"].iloc[i] or df["bullish_pinbar"].iloc[i]
        pa_bear = df["bearish_engulfing"].iloc[i] or df["bearish_pinbar"].iloc[i]

        # --- سیگنال خرید ---
        if trend == "up" and zone == "discount" and pa_bull and last_bull_ob_low is not None:
            entry = df["close"].iloc[i]
            sl = last_bull_ob_low * (1 - sl_buffer_pct)
            risk = entry - sl
            if risk > 0:
                tp = entry + risk * rr_ratio
                df.iloc[i, df.columns.get_loc("signal")] = "BUY"
                df.iloc[i, df.columns.get_loc("entry")] = entry
                df.iloc[i, df.columns.get_loc("stop_loss")] = sl
                df.iloc[i, df.columns.get_loc("take_profit")] = tp
                df.iloc[i, df.columns.get_loc("reason")] = "BOS صعودی + ناحیه Discount + تایید Price Action"

        # --- سیگنال فروش ---
        elif trend == "down" and zone == "premium" and pa_bear and last_bear_ob_high is not None:
            entry = df["close"].iloc[i]
            sl = last_bear_ob_high * (1 + sl_buffer_pct)
            risk = sl - entry
            if risk > 0:
                tp = entry - risk * rr_ratio
                df.iloc[i, df.columns.get_loc("signal")] = "SELL"
                df.iloc[i, df.columns.get_loc("entry")] = entry
                df.iloc[i, df.columns.get_loc("stop_loss")] = sl
                df.iloc[i, df.columns.get_loc("take_profit")] = tp
                df.iloc[i, df.columns.get_loc("reason")] = "BOS نزولی + ناحیه Premium + تایید Price Action"

    return df


def get_active_signals(df: pd.DataFrame) -> pd.DataFrame:
    """فقط ردیف‌هایی که سیگنال دارن رو برمی‌گردونه، برای نمایش/ارسال."""
    cols = ["signal", "entry", "stop_loss", "take_profit", "reason"]
    return df[df["signal"].notna()][cols]
