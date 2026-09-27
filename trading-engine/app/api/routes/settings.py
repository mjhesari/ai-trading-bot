"""Runtime settings API — change data source / Twelve Data key from the UI."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.runtime_config import get_runtime_config, public_settings_dict, update_runtime_config
from app.market.provider import load_candles

router = APIRouter(tags=["settings"])


class SettingsUpdate(BaseModel):
    dataSource: str | None = Field(default=None, description="yahoo|twelvedata|auto|sample")
    twelveDataApiKey: str | None = Field(default=None, description="Leave empty to keep current key")
    clearTwelveDataApiKey: bool = False


@router.get("/api/settings")
def get_settings_api() -> dict:
    return public_settings_dict()


@router.put("/api/settings")
def put_settings_api(body: SettingsUpdate) -> dict:
    try:
        update_runtime_config(
            data_source=body.dataSource,
            twelve_data_api_key=body.twelveDataApiKey,
            clear_twelve_key=body.clearTwelveDataApiKey,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return public_settings_dict()


@router.post("/api/settings/test-source")
def test_source(symbol: str = "EURUSD", timeframe: str = "1h") -> dict:
    """Fetch a few bars with the current runtime source to verify the key works."""
    cfg = get_runtime_config()
    try:
        bundle = load_candles(symbol, timeframe, count=30, source=cfg.data_source)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "ok": True,
        "source": bundle.source,
        "message": bundle.message,
        "bars": len(bundle.candles),
        "symbol": bundle.symbol,
        "timeframe": bundle.timeframe,
        "lastClose": float(bundle.candles["close"].iloc[-1]) if len(bundle.candles) else None,
    }
