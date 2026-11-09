import pandas as pd

from src.storage.database import get_connection
from src.utils.config import load_settings

pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 100)

settings = load_settings()
conn = get_connection(settings["database_path"])

data = pd.read_sql_query(
    "SELECT n.id, n.published_at, n.tier, n.source, n.title, n.symbols, "
    "s.label, s.score FROM news_scores s JOIN news_items n ON n.id = s.news_id "
    "ORDER BY n.published_at DESC",
    conn,
)
print("Scored headlines:", len(data))
print("\nBy label:")
print(data["label"].value_counts().to_string())

tagged = data.copy()
tagged["symbol"] = tagged["symbols"].str.split(",")
per_symbol = (
    tagged.explode("symbol")
    .groupby("symbol")["score"]
    .agg(["count", "mean"])
    .round(2)
    .sort_values("mean")
)
print("\nAverage sentiment per stock (-1 negative to +1 positive):")
print(per_symbol.to_string())

print("\nMost positive headlines (model reading, not verified fact):")
for _, r in data.nlargest(5, "score").iterrows():
    print(f"  {r['score']:+.2f} [{r['tier']}] {r['title']}")
print("\nMost negative headlines:")
for _, r in data.nsmallest(5, "score").iterrows():
    print(f"  {r['score']:+.2f} [{r['tier']}] {r['title']}")
conn.close()