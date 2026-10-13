import pandas as pd

from app.signals.outcome import grade_forward


def _bars(rows: list[tuple[float, float]]) -> pd.DataFrame:
    idx = pd.date_range("2026-01-01", periods=len(rows), freq="h")
    highs = [h for h, _ in rows]
    lows = [l for _, l in rows]
    return pd.DataFrame({"high": highs, "low": lows, "close": highs}, index=idx)


def test_buy_tp1_before_sl():
    future = _bars([(1.105, 1.101), (1.120, 1.108)])
    grade = grade_forward(direction="BUY", entry=1.10, sl=1.09, tp1=1.12, tp2=1.14, future=future)
    assert grade["outcome"] == "TP1"
    assert grade["correct"] is True
    assert grade["barsHeld"] == 2


def test_buy_sl_same_bar_beats_tp():
    future = _bars([(1.13, 1.08)])
    grade = grade_forward(direction="BUY", entry=1.10, sl=1.09, tp1=1.12, tp2=1.14, future=future)
    assert grade["outcome"] == "SL"
    assert grade["correct"] is False


def test_open_when_neither_hit():
    future = _bars([(1.101, 1.099)])
    grade = grade_forward(direction="BUY", entry=1.10, sl=1.09, tp1=1.12, tp2=1.14, future=future)
    assert grade["outcome"] == "OPEN"
    assert grade["correct"] is None
