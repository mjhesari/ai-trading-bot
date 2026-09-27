"""Unified market data: Yahoo → Twelve Data → sample (Mac/Linux/VPS first)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from app.core.config import get_settings
from app.core.logging import get_logger
from app.market.data import fetch_yahoo_data, generate_sample_data
from app.market.symbol import normalize_symbol
from app.market.timeframe import normalize_timeframe
from app.market.twelvedata import fetch_twelvedata

logger = get_logger(__name__)

DataSource = Literal["yahoo", "twelvedata", "sample", "mt5"]

DEFAULT_PAIRS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "USDCHF",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
    "EURGBP",
    "EURJPY",
    "GBPJPY",
    "AUDJPY",
    "EURAUD",
    "EURCHF",
    "GBPCHF",
    "XAUUSD",
]


@dataclass
class CandleBundle:
    symbol: str
    timeframe: str
    source: DataSource
    candles: pd.DataFrame
    message: str | None = None


def preferred_sources(force: str | None = None) -> list[DataSource]:
    from app.core.runtime_config import get_runtime_config

    runtime = get_runtime_config()
    mode = (force or runtime.data_source or "yahoo").lower()
    has_twelve = bool(runtime.twelve_data_api_key)

    if mode == "yahoo":
        return ["yahoo"]
    if mode == "twelvedata":
        # Without a key, fall back to Yahoo instead of hard-failing the UI
        return ["twelvedata", "yahoo"] if has_twelve else ["yahoo"]
    if mode == "sample":
        return ["sample"]
    if mode == "mt5":
        return ["mt5", "yahoo"]
    # auto: real APIs first — prefer Twelve Data when keyed
    order: list[DataSource] = []
    if has_twelve:
        order.append("twelvedata")
    order.append("yahoo")
    order.append("sample")
    return order


def load_candles(
    symbol: str,
    timeframe: str = "1h",
    *,
    count: int = 500,
    source: str | None = None,
    period: str | None = None,
) -> CandleBundle:
    from app.core.runtime_config import get_runtime_config

    settings = get_settings()
    runtime = get_runtime_config()
    symbol = normalize_symbol(symbol)
    timeframe = normalize_timeframe(timeframe)
    period = period or settings.lookback_period
    errors: list[str] = []

    for src in preferred_sources(source):
        try:
            if src == "yahoo":
                df = fetch_yahoo_data(symbol, timeframe=timeframe, period=period if timeframe == "1d" else None)
                return CandleBundle(
                    symbol=symbol,
                    timeframe=timeframe,
                    source="yahoo",
                    candles=df.tail(count),
                    message="Yahoo Finance real FX/metal OHLC",
                )

            if src == "twelvedata":
                key = runtime.twelve_data_api_key
                if not key:
                    raise RuntimeError("TWELVE_DATA_API_KEY missing — set it in Settings")
                df = fetch_twelvedata(symbol, timeframe, api_key=key, count=count)
                return CandleBundle(
                    symbol=symbol,
                    timeframe=timeframe,
                    source="twelvedata",
                    candles=df.tail(count),
                    message="Twelve Data real OHLC",
                )

            if src == "mt5":
                from app.mt5.client import get_mt5_client
                from app.mt5.market_data import MT5MarketData

                client = get_mt5_client()
                if not client.connected:
                    client.connect()
                if not client.connected:
                    raise RuntimeError(client.last_error or "MT5 not connected")
                df = MT5MarketData(client).candles(symbol, timeframe, count=count)
                return CandleBundle(symbol=symbol, timeframe=timeframe, source="mt5", candles=df.tail(count))

            df = generate_sample_data(n=max(count, 200))
            return CandleBundle(
                symbol=symbol,
                timeframe=timeframe,
                source="sample",
                candles=df.tail(count),
                message="Synthetic sample OHLC (demo only)",
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{src}: {exc}")
            logger.warning("market source %s failed for %s: %s", src, symbol, exc)

    raise RuntimeError("All market sources failed: " + " | ".join(errors))


def list_watchlist() -> list[str]:
    settings = get_settings()
    raw = settings.forex_pairs.strip()
    if raw:
        return [normalize_symbol(p) for p in raw.split(",") if p.strip()]
    return list(DEFAULT_PAIRS)


def frame_to_rows(df: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    for idx, row in df.iterrows():
        ts = idx
        if hasattr(ts, "isoformat"):
            iso = ts.isoformat()
        elif hasattr(ts, "to_pydatetime"):
            iso = ts.to_pydatetime().isoformat()
        else:
            iso = str(ts)
        rows.append(
            {
                "time": iso,
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": float(row.volume),
            }
        )
    return rows
