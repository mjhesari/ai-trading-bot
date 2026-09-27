"use client";

import { useCallback, useEffect, useState } from "react";
import { DEFAULT_PAIRS } from "@/lib/pairs";
import { getPairs } from "@/services/trading-engine";

export function usePairs() {
  const [pairs, setPairs] = useState<string[]>([...DEFAULT_PAIRS]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getPairs();
      if (data.pairs?.length) setPairs(data.pairs);
    } catch {
      setPairs([...DEFAULT_PAIRS]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { pairs, loading, refresh };
}
