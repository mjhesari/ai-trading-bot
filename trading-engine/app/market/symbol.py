"""Symbol utilities for real market APIs (Yahoo / Twelve Data)."""

from __future__ import annotations

from app.core.constants import YAHOO_FOREX_SUFFIX

# Metals / special Yahoo tickers
YAHOO_ALIASES = {
    "XAUUSD": "GC=F",
    "GOLD": "GC=F",
    "XAGUSD": "SI=F",
    "SILVER": "SI=F",
}


def normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper().replace("/", "").replace("-", "").replace("_", "")
    if s.endswith(YAHOO_FOREX_SUFFIX):
        return s[: -len(YAHOO_FOREX_SUFFIX)]
    if s.endswith("=F"):
        # reverse common futures aliases
        if s == "GC=F":
            return "XAUUSD"
        if s == "SI=F":
            return "XAGUSD"
    return s


def to_yahoo_symbol(symbol: str) -> str:
    """Map broker-style symbols to Yahoo Finance tickers."""
    s = normalize_symbol(symbol)
    if s in YAHOO_ALIASES:
        return YAHOO_ALIASES[s]
    if s.endswith(YAHOO_FOREX_SUFFIX) or s.endswith("=F"):
        return s
    if len(s) == 6 and s.isalpha():
        return f"{s}{YAHOO_FOREX_SUFFIX}"
    return s


def to_twelvedata_symbol(symbol: str) -> str:
    """Twelve Data forex format: EUR/USD"""
    s = normalize_symbol(symbol)
    if s == "XAUUSD":
        return "XAU/USD"
    if s == "XAGUSD":
        return "XAG/USD"
    if len(s) == 6 and s.isalpha():
        return f"{s[:3]}/{s[3:]}"
    return s
