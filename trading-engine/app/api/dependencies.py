"""FastAPI shared dependencies."""

from __future__ import annotations

from functools import lru_cache

from app.backtest.runner import BacktestRunner
from app.core.config import Settings, get_settings


@lru_cache
def get_backtest_runner() -> BacktestRunner:
    return BacktestRunner()


def settings_dep() -> Settings:
    return get_settings()
