"""Backtest smoke test."""

from app.backtest.runner import BacktestRunner


def test_backtest_runner_sample():
    report = BacktestRunner().run(use_sample=True, sample_n=400)
    assert "id" in report
    assert "metrics" in report
    assert "totalTrades" in report["metrics"]
