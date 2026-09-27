"""SMC Strategy V1 — wraps the Claude smc_bot engine for the FastAPI app."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.core.config import Settings, get_settings
from app.smc_engine.pipeline import run_smc_pipeline


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
    Pipeline (Claude smc_bot):
      swings -> structure -> OB -> FVG -> liquidity -> premium/discount -> PA -> signals

    Enriches raw engine output with TP2 / confidence / reasons for the API.
    """

    def __init__(self, config: SMCv1Config | None = None) -> None:
        self.config = config or SMCv1Config.from_settings()

    def analyze(self, candles: pd.DataFrame) -> pd.DataFrame:
        df = run_smc_pipeline(
            candles,
            swing_lookback=self.config.swing_lookback,
            fvg_min_gap_pct=self.config.fvg_min_gap_pct,
            liquidity_equal_tolerance=self.config.liquidity_equal_tolerance,
            premium_discount_level=self.config.premium_discount_level,
            risk_reward_ratio=self.config.risk_reward_ratio,
            sl_buffer_pct=self.config.sl_buffer_pct,
        )
        return self._enrich(df)

    def _enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["take_profit_1"] = None
        out["take_profit_2"] = None
        out["risk_reward"] = None
        out["confidence"] = None
        out["reasons"] = [None] * len(out)
        out["reasons"] = out["reasons"].astype(object)

        rr = self.config.risk_reward_ratio

        for i in range(len(out)):
            if out["signal"].iloc[i] is None:
                continue

            entry = float(out["entry"].iloc[i])
            sl = float(out["stop_loss"].iloc[i])
            direction = str(out["signal"].iloc[i])
            risk = abs(entry - sl)
            if risk <= 0:
                continue

            if direction == "BUY":
                tp1 = entry + risk * rr
                tp2 = entry + risk * (rr + 1.0)
            else:
                tp1 = entry - risk * rr
                tp2 = entry - risk * (rr + 1.0)

            # Prefer engine TP when present
            engine_tp = out["take_profit"].iloc[i]
            if engine_tp is not None and not (isinstance(engine_tp, float) and pd.isna(engine_tp)):
                tp1 = float(engine_tp)

            reasons = self._build_reasons(out, i, direction)
            conf = min(95.0, 55.0 + 8.0 * len(reasons))

            out.iat[i, out.columns.get_loc("take_profit_1")] = tp1
            out.iat[i, out.columns.get_loc("take_profit_2")] = tp2
            out.iat[i, out.columns.get_loc("risk_reward")] = rr
            out.iat[i, out.columns.get_loc("confidence")] = conf
            out.at[out.index[i], "reasons"] = reasons

        return out

    @staticmethod
    def _build_reasons(df: pd.DataFrame, i: int, direction: str) -> list[str]:
        bull = direction == "BUY"
        reasons: list[str] = []

        if bull:
            reasons.append("Bullish BOS/structure")
            reasons.append("Discount zone")
            reasons.append("Bullish price action")
            if bool(df["bullish_fvg"].iloc[max(0, i - 3) : i + 1].any()):
                reasons.append("Bullish FVG nearby")
            if bool(df["choch"].iloc[i]):
                reasons.append("Bullish CHoCH")
            if bool(df["equal_low"].iloc[max(0, i - 5) : i + 1].any()):
                reasons.append("Bullish liquidity sweep context")
        else:
            reasons.append("Bearish BOS/structure")
            reasons.append("Premium zone")
            reasons.append("Bearish price action")
            if bool(df["bearish_fvg"].iloc[max(0, i - 3) : i + 1].any()):
                reasons.append("Bearish FVG nearby")
            if bool(df["choch"].iloc[i]):
                reasons.append("Bearish CHoCH")
            if bool(df["equal_high"].iloc[max(0, i - 5) : i + 1].any()):
                reasons.append("Bearish liquidity sweep context")

        engine_reason = df["reason"].iloc[i] if "reason" in df.columns else None
        if engine_reason and isinstance(engine_reason, str):
            # Keep English reasons for the API; engine Persian reason is optional context
            pass

        return reasons
