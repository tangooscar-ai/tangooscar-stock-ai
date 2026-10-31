import numpy as np
import pandas as pd


def sma(series, window):
    return series.rolling(window).mean()


def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def rsi(close, period=14):
    change = close.diff()
    gain = change.clip(lower=0)
    loss = (-change).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(close, fast=12, slow=26, signal=9):
    line = ema(close, fast) - ema(close, slow)
    signal_line = ema(line, signal)
    return line, signal_line, line - signal_line


def bollinger(close, window=20, num_std=2):
    mid = close.rolling(window).mean()
    std = close.rolling(window).std()
    return mid + num_std * std, mid, mid - num_std * std


def atr(high, low, close, period=14):
    prev_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def add_indicators(df):
    out = df.sort_values("date").reset_index(drop=True).copy()
    close = out["close"]

    out["return_1d"] = out["adj_close"].pct_change()
    out["return_5d"] = out["adj_close"].pct_change(5)
    out["return_20d"] = out["adj_close"].pct_change(20)

    out["sma_20"] = sma(close, 20)
    out["sma_50"] = sma(close, 50)
    out["sma_200"] = sma(close, 200)
    out["ema_12"] = ema(close, 12)
    out["ema_26"] = ema(close, 26)

    out["rsi_14"] = rsi(close, 14)
    out["macd"], out["macd_signal"], out["macd_hist"] = macd(close)
    out["bb_upper"], out["bb_mid"], out["bb_lower"] = bollinger(close)

    out["atr_14"] = atr(out["high"], out["low"], close)
    out["atr_pct"] = out["atr_14"] / close * 100
    out["volatility_20d"] = out["return_1d"].rolling(20).std() * np.sqrt(252) * 100

    out["drawdown_pct"] = (out["adj_close"] / out["adj_close"].cummax() - 1) * 100

    volume = out["volume"].replace(0, np.nan)
    out["volume_avg_20"] = volume.rolling(20, min_periods=10).mean()
    out["volume_ratio"] = volume / out["volume_avg_20"]
    return out


def add_relative_strength(df, benchmark_df, name="nifty50"):
    out = df.copy()
    bench = benchmark_df.set_index("date")["close"]
    bench_aligned = out["date"].map(bench)
    out[name + "_close"] = bench_aligned
    out["rel_strength_20d"] = (
        out["adj_close"].pct_change(20) - bench_aligned.pct_change(20)
    ) * 100
    return out