"""CHoCH (Change of Character) helpers — used by MarketStructure."""

from __future__ import annotations


def is_bullish_choch(trend: str | None, close: float, last_swing_high: float | None) -> bool:
    if last_swing_high is None:
        return False
    return trend == "down" and close > last_swing_high


def is_bearish_choch(trend: str | None, close: float, last_swing_low: float | None) -> bool:
    if last_swing_low is None:
        return False
    return trend == "up" and close < last_swing_low
