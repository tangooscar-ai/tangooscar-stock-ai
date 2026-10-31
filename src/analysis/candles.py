import numpy as np
import pandas as pd

PATTERNS = [
    "cdl_doji", "cdl_hammer", "cdl_shooting_star",
    "cdl_bullish_engulfing", "cdl_bearish_engulfing",
    "cdl_bullish_harami", "cdl_bearish_harami",
    "cdl_morning_star", "cdl_evening_star",
    "cdl_gap_up", "cdl_gap_down",
]


def add_candles(df):
    out = df.sort_values("date").reset_index(drop=True).copy()
    o, h, l, c = out["open"], out["high"], out["low"], out["close"]

    body = (c - o).abs()
    rng = (h - l).replace(0, np.nan)
    upper = h - np.maximum(o, c)
    lower = np.minimum(o, c) - l
    prior_move = c / c.shift(5) - 1
    bull, bear = c > o, c < o

    out["cdl_doji"] = body <= 0.1 * rng
    out["cdl_hammer"] = (
        (lower >= 2 * body) & (upper <= 0.1 * rng) & (body > 0) & (prior_move < 0)
    )
    out["cdl_shooting_star"] = (
        (upper >= 2 * body) & (lower <= 0.1 * rng) & (body > 0) & (prior_move > 0)
    )

    prev_o, prev_c = o.shift(1), c.shift(1)
    prev_bear, prev_bull = prev_c < prev_o, prev_c > prev_o
    out["cdl_bullish_engulfing"] = prev_bear & bull & (o <= prev_c) & (c >= prev_o)
    out["cdl_bearish_engulfing"] = prev_bull & bear & (o >= prev_c) & (c <= prev_o)
    out["cdl_bullish_harami"] = prev_bear & bull & (o > prev_c) & (c < prev_o)
    out["cdl_bearish_harami"] = prev_bull & bear & (o < prev_c) & (c > prev_o)

    o1, c1 = o.shift(2), c.shift(2)
    body1 = (c1 - o1).abs()
    body2 = body.shift(1)
    long1 = body1 >= 0.6 * rng.shift(2)
    mid1 = (o1 + c1) / 2
    out["cdl_morning_star"] = long1 & (c1 < o1) & (body2 <= 0.3 * body1) & bull & (c > mid1)
    out["cdl_evening_star"] = long1 & (c1 > o1) & (body2 <= 0.3 * body1) & bear & (c < mid1)

    out["cdl_gap_up"] = l > h.shift(1)
    out["cdl_gap_down"] = h < l.shift(1)
    return out


def recent_patterns(df, days=10):
    found = []
    for _, row in df.tail(days).iterrows():
        for name in PATTERNS:
            if row[name]:
                label = name.replace("cdl_", "").replace("_", " ")
                found.append(f"{row['date']}: {label}")
    return found