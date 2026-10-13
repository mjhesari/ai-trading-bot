"""Backtest API — real Yahoo/Twelve Data history by default."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_backtest_runner
from app.backtest.runner import BacktestRunner
from app.strategy.registry import list_strategies

router = APIRouter(tags=["backtest"])


class BacktestRequest(BaseModel):
    symbol: str = "EURUSD"
    timeframe: str = "1h"
    strategy: str = Field(default="smc", description="smc | ict")
    useSample: bool = False
    source: str | None = Field(default=None, description="yahoo|twelvedata|auto|sample — default: engine Settings")
    start: str | None = None
    end: str | None = None
    sampleN: int = Field(default=1000, ge=100, le=5000)
    initialBalance: float = Field(default=10_000.0, gt=0, le=10_000_000)
    riskPerTradePct: float = Field(default=1.0, gt=0, le=10, description="Percent of balance risked per trade")
    spreadPips: float = Field(default=0.8, ge=0, le=50)
    commissionPerLot: float = Field(default=7.0, ge=0, le=100)
    minLot: float = Field(default=0.01, gt=0, le=100)
    maxLot: float = Field(default=10.0, gt=0, le=100)
    partialClosePct: float = Field(default=0.5, ge=0, le=1, description="Close this fraction at TP1; remainder runs to TP2 at BE")


@router.get("/api/strategies")
def get_strategies() -> dict:
    return {"strategies": list_strategies(), "default": "smc"}


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
            strategy=body.strategy,
            initial_balance=body.initialBalance,
            risk_pct=body.riskPerTradePct / 100.0,
            spread_pips=body.spreadPips,
            commission_per_lot=body.commissionPerLot,
            min_lot=body.minLot,
            max_lot=body.maxLot,
            partial_close_pct=body.partialClosePct,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
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
