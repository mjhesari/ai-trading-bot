"""Risk helpers."""

from __future__ import annotations


def position_size(balance: float, risk_pct: float, entry: float, stop_loss: float, pip_value: float = 10.0) -> float:
    risk_amount = balance * risk_pct
    stop_distance = abs(entry - stop_loss)
    if stop_distance <= 0:
        return 0.0
    # Approximate lots for forex majors (pip ~ 0.0001)
    pips = stop_distance / 0.0001
    if pips <= 0:
        return 0.0
    return round(risk_amount / (pips * pip_value), 2)


def compute_stop_loss(entry: float, direction: str, structure_level: float, buffer_pct: float) -> float:
    if direction.upper() == "BUY":
        return structure_level * (1 - buffer_pct)
    return structure_level * (1 + buffer_pct)


def compute_take_profits(entry: float, stop_loss: float, direction: str, rr: float = 2.0) -> tuple[float, float]:
    risk = abs(entry - stop_loss)
    if direction.upper() == "BUY":
        return entry + risk * rr, entry + risk * (rr + 1.0)
    return entry - risk * rr, entry - risk * (rr + 1.0)
