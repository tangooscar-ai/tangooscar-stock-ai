from src.analysis.candles import add_candles
from src.analysis.indicators import add_indicators, add_relative_strength
from src.analysis.levels import breakout_signals, support_resistance
from src.analysis.liquidity import add_liquidity
from src.storage.queries import load_prices


def analyse_symbol(conn, symbol, benchmark="^NSEI"):
    df = load_prices(conn, symbol)
    if df.empty:
        raise ValueError(
            f"No data for {symbol}. Add it to config/settings.yaml "
            "and run collect_data.py first."
        )
    df = add_indicators(df)
    df = add_candles(df)
    df = breakout_signals(df)
    df = add_liquidity(df)
    df = add_relative_strength(df, load_prices(conn, benchmark))
    support, resistance = support_resistance(df)
    return df, support, resistance