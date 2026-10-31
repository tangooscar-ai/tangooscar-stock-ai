import pandas as pd

from src.analysis.indicators import add_indicators, add_relative_strength
from src.storage.database import get_connection
from src.storage.queries import load_prices
from src.utils.config import load_settings

pd.set_option("display.width", 200)

settings = load_settings()
conn = get_connection(settings["database_path"])

symbol = "RELIANCE.NS"
stock = load_prices(conn, symbol)
nifty = load_prices(conn, "^NSEI")
data = add_relative_strength(add_indicators(stock), nifty)
last = data.iloc[-1]

print(f"{symbol} on {last['date']}")
print(f"Close {last['close']:.2f} | RSI(14) {last['rsi_14']:.1f} | ATR(14) {last['atr_14']:.2f} ({last['atr_pct']:.2f}% of price)")
print(f"SMA 20/50/200: {last['sma_20']:.2f} / {last['sma_50']:.2f} / {last['sma_200']:.2f}")
print(f"MACD {last['macd']:.2f} | signal {last['macd_signal']:.2f} | hist {last['macd_hist']:.2f}")
print(f"Bollinger range: {last['bb_lower']:.2f} to {last['bb_upper']:.2f}")
print(f"Volatility, 20 days, annualised: {last['volatility_20d']:.1f}%")
print(f"Drawdown from 3-year high: {last['drawdown_pct']:.1f}%")
print(f"Worst drawdown in 3 years: {data['drawdown_pct'].min():.1f}%")
print(f"Volume vs 20-day average: {last['volume_ratio']:.2f}x")
print(f"Relative strength vs NIFTY 50 (20 days): {last['rel_strength_20d']:+.1f} points")
conn.close()