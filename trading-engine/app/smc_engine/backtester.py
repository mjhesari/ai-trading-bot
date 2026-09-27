"""
بک‌تست ساده روی سیگنال‌های تولیدشده.

منطق: برای هر سیگنال، از کندل بعدی به بعد جلو می‌ریم تا ببینیم اول
Stop Loss لمس می‌شه یا Take Profit؛ نتیجه رو به‌صورت R-multiple (نسبت به ریسک) ثبت می‌کنیم.
این یک بک‌تست ساده‌شده است (بدون اسپرد/کمیسیون/اسلیپیج) و صرفا برای
سنجش اولیه‌ی منطق استراتژی مناسبه.
"""

import pandas as pd


def run_backtest(df: pd.DataFrame, initial_balance: float = 10000, risk_pct: float = 0.01) -> dict:
    balance = initial_balance
    equity_curve = [balance]
    trades = []

    signal_rows = df[df["signal"].notna()]

    for idx in signal_rows.index:
        i = df.index.get_loc(idx)
        row = df.loc[idx]
        direction = row["signal"]
        entry, sl, tp = row["entry"], row["stop_loss"], row["take_profit"]
        risk_amount = balance * risk_pct

        outcome = None
        exit_price = None

        for j in range(i + 1, len(df)):
            future_high = df["high"].iloc[j]
            future_low = df["low"].iloc[j]

            if direction == "BUY":
                if future_low <= sl:
                    outcome, exit_price = "SL", sl
                    break
                if future_high >= tp:
                    outcome, exit_price = "TP", tp
                    break
            else:  # SELL
                if future_high >= sl:
                    outcome, exit_price = "SL", sl
                    break
                if future_low <= tp:
                    outcome, exit_price = "TP", tp
                    break

        if outcome is None:
            continue  # معامله تا آخر دیتا بسته نشده، نادیده گرفته می‌شه

        r_multiple = 1 if outcome == "TP" else -1
        pnl = risk_amount * (r_multiple if outcome == "SL" else r_multiple * (abs(tp - entry) / abs(entry - sl)))
        balance += pnl
        equity_curve.append(balance)

        trades.append({
            "time": idx, "direction": direction, "entry": entry, "sl": sl, "tp": tp,
            "outcome": outcome, "pnl": pnl, "balance": balance
        })

    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        return {"trades": trades_df, "stats": {"total_trades": 0}}

    wins = (trades_df["outcome"] == "TP").sum()
    total = len(trades_df)
    win_rate = wins / total * 100

    equity = pd.Series(equity_curve)
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    max_dd = drawdown.min() * 100

    stats = {
        "total_trades": total,
        "wins": int(wins),
        "losses": int(total - wins),
        "win_rate_pct": round(win_rate, 2),
        "final_balance": round(balance, 2),
        "net_profit": round(balance - initial_balance, 2),
        "return_pct": round((balance - initial_balance) / initial_balance * 100, 2),
        "max_drawdown_pct": round(max_dd, 2),
    }

    return {"trades": trades_df, "stats": stats}
