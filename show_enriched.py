import pandas as pd

from src.storage.database import get_connection
from src.utils.config import load_settings

pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 90)

settings = load_settings()
conn = get_connection(settings["database_path"])
data = pd.read_sql_query("SELECT * FROM news_view", conn)
stories = data[data["duplicate_of"].isna()]

print(f"Items: {len(data)}   Unique stories: {len(stories)}")
print("\nBy primary event type (unique stories):")
print(stories["primary_event"].value_counts().to_string())
print("\nPrice-move-only stories:", int(stories["reaction_only"].fillna(0).sum()))

print("\nAverage source reliability by tier (heuristic, editable in config):")
print(data.groupby("tier")["reliability"].mean().round(2).to_string())

outlets = data.groupby("story_id")["source"].nunique()
counts = outlets.clip(upper=3).value_counts().sort_index()
print("\nStories by number of different outlets (same-wire copies not yet separated):")
for n, c in counts.items():
    print(f"  {n}{'+' if n == 3 else ''} outlet(s): {c} stories")

mask = stories["symbols"].fillna("").str.contains("RELIANCE.NS", regex=False)
print("\nLatest Reliance stories (times in UTC):")
latest = stories[mask].sort_values("published_at", ascending=False).head(8)
for _, r in latest.iterrows():
    score = "n/a" if pd.isna(r["score"]) else f"{r['score']:+.2f}"
    print(f"{str(r['published_at'])[:16]}  {str(r['primary_event']):<16} "
          f"rel {r['reliability']:.2f}  sent {score}")
    print("    " + str(r["title"]))
conn.close()