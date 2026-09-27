"""Market data: Yahoo Finance (primary on Mac/Linux/VPS) + sample fallback."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.market.candle import normalize_ohlc
from app.market.symbol import to_yahoo_symbol
from app.market.timeframe import normalize_timeframe

# Yahoo interval limits — pick a period that actually returns enough bars
_TF_PERIOD = {
    "1m": "7d",
    "5m": "60d",
    "15m": "60d",
    "30m": "60d",
    "1h": "730d",
    "2h": "730d",  # fetched as 1h then resampled
    "4h": "730d",  # fetched as 1h then resampled
    "1d": "5y",
    "1w": "10y",
}

_TF_YAHOO_INTERVAL = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "2h": "1h",
    "4h": "1h",
    "1d": "1d",
    "1w": "1wk",
}

_TF_RESAMPLE = {
    "2h": "2h",
    "4h": "4h",
}


def generate_sample_data(n: int = 800, seed: int = 42, start_price: float = 1.1000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="h")

    trend = np.concatenate(
        [
            np.linspace(0, 0.02, n // 3),
            np.linspace(0.02, -0.01, n // 3),
            np.linspace(-0.01, 0.03, n - 2 * (n // 3)),
        ]
    )
    noise = rng.normal(0, 0.0015, n).cumsum() * 0.3
    close = start_price + trend + noise

    highs, lows, opens = [], [], []
    prev_close = close[0]
    for c in close:
        o = prev_close + rng.normal(0, 0.0005)
        h = max(o, c) + abs(rng.normal(0, 0.0008))
        l = min(o, c) - abs(rng.normal(0, 0.0008))
        opens.append(o)
        highs.append(h)
        lows.append(l)
        prev_close = c

    df = pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": close,
            "volume": rng.integers(100, 1000, n),
        },
        index=dates,
    )
    df.index.name = "time"
    return normalize_ohlc(df)


def _resample_ohlc(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    agg = df.resample(rule).agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    )
    return normalize_ohlc(agg.dropna())


def fetch_yahoo_data(
    symbol: str,
    timeframe: str = "1h",
    period: str | None = None,
) -> pd.DataFrame:
    """Download real OHLC from Yahoo Finance (works on Mac / Linux / VPS)."""
    import yfinance as yf

    tf = normalize_timeframe(timeframe)
    ticker = to_yahoo_symbol(symbol)
    interval = _TF_YAHOO_INTERVAL[tf]
    use_period = period or _TF_PERIOD[tf]

    df = yf.download(ticker, period=use_period, interval=interval, progress=False, auto_adjust=False)
    if df.empty:
        # one retry with alternate period for intraday
        alt = "60d" if tf in {"1h", "2h", "4h"} else "1y"
        df = yf.download(ticker, period=alt, interval=interval, progress=False, auto_adjust=False)
    if df.empty:
        raise ValueError(f"Yahoo returned no data for {ticker} ({tf})")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    out = normalize_ohlc(df)
    if not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index)
    if out.index.tz is None:
        out.index = out.index.tz_localize("UTC")
    else:
        out.index = out.index.tz_convert("UTC")
    out.index.name = "time"

    if tf in _TF_RESAMPLE:
        out = _resample_ohlc(out, _TF_RESAMPLE[tf])

    return out
