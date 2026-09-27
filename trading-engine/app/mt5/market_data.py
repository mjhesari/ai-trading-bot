"""Fetch OHLC candles from a live MetaTrader5 terminal."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from app.market.candle import normalize_ohlc
from app.market.timeframe import normalize_timeframe
from app.mt5.client import MT5Client, get_mt5_client
from app.mt5.timeframes import resolve_mt5_timeframe


class MT5MarketData:
    def __init__(self, client: MT5Client | None = None) -> None:
        self.client = client or get_mt5_client()

    def candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        count: int = 500,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        if not self.client.connected:
            raise RuntimeError(self.client.last_error or "MT5 is not connected")

        mt5 = self.client.api()
        symbol = self.client.ensure_symbol(symbol)
        tf = normalize_timeframe(timeframe)
        mt5_tf = resolve_mt5_timeframe(mt5, tf)

        if start is not None:
            end = end or datetime.now(timezone.utc)
            rates = mt5.copy_rates_range(symbol, mt5_tf, start, end)
        else:
            rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, int(count))

        if rates is None or len(rates) == 0:
            err = mt5.last_error()
            raise RuntimeError(f"MT5 returned no rates for {symbol} {tf}: {err}")

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.set_index("time")
        df = df.rename(columns={"tick_volume": "volume"})
        if "volume" not in df.columns:
            df["volume"] = df.get("real_volume", 0)
        return normalize_ohlc(df[["open", "high", "low", "close", "volume"]])

    def symbol_tick(self, symbol: str) -> dict[str, Any]:
        mt5 = self.client.api()
        symbol = self.client.ensure_symbol(symbol)
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"No tick for {symbol}: {mt5.last_error()}")
        return {
            "symbol": symbol,
            "bid": tick.bid,
            "ask": tick.ask,
            "last": tick.last,
            "volume": tick.volume,
            "time": datetime.fromtimestamp(tick.time, tz=timezone.utc).isoformat(),
        }

    def list_forex_symbols(self, limit: int = 80) -> list[dict[str, Any]]:
        mt5 = self.client.api()
        symbols = mt5.symbols_get()
        if symbols is None:
            raise RuntimeError(f"symbols_get failed: {mt5.last_error()}")

        out: list[dict[str, Any]] = []
        for s in symbols:
            path = (s.path or "").lower()
            name = s.name.upper()
            # Prefer forex majors/minors; skip if path clearly non-fx when available
            is_fx_path = "forex" in path or "fx" in path or "currency" in path
            looks_fx = len(name.replace(".", "").replace("m", "").replace("pro", "")[:6]) == 6
            if not (is_fx_path or looks_fx):
                continue
            out.append(
                {
                    "symbol": s.name,
                    "description": s.description,
                    "digits": s.digits,
                    "spread": s.spread,
                    "tradeMode": s.trade_mode,
                    "visible": s.visible,
                    "path": s.path,
                }
            )
            if len(out) >= limit:
                break
        return out
