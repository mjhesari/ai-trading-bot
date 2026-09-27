"""Execution facade."""

from __future__ import annotations

from app.execution.live import LiveExecutor
from app.execution.paper import PaperExecutor
from app.signals.models import TradingSignal


class Executor:
    def __init__(self, mode: str = "paper") -> None:
        self.mode = mode
        self._impl = PaperExecutor() if mode == "paper" else LiveExecutor()

    def execute(self, signal: TradingSignal) -> dict:
        return self._impl.execute(signal)
