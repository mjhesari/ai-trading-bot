"""Grade historical signals against later OHLC (SL vs TP1/TP2)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from app.signals.models import TradingSignal

# Conservative: if SL and TP print on the same bar, count the stop first.
OUTCOME_OPEN = "OPEN"
OUTCOME_SL = "SL"
OUTCOME_TP1 = "TP1"
OUTCOME_TP2 = "TP2"


def _bar_hit(direction: str, high: float, low: float, sl: float, tp1: float, tp2: float) -> str | None:
    if direction == "BUY":
        hit_sl = low <= sl
        hit_tp2 = high >= tp2
        hit_tp1 = high >= tp1
    else:
        hit_sl = high >= sl
        hit_tp2 = low <= tp2
        hit_tp1 = low <= tp1

    if hit_sl:
        return OUTCOME_SL
    if hit_tp2:
        return OUTCOME_TP2
    if hit_tp1:
        return OUTCOME_TP1
    return None


def grade_forward(
    *,
    direction: str,
    entry: float,
    sl: float,
    tp1: float,
    tp2: float,
    future: pd.DataFrame,
) -> dict[str, Any]:
    direction = str(direction).upper()
    risk = abs(entry - sl)
    for bars_held, (idx, row) in enumerate(future.iterrows(), start=1):
        hit = _bar_hit(direction, float(row["high"]), float(row["low"]), sl, tp1, tp2)
        if hit is None:
            continue
        if hit == OUTCOME_SL:
            exit_price = sl
            r_mult = -1.0
            correct = False
        elif hit == OUTCOME_TP2:
            exit_price = tp2
            r_mult = (abs(tp2 - entry) / risk) if risk > 0 else 0.0
            correct = True
        else:
            exit_price = tp1
            r_mult = (abs(tp1 - entry) / risk) if risk > 0 else 0.0
            correct = True
        exit_time = idx.to_pydatetime() if hasattr(idx, "to_pydatetime") else None
        return {
            "outcome": hit,
            "correct": correct,
            "exitPrice": float(exit_price),
            "exitTime": exit_time.isoformat() if isinstance(exit_time, datetime) else None,
            "barsHeld": bars_held,
            "rMultiple": round(float(r_mult), 3),
        }

    return {
        "outcome": OUTCOME_OPEN,
        "correct": None,
        "exitPrice": None,
        "exitTime": None,
        "barsHeld": int(len(future)),
        "rMultiple": None,
    }


def apply_grade(sig: TradingSignal, grade: dict[str, Any]) -> TradingSignal:
    sig.outcome = grade["outcome"]
    sig.correct = grade["correct"]
    sig.exit_price = grade["exitPrice"]
    sig.exit_time = datetime.fromisoformat(grade["exitTime"]) if grade["exitTime"] else None
    sig.bars_held = grade["barsHeld"]
    sig.r_multiple = grade["rMultiple"]
    return sig


def grade_from_index(sig: TradingSignal, df: pd.DataFrame, pos: int) -> TradingSignal:
    future = df.iloc[pos + 1 :] if pos >= 0 else df.iloc[0:0]
    return apply_grade(
        sig,
        grade_forward(
            direction=sig.direction,
            entry=sig.entry,
            sl=sig.stop_loss,
            tp1=sig.take_profit_1,
            tp2=sig.take_profit_2,
            future=future,
        ),
    )


def outcome_summary(signals: list[TradingSignal] | list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for s in signals:
        if isinstance(s, TradingSignal):
            rows.append(
                {
                    "outcome": s.outcome,
                    "correct": s.correct,
                }
            )
        else:
            rows.append(s)

    wins = sum(1 for r in rows if r.get("correct") is True)
    losses = sum(1 for r in rows if r.get("correct") is False)
    open_n = sum(1 for r in rows if r.get("outcome") == OUTCOME_OPEN or r.get("correct") is None)
    closed = wins + losses
    return {
        "total": len(rows),
        "wins": wins,
        "losses": losses,
        "open": open_n,
        "winRate": round(wins / closed, 4) if closed else None,
    }
