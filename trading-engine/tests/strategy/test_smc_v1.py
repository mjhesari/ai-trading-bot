"""Strategy tests on sample data + Claude smc_engine."""

from app.market.data import generate_sample_data
from app.signals.generator import SignalGenerator
from app.smc_engine.market_structure import find_swings
from app.smc_engine.pipeline import run_smc_pipeline
from app.smc_engine.smc_detector import detect_fvg
from app.strategy.strategies.smc_v1 import SMCv1Strategy


def test_swing_detector_marks_extrema():
    candles = generate_sample_data(n=200)
    out = find_swings(candles, lookback=3)
    assert "swing_high" in out.columns
    assert out["swing_high"].any() or out["swing_low"].any()


def test_fvg_detector_runs():
    candles = generate_sample_data(n=200)
    swung = find_swings(candles, lookback=3)
    out = detect_fvg(swung)
    assert "bullish_fvg" in out.columns
    assert "bearish_fvg" in out.columns


def test_claude_pipeline_runs():
    candles = generate_sample_data(n=400)
    out = run_smc_pipeline(candles)
    assert "signal" in out.columns
    assert "zone" in out.columns
    assert "trend" in out.columns


def test_smc_v1_produces_signals():
    candles = generate_sample_data(n=800)
    analyzed = SMCv1Strategy().analyze(candles)
    signals = SignalGenerator().from_frame(analyzed)
    assert isinstance(signals, list)
    assert "signal" in analyzed.columns
    assert "take_profit_1" in analyzed.columns
    if signals:
        s = signals[0]
        assert s.direction in {"BUY", "SELL"}
        assert s.entry > 0
        assert s.stop_loss > 0
        assert s.take_profit_1 > 0
