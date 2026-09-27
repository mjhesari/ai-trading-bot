"""Convert analyzed DataFrame rows into TradingSignal objects."""

from __future__ import annotations

import pandas as pd

from app.signals.models import TradingSignal
from app.signals.scorer import SignalScorer


class SignalGenerator:
    def __init__(self, symbol: str = "EURUSD", timeframe: str = "1h") -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.scorer = SignalScorer()

    def from_frame(self, df: pd.DataFrame) -> list[TradingSignal]:
        rows = df[df["signal"].notna()]
        signals: list[TradingSignal] = []
        for idx, row in rows.iterrows():
            reasons = row["reasons"]
            if reasons is None:
                reasons = []
            elif not isinstance(reasons, list):
                reasons = [str(reasons)]

            sig = TradingSignal(
                symbol=self.symbol,
                timeframe=self.timeframe,
                direction=str(row["signal"]),
                entry=float(row["entry"]),
                stop_loss=float(row["stop_loss"]),
                take_profit_1=float(row["take_profit_1"]),
                take_profit_2=float(row["take_profit_2"]),
                risk_reward=float(row["risk_reward"]),
                confidence=float(row["confidence"] or 60.0),
                reasons=reasons,
                time=idx.to_pydatetime() if hasattr(idx, "to_pydatetime") else None,
            )
            signals.append(self.scorer.score(sig))
        return signals
