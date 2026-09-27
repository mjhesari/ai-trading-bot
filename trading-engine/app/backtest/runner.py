"""Backtest runner — load real market data, run strategy, return report."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.backtest.engine import BacktestEngine
from app.backtest.reports import build_report
from app.core.config import get_settings
from app.market.provider import load_candles
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
        use_sample: bool = False,
        source: str | None = None,
        start: str | None = None,
        end: str | None = None,
        sample_n: int = 1000,
    ) -> dict[str, Any]:
        settings = get_settings()
        symbol = normalize_symbol(symbol)
        timeframe = normalize_timeframe(timeframe)

        resolved = "sample" if use_sample else source

        bundle = load_candles(symbol, timeframe, count=sample_n, source=resolved)
        candles = bundle.candles
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
        report["source"] = bundle.source
        report["message"] = bundle.message
        report["bars"] = len(candles)
        self._store[report["id"]] = report
        return report

    def get(self, backtest_id: str) -> dict[str, Any] | None:
        return self._store.get(backtest_id)
