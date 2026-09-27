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
import { toPairOptions } from "@/lib/pairs";
import { DATA_SOURCES, TIMEFRAMES } from "@/lib/timeframes";

export default function BacktestPage() {
  const { report, loading, error, run } = useBacktest();
  const { source: engineSource, ready } = useEngineSource("yahoo");
  const { pairs } = usePairs();
  const [symbol, setSymbol] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState("1h");
  const [sampleN, setSampleN] = useState(800);
  const [source, setSource] = useState("yahoo");

  useEffect(() => {
    if (ready) setSource(engineSource);
  }, [ready, engineSource]);

  useEffect(() => {
    if (pairs.length && !pairs.includes(symbol)) {
      setSymbol(pairs[0]);
    }
  }, [pairs, symbol]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    await run({ symbol, timeframe, source, sampleN, useSample: false });
  }

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <h1>Backtest</h1>
          <p>
            Pick any pair and timeframe. Default source: <strong>{engineSource}</strong>.
          </p>
        </div>
      </div>

      <div className="panel">
        <form className="form-grid" onSubmit={(e) => void onSubmit(e)}>
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
          <Button type="submit" disabled={loading}>
            {loading ? "Running…" : "Run backtest"}
          </Button>
        </form>

        {error ? <p className="error">{error}</p> : null}

        {report ? (
          <>
            <p className="muted" style={{ fontFamily: "var(--font-mono)", fontSize: "0.78rem" }}>
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
          <p className="muted">Choose a symbol and run a backtest.</p>
        )}
      </div>

      {report?.trades?.length ? (
        <div className="panel">
          <h2 className="panel-title">Trades · {report.symbol}</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Dir</th>
                  <th>Entry</th>
                  <th>Outcome</th>
                  <th>R</th>
                  <th>PnL</th>
                </tr>
              </thead>
              <tbody>
                {report.trades.slice(-20).map((t, i) => (
                  <tr key={`${String(t.time)}-${i}`}>
                    <td>{String(t.time ?? "—")}</td>
                    <td className={t.direction === "BUY" ? "buy" : "sell"}>{String(t.direction)}</td>
                    <td>{Number(t.entry).toFixed(5)}</td>
                    <td>{String(t.outcome)}</td>
                    <td>{Number(t.r_multiple).toFixed(2)}</td>
                    <td>{Number(t.pnl).toFixed(2)}</td>
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
