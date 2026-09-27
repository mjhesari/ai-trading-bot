"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FieldSelect } from "@/components/ui/field-select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ENGINE_URL } from "@/lib/api";
import { DATA_SOURCES } from "@/lib/timeframes";
import {
  getEngineSettings,
  testEngineSource,
  updateEngineSettings,
} from "@/services/trading-engine";
import type { EngineSettings, SourceTestResult } from "@/types/settings";

export default function SettingsPage() {
  const [settings, setSettings] = useState<EngineSettings | null>(null);
  const [dataSource, setDataSource] = useState("yahoo");
  const [apiKey, setApiKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [okMsg, setOkMsg] = useState<string | null>(null);
  const [test, setTest] = useState<SourceTestResult | null>(null);

  const refresh = useCallback(async () => {
    const s = await getEngineSettings();
    setSettings(s);
    setDataSource(s.dataSource);
  }, []);

  useEffect(() => {
    refresh().catch((e) => setError(e instanceof Error ? e.message : "Failed to load settings"));
  }, [refresh]);

  async function onSave(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setOkMsg(null);
    setTest(null);
    try {
      const body: { dataSource: string; twelveDataApiKey?: string } = { dataSource };
      if (apiKey.trim()) body.twelveDataApiKey = apiKey.trim();
      const next = await updateEngineSettings(body);
      setSettings(next);
      setDataSource(next.dataSource);
      setApiKey("");
      setOkMsg(`Saved. Active source: ${next.dataSource}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function onTest() {
    setBusy(true);
    setError(null);
    setTest(null);
    try {
      const result = await testEngineSource("EURUSD", "1h");
      setTest(result);
      setOkMsg(`Test OK · ${result.source} · ${result.bars} bars`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Test failed");
    } finally {
      setBusy(false);
    }
  }

  async function onClearKey() {
    setBusy(true);
    setError(null);
    try {
      const next = await updateEngineSettings({ clearTwelveDataApiKey: true });
      setSettings(next);
      setOkMsg("Twelve Data API key cleared");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Clear failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <h1>Settings</h1>
          <p>Switch market source and manage Twelve Data API key.</p>
        </div>
      </div>

      <div className="grid-stats">
        <div className="stat-card">
          <div className="label">Engine</div>
          <div className="value" style={{ fontSize: "0.85rem", wordBreak: "break-all" }}>
            {ENGINE_URL.replace(/^https?:\/\//, "")}
          </div>
          <div className="hint">NEXT_PUBLIC_ENGINE_URL</div>
        </div>
        <div className="stat-card">
          <div className="label">Active source</div>
          <div className="value" style={{ fontSize: "1.1rem" }}>
            {settings?.dataSource ?? "…"}
          </div>
          <div className="hint">charts / signals / backtest</div>
        </div>
        <div className="stat-card">
          <div className="label">Twelve Data</div>
          <div className="value">
            <Badge variant={settings?.twelveDataApiKeySet ? "success" : "secondary"}>
              {settings?.twelveDataApiKeySet ? "KEY" : "OFF"}
            </Badge>
          </div>
          <div className="hint">{settings?.twelveDataApiKeyMasked ?? "no key"}</div>
        </div>
      </div>

      {error ? <p className="error">{error}</p> : null}
      {okMsg ? <p className="muted">{okMsg}</p> : null}

      <div className="panel">
        <h2 className="panel-title">Market data source</h2>
        <p className="muted" style={{ marginTop: 0, lineHeight: 1.5 }}>
          Free key from{" "}
          <a href="https://twelvedata.com" target="_blank" rel="noreferrer" className="text-primary underline">
            twelvedata.com
          </a>
          . Choose <strong>Twelve Data</strong>, paste key, Save, then Test.
        </p>

        <form className="form-grid" onSubmit={(e) => void onSave(e)}>
          <FieldSelect
            label="Data source"
            value={dataSource}
            onValueChange={setDataSource}
            options={DATA_SOURCES.map((s) => ({ value: s.value, label: s.label }))}
          />
          <div className="grid gap-2 md:col-span-2">
            <Label htmlFor="td-key">Twelve Data API key</Label>
            <Input
              id="td-key"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={
                settings?.twelveDataApiKeySet
                  ? `saved (${settings.twelveDataApiKeyMasked}) — paste to replace`
                  : "paste API key"
              }
              autoComplete="off"
            />
          </div>
          <Button type="submit" disabled={busy}>
            {busy ? "Saving…" : "Save"}
          </Button>
          <Button type="button" variant="outline" disabled={busy} onClick={() => void onTest()}>
            Test source
          </Button>
          <Button type="button" variant="ghost" disabled={busy} onClick={() => void onClearKey()}>
            Clear key
          </Button>
        </form>

        {test ? (
          <p className="muted font-mono text-xs mt-3">
            test → {test.source} · {test.symbol} {test.timeframe} · bars {test.bars}
            {test.lastClose != null ? ` · last ${test.lastClose}` : ""}
          </p>
        ) : null}
      </div>
    </main>
  );
}
