"""BOS (Break of Structure) helpers — used by MarketStructure."""

from __future__ import annotations


def is_bullish_bos(trend: str | None, close: float, last_swing_high: float | None) -> bool:
    if last_swing_high is None:
        return False
    return close > last_swing_high and trend != "down"


def is_bearish_bos(trend: str | None, close: float, last_swing_low: float | None) -> bool:
    if last_swing_low is None:
        return False
    return close < last_swing_low and trend != "up"
