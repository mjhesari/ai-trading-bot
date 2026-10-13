"""Live quote + forming-candle helpers.

Yahoo `fast_info` is often sticky for FX. We build the in-progress bar from
1-minute OHLC so high/low/close actually move as new minutes print.
"""

from __future__ import annotations

import time
from typing import Any

import pandas as pd

from app.core.logging import get_logger
from app.market.symbol import normalize_symbol, to_yahoo_symbol, to_twelvedata_symbol
from app.market.timeframe import normalize_timeframe

logger = get_logger(__name__)

_QUOTE_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_QUOTE_TTL_SEC = 0.75
_M1_CACHE: dict[str, tuple[float, pd.DataFrame]] = {}
_M1_TTL_SEC = 0.75

TF_MS = {
    "1m": 60_000,
    "5m": 300_000,
    "15m": 900_000,
    "30m": 1_800_000,
    "1h": 3_600_000,
    "2h": 7_200_000,
    "4h": 14_400_000,
    "1d": 86_400_000,
    "1w": 604_800_000,
}


def bar_open_ms(now_ms: int, timeframe: str) -> int:
    tf = normalize_timeframe(timeframe)
    step = TF_MS[tf]
    if tf == "1w":
        from datetime import datetime, timedelta, timezone

        dt = datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc)
        monday = (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        return int(monday.timestamp() * 1000)
    if tf == "1d":
        return int(now_ms // 86_400_000) * 86_400_000
    return int(now_ms // step) * step


def _normalize_yahoo_frame(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    rename = {c: c.lower() for c in df.columns}
    out = df.rename(columns=rename)
    needed = ["open", "high", "low", "close"]
    for col in needed:
        if col not in out.columns:
            raise RuntimeError(f"Yahoo frame missing {col}")
    if "volume" not in out.columns:
        out["volume"] = 0.0
    if not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index)
    if out.index.tz is None:
        out.index = out.index.tz_localize("UTC")
    else:
        out.index = out.index.tz_convert("UTC")
    return out[["open", "high", "low", "close", "volume"]].dropna()


def fetch_yahoo_m1(symbol: str) -> pd.DataFrame:
    """Recent 1-minute bars — used to animate forming candles on any TF."""
    import yfinance as yf

    ticker = to_yahoo_symbol(symbol)
    cache_key = ticker
    now = time.monotonic()
    cached = _M1_CACHE.get(cache_key)
    if cached and now - cached[0] < _M1_TTL_SEC:
        return cached[1]

    yt = yf.Ticker(ticker)
    hist = yt.history(period="5d", interval="1m", auto_adjust=False)
    if hist is None or hist.empty:
        # fallback download
        hist = yf.download(ticker, period="5d", interval="1m", progress=False, auto_adjust=False)
    if hist is None or hist.empty:
        raise RuntimeError(f"No 1m Yahoo data for {ticker}")

    out = _normalize_yahoo_frame(hist)
    _M1_CACHE[cache_key] = (now, out)
    return out


def aggregate_forming_from_m1(m1: pd.DataFrame, timeframe: str, now_ms: int | None = None) -> dict[str, Any]:
    now_ms = now_ms or int(time.time() * 1000)
    open_ms = bar_open_ms(now_ms, timeframe)
    open_ts = pd.Timestamp(open_ms, unit="ms", tz="UTC")
    window = m1[m1.index >= open_ts]
    last_m1 = m1.iloc[-1]
    last_price = float(last_m1["close"])

    if window.empty:
        # Yahoo often lags the current minute — seed the forming bar from last known tick.
        return {
            "time": open_ts.isoformat(),
            "open": last_price,
            "high": last_price,
            "low": last_price,
            "close": last_price,
            "volume": 0.0,
            "price": last_price,
            "barOpenMs": open_ms,
            "m1Count": 0,
        }

    price = float(window["close"].iloc[-1])
    return {
        "time": open_ts.isoformat(),
        "open": float(window["open"].iloc[0]),
        "high": float(max(float(window["high"].max()), price)),
        "low": float(min(float(window["low"].min()), price)),
        "close": price,
        "volume": float(window["volume"].sum()),
        "price": price,
        "barOpenMs": open_ms,
        "m1Count": int(len(window)),
    }


def fetch_yahoo_quote(symbol: str, timeframe: str = "1m") -> dict[str, Any]:
    tf = normalize_timeframe(timeframe)
    m1 = fetch_yahoo_m1(symbol)
    forming = aggregate_forming_from_m1(m1, tf)
    return {
        "symbol": normalize_symbol(symbol),
        "price": forming["price"],
        "asOf": m1.index[-1].isoformat(),
        "source": "yahoo",
        "forming": {
            "time": forming["time"],
            "open": forming["open"],
            "high": forming["high"],
            "low": forming["low"],
            "close": forming["close"],
            "volume": forming["volume"],
        },
        "barOpenMs": forming["barOpenMs"],
        "m1Count": forming["m1Count"],
        "timeframe": tf,
    }


def fetch_twelvedata_quote(symbol: str, api_key: str, timeframe: str = "1m") -> dict[str, Any]:
    import httpx

    pair = to_twelvedata_symbol(symbol)
    with httpx.Client(timeout=8.0) as client:
        res = client.get(
            "https://api.twelvedata.com/price",
            params={"symbol": pair, "apikey": api_key},
        )
        res.raise_for_status()
        data = res.json()
    if "price" not in data:
        raise RuntimeError(data.get("message") or f"Twelve Data quote failed for {pair}")
    price = float(data["price"])
    now_ms = int(time.time() * 1000)
    open_ms = bar_open_ms(now_ms, timeframe)
    return {
        "symbol": normalize_symbol(symbol),
        "price": price,
        "asOf": data.get("datetime"),
        "source": "twelvedata",
        "forming": {
            "time": pd.Timestamp(open_ms, unit="ms", tz="UTC").isoformat(),
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": 0.0,
        },
        "barOpenMs": open_ms,
        "timeframe": normalize_timeframe(timeframe),
    }


def _sample_quote(symbol: str, timeframe: str) -> dict[str, Any]:
    """Deterministic walk so demo charts visibly tick every poll."""
    now = time.time()
    # smooth walk + higher-frequency wiggle
    base = 1.1000 + (now % 300) * 0.00002
    wiggle = ((now * 13.0) % 1.0 - 0.5) * 0.00035
    price = round(base + wiggle, 5)
    now_ms = int(now * 1000)
    open_ms = bar_open_ms(now_ms, timeframe)
    # fake path since bar open so H/L expand
    seed = int(open_ms // 1000)
    path = [price]
    for i in range(8):
        path.append(round(price + ((seed + i * 17) % 11 - 5) * 0.00004, 5))
    return {
        "symbol": symbol,
        "price": price,
        "asOf": pd.Timestamp.utcnow().isoformat(),
        "source": "sample",
        "forming": {
            "time": pd.Timestamp(open_ms, unit="ms", tz="UTC").isoformat(),
            "open": path[0],
            "high": max(path),
            "low": min(path),
            "close": price,
            "volume": float(100 + (seed % 50)),
        },
        "barOpenMs": open_ms,
        "timeframe": normalize_timeframe(timeframe),
    }


def get_live_quote(symbol: str, source: str | None = None, timeframe: str = "1m") -> dict[str, Any]:
    from app.core.runtime_config import get_runtime_config

    symbol = normalize_symbol(symbol)
    tf = normalize_timeframe(timeframe) if timeframe else "1m"
    runtime = get_runtime_config()
    mode = (source or runtime.data_source or "yahoo").lower()
    cache_key = f"{symbol}:{mode}:{tf}"
    now = time.monotonic()
    cached = _QUOTE_CACHE.get(cache_key)
    if cached and now - cached[0] < _QUOTE_TTL_SEC:
        return cached[1]

    errors: list[str] = []
    if mode == "sample":
        order = ["sample"]
    else:
        # Yahoo 1m aggregation is the only free path that actually moves intra-bar.
        order = ["yahoo"]
        if runtime.twelve_data_api_key and mode in {"twelvedata", "auto"}:
            order.append("twelvedata")

    quote: dict[str, Any] | None = None
    for src in order:
        try:
            if src == "yahoo":
                quote = fetch_yahoo_quote(symbol, timeframe=tf)
            elif src == "twelvedata":
                key = runtime.twelve_data_api_key
                if not key:
                    raise RuntimeError("TWELVE_DATA_API_KEY missing")
                quote = fetch_twelvedata_quote(symbol, key, timeframe=tf)
            elif src == "sample":
                quote = _sample_quote(symbol, tf)
            break
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{src}: {exc}")
            logger.warning("live quote %s failed for %s: %s", src, symbol, exc)

    if quote is None:
        raise RuntimeError("Live quote failed: " + " | ".join(errors))

    quote["ts"] = int(time.time() * 1000)
    _QUOTE_CACHE[cache_key] = (now, quote)
    return quote


def patch_forming_candle(
    rows: list[dict],
    price: float,
    timeframe: str,
    now_ms: int | None = None,
    forming: dict[str, Any] | None = None,
) -> list[dict]:
    """Replace/update the in-progress bar using live price or a full forming OHLC."""
    if not rows:
        return rows
    now_ms = now_ms or int(time.time() * 1000)
    open_ms = bar_open_ms(now_ms, timeframe)
    open_iso = pd.Timestamp(open_ms, unit="ms", tz="UTC").isoformat()
    out = list(rows)
    last = dict(out[-1])
    last_ms = int(pd.Timestamp(last["time"]).timestamp() * 1000)

    if forming and all(k in forming for k in ("open", "high", "low", "close")):
        bar = {
            "time": forming.get("time") or open_iso,
            "open": float(forming["open"]),
            "high": float(forming["high"]),
            "low": float(forming["low"]),
            "close": float(forming["close"]),
            "volume": float(forming.get("volume") or 0.0),
        }
        if last_ms < open_ms:
            out.append(bar)
        else:
            # Keep historical open if provider already opened the bar; expand H/L from live.
            bar["open"] = float(last["open"])
            bar["high"] = max(float(last["high"]), bar["high"], bar["close"])
            bar["low"] = min(float(last["low"]), bar["low"], bar["close"])
            out[-1] = bar
        return out

    if price != price:  # NaN
        return rows

    if last_ms < open_ms:
        out.append(
            {
                "time": open_iso,
                "open": float(price),
                "high": float(price),
                "low": float(price),
                "close": float(price),
                "volume": 0.0,
            }
        )
        return out

    last["close"] = float(price)
    last["high"] = max(float(last["high"]), float(price))
    last["low"] = min(float(last["low"]), float(price))
    out[-1] = last
    return out
