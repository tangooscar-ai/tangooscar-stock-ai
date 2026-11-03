import feedparser
import requests

from src.data.news_data import HEADERS

URLS = [
    "https://rbi.org.in/pressreleases_rss.xml",
    "https://www.sebi.gov.in/sebirss.xml",
]

for url in URLS:
    response = requests.get(url, headers=HEADERS, timeout=20)
    entry = feedparser.parse(response.content).entries[0]
    print(url)
    print("  fields:", sorted(entry.keys()))
    for key in entry.keys():
        low = key.lower()
        if "date" in low or "publish" in low or "updated" in low:
            print("  ", key, "=", str(entry[key])[:70])