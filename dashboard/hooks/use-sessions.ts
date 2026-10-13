"use client";

import { useCallback, useEffect, useState } from "react";
import { getSessions } from "@/services/trading-engine";
import type { SessionSnapshot } from "@/types/session";

export function useSessions(pollMs = 30_000) {
  const [sessions, setSessions] = useState<SessionSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const next = await getSessions();
      setSessions(next);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sessions");
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), pollMs);
    return () => window.clearInterval(id);
  }, [pollMs, refresh]);

  return { sessions, error, refresh };
}
