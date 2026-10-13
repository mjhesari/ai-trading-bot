"""ICT v1 — killzone + liquidity sweep + displacement/FVG entry, SL beyond the raid, TP at 2R / opposing liquidity."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.core.config import Settings, get_settings
from app.market.session import bar_in_killzone
from app.smc_engine.pipeline import run_smc_pipeline
from app.strategy.smc.displacement import DisplacementDetector


@dataclass
class ICTv1Config:
    swing_lookback: int = 5
    fvg_min_gap_pct: float = 0.0002
    liquidity_equal_tolerance: float = 0.0005
    premium_discount_level: float = 0.5
    risk_reward_ratio: float = 2.0
    sl_buffer_pct: float = 0.0005
    confirm_bars: int = 12
    cooldown_bars: int = 5
    timeframe: str = "1h"

    @classmethod
    def from_settings(cls, settings: Settings | None = None, timeframe: str = "1h") -> "ICTv1Config":
        s = settings or get_settings()
        return cls(
            swing_lookback=s.swing_lookback,
            fvg_min_gap_pct=s.fvg_min_gap_pct,
            liquidity_equal_tolerance=s.liquidity_equal_tolerance,
            premium_discount_level=s.premium_discount_level,
            risk_reward_ratio=s.risk_reward_ratio,
            sl_buffer_pct=s.sl_buffer_pct,
            timeframe=timeframe,
        )


class ICTv1Strategy:
    """
    ICT sequence:
      1. Killzone (London / NY open)
      2. Liquidity raid (sweep of a recent swing high/low, close back inside)
      3. Displacement / FVG in the opposite direction + MSS (BOS/CHoCH)
      4. Entry at close; SL beyond the swept wick; TP1 = RR; TP2 = opposing swing liquidity
    """

    def __init__(self, config: ICTv1Config | None = None, timeframe: str = "1h") -> None:
        self.config = config or ICTv1Config.from_settings(timeframe=timeframe)
        if timeframe:
            self.config.timeframe = timeframe

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
        df = DisplacementDetector().detect(df)
        return self._signals(df)

    def _signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["signal"] = None
        out["entry"] = None
        out["stop_loss"] = None
        out["take_profit"] = None
        out["take_profit_1"] = None
        out["take_profit_2"] = None
        out["risk_reward"] = None
        out["confidence"] = None
        out["reason"] = None
        out["reasons"] = [None] * len(out)
        out["reasons"] = out["reasons"].astype(object)

        last_sh = None
        last_sl = None
        sweep_low_i = None
        sweep_low_px = None
        sweep_high_i = None
        sweep_high_px = None
        last_signal_i = -999
        rr = self.config.risk_reward_ratio
        confirm = self.config.confirm_bars
        cooldown = self.config.cooldown_bars
        buf = self.config.sl_buffer_pct
        tf = self.config.timeframe

        for i in range(len(out)):
            high = float(out["high"].iloc[i])
            low = float(out["low"].iloc[i])
            close = float(out["close"].iloc[i])

            if bool(out["swing_high"].iloc[i]):
                last_sh = high
            if bool(out["swing_low"].iloc[i]):
                last_sl = low

            if last_sl is not None and low < last_sl and close > last_sl:
                sweep_low_i, sweep_low_px = i, low
            if last_sh is not None and high > last_sh and close < last_sh:
                sweep_high_i, sweep_high_px = i, high

            if i - last_signal_i < cooldown:
                continue
            ts = out.index[i]
            if not bar_in_killzone(ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts, tf):
                continue

            trend = out["trend"].iloc[i]
            choch = bool(out["choch"].iloc[i])
            bos = bool(out["bos"].iloc[i])
            bull_disp = bool(out["bullish_displacement"].iloc[i]) or bool(out["bullish_fvg"].iloc[i])
            bear_disp = bool(out["bearish_displacement"].iloc[i]) or bool(out["bearish_fvg"].iloc[i])

            buy = (
                sweep_low_i is not None
                and i - sweep_low_i <= confirm
                and bull_disp
                and (trend == "up" or choch or bos)
            )
            sell = (
                sweep_high_i is not None
                and i - sweep_high_i <= confirm
                and bear_disp
                and (trend == "down" or choch or bos)
            )

            if buy and sweep_low_px is not None:
                entry = close
                sl = sweep_low_px * (1 - buf)
                risk = entry - sl
                if risk <= 0:
                    continue
                tp1 = entry + risk * rr
                tp2 = last_sh if last_sh is not None and last_sh > tp1 else entry + risk * (rr + 1.0)
                reasons = ["ICT killzone", "Liquidity sweep (lows)", "Bullish displacement/FVG"]
                if choch:
                    reasons.append("Bullish CHoCH / MSS")
                elif bos:
                    reasons.append("Bullish BOS")
                self._write_row(out, i, "BUY", entry, sl, tp1, tp2, rr, reasons)
                last_signal_i = i
                sweep_low_i = None
            elif sell and sweep_high_px is not None:
                entry = close
                sl = sweep_high_px * (1 + buf)
                risk = sl - entry
                if risk <= 0:
                    continue
                tp1 = entry - risk * rr
                tp2 = last_sl if last_sl is not None and last_sl < tp1 else entry - risk * (rr + 1.0)
                reasons = ["ICT killzone", "Liquidity sweep (highs)", "Bearish displacement/FVG"]
                if choch:
                    reasons.append("Bearish CHoCH / MSS")
                elif bos:
                    reasons.append("Bearish BOS")
                self._write_row(out, i, "SELL", entry, sl, tp1, tp2, rr, reasons)
                last_signal_i = i
                sweep_high_i = None

        return out

    @staticmethod
    def _write_row(
        out: pd.DataFrame,
        i: int,
        direction: str,
        entry: float,
        sl: float,
        tp1: float,
        tp2: float,
        rr: float,
        reasons: list[str],
    ) -> None:
        loc = out.columns.get_loc
        out.iat[i, loc("signal")] = direction
        out.iat[i, loc("entry")] = entry
        out.iat[i, loc("stop_loss")] = sl
        out.iat[i, loc("take_profit")] = tp1
        out.iat[i, loc("take_profit_1")] = tp1
        out.iat[i, loc("take_profit_2")] = tp2
        out.iat[i, loc("risk_reward")] = rr
        out.iat[i, loc("confidence")] = min(95.0, 58.0 + 8.0 * len(reasons))
        out.iat[i, loc("reason")] = " · ".join(reasons)
        out.at[out.index[i], "reasons"] = reasons
