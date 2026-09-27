"""Risk manager facade."""

from __future__ import annotations

from app.core.config import get_settings
from app.risk.position_size import compute_stop_loss, compute_take_profits, position_size


class RiskManager:
    def __init__(self, balance: float | None = None, risk_pct: float | None = None) -> None:
        settings = get_settings()
        self.balance = balance if balance is not None else settings.initial_balance
        self.risk_pct = risk_pct if risk_pct is not None else settings.risk_per_trade_pct

    def size(self, entry: float, stop_loss: float) -> float:
        return position_size(self.balance, self.risk_pct, entry, stop_loss)

    def stops(
        self, entry: float, direction: str, structure_level: float, buffer_pct: float, rr: float
    ) -> tuple[float, float, float]:
        sl = compute_stop_loss(entry, direction, structure_level, buffer_pct)
        tp1, tp2 = compute_take_profits(entry, sl, direction, rr)
        return sl, tp1, tp2
