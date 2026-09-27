"""Signals API."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.config import get_settings
from app.market.data import fetch_yahoo_data, generate_sample_data
from app.market.symbol import normalize_symbol
from app.market.timeframe import normalize_timeframe
from app.signals.generator import SignalGenerator
from app.strategy.strategies.smc_v1 import SMCv1Strategy

router = APIRouter(tags=["signals"])


@router.get("/api/signals")
def list_signals(
    symbol: str | None = None,
    timeframe: str | None = None,
    use_sample: bool = Query(True),
    limit: int = Query(50, ge=1, le=500),
) -> dict:
    settings = get_settings()
    symbol = normalize_symbol(symbol or settings.default_symbol)
    timeframe = normalize_timeframe(timeframe or settings.default_timeframe)

    if use_sample:
        candles = generate_sample_data(n=800)
    else:
        candles = fetch_yahoo_data(symbol, timeframe=timeframe, period=settings.lookback_period)

    analyzed = SMCv1Strategy().analyze(candles)
    signals = SignalGenerator(symbol=symbol, timeframe=timeframe).from_frame(analyzed)
    payload = [s.to_api_dict() for s in signals[-limit:]]
    return {"symbol": symbol, "timeframe": timeframe, "count": len(payload), "signals": payload}
