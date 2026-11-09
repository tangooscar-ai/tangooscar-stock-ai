from datetime import datetime, timezone

from src.analysis.events import classify_event, compile_event_rules, load_rules
from src.analysis.reliability import source_score
from src.analysis.sentiment import probs_to_result
from src.data.news_data import normalise_entry
from src.storage.database import get_connection
from src.storage.enrichment_store import create_enrichment_tables
from src.storage.news_store import create_news_table, save_items
from src.storage.sentiment_store import create_scores_table, save_scores

RULES = load_rules()
COMPILED = compile_event_rules(RULES)


def kind(title):
    return classify_event(title, COMPILED)


def test_results_headline():
    assert kind("ITC Q2 net profit drops 20% amid cigarette tax hike")["primary"] == "results"
    assert kind("SBI Q2FY27 results: net profit rose 14%")["primary"] == "results"


def test_results_plus_price_reaction_is_not_reaction_only():
    result = kind("SBI shares fall despite 14% Q2 profit rise")
    assert "price_move" in result["events"]
    assert result["primary"] == "results"
    assert not result["reaction_only"]


def test_pure_price_move_is_reaction_only():
    result = kind("Bharti Airtel stock down 2% in morning trade")
    assert result["primary"] == "price_move"
    assert result["reaction_only"]


def test_other_event_types():
    assert kind("Board meeting scheduled for November 5 to consider quarterly results")["primary"] == "scheduled_event"
    assert kind("SEBI bars promoters over alleged fraud")["primary"] == "regulatory"
    assert kind("L&T bags order worth Rs 2,000 crore")["primary"] == "deal"
    assert kind("Brokerage raises target price for Reliance")["primary"] == "analyst_view"
    assert kind("RBI keeps repo rate unchanged")["primary"] == "macro"
    assert kind("Company declares interim dividend")["primary"] == "corporate_action"
    assert kind("Weather forecast for the weekend")["primary"] == "other"


def test_source_reliability_rules():
    assert source_score("official", "RBI press releases", RULES) == 0.95
    assert source_score("major", "Some Unknown Daily", RULES) == 0.70
    assert source_score("aggregator", "The Economic Times", RULES) == 0.80
    assert source_score("aggregator", "Random Blog", RULES) == 0.45


def test_view_lets_duplicates_inherit_scores(tmp_path):
    conn = get_connection(tmp_path / "t.db")
    create_news_table(conn)
    create_scores_table(conn)
    create_enrichment_tables(conn)
    now = datetime.now(timezone.utc)
    first = normalise_entry(
        {"title": "Reliance wins order", "link": "https://a.example/1", "summary": ""},
        "A", "major", now,
    )
    second = normalise_entry(
        {"title": "Reliance wins order!", "link": "https://b.example/2", "summary": ""},
        "B", "major", now,
    )
    first["symbols"] = "RELIANCE.NS"
    second["symbols"] = "RELIANCE.NS"
    save_items(conn, [first, second])
    save_scores(
        conn, "m", [1],
        [probs_to_result({"positive": 0.9, "negative": 0.05, "neutral": 0.05})],
    )
    rows = conn.execute("SELECT id, score, story_id FROM news_view ORDER BY id").fetchall()
    assert rows[0][1] == rows[1][1]
    assert rows[1][2] == 1
    conn.close()