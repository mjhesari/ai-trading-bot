"use client";

import { useCallback, useEffect, useState } from "react";
import { getEngineSettings } from "@/services/trading-engine";

/** Load engine default data source (from Settings). */
export function useEngineSource(fallback = "yahoo") {
  const [source, setSource] = useState(fallback);
  const [ready, setReady] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const s = await getEngineSettings();
      setSource(s.dataSource || fallback);
    } catch {
      setSource(fallback);
    } finally {
      setReady(true);
    }
  }, [fallback]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { source, setSource, ready, refresh };
}
