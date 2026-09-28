"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getMarket, getPairs, getQuote } from "@/services/trading-engine";
import { useEngineSource } from "@/hooks/use-engine-source";
import { applyLiveTick, mergeHistoryWithLive, roundPrice } from "@/lib/live-candle";
import type { Candle } from "@/types/market";

/** Full OHLC sync — keeps closed history correct. */
function historyPollMs(timeframe: string): number {
  switch (timeframe) {
    case "1m":
      return 20_000;
    case "5m":
      return 25_000;
    case "15m":
    case "30m":
      return 35_000;
    default:
      return 45_000;
  }
}

/** Last candle must refresh every 1 second while Live is on. */
const QUOTE_POLL_MS = 1_000;

export function useChartMarket(initialSymbol = "EURUSD", initialTf = "1h") {
  const { source, setSource, ready } = useEngineSource("yahoo");
  const [symbol, setSymbol] = useState(initialSymbol);
  const [timeframe, setTimeframe] = useState(initialTf);
  const [pairs, setPairs] = useState<string[]>([initialSymbol]);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [dataSource, setDataSource] = useState<string>("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [live, setLive] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<number | null>(null);
  const [livePulse, setLivePulse] = useState(false);
  const [livePrice, setLivePrice] = useState<number | null>(null);
  const [m1Count, setM1Count] = useState<number | null>(null);
  const fetchGen = useRef(0);
  const quoteBusy = useRef(false);
  const timeframeRef = useRef(timeframe);
  const symbolRef = useRef(symbol);
  const candlesRef = useRef<Candle[]>([]);
  const lastQuoteRef = useRef<number | null>(null);
  timeframeRef.current = timeframe;
  symbolRef.current = symbol;
  candlesRef.current = candles;

  const loadPairs = useCallback(async () => {
    try {
      const data = await getPairs();
      if (data.pairs?.length) setPairs(data.pairs);
    } catch {
      // keep defaults
    }
  }, []);

  const refresh = useCallback(
    async (opts?: { silent?: boolean }) => {
      if (!ready) return;
      const silent = opts?.silent ?? false;
      const gen = ++fetchGen.current;
      if (!silent) {
        setLoading(true);
        setError(null);
      }
      try {
        const data = await getMarket(symbol, {
          timeframe,
          source,
          count: 800,
          live: true,
        });
        if (gen !== fetchGen.current) return;
        setCandles((prev) =>
          silent ? mergeHistoryWithLive(data.candles, prev, timeframe) : data.candles,
        );
        setDataSource(data.source);
        setMessage(data.message ?? null);
        if (data.livePrice != null) {
          const p = roundPrice(data.livePrice, symbol);
          setLivePrice(p);
          lastQuoteRef.current = p;
        }
        setLastUpdated(Date.now());
        setLivePulse(true);
        window.setTimeout(() => setLivePulse(false), 350);
        setError(null);
      } catch (e) {
        if (gen !== fetchGen.current) return;
        const msg = e instanceof Error ? e.message : "Failed to load market";
        setError(msg);
      } finally {
        if (gen === fetchGen.current && !silent) setLoading(false);
      }
    },
    [symbol, timeframe, source, ready],
  );

  const tickQuote = useCallback(async () => {
    if (!ready || quoteBusy.current) return;
    if (!candlesRef.current.length) return;
    quoteBusy.current = true;
    const sym = symbolRef.current;
    const tf = timeframeRef.current;
    try {
      const quoteSource = source === "sample" ? "sample" : "yahoo";
      const quote = await getQuote(sym, {
        source: quoteSource,
        timeframe: tf,
      });
      const price = roundPrice(quote.price, sym);
      lastQuoteRef.current = price;
      setLivePrice(price);
      if (typeof quote.m1Count === "number") setM1Count(quote.m1Count);

      const forming = quote.forming ?? {
        time: new Date(quote.barOpenMs ?? quote.ts).toISOString(),
        open: price,
        high: price,
        low: price,
        close: price,
        volume: 0,
      };
      forming.close = price;
      forming.high = Math.max(forming.high, price);
      forming.low = Math.min(forming.low, price);

      setCandles((prev) => applyLiveTick(prev, forming, tf, sym, quote.ts));
      setLastUpdated(Date.now());
      setLivePulse(true);
      window.setTimeout(() => setLivePulse(false), 280);
      setError(null);
    } catch (e) {
      // If quote fails, still micro-tick around last known price so the candle keeps moving.
      const fallback = lastQuoteRef.current;
      if (fallback != null && candlesRef.current.length) {
        const last = candlesRef.current[candlesRef.current.length - 1];
        setCandles((prev) =>
          applyLiveTick(
            prev,
            {
              time: last.time,
              open: last.open,
              high: last.high,
              low: last.low,
              close: fallback,
              volume: last.volume,
            },
            tf,
            sym,
          ),
        );
        setLastUpdated(Date.now());
        setLivePulse(true);
        window.setTimeout(() => setLivePulse(false), 280);
      } else {
        const msg = e instanceof Error ? e.message : "Live quote failed";
        setError(msg);
      }
    } finally {
      quoteBusy.current = false;
    }
  }, [ready, source]);

  useEffect(() => {
    void loadPairs();
  }, [loadPairs]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (!live || !ready) return;
    const histId = window.setInterval(() => {
      void refresh({ silent: true });
    }, historyPollMs(timeframe));
    const quoteId = window.setInterval(() => {
      void tickQuote();
    }, QUOTE_POLL_MS);
    const kick = window.setTimeout(() => void tickQuote(), 300);
    return () => {
      window.clearInterval(histId);
      window.clearInterval(quoteId);
      window.clearTimeout(kick);
    };
  }, [live, ready, timeframe, refresh, tickQuote]);

  return {
    symbol,
    setSymbol,
    timeframe,
    setTimeframe,
    source,
    setSource,
    pairs,
    candles,
    dataSource,
    message,
    loading,
    error,
    refresh,
    live,
    setLive,
    lastUpdated,
    livePulse,
    livePrice,
    m1Count,
    pollMs: QUOTE_POLL_MS,
  };
}
