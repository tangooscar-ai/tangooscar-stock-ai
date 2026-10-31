import numpy as np
import pandas as pd

from src.analysis.candles import add_candles
from src.analysis.levels import breakout_signals, support_resistance
from src.analysis.liquidity import add_liquidity, liquidity_label


def make(rows):
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"])
    df["date"] = pd.date_range("2025-01-01", periods=len(df)).strftime("%Y-%m-%d")
    df["volume"] = 1000.0
    df["adj_close"] = df["close"]
    return df


def test_doji():
    out = add_candles(make([[100, 102, 98, 100.1]]))
    assert out["cdl_doji"].iloc[0]


def test_hammer_after_decline():
    rows = [[c, c + 0.5, c - 0.5, c] for c in [110, 108, 106, 104, 102]]
    rows.append([100, 101.2, 94, 101])
    out = add_candles(make(rows))
    assert out["cdl_hammer"].iloc[-1]


def test_bullish_engulfing():
    out = add_candles(make([[105, 106, 99, 100], [99, 107, 98, 106]]))
    assert out["cdl_bullish_engulfing"].iloc[-1]


def test_gap_up():
    out = add_candles(make([[100, 101, 99, 100], [104, 106, 103, 105]]))
    assert out["cdl_gap_up"].iloc[-1]
    assert not out["cdl_gap_down"].iloc[-1]


def test_support_and_resistance_found():
    t = np.arange(140)
    close = 100 + 10 * np.sin(2 * np.pi * t / 20)
    df = pd.DataFrame(
        {"open": close, "high": close + 1, "low": close - 1, "close": close}
    )
    df["date"] = pd.date_range("2025-01-01", periods=140).strftime("%Y-%m-%d")
    df["volume"] = 1000.0
    df["adj_close"] = close
    support, resistance = support_resistance(df)
    last_close = df["close"].iloc[-1]
    assert any(105 < lv["level"] < 115 for lv in resistance)
    assert any(85 < lv["level"] < 95 for lv in support)
    assert all(lv["level"] > last_close for lv in resistance)
    assert all(lv["level"] <= last_close for lv in support)


def test_breakout_with_heavy_volume():
    rows = [[100, 101, 99, 100]] * 30 + [[101, 106, 100, 105]]
    df = make(rows)
    df.loc[df.index[-1], "volume"] = 3000.0
    out = breakout_signals(df)
    assert out["breakout_up"].iloc[-1]
    assert out["breakout_confirmed"].iloc[-1]
    assert not out["breakdown"].iloc[-1]


def test_liquidity_value_and_label():
    df = make([[100, 101, 99, 100]] * 40)
    df["volume"] = 2_000_000.0
    out = add_liquidity(df)
    assert abs(out["avg_traded_value_cr"].iloc[-1] - 20.0) < 1e-6
    assert liquidity_label(20.0) == "Moderate"
    assert liquidity_label(500.0) == "High"
    assert liquidity_label(0.5) == "Very low"