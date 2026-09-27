"""Simple confidence scorer for signals."""

from __future__ import annotations

from app.signals.models import TradingSignal


class SignalScorer:
    def score(self, signal: TradingSignal) -> TradingSignal:
        base = 50.0
        base += min(30.0, 6.0 * len(signal.reasons))
        if signal.risk_reward >= 2:
            base += 10.0
        signal.confidence = min(95.0, max(signal.confidence, base))
        return signal
