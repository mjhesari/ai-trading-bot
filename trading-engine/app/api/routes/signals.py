"""Signals API — real market OHLC → SMC pipeline."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.market.provider import load_candles
from app.market.symbol import normalize_symbol
from app.market.timeframe import normalize_timeframe
from app.signals.generator import SignalGenerator
from app.strategy.strategies.smc_v1 import SMCv1Strategy

router = APIRouter(tags=["signals"])


@router.get("/api/signals")
def list_signals(
    symbol: str | None = None,
    timeframe: str | None = None,
    source: str | None = Query(None, description="yahoo|twelvedata|auto|sample — default: engine Settings"),
    limit: int = Query(50, ge=1, le=500),
    count: int = Query(800, ge=100, le=5000),
) -> dict:
    settings = get_settings()
    symbol = normalize_symbol(symbol or settings.default_symbol)
    timeframe = normalize_timeframe(timeframe or settings.default_timeframe)

    try:
        bundle = load_candles(symbol, timeframe, count=count, source=source)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    analyzed = SMCv1Strategy().analyze(bundle.candles)
    signals = SignalGenerator(symbol=symbol, timeframe=timeframe).from_frame(analyzed)
    payload = [s.to_api_dict() for s in signals[-limit:]]
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "source": bundle.source,
        "message": bundle.message,
        "bars": len(bundle.candles),
        "count": len(payload),
        "signals": payload,
    }
