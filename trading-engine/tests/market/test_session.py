from datetime import datetime, timezone

from app.market.session import hour_in_range, is_london_session, session_snapshot


def test_overnight_hour_range():
    assert hour_in_range(22, 21, 6)
    assert hour_in_range(3, 21, 6)
    assert not hour_in_range(12, 21, 6)


def test_tehran_converts_london_hours():
    now = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
    snap = session_snapshot("Asia/Tehran", now=now)
    london = next(s for s in snap["sessions"] if s["id"] == "london")
    assert london["utcStart"] == "07:00"
    assert london["localStart"] == "10:30"
    assert london["localEnd"] == "19:30"
    assert london["active"] is True
    assert snap["offset"] == "+03:30"
    assert snap["nowLocal"] == "13:30"


def test_london_session_uses_utc_not_display_zone():
    ts = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
    assert is_london_session(ts) is True
