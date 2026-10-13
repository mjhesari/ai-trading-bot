"""FX session clock. Canonical hours are UTC; display converts to a chosen IANA zone."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Winter-style FX hours used by most desks (UTC). Overnight windows wrap midnight.
SESSIONS: tuple[dict[str, object], ...] = (
    {"id": "sydney", "label": "Sydney", "utc_start": 21, "utc_end": 6},
    {"id": "tokyo", "label": "Tokyo", "utc_start": 0, "utc_end": 9},
    {"id": "london", "label": "London", "utc_start": 7, "utc_end": 16},
    {"id": "new_york", "label": "New York", "utc_start": 12, "utc_end": 21},
)

KILLZONES: tuple[dict[str, object], ...] = (
    {"id": "london_open", "label": "London Open", "utc_start": 7, "utc_end": 10},
    {"id": "ny_open", "label": "NY Open", "utc_start": 12, "utc_end": 15},
)

# Curated desk locations for the Settings dropdown.
DISPLAY_TIMEZONES: tuple[tuple[str, str], ...] = (
    ("UTC", "UTC"),
    ("Asia/Tehran", "Tehran"),
    ("Asia/Dubai", "Dubai"),
    ("Europe/Istanbul", "Istanbul"),
    ("Europe/London", "London"),
    ("Europe/Berlin", "Frankfurt"),
    ("Europe/Moscow", "Moscow"),
    ("America/New_York", "New York"),
    ("America/Chicago", "Chicago"),
    ("America/Los_Angeles", "Los Angeles"),
    ("Asia/Tokyo", "Tokyo"),
    ("Asia/Singapore", "Singapore"),
    ("Asia/Hong_Kong", "Hong Kong"),
    ("Australia/Sydney", "Sydney"),
)

DEFAULT_SESSION_TIMEZONE = "UTC"


@dataclass(frozen=True)
class SessionWindow:
    id: str
    label: str
    utc_start: int
    utc_end: int


def _windows(rows: tuple[dict[str, object], ...]) -> list[SessionWindow]:
    return [
        SessionWindow(
            id=str(row["id"]),
            label=str(row["label"]),
            utc_start=int(row["utc_start"]),
            utc_end=int(row["utc_end"]),
        )
        for row in rows
    ]


def hour_in_range(hour: int, start: int, end: int) -> bool:
    hour = hour % 24
    if start == end:
        return True
    if start < end:
        return start <= hour < end
    return hour >= start or hour < end


def in_ict_killzone(ts: datetime) -> bool:
    """London Open (07–10 UTC) or NY Open (12–15 UTC)."""
    hour = _aware(ts).astimezone(timezone.utc).hour
    return any(hour_in_range(hour, int(z["utc_start"]), int(z["utc_end"])) for z in KILLZONES)


def resolve_timezone(name: str | None) -> ZoneInfo:
    key = (name or DEFAULT_SESSION_TIMEZONE).strip() or DEFAULT_SESSION_TIMEZONE
    if key.upper() == "UTC":
        return ZoneInfo("UTC")
    try:
        return ZoneInfo(key)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone: {name}") from exc


def allowed_timezones(now: datetime | None = None) -> list[dict[str, str]]:
    now_utc = _aware(now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    out: list[dict[str, str]] = []
    for tz_id, label in DISPLAY_TIMEZONES:
        tz = resolve_timezone(tz_id)
        out.append(
            {
                "id": tz_id,
                "label": label,
                "offset": _offset_label(now_utc, tz),
            }
        )
    return out


def _aware(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts


def _offset_label(now_utc: datetime, tz: ZoneInfo) -> str:
    local = now_utc.astimezone(tz)
    delta = local.utcoffset() or timedelta(0)
    total = int(delta.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, rem = divmod(total, 3600)
    minutes = rem // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def _fmt_hour(hour: int) -> str:
    return f"{hour % 24:02d}:00"


def _local_clock(now_utc: datetime, utc_hour: int, tz: ZoneInfo) -> str:
    dt = now_utc.replace(hour=utc_hour % 24, minute=0, second=0, microsecond=0)
    return dt.astimezone(tz).strftime("%H:%M")


def _window_payload(window: SessionWindow, now_utc: datetime, tz: ZoneInfo) -> dict:
    utc_hour = now_utc.hour
    active = hour_in_range(utc_hour, window.utc_start, window.utc_end)
    return {
        "id": window.id,
        "label": window.label,
        "active": active,
        "utcStart": _fmt_hour(window.utc_start),
        "utcEnd": _fmt_hour(window.utc_end),
        "localStart": _local_clock(now_utc, window.utc_start, tz),
        "localEnd": _local_clock(now_utc, window.utc_end, tz),
    }


def is_london_session(ts: datetime) -> bool:
    hour = _aware(ts).astimezone(timezone.utc).hour
    return hour_in_range(hour, 7, 16)


def is_new_york_session(ts: datetime) -> bool:
    hour = _aware(ts).astimezone(timezone.utc).hour
    return hour_in_range(hour, 12, 21)


def is_killzone(ts: datetime) -> bool:
    hour = _aware(ts).astimezone(timezone.utc).hour
    return any(hour_in_range(hour, int(z["utc_start"]), int(z["utc_end"])) for z in KILLZONES)


_TF_HOURS = {"1m": 0, "5m": 0, "15m": 0, "30m": 0, "1h": 1, "2h": 2, "4h": 4}


def bar_in_killzone(ts: datetime, timeframe: str = "1h") -> bool:
    """True if this candle overlaps London/NY open killzones. Daily+ always allowed."""
    if timeframe in {"1d", "1w"}:
        return True
    span = _TF_HOURS.get(timeframe, 1)
    if span <= 1:
        return is_killzone(ts)
    start = _aware(ts).astimezone(timezone.utc)
    for h in range(max(span, 1)):
        if is_killzone(start + timedelta(hours=h)):
            return True
    return False


def session_snapshot(timezone_name: str | None, now: datetime | None = None) -> dict:
    tz_name = (timezone_name or DEFAULT_SESSION_TIMEZONE).strip() or DEFAULT_SESSION_TIMEZONE
    tz = resolve_timezone(tz_name)
    now_utc = _aware(now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    local = now_utc.astimezone(tz)
    sessions = [_window_payload(w, now_utc, tz) for w in _windows(SESSIONS)]
    killzones = [_window_payload(w, now_utc, tz) for w in _windows(KILLZONES)]
    active_ids = [s["id"] for s in sessions if s["active"]]
    label = next((name for tz_id, name in DISPLAY_TIMEZONES if tz_id == tz_name), tz_name)
    return {
        "timezone": tz_name,
        "timezoneLabel": label,
        "offset": _offset_label(now_utc, tz),
        "nowUtc": now_utc.strftime("%H:%M"),
        "nowLocal": local.strftime("%H:%M"),
        "nowIso": now_utc.isoformat(),
        "active": active_ids,
        "overlap": len(active_ids) >= 2,
        "killzone": any(k["active"] for k in killzones),
        "sessions": sessions,
        "killzones": killzones,
        "allowedTimezones": allowed_timezones(now_utc),
    }
