from pathlib import Path

import pandas as pd

from src.storage.database import get_connection
from src.utils.config import load_settings

settings = load_settings()
db_path = Path(settings["database_path"])

if not db_path.exists():
    print("Database not found. Run collect_data.py first.")
else:
    conn = get_connection(db_path)

    summary = pd.read_sql_query(
        "SELECT symbol, COUNT(*) AS n_rows, MIN(date) AS first_date, "
        "MAX(date) AS last_date FROM prices GROUP BY symbol ORDER BY symbol",
        conn,
    )
    print(summary.to_string(index=False))

    print("\nLatest 5 days for RELIANCE.NS:")
    sample = pd.read_sql_query(
        "SELECT date, open, high, low, close, adj_close, volume FROM prices "
        "WHERE symbol = 'RELIANCE.NS' ORDER BY date DESC LIMIT 5",
        conn,
    )
    print(sample.to_string(index=False))

    log = pd.read_sql_query(
        "SELECT symbol, status, note FROM fetch_log "
        "WHERE id IN (SELECT MAX(id) FROM fetch_log GROUP BY symbol) "
        "AND note != '' ORDER BY symbol",
        conn,
    )
    if not log.empty:
        print("\nQuality notes:")
        print(log.to_string(index=False))