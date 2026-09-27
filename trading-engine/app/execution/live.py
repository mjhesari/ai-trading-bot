"""Live execution stub."""

from __future__ import annotations

from typing import Any

from app.signals.models import TradingSignal


class LiveExecutor:
    def execute(self, signal: TradingSignal) -> dict[str, Any]:
        raise NotImplementedError("Live execution requires MT5 on Windows/VPS")
