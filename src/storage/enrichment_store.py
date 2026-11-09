from src.storage.sentiment_store import create_scores_table


def create_enrichment_tables(conn):
    create_scores_table(conn)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS news_enrichment (
            news_id INTEGER PRIMARY KEY,
            events TEXT,
            primary_event TEXT,
            reaction_only INTEGER,
            reliability REAL,
            rules_version TEXT,
            enriched_at TEXT
        )
        """
    )
    conn.execute("DROP VIEW IF EXISTS news_view")
    conn.execute(
        """
        CREATE VIEW news_view AS
        SELECT n.id, n.published_at, n.collected_at, n.tier, n.source, n.title,
               n.symbols, n.duplicate_of,
               COALESCE(n.duplicate_of, n.id) AS story_id,
               e.events, e.primary_event, e.reaction_only, e.reliability,
               s.label, s.score
        FROM news_items n
        LEFT JOIN news_enrichment e ON e.news_id = n.id
        LEFT JOIN news_scores s ON s.news_id = COALESCE(n.duplicate_of, n.id)
        """
    )
    conn.commit()


def get_to_enrich(conn, redo=False):
    sql = (
        "SELECT n.id, n.title, n.tier, n.source FROM news_items n "
        "LEFT JOIN news_enrichment e ON e.news_id = n.id"
    )
    if not redo:
        sql += " WHERE e.news_id IS NULL"
    return conn.execute(sql).fetchall()


def save_enrichment(conn, records):
    conn.executemany(
        "INSERT OR REPLACE INTO news_enrichment VALUES (?,?,?,?,?,?,?)", records
    )
    conn.commit()
    return len(records)