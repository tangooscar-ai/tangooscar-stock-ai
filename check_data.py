from pathlib import Path

import pandas as pd

from src.storage.database import get_connection
from src.utils.config import load_settings

settings = load_settings()
db_path = Path(settings["database_path"])
conn = get_connection(db_path)

summary = pd.read_sql_query(
    "SELECT symbol, COUNT(*) AS n_rows, MIN(date) AS first_date, "
    "MAX(date) AS last_date FROM prices GROUP BY symbol ORDER BY symbol",
    conn,
)
print(summary.to_string(index=False))

have = dict(zip(summary["symbol"], summary["n_rows"]))
stocks_ok = all(have.get(s, 0) >= 600 for s in settings["stocks"])
missing_idx = [i for i in settings["indices"] if i not in have]
if missing_idx:
    print("\nIndices not available (not blocking):", missing_idx)

size_mb = db_path.stat().st_size / (1024 * 1024)
print(f"\nDatabase size: {size_mb:.1f} MB")
print("\nPHASE 3 COMPLETE" if stocks_ok else "\nSOME STOCKS ARE MISSING DATA - run collect_data.py again")
conn.close()