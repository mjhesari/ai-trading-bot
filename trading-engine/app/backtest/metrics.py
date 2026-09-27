"""Backtest metrics."""

from __future__ import annotations

from typing import Any

import pandas as pd


def compute_metrics(trades: pd.DataFrame, equity_curve: list[float], initial_balance: float) -> dict[str, Any]:
    if trades.empty:
        return {
            "totalTrades": 0,
            "winRate": 0.0,
            "profitFactor": 0.0,
            "expectancy": 0.0,
            "maxDrawdown": 0.0,
            "averageR": 0.0,
            "sharpe": 0.0,
            "finalBalance": initial_balance,
            "netProfit": 0.0,
            "returnPct": 0.0,
            "equityCurve": equity_curve,
        }

    wins = trades[trades["outcome"] == "TP"]
    losses = trades[trades["outcome"] == "SL"]
    total = len(trades)
    win_rate = len(wins) / total * 100

    gross_profit = wins["pnl"].sum() if not wins.empty else 0.0
    gross_loss = abs(losses["pnl"].sum()) if not losses.empty else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf") if gross_profit > 0 else 0.0

    expectancy = trades["pnl"].mean()
    average_r = trades["r_multiple"].mean()

    equity = pd.Series(equity_curve)
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    max_dd = float(drawdown.min() * 100)

    returns = equity.pct_change().dropna()
    sharpe = 0.0
    if len(returns) > 1 and returns.std() > 0:
        sharpe = float((returns.mean() / returns.std()) * (252 ** 0.5))

    final_balance = float(equity.iloc[-1])
    return {
        "totalTrades": total,
        "wins": int(len(wins)),
        "losses": int(len(losses)),
        "winRate": round(win_rate, 2),
        "profitFactor": round(profit_factor if profit_factor != float("inf") else 999.0, 2),
        "expectancy": round(float(expectancy), 2),
        "maxDrawdown": round(max_dd, 2),
        "averageR": round(float(average_r), 2),
        "sharpe": round(sharpe, 2),
        "finalBalance": round(final_balance, 2),
        "netProfit": round(final_balance - initial_balance, 2),
        "returnPct": round((final_balance - initial_balance) / initial_balance * 100, 2),
        "equityCurve": [round(float(x), 2) for x in equity_curve],
    }
