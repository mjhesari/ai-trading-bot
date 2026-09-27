"""Simple bar-by-bar backtest engine."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.backtest.metrics import compute_metrics


class BacktestEngine:
    def __init__(self, initial_balance: float = 10_000.0, risk_pct: float = 0.01) -> None:
        self.initial_balance = initial_balance
        self.risk_pct = risk_pct

    def run(self, df: pd.DataFrame) -> dict[str, Any]:
        balance = self.initial_balance
        equity_curve = [balance]
        trades: list[dict[str, Any]] = []

        signal_rows = df[df["signal"].notna()]

        for idx in signal_rows.index:
            i = df.index.get_loc(idx)
            row = df.loc[idx]
            direction = row["signal"]
            entry = float(row["entry"])
            sl = float(row["stop_loss"])
            tp = float(row["take_profit_1"])
            risk_amount = balance * self.risk_pct

            outcome = None
            exit_price = None

            for j in range(i + 1, len(df)):
                future_high = float(df["high"].iloc[j])
                future_low = float(df["low"].iloc[j])

                if direction == "BUY":
                    if future_low <= sl:
                        outcome, exit_price = "SL", sl
                        break
                    if future_high >= tp:
                        outcome, exit_price = "TP", tp
                        break
                else:
                    if future_high >= sl:
                        outcome, exit_price = "SL", sl
                        break
                    if future_low <= tp:
                        outcome, exit_price = "TP", tp
                        break

            if outcome is None:
                continue

            risk_dist = abs(entry - sl)
            reward_dist = abs(tp - entry)
            r_multiple = (reward_dist / risk_dist) if outcome == "TP" and risk_dist > 0 else -1.0
            pnl = risk_amount * r_multiple
            balance += pnl
            equity_curve.append(balance)
            trades.append(
                {
                    "time": str(idx),
                    "direction": direction,
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "outcome": outcome,
                    "exit": exit_price,
                    "r_multiple": r_multiple,
                    "pnl": pnl,
                    "balance": balance,
                }
            )

        trades_df = pd.DataFrame(trades)
        metrics = compute_metrics(trades_df, equity_curve, self.initial_balance)
        return {"trades": trades, "metrics": metrics}
