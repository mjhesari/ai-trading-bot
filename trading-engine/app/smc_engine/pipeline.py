"""Full SMC + Price Action pipeline from the Claude smc_bot engine."""

from __future__ import annotations

import pandas as pd

from app.smc_engine.market_structure import detect_structure, find_swings
from app.smc_engine.price_action import detect_price_action
from app.smc_engine.signal_engine import generate_signals
from app.smc_engine.smc_detector import (
    detect_fvg,
    detect_liquidity_zones,
    detect_order_blocks,
    detect_premium_discount,
)


def run_smc_pipeline(
    df: pd.DataFrame,
    *,
    swing_lookback: int = 5,
    fvg_min_gap_pct: float = 0.0002,
    liquidity_equal_tolerance: float = 0.0005,
    premium_discount_level: float = 0.5,
    risk_reward_ratio: float = 2.0,
    sl_buffer_pct: float = 0.0005,
) -> pd.DataFrame:
    """
    Run the Claude smc_bot detection chain:
      swings -> structure -> OB -> FVG -> liquidity -> premium/discount -> PA -> signals
    """
    out = find_swings(df, lookback=swing_lookback)
    out = detect_structure(out)
    out = detect_order_blocks(out)
    out = detect_fvg(out, min_gap_pct=fvg_min_gap_pct)
    out = detect_liquidity_zones(out, tolerance=liquidity_equal_tolerance)
    out = detect_premium_discount(out, level=premium_discount_level)
    out = detect_price_action(out)
    out = generate_signals(out, rr_ratio=risk_reward_ratio, sl_buffer_pct=sl_buffer_pct)
    return out
