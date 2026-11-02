import numpy as np
import pandas as pd

from src.analysis.candles import add_candles
from src.analysis.charts import build_chart
from src.analysis.indicators import add_indicators
from src.analysis.levels import breakout_signals, support_resistance
from src.analysis.liquidity import add_liquidity


def prepared_frame(n=300):
    rng = np.random.default_rng(5)
    close = 100 + rng.normal(0, 1, n).cumsum()
    close = close - close.min() + 50
    df = pd.DataFrame(
        {
            "date": pd.bdate_range("2025-01-01", periods=n).strftime("%Y-%m-%d"),
            "open": close - 0.3,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "adj_close": close,
            "volume": rng.integers(1000, 5000, n).astype(float),
        }
    )
    return add_liquidity(breakout_signals(add_candles(add_indicators(df))))


def test_build_chart_returns_figure_with_traces():
    df = prepared_frame()
    support, resistance = support_resistance(df)
    fig = build_chart(df, "TEST.NS", support, resistance, days=120)
    assert len(fig.data) >= 10
    assert fig.data[0].type == "candlestick"
    assert "TEST.NS" in fig.layout.title.text


def test_chart_with_patterns_visible():
    df = prepared_frame()
    support, resistance = support_resistance(df)
    fig = build_chart(df, "TEST.NS", support, resistance, days=120, show_patterns=True)
    assert len(fig.data) >= 10