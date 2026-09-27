"""Market data loading: sample generator and Yahoo Finance."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.market.candle import normalize_ohlc
from app.market.symbol import to_yahoo_symbol
from app.market.timeframe import normalize_timeframe


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


def fetch_yahoo_data(symbol: str, timeframe: str = "1h", period: str = "60d") -> pd.DataFrame:
    import yfinance as yf

    ticker = to_yahoo_symbol(symbol)
    tf = normalize_timeframe(timeframe)
    df = yf.download(ticker, period=period, interval=tf, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker} ({tf})")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return normalize_ohlc(df)
