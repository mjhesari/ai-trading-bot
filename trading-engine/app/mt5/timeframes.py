"""MT5 timeframe mapping helpers."""

from __future__ import annotations

# String TF → MetaTrader5 TIMEFRAME_* constant name
TF_TO_MT5_NAME = {
    "1m": "TIMEFRAME_M1",
    "5m": "TIMEFRAME_M5",
    "15m": "TIMEFRAME_M15",
    "30m": "TIMEFRAME_M30",
    "1h": "TIMEFRAME_H1",
    "2h": "TIMEFRAME_H2",
    "4h": "TIMEFRAME_H4",
    "1d": "TIMEFRAME_D1",
    "1w": "TIMEFRAME_W1",
}


def resolve_mt5_timeframe(mt5, timeframe: str) -> int:
    name = TF_TO_MT5_NAME.get(timeframe)
    if name is None:
        raise ValueError(f"Unsupported MT5 timeframe: {timeframe}")
    return int(getattr(mt5, name))
