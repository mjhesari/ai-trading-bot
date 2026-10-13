"""Backtest runner — load real market data, run a named strategy, return report."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.backtest.engine import BacktestEngine
from app.backtest.reports import build_report
from app.core.config import get_settings
from app.market.provider import load_candles
from app.market.symbol import normalize_symbol
from app.market.timeframe import normalize_timeframe
from app.strategy.registry import STRATEGIES, resolve_strategy


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
        strategy: str | None = None,
        initial_balance: float | None = None,
        risk_pct: float | None = None,
        spread_pips: float = 0.8,
        commission_per_lot: float = 7.0,
        min_lot: float | None = None,
        max_lot: float | None = None,
        partial_close_pct: float = 0.5,
    ) -> dict[str, Any]:
        settings = get_settings()
        symbol = normalize_symbol(symbol)
        timeframe = normalize_timeframe(timeframe)
        strategy_id, strat = resolve_strategy(strategy, timeframe=timeframe)

        resolved = "sample" if use_sample else source

        bundle = load_candles(symbol, timeframe, count=sample_n, source=resolved)
        candles = bundle.candles
        if start:
            candles = candles[candles.index >= start]
        if end:
            candles = candles[candles.index <= end]

        analyzed = strat.analyze(candles)
        engine = BacktestEngine(
            symbol=symbol,
            initial_balance=initial_balance if initial_balance is not None else settings.initial_balance,
            risk_pct=risk_pct if risk_pct is not None else settings.risk_per_trade_pct,
            spread_pips=spread_pips,
            commission_per_lot=commission_per_lot,
            min_lot=min_lot,
            max_lot=max_lot,
            partial_close_pct=partial_close_pct,
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
        report["strategy"] = strategy_id
        report["strategyLabel"] = str(STRATEGIES[strategy_id]["label"])
        self._store[report["id"]] = report
        return report

    def get(self, backtest_id: str) -> dict[str, Any] | None:
        return self._store.get(backtest_id)
