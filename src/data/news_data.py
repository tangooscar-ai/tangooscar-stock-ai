import calendar
import hashlib
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote_plus

import feedparser
import requests
import yaml

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; tangooscar-research/0.1; personal research)"
}


def load_sources():
    path = Path("config") / "news_sources.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def google_news_url(query, days=7):
    q = quote_plus('"' + query + '" when:' + str(days) + "d")
    return "https://news.google.com/rss/search?q=" + q + "&hl=en-IN&gl=IN&ceid=IN:en"


def clean_text(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def title_key(title):
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def make_hash(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:20]


def parse_time(entry):
    stamp = entry.get("published_parsed") or entry.get("updated_parsed")
    if not stamp:
        return None
    return datetime.fromtimestamp(calendar.timegm(stamp), tz=timezone.utc)


def fetch_feed(url, timeout=20):
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    parsed = feedparser.parse(response.content)
    if not parsed.entries and parsed.bozo:
        raise ValueError("unreadable feed")
    return parsed.entries


IST = timezone(timedelta(hours=5, minutes=30))


def parse_loose(text):
    text = (text or "").strip()
    if not text:
        return None, False
    try:
        return datetime.strptime(text, "%a, %d %b %Y %H:%M:%S").replace(tzinfo=IST), False
    except ValueError:
        pass
    cleaned = re.sub(r"\s*[+-]\d{4}$", "", text)
    for fmt in ("%d %b, %Y", "%d %b %Y"):
        try:
            day = datetime.strptime(cleaned, fmt)
            return day.replace(hour=23, minute=59, second=59, tzinfo=IST), True
        except ValueError:
            pass
    return None, False


def normalise_entry(entry, feed_name, tier, collected_at):
    source = (entry.get("source") or {}).get("title") or feed_name
    title = clean_text(entry.get("title", ""))
    if source and title.endswith(" - " + source):
        title = title[: -len(source) - 3].strip()
    url = (entry.get("link") or "").strip()
    if not title or not url:
        return None

    published = parse_time(entry)
    date_only = False
    if published is None:
        published, date_only = parse_loose(entry.get("published"))
        if published is not None:
            published = published.astimezone(timezone.utc)

    flags = []
    if published is None:
        flags.append("no_date")
    else:
        if date_only:
            flags.append("date_only")
            published = min(published, collected_at)
        if published > collected_at + timedelta(minutes=5):
            flags.append("future_dated")

    return {
        "title": title,
        "summary": clean_text(entry.get("summary", ""))[:500],
        "source": source,
        "feed": feed_name,
        "tier": tier,
        "url": url,
        "url_hash": make_hash(url),
        "title_key": title_key(title),
        "published_at": published.isoformat(timespec="seconds") if published else None,
        "collected_at": collected_at.isoformat(timespec="seconds"),
        "flags": ",".join(flags),
    }