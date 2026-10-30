import time

import pandas as pd
import yfinance as yf


def standardise(df, symbol):
    df = df.copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    out = pd.DataFrame(
        {
            "symbol": symbol,
            "date": df.index.strftime("%Y-%m-%d"),
            "open": df["Open"].values,
            "high": df["High"].values,
            "low": df["Low"].values,
            "close": df["Close"].values,
            "adj_close": df.get("Adj Close", df["Close"]).values,
            "volume": df["Volume"].values,
            "dividends": df.get("Dividends", pd.Series(0.0, index=df.index)).values,
            "stock_splits": df.get("Stock Splits", pd.Series(0.0, index=df.index)).values,
        }
    )
    out = out.dropna(subset=["close"])
    out = out.drop_duplicates(subset=["date"]).sort_values("date")
    return out.reset_index(drop=True)


def download_history(symbol, years=3, retries=3):
    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            raw = yf.Ticker(symbol).history(
                period=f"{years}y", auto_adjust=False, actions=True
            )
            if raw is not None and not raw.empty:
                return standardise(raw, symbol), ""
            last_error = "no data returned"
        except Exception as err:
            last_error = str(err)
        time.sleep(3 * attempt)
    return None, last_error