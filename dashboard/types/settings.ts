import type { AllowedTimezone, SessionSnapshot } from "@/types/session";

export type EngineSettings = {
  dataSource: string;
  twelveDataApiKeySet: boolean;
  twelveDataApiKeyMasked: string | null;
  allowedSources: string[];
  sessionTimezone: string;
  sessionTimezoneLabel: string;
  sessionOffset: string;
  allowedTimezones: AllowedTimezone[];
  sessions: SessionSnapshot;
};

export type SettingsUpdate = {
  dataSource?: string;
  twelveDataApiKey?: string;
  clearTwelveDataApiKey?: boolean;
  sessionTimezone?: string;
};

export type SourceTestResult = {
  ok: boolean;
  source: string;
  message?: string | null;
  bars: number;
  symbol: string;
  timeframe: string;
  lastClose?: number | null;
};
