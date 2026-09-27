"""Market data API."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.config import get_settings
from app.market.data import fetch_yahoo_data, generate_sample_data
from app.market.symbol import normalize_symbol
from app.market.timeframe import normalize_timeframe

router = APIRouter(tags=["market"])


@router.get("/api/market/{symbol}")
def get_market(
    symbol: str,
    timeframe: str | None = None,
    use_sample: bool = Query(True),
    limit: int = Query(100, ge=1, le=2000),
) -> dict:
    settings = get_settings()
    symbol = normalize_symbol(symbol)
    timeframe = normalize_timeframe(timeframe or settings.default_timeframe)

    if use_sample:
        candles = generate_sample_data(n=max(limit, 200))
    else:
        candles = fetch_yahoo_data(symbol, timeframe=timeframe, period=settings.lookback_period)

    tail = candles.tail(limit)
    rows = [
        {
            "time": str(idx),
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
            "volume": float(row.volume),
        }
        for idx, row in tail.iterrows()
    ]
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "count": len(rows),
        "candles": rows,
    }
