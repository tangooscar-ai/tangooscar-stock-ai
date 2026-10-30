import sqlite3
from datetime import datetime
from pathlib import Path

PRICE_COLUMNS = [
    "symbol", "date", "open", "high", "low", "close",
    "adj_close", "volume", "dividends", "stock_splits",
]


def get_connection(db_path):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def create_tables(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL, high REAL, low REAL, close REAL,
            adj_close REAL, volume REAL,
            dividends REAL, stock_splits REAL,
            PRIMARY KEY (symbol, date)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS fetch_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            fetched_at TEXT,
            rows INTEGER,
            status TEXT,
            note TEXT
        )
        """
    )
    conn.commit()


def save_prices(conn, df):
    data = df[PRICE_COLUMNS]
    clean = data.astype(object).where(data.notnull(), None)
    placeholders = ",".join(["?"] * len(PRICE_COLUMNS))
    sql = (
        "INSERT OR REPLACE INTO prices ("
        + ",".join(PRICE_COLUMNS)
        + ") VALUES ("
        + placeholders
        + ")"
    )
    conn.executemany(sql, clean.values.tolist())
    conn.commit()
    return len(clean)


def log_fetch(conn, symbol, rows, status, note=""):
    conn.execute(
        "INSERT INTO fetch_log (symbol, fetched_at, rows, status, note) "
        "VALUES (?,?,?,?,?)",
        (symbol, datetime.now().isoformat(timespec="seconds"), rows, status, note),
    )
    conn.commit()