"""Optional Twelve Data forex API (free key) — real OHLC on any OS."""

from __future__ import annotations

import pandas as pd
import httpx

from app.market.candle import normalize_ohlc
from app.market.symbol import to_twelvedata_symbol
from app.market.timeframe import normalize_timeframe

_TF_MAP = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "1h",
    "2h": "2h",
    "4h": "4h",
    "1d": "1day",
    "1w": "1week",
}


def fetch_twelvedata(
    symbol: str,
    timeframe: str = "1h",
    *,
    api_key: str,
    count: int = 500,
) -> pd.DataFrame:
    if not api_key:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")

    tf = normalize_timeframe(timeframe)
    pair = to_twelvedata_symbol(symbol)
    interval = _TF_MAP[tf]
    outputsize = min(max(count, 50), 5000)

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": pair,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": api_key,
        "format": "JSON",
        "timezone": "UTC",
    }

    with httpx.Client(timeout=30.0) as client:
        res = client.get(url, params=params)
        res.raise_for_status()
        payload = res.json()

    if payload.get("status") == "error" or "values" not in payload:
        raise RuntimeError(payload.get("message") or f"Twelve Data error for {pair}")

    rows = payload["values"]
    if not rows:
        raise ValueError(f"Twelve Data empty series for {pair}")

    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["datetime"], utc=True)
    df = df.set_index("time").sort_index()
    for col in ("open", "high", "low", "close"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
    else:
        df["volume"] = 0.0
    return normalize_ohlc(df[["open", "high", "low", "close", "volume"]].dropna())
