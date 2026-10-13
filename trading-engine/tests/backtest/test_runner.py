"""Backtest smoke test — sample + real yahoo path."""

import pytest

from app.backtest.runner import BacktestRunner


def test_backtest_runner_sample():
    report = BacktestRunner().run(source="sample", sample_n=400, strategy="smc")
    assert "id" in report
    assert "metrics" in report
    assert "totalTrades" in report["metrics"]
    assert report.get("source") == "sample"
    assert report.get("strategy") == "smc"


def test_backtest_runner_ict_sample_has_lots():
    report = BacktestRunner().run(
        source="sample",
        sample_n=800,
        strategy="ict",
        initial_balance=10_000,
        risk_pct=0.01,
        spread_pips=0.8,
        commission_per_lot=7.0,
        min_lot=0.01,
        max_lot=5.0,
    )
    assert report.get("strategy") == "ict"
    assert "avgLots" in report["metrics"]
    for trade in report["trades"]:
        assert trade["lots"] > 0
        assert "tp1" in trade and "tp2" in trade
        assert "sl" in trade
        assert "commission" in trade


def test_backtest_runner_yahoo():
    try:
        report = BacktestRunner().run(symbol="EURUSD", timeframe="1h", source="yahoo", sample_n=300)
    except RuntimeError as exc:
        if "yahoo" in str(exc).lower() or "All market sources failed" in str(exc):
            pytest.skip(f"Yahoo unreachable in this environment: {exc}")
        raise
    assert report.get("source") == "yahoo"
    assert report.get("bars", 0) > 50
    assert "metrics" in report
