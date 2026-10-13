"use client";

import { FormEvent, useEffect, useState } from "react";
import { EquityChart } from "@/components/backtest/EquityChart";
import { MetricsPanel } from "@/components/backtest/MetricsPanel";
import { Button } from "@/components/ui/button";
import { FieldSelect } from "@/components/ui/field-select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useBacktest } from "@/hooks/use-backtest";
import { useEngineSource } from "@/hooks/use-engine-source";
import { usePairs } from "@/hooks/use-pairs";
import { priceDigits } from "@/lib/live-candle";
import { toPairOptions } from "@/lib/pairs";
import { STRATEGIES } from "@/lib/strategies";
import { DATA_SOURCES, TIMEFRAMES } from "@/lib/timeframes";


export default function BacktestPage() {
  const { report, loading, error, run } = useBacktest();
  const { source: engineSource, ready } = useEngineSource("yahoo");
  const { pairs } = usePairs();
  const [symbol, setSymbol] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState("1h");
  const [strategy, setStrategy] = useState("smc");
  const [sampleN, setSampleN] = useState(800);
  const [source, setSource] = useState("yahoo");
  const [initialBalance, setInitialBalance] = useState(10000);
  const [riskPerTradePct, setRiskPerTradePct] = useState(1);
  const [spreadPips, setSpreadPips] = useState(0.8);
  const [commissionPerLot, setCommissionPerLot] = useState(7);
  const [minLot, setMinLot] = useState(0.01);
  const [maxLot, setMaxLot] = useState(10);
  const [partialClosePct, setPartialClosePct] = useState(50);

  useEffect(() => {
    if (ready) setSource(engineSource);
  }, [ready, engineSource]);

  useEffect(() => {
    if (pairs.length && !pairs.includes(symbol)) {
      setSymbol(pairs[0]);
    }
  }, [pairs, symbol]);

  const selected = STRATEGIES.find((s) => s.value === strategy);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    await run({
      symbol,
      timeframe,
      strategy,
      source,
      sampleN,
      useSample: false,
      initialBalance,
      riskPerTradePct,
      spreadPips,
      commissionPerLot,
      minLot,
      maxLot,
      partialClosePct: partialClosePct / 100,
    });
  }

  const d = priceDigits(symbol);

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <h1>Backtest</h1>
          <p>
            Compare <strong>SMC</strong> and <strong>ICT</strong> on the same tape. Position size is
            lot-based from account risk, with spread and commission.
          </p>
        </div>
      </div>

      <div className="panel">
        <form onSubmit={(e) => void onSubmit(e)}>
          <div className="form-grid">
            <FieldSelect
              label="Strategy"
              value={strategy}
              onValueChange={setStrategy}
              options={STRATEGIES.map((s) => ({ value: s.value, label: s.label }))}
            />
            <FieldSelect
              label="Symbol"
              value={symbol}
              onValueChange={setSymbol}
              options={toPairOptions(pairs)}
              placeholder="Select pair"
            />
            <FieldSelect
              label="Timeframe"
              value={timeframe}
              onValueChange={setTimeframe}
              options={TIMEFRAMES.map((t) => ({ value: t.value, label: t.label }))}
            />
            <FieldSelect
              label="Source"
              value={source}
              onValueChange={setSource}
              options={DATA_SOURCES.map((s) => ({ value: s.value, label: s.label }))}
            />
            <div className="grid gap-2">
              <Label htmlFor="bars">Bars</Label>
              <Input
                id="bars"
                type="number"
                min={200}
                max={5000}
                value={sampleN}
                onChange={(e) => setSampleN(Number(e.target.value))}
              />
            </div>
          </div>

          {selected ? <p className="muted chart-msg">{selected.description}</p> : null}

          <h2 className="panel-title">Account &amp; costs</h2>
          <div className="form-grid">
            <div className="grid gap-2">
              <Label htmlFor="bal">Balance</Label>
              <Input
                id="bal"
                type="number"
                min={100}
                step={100}
                value={initialBalance}
                onChange={(e) => setInitialBalance(Number(e.target.value))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="risk">Risk % / trade</Label>
              <Input
                id="risk"
                type="number"
                min={0.1}
                max={10}
                step={0.1}
                value={riskPerTradePct}
                onChange={(e) => setRiskPerTradePct(Number(e.target.value))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="spread">Spread (pips)</Label>
              <Input
                id="spread"
                type="number"
                min={0}
                step={0.1}
                value={spreadPips}
                onChange={(e) => setSpreadPips(Number(e.target.value))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="comm">Commission / lot</Label>
              <Input
                id="comm"
                type="number"
                min={0}
                step={0.5}
                value={commissionPerLot}
                onChange={(e) => setCommissionPerLot(Number(e.target.value))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="minlot">Min lot</Label>
              <Input
                id="minlot"
                type="number"
                min={0.01}
                step={0.01}
                value={minLot}
                onChange={(e) => setMinLot(Number(e.target.value))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="maxlot">Max lot</Label>
              <Input
                id="maxlot"
                type="number"
                min={0.01}
                step={0.01}
                value={maxLot}
                onChange={(e) => setMaxLot(Number(e.target.value))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="partial">TP1 close %</Label>
              <Input
                id="partial"
                type="number"
                min={0}
                max={100}
                step={10}
                value={partialClosePct}
                onChange={(e) => setPartialClosePct(Number(e.target.value))}
              />
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? "Running…" : "Run backtest"}
            </Button>
          </div>
        </form>

        {error ? <p className="error">{error}</p> : null}

        {report ? (
          <>
            <p className="muted" style={{ fontFamily: "var(--font-mono)", fontSize: "0.78rem" }}>
              <strong>{report.strategyLabel ?? report.strategy ?? "SMC"}</strong>
              {" · "}
              source <strong>{report.source ?? "—"}</strong>
              {" · "}
              {report.symbol} · {report.timeframe}
              {" · "}
              bars {report.bars ?? "—"}
            </p>
            <MetricsPanel metrics={report.metrics} />
            <EquityChart points={report.metrics.equityCurve ?? []} />
          </>
        ) : (
          <p className="muted">Choose a strategy and run a backtest.</p>
        )}
      </div>

      {report?.trades?.length ? (
        <div className="panel">
          <h2 className="panel-title">
            Trades · {report.symbol} · {report.strategyLabel ?? report.strategy}
          </h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Signal</th>
                  <th>Dir</th>
                  <th>Lots</th>
                  <th>Entry</th>
                  <th>SL</th>
                  <th>TP1</th>
                  <th>TP2</th>
                  <th>Exit</th>
                  <th>Out</th>
                  <th>R</th>
                  <th>PnL</th>
                </tr>
              </thead>
              <tbody>
                {report.trades.slice(-30).map((t, i) => (
                  <tr key={`${String(t.time)}-${i}`}>
                    <td>{String(t.time ?? "—").replace("T", " ").slice(0, 16)}</td>
                    <td className={t.direction === "BUY" ? "buy" : "sell"}>{String(t.direction)}</td>
                    <td>{Number(t.lots ?? 0).toFixed(2)}</td>
                    <td>{Number(t.entry).toFixed(d)}</td>
                    <td>{Number(t.sl ?? 0).toFixed(d)}</td>
                    <td>{Number(t.tp1 ?? t.tp ?? 0).toFixed(d)}</td>
                    <td>{Number(t.tp2 ?? 0).toFixed(d)}</td>
                    <td>{Number(t.exit ?? 0).toFixed(d)}</td>
                    <td>{String(t.outcome)}</td>
                    <td>{Number(t.r_multiple).toFixed(2)}</td>
                    <td className={(t.pnl ?? 0) >= 0 ? "buy" : "sell"}>{Number(t.pnl).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </main>
  );
}
