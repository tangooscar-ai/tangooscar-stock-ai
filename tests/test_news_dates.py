from datetime import datetime, timezone

from src.data.news_data import IST, normalise_entry, parse_loose


def test_rbi_style_time_is_read_as_india_time():
    value, date_only = parse_loose("Tue, 03 Nov 2026 17:05:00")
    assert not date_only
    assert value.astimezone(timezone.utc).isoformat() == "2026-11-03T11:35:00+00:00"


def test_sebi_style_date_is_marked_date_only():
    value, date_only = parse_loose("02 Nov, 2026 +0530")
    assert date_only
    assert value.astimezone(timezone.utc).isoformat() == "2026-11-02T18:29:59+00:00"


def test_date_only_item_dated_today_is_not_future():
    now = datetime.now(timezone.utc)
    entry = {
        "title": "SEBI order",
        "link": "https://sebi.example/1",
        "published": now.astimezone(IST).strftime("%d %b, %Y") + " +0530",
    }
    item = normalise_entry(entry, "SEBI", "official", now)
    assert "date_only" in item["flags"]
    assert "future_dated" not in item["flags"]
    assert item["published_at"] == now.isoformat(timespec="seconds")