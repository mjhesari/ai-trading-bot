"""SMC Strategy V1 — composes detectors and evaluates entries."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.core.config import Settings, get_settings
from app.strategy.price_action.patterns import PatternDetector
from app.strategy.smc.displacement import DisplacementDetector
from app.strategy.smc.fvg import FVGDetector
from app.strategy.smc.liquidity import LiquidityDetector
from app.strategy.smc.order_block import OrderBlockDetector
from app.strategy.smc.structure import MarketStructure
from app.strategy.smc.swing import SwingDetector


@dataclass
class SMCv1Config:
    swing_lookback: int = 5
    fvg_min_gap_pct: float = 0.0002
    liquidity_equal_tolerance: float = 0.0005
    premium_discount_level: float = 0.5
    risk_reward_ratio: float = 2.0
    sl_buffer_pct: float = 0.0005

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "SMCv1Config":
        s = settings or get_settings()
        return cls(
            swing_lookback=s.swing_lookback,
            fvg_min_gap_pct=s.fvg_min_gap_pct,
            liquidity_equal_tolerance=s.liquidity_equal_tolerance,
            premium_discount_level=s.premium_discount_level,
            risk_reward_ratio=s.risk_reward_ratio,
            sl_buffer_pct=s.sl_buffer_pct,
        )


class SMCv1Strategy:
    """
    Pipeline:
      swings -> structure -> liquidity -> FVG -> order blocks -> displacement -> PA -> evaluate
    """

    def __init__(self, config: SMCv1Config | None = None) -> None:
        self.config = config or SMCv1Config.from_settings()
        self.swing = SwingDetector(lookback=self.config.swing_lookback)
        self.structure = MarketStructure()
        self.liquidity = LiquidityDetector(
            tolerance=self.config.liquidity_equal_tolerance,
            level=self.config.premium_discount_level,
        )
        self.fvg = FVGDetector(min_gap_pct=self.config.fvg_min_gap_pct)
        self.order_block = OrderBlockDetector()
        self.displacement = DisplacementDetector()
        self.price_action = PatternDetector()

    def analyze(self, candles: pd.DataFrame) -> pd.DataFrame:
        df = self.swing.detect(candles)
        df = self.structure.detect(df)
        df = self.liquidity.detect(df, structure=df)
        fvg_df = self.fvg.detect(df)
        for col in ("bullish_fvg", "bearish_fvg"):
            df[col] = fvg_df[col]
        df = self.order_block.detect(df)
        disp = self.displacement.detect(df)
        for col in ("bullish_displacement", "bearish_displacement"):
            df[col] = disp[col]
        pa = self.price_action.detect(df)
        for col in (
            "bullish_engulfing",
            "bearish_engulfing",
            "bullish_pinbar",
            "bearish_pinbar",
            "inside_bar",
        ):
            df[col] = pa[col]
        return self.evaluate(df)

    def evaluate(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["signal"] = None
        out["entry"] = None
        out["stop_loss"] = None
        out["take_profit_1"] = None
        out["take_profit_2"] = None
        out["risk_reward"] = None
        out["confidence"] = None
        out["reasons"] = [None] * len(out)
        out["reasons"] = out["reasons"].astype(object)

        last_bull_ob_low = None
        last_bear_ob_high = None
        rr = self.config.risk_reward_ratio
        buf = self.config.sl_buffer_pct

        for i in range(len(out)):
            if out["bullish_ob"].iloc[i]:
                last_bull_ob_low = float(out["low"].iloc[i])
            if out["bearish_ob"].iloc[i]:
                last_bear_ob_high = float(out["high"].iloc[i])

            trend = out["trend"].iloc[i]
            zone = out["zone"].iloc[i]
            pa_bull = bool(out["bullish_engulfing"].iloc[i] or out["bullish_pinbar"].iloc[i])
            pa_bear = bool(out["bearish_engulfing"].iloc[i] or out["bearish_pinbar"].iloc[i])

            if trend == "up" and zone == "discount" and pa_bull and last_bull_ob_low is not None:
                entry = float(out["close"].iloc[i])
                sl = last_bull_ob_low * (1 - buf)
                risk = entry - sl
                if risk > 0:
                    reasons = ["Bullish BOS/structure", "Discount zone", "Bullish price action"]
                    if out["bullish_fvg"].iloc[i] or out["bullish_fvg"].iloc[max(0, i - 3) : i + 1].any():
                        reasons.append("Bullish FVG nearby")
                    if out["bullish_displacement"].iloc[i]:
                        reasons.append("Bullish displacement")
                    if out["choch"].iloc[i]:
                        reasons.append("Bullish CHoCH")
                    if out["equal_low"].iloc[max(0, i - 5) : i + 1].any():
                        reasons.append("Bullish liquidity sweep context")

                    conf = min(95.0, 55.0 + 8.0 * len(reasons))
                    out.iat[i, out.columns.get_loc("signal")] = "BUY"
                    out.iat[i, out.columns.get_loc("entry")] = entry
                    out.iat[i, out.columns.get_loc("stop_loss")] = sl
                    out.iat[i, out.columns.get_loc("take_profit_1")] = entry + risk * rr
                    out.iat[i, out.columns.get_loc("take_profit_2")] = entry + risk * (rr + 1.0)
                    out.iat[i, out.columns.get_loc("risk_reward")] = rr
                    out.iat[i, out.columns.get_loc("confidence")] = conf
                    out.at[out.index[i], "reasons"] = reasons

            elif trend == "down" and zone == "premium" and pa_bear and last_bear_ob_high is not None:
                entry = float(out["close"].iloc[i])
                sl = last_bear_ob_high * (1 + buf)
                risk = sl - entry
                if risk > 0:
                    reasons = ["Bearish BOS/structure", "Premium zone", "Bearish price action"]
                    if out["bearish_fvg"].iloc[i] or out["bearish_fvg"].iloc[max(0, i - 3) : i + 1].any():
                        reasons.append("Bearish FVG nearby")
                    if out["bearish_displacement"].iloc[i]:
                        reasons.append("Bearish displacement")
                    if out["choch"].iloc[i]:
                        reasons.append("Bearish CHoCH")
                    if out["equal_high"].iloc[max(0, i - 5) : i + 1].any():
                        reasons.append("Bearish liquidity sweep context")

                    conf = min(95.0, 55.0 + 8.0 * len(reasons))
                    out.iat[i, out.columns.get_loc("signal")] = "SELL"
                    out.iat[i, out.columns.get_loc("entry")] = entry
                    out.iat[i, out.columns.get_loc("stop_loss")] = sl
                    out.iat[i, out.columns.get_loc("take_profit_1")] = entry - risk * rr
                    out.iat[i, out.columns.get_loc("take_profit_2")] = entry - risk * (rr + 1.0)
                    out.iat[i, out.columns.get_loc("risk_reward")] = rr
                    out.iat[i, out.columns.get_loc("confidence")] = conf
                    out.at[out.index[i], "reasons"] = reasons

        return out
