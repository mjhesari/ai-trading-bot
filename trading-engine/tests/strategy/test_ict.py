from app.market.data import generate_sample_data
from app.signals.generator import SignalGenerator
from app.strategy.registry import resolve_strategy
from app.strategy.strategies.ict_v1 import ICTv1Strategy


def test_ict_analyze_has_entry_exits():
    candles = generate_sample_data(n=800)
    out = ICTv1Strategy(timeframe="1h").analyze(candles)
    assert "signal" in out.columns
    assert "take_profit_1" in out.columns
    assert "take_profit_2" in out.columns
    hits = out[out["signal"].notna()]
    if len(hits) == 0:
        return
    row = hits.iloc[0]
    assert row["signal"] in {"BUY", "SELL"}
    assert float(row["entry"]) > 0
    assert float(row["stop_loss"]) > 0
    assert float(row["take_profit_1"]) > 0


def test_registry_resolves_both():
    sid, smc = resolve_strategy("smc")
    iid, ict = resolve_strategy("ict", timeframe="1h")
    assert sid == "smc"
    assert iid == "ict"
    assert smc.__class__.__name__ == "SMCv1Strategy"
    assert ict.__class__.__name__ == "ICTv1Strategy"


def test_ict_signals_generator():
    candles = generate_sample_data(n=800)
    analyzed = ICTv1Strategy(timeframe="1h").analyze(candles)
    signals = SignalGenerator().from_frame(analyzed)
    assert isinstance(signals, list)
