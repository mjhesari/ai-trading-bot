"""Backtest API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_backtest_runner
from app.backtest.runner import BacktestRunner

router = APIRouter(tags=["backtest"])


class BacktestRequest(BaseModel):
    symbol: str = "EURUSD"
    timeframe: str = "1h"
    useSample: bool = True
    start: str | None = None
    end: str | None = None
    sampleN: int = Field(default=800, ge=100, le=5000)


@router.post("/api/backtest")
def run_backtest(
    body: BacktestRequest,
    runner: BacktestRunner = Depends(get_backtest_runner),
) -> dict:
    return runner.run(
        symbol=body.symbol,
        timeframe=body.timeframe,
        use_sample=body.useSample,
        start=body.start,
        end=body.end,
        sample_n=body.sampleN,
    )


@router.get("/api/backtest/{backtest_id}")
def get_backtest(
    backtest_id: str,
    runner: BacktestRunner = Depends(get_backtest_runner),
) -> dict:
    report = runner.get(backtest_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return report
