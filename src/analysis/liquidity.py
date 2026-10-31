import numpy as np
import pandas as pd

CRORE = 10_000_000


def add_liquidity(df, window=20):
    out = df.copy()
    volume = out["volume"].replace(0, np.nan)

    out["traded_value_cr"] = out["close"] * out["volume"] / CRORE
    out["avg_traded_value_cr"] = (
        out["traded_value_cr"].rolling(window, min_periods=10).mean()
    )
    out["liq_volume_ratio"] = volume / volume.rolling(window, min_periods=10).mean()

    daily_move_pct = out["adj_close"].pct_change().abs() * 100
    value = out["traded_value_cr"].replace(0, np.nan)
    out["move_pct_per_100cr"] = (
        (daily_move_pct / value * 100).rolling(window, min_periods=10).mean()
    )
    out["zero_volume_60d"] = (out["volume"] == 0).rolling(60, min_periods=1).sum()
    out["volume_spike"] = out["liq_volume_ratio"] >= 2
    return out


def liquidity_label(avg_value_cr):
    if pd.isna(avg_value_cr):
        return "Unknown"
    if avg_value_cr >= 100:
        return "High"
    if avg_value_cr >= 10:
        return "Moderate"
    if avg_value_cr >= 1:
        return "Low"
    return "Very low"


def liquidity_summary(df):
    last = df.iloc[-1]
    return {
        "avg_value_cr": float(last["avg_traded_value_cr"]),
        "label": liquidity_label(last["avg_traded_value_cr"]),
        "volume_ratio": float(last["liq_volume_ratio"]),
        "move_pct_per_100cr": float(last["move_pct_per_100cr"]),
        "zero_volume_60d": int(last["zero_volume_60d"]),
        "spike": bool(last["volume_spike"]),
    }