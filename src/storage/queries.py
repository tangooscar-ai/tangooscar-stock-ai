import pandas as pd


def load_prices(conn, symbol):
    return pd.read_sql_query(
        "SELECT date, open, high, low, close, adj_close, volume, "
        "dividends, stock_splits FROM prices WHERE symbol = ? ORDER BY date",
        conn,
        params=(symbol,),
    )