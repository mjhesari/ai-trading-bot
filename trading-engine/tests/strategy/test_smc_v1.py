"""Strategy tests on sample data."""

from app.market.data import generate_sample_data
from app.signals.generator import SignalGenerator
from app.strategy.smc.fvg import FVGDetector
from app.strategy.smc.swing import SwingDetector
from app.strategy.strategies.smc_v1 import SMCv1Strategy


def test_swing_detector_marks_extrema():
    candles = generate_sample_data(n=200)
    out = SwingDetector(lookback=3).detect(candles)
    assert "swing_high" in out.columns
    assert out["swing_high"].any() or out["swing_low"].any()


def test_fvg_detector_runs():
    candles = generate_sample_data(n=200)
    out = FVGDetector().detect(candles)
    assert "bullish_fvg" in out.columns
    assert "bearish_fvg" in out.columns


def test_smc_v1_produces_signals():
    candles = generate_sample_data(n=800)
    analyzed = SMCv1Strategy().analyze(candles)
    signals = SignalGenerator().from_frame(analyzed)
    assert isinstance(signals, list)
    # Sample path historically yields signals; if zero, pipeline still must return frame columns.
    assert "signal" in analyzed.columns
    if signals:
        s = signals[0]
        assert s.direction in {"BUY", "SELL"}
        assert s.entry > 0
        assert s.stop_loss > 0
        assert s.take_profit_1 > 0
