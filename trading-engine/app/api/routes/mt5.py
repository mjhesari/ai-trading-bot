"""MT5 connection & trading endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.market.provider import DEFAULT_PAIRS, list_watchlist
from app.mt5.account import MT5Account
from app.mt5.client import get_mt5_client
from app.mt5.market_data import MT5MarketData
from app.mt5.orders import MT5Orders
from app.mt5.positions import MT5Positions

router = APIRouter(tags=["mt5"])


class ConnectBody(BaseModel):
    login: int | None = None
    password: str | None = None
    server: str | None = None
    path: str | None = None


class OrderBody(BaseModel):
    symbol: str = "EURUSD"
    direction: str = "BUY"
    volume: float = Field(gt=0, default=0.01)
    sl: float | None = None
    tp: float | None = None
    comment: str = "aether-smc"


@router.get("/api/mt5/status")
def mt5_status() -> dict:
    return get_mt5_client().status()


@router.post("/api/mt5/connect")
def mt5_connect(body: ConnectBody | None = None) -> dict:
    client = get_mt5_client()
    if body:
        if body.login is not None:
            client.settings.mt5_login = body.login
        if body.password is not None:
            client.settings.mt5_password = body.password
        if body.server is not None:
            client.settings.mt5_server = body.server
        if body.path is not None:
            client.settings.mt5_path = body.path
    ok = client.connect()
    if not ok:
        raise HTTPException(status_code=503, detail=client.last_error or "MT5 connect failed")
    return client.status()


@router.post("/api/mt5/disconnect")
def mt5_disconnect() -> dict:
    client = get_mt5_client()
    client.disconnect()
    return {"connected": False, "message": "disconnected"}


@router.get("/api/mt5/account")
def mt5_account() -> dict:
    return MT5Account().info()


@router.get("/api/mt5/positions")
def mt5_positions(symbol: str | None = None) -> dict:
    client = get_mt5_client()
    if not client.connected:
        return {"connected": False, "positions": [], "message": client.last_error}
    return {"connected": True, "positions": MT5Positions(client).list(symbol)}


@router.get("/api/mt5/symbols")
def mt5_symbols(limit: int = 80) -> dict:
    client = get_mt5_client()
    if client.connected:
        try:
            symbols = MT5MarketData(client).list_forex_symbols(limit=limit)
            return {"source": "mt5", "count": len(symbols), "symbols": symbols}
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Fallback watchlist for Mac / offline
    pairs = list_watchlist() or DEFAULT_PAIRS
    return {
        "source": "watchlist",
        "count": len(pairs),
        "symbols": [{"symbol": p, "description": p, "digits": 5, "visible": True} for p in pairs],
        "message": client.last_error or "MT5 offline — returning default forex watchlist",
    }


@router.post("/api/mt5/order")
def mt5_order(body: OrderBody) -> dict:
    """Place a market order via the same MT5 connection (demo recommended)."""
    client = get_mt5_client()
    if not client.connected:
        raise HTTPException(status_code=503, detail=client.last_error or "MT5 not connected")
    try:
        result = MT5Orders(client).place(
            symbol=body.symbol,
            direction=body.direction.upper(),
            volume=body.volume,
            sl=body.sl,
            tp=body.tp,
            comment=body.comment,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)
    return result
