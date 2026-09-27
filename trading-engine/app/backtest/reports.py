"""Backtest report builder."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_report(
    *,
    backtest_id: str,
    symbol: str,
    timeframe: str,
    metrics: dict[str, Any],
    trades: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": backtest_id,
        "symbol": symbol,
        "timeframe": timeframe,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "trades": trades,
    }
