import numpy as np
import pandas as pd

from src.analysis.indicators import add_indicators, atr, bollinger, rsi, sma


def test_sma_simple():
    s = pd.Series([1, 2, 3, 4, 5], dtype=float)
    result = sma(s, 3)
    assert result.iloc[2] == 2.0
    assert result.iloc[4] == 4.0
    assert np.isnan(result.iloc[1])


def test_rsi_rising_prices_is_100():
    s = pd.Series(np.arange(1, 40, dtype=float))
    assert rsi(s, 14).iloc[-1] == 100.0


def test_rsi_stays_between_0_and_100():
    rng = np.random.default_rng(1)
    s = pd.Series(100 + rng.normal(0, 1, 300).cumsum())
    values = rsi(s, 14).dropna()
    assert values.min() >= 0
    assert values.max() <= 100


def test_bollinger_bands_order():
    rng = np.random.default_rng(2)
    s = pd.Series(100 + rng.normal(0, 1, 100).cumsum())
    upper, mid, lower = bollinger(s, 20, 2)
    assert (upper.dropna() >= lower.dropna()).all()


def test_atr_is_positive():
    high = pd.Series([11, 12, 13, 14, 15, 16], dtype=float)
    low = pd.Series([9, 10, 11, 12, 13, 14], dtype=float)
    close = pd.Series([10, 11, 12, 13, 14, 15], dtype=float)
    result = atr(high, low, close, 3).dropna()
    assert (result > 0).all()


def test_add_indicators_columns_and_length():
    n = 260
    rng = np.random.default_rng(3)
    close = 100 + rng.normal(0, 1, n).cumsum()
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=n).strftime("%Y-%m-%d"),
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "adj_close": close,
            "volume": 1000.0,
        }
    )
    out = add_indicators(df)
    assert len(out) == n
    for col in ["sma_200", "rsi_14", "macd", "bb_upper", "atr_14",
                "volume_ratio", "drawdown_pct"]:
        assert col in out.columns
    assert out["drawdown_pct"].max() <= 0