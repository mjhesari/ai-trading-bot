"""Backtest smoke test — sample + real yahoo path."""

import pytest

from app.backtest.runner import BacktestRunner


def test_backtest_runner_sample():
    report = BacktestRunner().run(source="sample", sample_n=400)
    assert "id" in report
    assert "metrics" in report
    assert "totalTrades" in report["metrics"]
    assert report.get("source") == "sample"


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
