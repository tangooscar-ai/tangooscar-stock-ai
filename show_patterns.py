import pandas as pd

from src.analysis.candles import add_candles, recent_patterns
from src.analysis.levels import breakout_signals, breakout_status, support_resistance
from src.analysis.liquidity import add_liquidity, liquidity_summary
from src.storage.database import get_connection
from src.storage.queries import load_prices
from src.utils.config import load_settings

pd.set_option("display.width", 200)

settings = load_settings()
conn = get_connection(settings["database_path"])


def analyse(symbol):
    df = load_prices(conn, symbol)
    df = add_liquidity(breakout_signals(add_candles(df)))
    support, resistance = support_resistance(df)
    return df, support, resistance


symbol = "RELIANCE.NS"
df, support, resistance = analyse(symbol)
last = df.iloc[-1]
print(f"{symbol} on {last['date']}  close {last['close']:.2f}")

print("\nCandlestick patterns, last 10 days:")
found = recent_patterns(df, 10)
print("\n".join("  " + f for f in found) if found else "  none")

print("\nResistance (above price):")
for lv in resistance:
    print(f"  {lv['level']:.2f} ({lv['distance_pct']:+.1f}%) touches {lv['touches']}, last {lv['last_touch']}")
print("Support (below price):")
for lv in support:
    print(f"  {lv['level']:.2f} ({lv['distance_pct']:+.1f}%) touches {lv['touches']}, last {lv['last_touch']}")

print("\nBreakout status:", breakout_status(last))

liq = liquidity_summary(df)
print("\nLiquidity:")
print(f"  Average daily traded value: Rs {liq['avg_value_cr']:.0f} crore ({liq['label']})")
print(f"  Volume vs 20-day average: {liq['volume_ratio']:.2f}x" + ("  VOLUME SPIKE" if liq["spike"] else ""))
print(f"  Typical price move per Rs 100 crore traded: {liq['move_pct_per_100cr']:.3f}%")
print(f"  Zero-volume days in last 60: {liq['zero_volume_60d']}")

print("\nAll stocks:")
rows = []
for sym in settings["stocks"]:
    d, sup, res = analyse(sym)
    row = d.iloc[-1]
    rows.append(
        {
            "symbol": sym,
            "close": round(float(row["close"]), 2),
            "support_pct": round(sup[0]["distance_pct"], 1) if sup else None,
            "resist_pct": round(res[0]["distance_pct"], 1) if res else None,
            "status": breakout_status(row),
            "liquidity": liquidity_summary(d)["label"],
        }
    )
print(pd.DataFrame(rows).to_string(index=False))
conn.close()