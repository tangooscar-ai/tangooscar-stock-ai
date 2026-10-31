import numpy as np
import pandas as pd


def find_swings(df, window=5):
    size = 2 * window + 1
    high, low = df["high"], df["low"]
    swing_high = high.where(high == high.rolling(size, center=True).max())
    swing_low = low.where(low == low.rolling(size, center=True).min())
    return swing_high, swing_low


def cluster_levels(prices, dates, tolerance=0.015):
    clusters = []
    for price, date in sorted(zip(prices, dates)):
        if clusters:
            mean = np.mean(clusters[-1]["prices"])
            if abs(price - mean) / mean <= tolerance:
                clusters[-1]["prices"].append(price)
                clusters[-1]["dates"].append(date)
                continue
        clusters.append({"prices": [price], "dates": [date]})
    return [
        {
            "level": float(np.mean(c["prices"])),
            "touches": len(c["prices"]),
            "last_touch": max(c["dates"]),
        }
        for c in clusters
    ]


def support_resistance(df, window=5, tolerance=0.015, min_touches=2, top_n=3):
    swing_high, swing_low = find_swings(df, window)
    mask_h, mask_l = swing_high.notna(), swing_low.notna()
    prices = list(swing_high[mask_h]) + list(swing_low[mask_l])
    dates = list(df.loc[mask_h, "date"]) + list(df.loc[mask_l, "date"])

    levels = [lv for lv in cluster_levels(prices, dates, tolerance)
              if lv["touches"] >= min_touches]
    last_close = float(df["close"].iloc[-1])

    resistance = sorted([lv for lv in levels if lv["level"] > last_close],
                        key=lambda x: x["level"])[:top_n]
    support = sorted([lv for lv in levels if lv["level"] <= last_close],
                     key=lambda x: -x["level"])[:top_n]
    for lv in resistance + support:
        lv["distance_pct"] = (lv["level"] / last_close - 1) * 100
    return support, resistance


def breakout_signals(df, lookback=20, volume_multiple=1.5):
    out = df.copy()
    prior_high = out["high"].shift(1).rolling(lookback).max()
    prior_low = out["low"].shift(1).rolling(lookback).min()
    out["breakout_up"] = out["close"] > prior_high
    out["breakdown"] = out["close"] < prior_low

    volume = out["volume"].replace(0, np.nan)
    avg_volume = volume.shift(1).rolling(20, min_periods=10).mean()
    heavy = volume >= volume_multiple * avg_volume
    out["breakout_confirmed"] = out["breakout_up"] & heavy
    out["breakdown_confirmed"] = out["breakdown"] & heavy

    out["failed_breakout"] = (
        out["breakout_up"].shift(1, fill_value=False) & (out["close"] < prior_high.shift(1))
    )
    out["failed_breakdown"] = (
        out["breakdown"].shift(1, fill_value=False) & (out["close"] > prior_low.shift(1))
    )
    return out


def breakout_status(row):
    if row["breakout_confirmed"]:
        return "Breakout (heavy volume)"
    if row["breakout_up"]:
        return "Breakout (light volume)"
    if row["breakdown_confirmed"]:
        return "Breakdown (heavy volume)"
    if row["breakdown"]:
        return "Breakdown (light volume)"
    if row["failed_breakout"]:
        return "Failed breakout"
    if row["failed_breakdown"]:
        return "Failed breakdown"
    return "None"