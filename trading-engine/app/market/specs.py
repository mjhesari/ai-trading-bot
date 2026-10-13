"""Per-symbol contract / pip specs for lot sizing."""

from __future__ import annotations

from dataclasses import dataclass

from app.market.symbol import normalize_symbol


@dataclass(frozen=True)
class InstrumentSpec:
    symbol: str
    pip_size: float
    contract_size: float
    min_lot: float
    max_lot: float
    lot_step: float


def instrument_spec(symbol: str) -> InstrumentSpec:
    s = normalize_symbol(symbol)
    if s.startswith("XAU") or s in {"GOLD"}:
        return InstrumentSpec(s, pip_size=0.01, contract_size=100.0, min_lot=0.01, max_lot=50.0, lot_step=0.01)
    if s == "SPX":
        # CFD-style: $1 per index point per 1.0 lot
        return InstrumentSpec(s, pip_size=0.01, contract_size=1.0, min_lot=0.01, max_lot=100.0, lot_step=0.01)
    if "JPY" in s:
        return InstrumentSpec(s, pip_size=0.01, contract_size=100_000.0, min_lot=0.01, max_lot=100.0, lot_step=0.01)
    return InstrumentSpec(s, pip_size=0.0001, contract_size=100_000.0, min_lot=0.01, max_lot=100.0, lot_step=0.01)


def round_lot(lots: float, spec: InstrumentSpec) -> float:
    if lots <= 0:
        return 0.0
    steps = round(lots / spec.lot_step)
    sized = steps * spec.lot_step
    sized = max(spec.min_lot, min(spec.max_lot, sized))
    return round(sized, 2)


def lots_for_risk(
    *,
    balance: float,
    risk_pct: float,
    entry: float,
    stop_loss: float,
    spec: InstrumentSpec,
    min_lot: float | None = None,
    max_lot: float | None = None,
) -> float:
    risk_amount = balance * risk_pct
    stop_dist = abs(entry - stop_loss)
    if stop_dist <= 0 or spec.contract_size <= 0 or risk_amount <= 0:
        return 0.0
    raw = risk_amount / (stop_dist * spec.contract_size)
    capped = InstrumentSpec(
        spec.symbol,
        spec.pip_size,
        spec.contract_size,
        min_lot if min_lot is not None else spec.min_lot,
        max_lot if max_lot is not None else spec.max_lot,
        spec.lot_step,
    )
    return round_lot(raw, capped)


def price_pnl(direction: str, entry: float, exit_price: float, lots: float, spec: InstrumentSpec) -> float:
    sign = 1.0 if str(direction).upper() == "BUY" else -1.0
    return sign * (exit_price - entry) * spec.contract_size * lots
