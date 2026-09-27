"""ML prediction / signal filter — V1 unused."""

from __future__ import annotations

from app.signals.models import TradingSignal


def predict_probability(signal: TradingSignal) -> float:
    """Future: return model probability to filter weak signals."""
    raise NotImplementedError("ML predict is not used in V1")
