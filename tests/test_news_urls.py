from src.data.news_data import google_news_url


def test_exact_query_is_quoted():
    url = google_news_url("Reliance Industries")
    assert "%22Reliance+Industries%22" in url


def test_filing_query_keeps_operators():
    url = google_news_url('"TCS" ("exchange filing" OR "board meeting")', exact=False)
    assert "OR" in url
    assert "when%3A7d" in url