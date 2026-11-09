from datetime import datetime, timezone

from src.analysis.sentiment import probs_to_result
from src.data.news_data import normalise_entry
from src.storage.database import get_connection
from src.storage.news_store import create_news_table, save_items
from src.storage.sentiment_store import create_scores_table, get_unscored, save_scores


def test_probs_to_result_picks_top_label_and_score():
    result = probs_to_result({"positive": 0.7, "negative": 0.1, "neutral": 0.2})
    assert result["label"] == "positive"
    assert abs(result["score"] - 0.6) < 1e-9


def test_scores_round_trip(tmp_path):
    conn = get_connection(tmp_path / "t.db")
    create_news_table(conn)
    create_scores_table(conn)
    now = datetime.now(timezone.utc)
    entry = {"title": "Reliance profit rises", "link": "https://x.example/1", "summary": ""}
    item = normalise_entry(entry, "Feed", "major", now)
    item["symbols"] = "RELIANCE.NS"
    save_items(conn, [item])

    rows = get_unscored(conn, "test-model")
    assert len(rows) == 1

    result = probs_to_result({"positive": 0.1, "negative": 0.8, "neutral": 0.1})
    save_scores(conn, "test-model", [rows[0][0]], [result])
    assert get_unscored(conn, "test-model") == []
    conn.close()