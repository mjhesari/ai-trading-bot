export type EngineSettings = {
  dataSource: string;
  twelveDataApiKeySet: boolean;
  twelveDataApiKeyMasked: string | null;
  allowedSources: string[];
};

export type SettingsUpdate = {
  dataSource?: string;
  twelveDataApiKey?: string;
  clearTwelveDataApiKey?: boolean;
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
