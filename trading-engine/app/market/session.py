"""Market session placeholders (London/NY overlap etc.). V1 unused in strategy."""

from __future__ import annotations

from datetime import datetime, timezone


def is_london_session(ts: datetime) -> bool:
    hour = ts.astimezone(timezone.utc).hour
    return 7 <= hour < 16


def is_new_york_session(ts: datetime) -> bool:
    hour = ts.astimezone(timezone.utc).hour
    return 12 <= hour < 21


def is_killzone(ts: datetime) -> bool:
    """Rough London open / NY open killzones."""
    hour = ts.astimezone(timezone.utc).hour
    return hour in {7, 8, 12, 13}
