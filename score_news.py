import sys
import time

from src.analysis.sentiment import MODEL_NAME, load_finbert, score_texts
from src.storage.database import get_connection
from src.storage.sentiment_store import create_scores_table, get_unscored, save_scores
from src.utils.config import load_settings

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 500

settings = load_settings()
conn = get_connection(settings["database_path"])
create_scores_table(conn)

rows = get_unscored(conn, MODEL_NAME, limit=limit)
print(f"Headlines to score: {len(rows)}")
if rows:
    tokenizer, model = load_finbert()
    ids = [r[0] for r in rows]
    texts = [r[1] for r in rows]
    started = time.time()
    results = score_texts(texts, tokenizer, model)
    save_scores(conn, MODEL_NAME, ids, results)
    print(f"Scored {len(results)} headlines in {time.time() - started:.0f} s")
conn.close()