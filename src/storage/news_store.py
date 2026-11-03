COLUMNS = [
    "url_hash", "title", "summary", "source", "feed", "tier", "url",
    "title_key", "published_at", "collected_at", "symbols", "flags",
]


def create_news_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS news_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_hash TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            source TEXT,
            feed TEXT,
            tier TEXT,
            url TEXT,
            title_key TEXT,
            published_at TEXT,
            collected_at TEXT,
            symbols TEXT,
            flags TEXT,
            duplicate_of INTEGER
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_news_title_key ON news_items (title_key)"
    )
    conn.commit()


def save_items(conn, items):
    new, duplicates, merged = 0, 0, 0
    for item in items:
        new_symbols = set(filter(None, (item.get("symbols") or "").split(",")))
        row = conn.execute(
            "SELECT id, symbols FROM news_items WHERE url_hash = ?",
            (item["url_hash"],),
        ).fetchone()
        if row:
            old = set(filter(None, (row[1] or "").split(",")))
            combined = old | new_symbols
            if combined != old:
                conn.execute(
                    "UPDATE news_items SET symbols = ? WHERE id = ?",
                    (",".join(sorted(combined)), row[0]),
                )
                merged += 1
            continue

        first = conn.execute(
            "SELECT id FROM news_items WHERE title_key = ? ORDER BY id LIMIT 1",
            (item["title_key"],),
        ).fetchone()
        duplicate_of = first[0] if first else None

        values = [item.get(c) for c in COLUMNS] + [duplicate_of]
        conn.execute(
            "INSERT INTO news_items ("
            + ",".join(COLUMNS)
            + ",duplicate_of) VALUES ("
            + ",".join(["?"] * (len(COLUMNS) + 1))
            + ")",
            values,
        )
        new += 1
        if duplicate_of:
            duplicates += 1
    conn.commit()
    return new, duplicates, merged