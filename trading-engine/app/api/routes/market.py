"""Market data API — real Yahoo / Twelve Data OHLC."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.market.provider import frame_to_rows, list_watchlist, load_candles
from app.market.symbol import normalize_symbol
from app.market.timeframe import TIMEFRAME_OPTIONS, normalize_timeframe

router = APIRouter(tags=["market"])


@router.get("/api/market/timeframes")
def list_timeframes() -> dict:
    return {"timeframes": TIMEFRAME_OPTIONS}


@router.get("/api/market/pairs")
def list_pairs() -> dict:
    pairs = list_watchlist()
    return {
        "source": "watchlist",
        "pairs": pairs,
        "details": [{"symbol": p} for p in pairs],
    }


@router.get("/api/market/{symbol}")
def get_market(
    symbol: str,
    timeframe: str | None = None,
    source: str | None = Query(None, description="yahoo|twelvedata|auto|sample — default: engine Settings"),
    count: int = Query(500, ge=20, le=5000),
) -> dict:
    try:
        bundle = load_candles(
            symbol,
            timeframe=timeframe or "1h",
            count=count,
            source=source,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    rows = frame_to_rows(bundle.candles)
    return {
        "symbol": normalize_symbol(bundle.symbol),
        "timeframe": normalize_timeframe(bundle.timeframe),
        "source": bundle.source,
        "message": bundle.message,
        "count": len(rows),
        "candles": rows,
    }
