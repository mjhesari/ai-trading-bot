"""Symbol utilities."""

from __future__ import annotations

from app.core.constants import YAHOO_FOREX_SUFFIX


def to_yahoo_symbol(symbol: str) -> str:
    """Map broker-style forex symbols to Yahoo Finance tickers."""
    s = symbol.strip().upper().replace("/", "")
    if s.endswith(YAHOO_FOREX_SUFFIX):
        return s
    if len(s) == 6 and s.isalpha():
        return f"{s}{YAHOO_FOREX_SUFFIX}"
    return s


def normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper().replace("/", "")
    if s.endswith(YAHOO_FOREX_SUFFIX):
        return s[: -len(YAHOO_FOREX_SUFFIX)]
    return s
