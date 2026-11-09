from datetime import datetime, timezone


def create_scores_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS news_scores (
            news_id INTEGER NOT NULL,
            model TEXT NOT NULL,
            scored_at TEXT,
            label TEXT,
            p_positive REAL,
            p_negative REAL,
            p_neutral REAL,
            score REAL,
            PRIMARY KEY (news_id, model)
        )
        """
    )
    conn.commit()


def get_unscored(conn, model_name, limit=500, tagged_only=True):
    sql = (
        "SELECT n.id, n.title FROM news_items n "
        "LEFT JOIN news_scores s ON s.news_id = n.id AND s.model = ? "
        "WHERE s.news_id IS NULL AND n.duplicate_of IS NULL"
    )
    if tagged_only:
        sql += " AND n.symbols IS NOT NULL AND n.symbols != ''"
    sql += " ORDER BY n.published_at DESC LIMIT ?"
    return conn.execute(sql, (model_name, limit)).fetchall()


def save_scores(conn, model_name, ids, results):
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = [
        (i, model_name, stamp, r["label"], r["p_positive"],
         r["p_negative"], r["p_neutral"], r["score"])
        for i, r in zip(ids, results)
    ]
    conn.executemany("INSERT OR REPLACE INTO news_scores VALUES (?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    return len(rows)