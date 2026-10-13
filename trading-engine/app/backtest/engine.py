"""Bar-by-bar backtest: lots, spread, commission, SL / TP1 / TP2, one position at a time."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from app.backtest.metrics import compute_metrics
from app.market.specs import InstrumentSpec, instrument_spec, lots_for_risk, price_pnl


@dataclass
class _Position:
    direction: str
    entry: float
    sl: float
    orig_sl: float
    tp1: float
    tp2: float
    lots: float
    remaining: float
    risk_amount: float
    entry_time: str
    signal_time: str
    partial_done: bool = False
    realized: float = 0.0


class BacktestEngine:
    def __init__(
        self,
        *,
        symbol: str = "EURUSD",
        initial_balance: float = 10_000.0,
        risk_pct: float = 0.01,
        spread_pips: float = 0.8,
        commission_per_lot: float = 7.0,
        min_lot: float | None = None,
        max_lot: float | None = None,
        partial_close_pct: float = 0.5,
        one_trade_at_a_time: bool = True,
    ) -> None:
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.risk_pct = risk_pct
        self.spread_pips = spread_pips
        self.commission_per_lot = commission_per_lot
        self.min_lot = min_lot
        self.max_lot = max_lot
        self.partial_close_pct = min(max(partial_close_pct, 0.0), 1.0)
        self.one_trade_at_a_time = one_trade_at_a_time
        self.spec: InstrumentSpec = instrument_spec(symbol)

    def _spread(self) -> float:
        return self.spread_pips * self.spec.pip_size

    def _fill_entry(self, direction: str, raw: float) -> float:
        spread = self._spread()
        if direction == "BUY":
            return raw + spread
        return raw - spread

    def run(self, df: pd.DataFrame) -> dict[str, Any]:
        balance = self.initial_balance
        equity_curve = [balance]
        trades: list[dict[str, Any]] = []
        pos: _Position | None = None
        pending: dict[str, Any] | None = None

        n = len(df)
        for i in range(n):
            row = df.iloc[i]
            ts = str(df.index[i])

            if pending is not None and pos is None:
                direction = pending["direction"]
                raw_entry = float(row["open"])
                entry = self._fill_entry(direction, raw_entry)
                sl = float(pending["sl"])
                tp1 = float(pending["tp1"])
                tp2 = float(pending["tp2"])
                lots = lots_for_risk(
                    balance=balance,
                    risk_pct=self.risk_pct,
                    entry=entry,
                    stop_loss=sl,
                    spec=self.spec,
                    min_lot=self.min_lot,
                    max_lot=self.max_lot,
                )
                if lots > 0 and abs(entry - sl) > 0:
                    pos = _Position(
                        direction=direction,
                        entry=entry,
                        sl=sl,
                        orig_sl=sl,
                        tp1=tp1,
                        tp2=tp2,
                        lots=lots,
                        remaining=lots,
                        risk_amount=balance * self.risk_pct,
                        entry_time=ts,
                        signal_time=pending["signal_time"],
                    )
                pending = None

            if pos is not None:
                closed = self._manage_bar(pos, row, ts, i == n - 1)
                if closed is not None:
                    commission = self.commission_per_lot * pos.lots
                    pnl = closed["pnl"] - commission
                    balance += pnl
                    equity_curve.append(balance)
                    risk_dist = abs(pos.entry - pos.sl)
                    r_mult = (pnl / pos.risk_amount) if pos.risk_amount else 0.0
                    trades.append(
                        {
                            "time": pos.signal_time,
                            "entryTime": pos.entry_time,
                            "exitTime": closed["exitTime"],
                            "direction": pos.direction,
                            "entry": round(pos.entry, 6),
                            "sl": round(pos.orig_sl, 6),
                            "tp": round(pos.tp1, 6),
                            "tp1": round(pos.tp1, 6),
                            "tp2": round(pos.tp2, 6),
                            "lots": pos.lots,
                            "riskAmount": round(pos.risk_amount, 2),
                            "spreadPips": self.spread_pips,
                            "commission": round(commission, 2),
                            "outcome": closed["outcome"],
                            "exit": round(closed["exit"], 6),
                            "r_multiple": round(r_mult, 3),
                            "pnl": round(pnl, 2),
                            "balance": round(balance, 2),
                        }
                    )
                    pos = None

            if pos is not None and self.one_trade_at_a_time:
                continue

            sig = row.get("signal")
            if sig is None or (isinstance(sig, float) and pd.isna(sig)):
                continue
            sl_v = row.get("stop_loss")
            tp_v = row.get("take_profit_1") if "take_profit_1" in df.columns else row.get("take_profit")
            if sl_v is None or tp_v is None or (isinstance(sl_v, float) and pd.isna(sl_v)):
                continue
            tp2_v = row.get("take_profit_2")
            if tp2_v is None or (isinstance(tp2_v, float) and pd.isna(tp2_v)):
                tp2_v = tp_v
            pending = {
                "direction": str(sig),
                "sl": float(sl_v),
                "tp1": float(tp_v),
                "tp2": float(tp2_v),
                "signal_time": ts,
            }

        trades_df = pd.DataFrame(trades)
        metrics = compute_metrics(trades_df, equity_curve, self.initial_balance)
        metrics["initialBalance"] = round(self.initial_balance, 2)
        metrics["riskPerTradePct"] = round(self.risk_pct * 100, 2)
        metrics["spreadPips"] = self.spread_pips
        metrics["commissionPerLot"] = self.commission_per_lot
        return {"trades": trades, "metrics": metrics}

    def _manage_bar(self, pos: _Position, row: Any, ts: str, last_bar: bool) -> dict[str, Any] | None:
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        buy = pos.direction == "BUY"

        hit_sl = low <= pos.sl if buy else high >= pos.sl
        hit_tp1 = high >= pos.tp1 if buy else low <= pos.tp1
        hit_tp2 = high >= pos.tp2 if buy else low <= pos.tp2

        if not pos.partial_done:
            if hit_sl:
                pnl = price_pnl(pos.direction, pos.entry, pos.sl, pos.remaining, self.spec)
                return {"outcome": "SL", "exit": pos.sl, "exitTime": ts, "pnl": pos.realized + pnl}
            if hit_tp2 and (self.partial_close_pct >= 1 or not hit_tp1):
                # full target if no partial, or TP2 without needing TP1 split
                if self.partial_close_pct >= 0.999:
                    pnl = price_pnl(pos.direction, pos.entry, pos.tp2, pos.remaining, self.spec)
                    return {"outcome": "TP2", "exit": pos.tp2, "exitTime": ts, "pnl": pos.realized + pnl}
            if hit_tp1:
                close_frac = self.partial_close_pct if self.partial_close_pct > 0 else 1.0
                close_lots = round(pos.remaining * close_frac, 2)
                if close_lots <= 0 or close_frac >= 0.999:
                    pnl = price_pnl(pos.direction, pos.entry, pos.tp1, pos.remaining, self.spec)
                    return {"outcome": "TP1", "exit": pos.tp1, "exitTime": ts, "pnl": pos.realized + pnl}
                pos.realized += price_pnl(pos.direction, pos.entry, pos.tp1, close_lots, self.spec)
                pos.remaining = round(pos.remaining - close_lots, 2)
                pos.partial_done = True
                pos.sl = pos.entry  # break-even remainder
                if pos.remaining <= 0:
                    return {"outcome": "TP1", "exit": pos.tp1, "exitTime": ts, "pnl": pos.realized}
                if hit_tp2:
                    pnl = price_pnl(pos.direction, pos.entry, pos.tp2, pos.remaining, self.spec)
                    return {
                        "outcome": "TP1_TP2",
                        "exit": pos.tp2,
                        "exitTime": ts,
                        "pnl": pos.realized + pnl,
                    }
                return None
            if last_bar:
                pnl = price_pnl(pos.direction, pos.entry, close, pos.remaining, self.spec)
                return {"outcome": "EOD", "exit": close, "exitTime": ts, "pnl": pos.realized + pnl}
            return None

        # Remainder after TP1, SL at break-even, target TP2
        if hit_sl:
            pnl = price_pnl(pos.direction, pos.entry, pos.sl, pos.remaining, self.spec)
            return {"outcome": "TP1_BE", "exit": pos.sl, "exitTime": ts, "pnl": pos.realized + pnl}
        if hit_tp2:
            pnl = price_pnl(pos.direction, pos.entry, pos.tp2, pos.remaining, self.spec)
            return {"outcome": "TP1_TP2", "exit": pos.tp2, "exitTime": ts, "pnl": pos.realized + pnl}
        if last_bar:
            pnl = price_pnl(pos.direction, pos.entry, close, pos.remaining, self.spec)
            return {"outcome": "EOD", "exit": close, "exitTime": ts, "pnl": pos.realized + pnl}
        return None
