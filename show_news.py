import pandas as pd

from src.storage.database import get_connection
from src.utils.config import load_settings

pd.set_option("display.width", 220)
pd.set_option("display.max_colwidth", 90)

settings = load_settings()
conn = get_connection(settings["database_path"])

items = pd.read_sql_query(
    "SELECT * FROM news_items ORDER BY published_at DESC", conn
)
print("Stored news items:", len(items))

by_feed = pd.read_sql_query(
    "SELECT tier, feed, COUNT(*) AS items, MAX(published_at) AS newest_utc "
    "FROM news_items GROUP BY tier, feed ORDER BY tier, feed",
    conn,
)
print("\nBy source:")
print(by_feed.to_string(index=False))

print("\nData quality:")
print("  duplicate headlines:", int(items["duplicate_of"].notna().sum()))
print("  no publish date    :", int(items["flags"].fillna("").str.contains("no_date").sum()))
print("  future-dated       :", int(items["flags"].fillna("").str.contains("future_dated").sum()))

tagged = items[items["symbols"].fillna("") != ""].copy()
tagged["symbol"] = tagged["symbols"].str.split(",")
print("\nItems mentioning each stock:")
print(tagged.explode("symbol")["symbol"].value_counts().to_string())

mask = items["symbols"].fillna("").str.contains("RELIANCE.NS", regex=False)
print("\nLatest Reliance headlines (times in UTC, duplicates hidden):")
latest = items[mask & items["duplicate_of"].isna()].head(8)
for _, row in latest.iterrows():
    print(f"{str(row['published_at'])[:16]}  [{row['tier']}] {row['source']}")
    print("    " + str(row["title"]))
conn.close()