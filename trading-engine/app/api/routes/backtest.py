"""Backtest API — real Yahoo/Twelve Data history by default."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_backtest_runner
from app.backtest.runner import BacktestRunner

router = APIRouter(tags=["backtest"])


class BacktestRequest(BaseModel):
    symbol: str = "EURUSD"
    timeframe: str = "1h"
    useSample: bool = False
    source: str | None = Field(default=None, description="yahoo|twelvedata|auto|sample — default: engine Settings")
    start: str | None = None
    end: str | None = None
    sampleN: int = Field(default=1000, ge=100, le=5000)


@router.post("/api/backtest")
def run_backtest(
    body: BacktestRequest,
    runner: BacktestRunner = Depends(get_backtest_runner),
) -> dict:
    source = body.source
    if body.useSample:
        source = "sample"
    try:
        return runner.run(
            symbol=body.symbol,
            timeframe=body.timeframe,
            use_sample=body.useSample,
            source=source,
            start=body.start,
            end=body.end,
            sample_n=body.sampleN,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/api/backtest/{backtest_id}")
def get_backtest(
    backtest_id: str,
    runner: BacktestRunner = Depends(get_backtest_runner),
) -> dict:
    report = runner.get(backtest_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return report
