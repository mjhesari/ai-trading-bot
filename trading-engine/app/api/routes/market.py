"""Market data API — real Yahoo / Twelve Data OHLC."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.market.provider import frame_to_rows, list_watchlist, load_candles
from app.market.quote import get_live_quote, patch_forming_candle
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


@router.get("/api/market/{symbol}/quote")
def get_quote(
    symbol: str,
    source: str | None = Query(None, description="yahoo|twelvedata|auto|sample"),
    timeframe: str = Query("1m", description="TF used to build the forming candle"),
) -> dict:
    try:
        return get_live_quote(symbol, source=source, timeframe=timeframe)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/api/market/{symbol}")
def get_market(
    symbol: str,
    timeframe: str | None = None,
    source: str | None = Query(None, description="yahoo|twelvedata|auto|sample — default: engine Settings"),
    count: int = Query(500, ge=20, le=5000),
    live: bool = Query(True, description="Patch the forming candle with a live quote"),
) -> dict:
    tf = timeframe or "1h"
    try:
        bundle = load_candles(
            symbol,
            timeframe=tf,
            count=count,
            source=source,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    rows = frame_to_rows(bundle.candles)
    live_price = None
    if live:
        try:
            quote_src = "sample" if (source or bundle.source) == "sample" else "yahoo"
            quote = get_live_quote(bundle.symbol, source=quote_src, timeframe=bundle.timeframe)
            live_price = float(quote["price"])
            rows = patch_forming_candle(
                rows,
                live_price,
                bundle.timeframe,
                forming=quote.get("forming"),
            )
        except Exception:  # noqa: BLE001
            pass

    return {
        "symbol": normalize_symbol(bundle.symbol),
        "timeframe": normalize_timeframe(bundle.timeframe),
        "source": bundle.source,
        "message": bundle.message,
        "count": len(rows),
        "candles": rows,
        "livePrice": live_price,
    }
