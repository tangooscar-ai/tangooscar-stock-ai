import time
from datetime import datetime, timezone

from src.analysis.news_match import compile_aliases, find_symbols
from src.data.news_data import fetch_feed, google_news_url, load_sources, normalise_entry
from src.storage.database import get_connection
from src.storage.news_store import create_news_table, save_items
from src.utils.config import load_settings


def main():
    settings = load_settings()
    sources = load_sources()
    compiled = compile_aliases(sources["companies"])
    conn = get_connection(settings["database_path"])
    create_news_table(conn)

    jobs = [(f["name"], f["url"], f["tier"]) for f in sources["feeds"]]
    for symbol, names in sources["companies"].items():
        jobs.append(("Google News: " + names[0], google_news_url(names[0]), "aggregator"))

    total_new = 0
    failed = []
    for name, url, tier in jobs:
        print(name + " ...", end=" ", flush=True)
        try:
            entries = fetch_feed(url)
        except Exception as err:
            print("FAILED (" + str(err)[:80] + ")")
            failed.append(name)
            continue

        collected_at = datetime.now(timezone.utc)
        items = []
        for entry in entries:
            item = normalise_entry(entry, name, tier, collected_at)
            if item is None:
                continue
            text = item["title"] + " " + item["summary"]
            item["symbols"] = ",".join(find_symbols(text, compiled))
            items.append(item)

        new, duplicates, merged = save_items(conn, items)
        print(f"{len(items)} items, {new} new, {duplicates} duplicates")
        total_new += new
        time.sleep(1)

    conn.close()
    print(f"\nFeeds OK: {len(jobs) - len(failed)} of {len(jobs)}   New items: {total_new}")
    if failed:
        print("Failed feeds:")
        for name in failed:
            print("  -", name)


main()