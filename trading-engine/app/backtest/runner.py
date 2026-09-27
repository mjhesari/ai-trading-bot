"""Backtest runner — load data, run strategy, return report."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.backtest.engine import BacktestEngine
from app.backtest.reports import build_report
from app.core.config import get_settings
from app.market.data import fetch_yahoo_data, generate_sample_data
from app.market.symbol import normalize_symbol
from app.market.timeframe import normalize_timeframe
from app.strategy.strategies.smc_v1 import SMCv1Strategy


class BacktestRunner:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def run(
        self,
        *,
        symbol: str = "EURUSD",
        timeframe: str = "1h",
        use_sample: bool = True,
        start: str | None = None,
        end: str | None = None,
        sample_n: int = 800,
    ) -> dict[str, Any]:
        settings = get_settings()
        symbol = normalize_symbol(symbol)
        timeframe = normalize_timeframe(timeframe)

        if use_sample:
            candles = generate_sample_data(n=sample_n)
        else:
            candles = fetch_yahoo_data(symbol, timeframe=timeframe, period=settings.lookback_period)
            if start:
                candles = candles[candles.index >= start]
            if end:
                candles = candles[candles.index <= end]

        strategy = SMCv1Strategy()
        analyzed = strategy.analyze(candles)
        engine = BacktestEngine(
            initial_balance=settings.initial_balance,
            risk_pct=settings.risk_per_trade_pct,
        )
        result = engine.run(analyzed)
        report = build_report(
            backtest_id=str(uuid4()),
            symbol=symbol,
            timeframe=timeframe,
            metrics=result["metrics"],
            trades=result["trades"],
        )
        self._store[report["id"]] = report
        return report

    def get(self, backtest_id: str) -> dict[str, Any] | None:
        return self._store.get(backtest_id)
