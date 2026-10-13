export type SessionWindow = {
  id: string;
  label: string;
  active: boolean;
  utcStart: string;
  utcEnd: string;
  localStart: string;
  localEnd: string;
};

export type AllowedTimezone = {
  id: string;
  label: string;
  offset: string;
};

export type SessionSnapshot = {
  timezone: string;
  timezoneLabel: string;
  offset: string;
  nowUtc: string;
  nowLocal: string;
  nowIso: string;
  active: string[];
  overlap: boolean;
  killzone: boolean;
  sessions: SessionWindow[];
  killzones: SessionWindow[];
  allowedTimezones: AllowedTimezone[];
};
