from datetime import datetime, timedelta, timezone

from src.analysis.news_match import compile_aliases, find_symbols
from src.data.news_data import clean_text, normalise_entry, title_key
from src.storage.database import get_connection
from src.storage.news_store import create_news_table, save_items


def sample_entry(title, link, published=None, source=None):
    entry = {"title": title, "link": link, "summary": "<p>Some  text</p>"}
    if published:
        entry["published_parsed"] = published.utctimetuple()
    if source:
        entry["source"] = {"title": source}
    return entry


def test_clean_text_removes_html_and_extra_spaces():
    assert clean_text("<p>Hello   <b>world</b></p>") == "Hello world"


def test_title_key_ignores_case_and_punctuation():
    assert title_key("Reliance, Q2 Profit UP!") == title_key("reliance q2 profit up")


def test_source_suffix_is_removed():
    now = datetime.now(timezone.utc)
    entry = sample_entry("Reliance profit rises - Economic Times", "https://x.example/1", now, "Economic Times")
    item = normalise_entry(entry, "Feed", "aggregator", now)
    assert item["title"] == "Reliance profit rises"


def test_future_and_missing_dates_are_flagged():
    now = datetime.now(timezone.utc)
    future = sample_entry("Headline", "https://x.example/2", now + timedelta(days=1))
    undated = sample_entry("Headline two", "https://x.example/3")
    assert "future_dated" in normalise_entry(future, "Feed", "major", now)["flags"]
    assert "no_date" in normalise_entry(undated, "Feed", "major", now)["flags"]


def test_find_symbols():
    companies = {
        "RELIANCE.NS": ["Reliance Industries", "RIL"],
        "LT.NS": ["Larsen & Toubro", "L&T"],
        "ITC.NS": ["ITC"],
    }
    compiled = compile_aliases(companies)
    assert find_symbols("Reliance Industries and L&T win orders", compiled) == ["LT.NS", "RELIANCE.NS"]
    assert find_symbols("ITC Ltd posts results", compiled) == ["ITC.NS"]
    assert find_symbols("The ritual of itching", compiled) == []
    assert find_symbols("ril is a nickname", compiled) == []


def test_save_items_flags_duplicates_and_merges_symbols(tmp_path):
    conn = get_connection(tmp_path / "test.db")
    create_news_table(conn)
    now = datetime.now(timezone.utc)
    first = normalise_entry(
        sample_entry("Reliance wins order", "https://a.example/1", now, "Site A"),
        "Feed A", "major", now,
    )
    second = normalise_entry(
        sample_entry("Reliance wins order!", "https://b.example/2", now, "Site B"),
        "Feed B", "major", now,
    )
    first["symbols"] = "RELIANCE.NS"
    second["symbols"] = "RELIANCE.NS"

    new, duplicates, merged = save_items(conn, [first, second])
    assert (new, duplicates) == (2, 1)

    again = dict(first)
    again["symbols"] = "TCS.NS"
    new2, duplicates2, merged2 = save_items(conn, [again])
    assert new2 == 0 and merged2 == 1

    stored = conn.execute(
        "SELECT symbols FROM news_items WHERE url_hash = ?", (first["url_hash"],)
    ).fetchone()[0]
    assert stored == "RELIANCE.NS,TCS.NS"

    rows = conn.execute("SELECT duplicate_of FROM news_items ORDER BY id").fetchall()
    assert rows[0][0] is None and rows[1][0] == 1
    conn.close()