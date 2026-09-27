"""Paper trading executor."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.signals.models import TradingSignal


class PaperExecutor:
    def __init__(self) -> None:
        self.orders: list[dict[str, Any]] = []

    def execute(self, signal: TradingSignal) -> dict[str, Any]:
        order = {
            "id": str(uuid4()),
            "mode": "paper",
            "status": "accepted",
            "signal": signal.to_api_dict(),
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        self.orders.append(order)
        return order
