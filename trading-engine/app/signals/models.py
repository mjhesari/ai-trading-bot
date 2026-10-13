"""Standard trading signal model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TradingSignal(BaseModel):
    symbol: str
    timeframe: str
    direction: str
    entry: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward: float
    confidence: float
    reasons: list[str] = Field(default_factory=list)
    time: datetime | None = None
    outcome: str | None = None
    correct: bool | None = None
    exit_price: float | None = None
    exit_time: datetime | None = None
    bars_held: int | None = None
    r_multiple: float | None = None

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "direction": self.direction,
            "entry": self.entry,
            "stopLoss": self.stop_loss,
            "takeProfit1": self.take_profit_1,
            "takeProfit2": self.take_profit_2,
            "riskReward": self.risk_reward,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "time": self.time.isoformat() if self.time else None,
            "outcome": self.outcome,
            "correct": self.correct,
            "exitPrice": self.exit_price,
            "exitTime": self.exit_time.isoformat() if self.exit_time else None,
            "barsHeld": self.bars_held,
            "rMultiple": self.r_multiple,
        }
