import time
import warnings

from src.data.market_data import download_history
from src.data.quality import check_quality
from src.storage.database import create_tables, get_connection, log_fetch, save_prices
from src.utils.config import load_settings

warnings.filterwarnings("ignore")


def main():
    settings = load_settings()
    conn = get_connection(settings["database_path"])
    create_tables(conn)

    jobs = [(s, False) for s in settings["stocks"]]
    jobs += [(s, True) for s in settings["indices"]]

    saved = 0
    failed = []
    for symbol, is_index in jobs:
        print(f"Downloading {symbol} ...", end=" ", flush=True)
        df, error = download_history(symbol, settings["history_years"])
        if df is None:
            print(f"FAILED ({error})")
            log_fetch(conn, symbol, 0, "failed", error)
            failed.append(symbol)
            continue

        issues = check_quality(df, is_index)
        rows = save_prices(conn, df)
        note = "; ".join(issues)
        log_fetch(conn, symbol, rows, "warning" if issues else "ok", note)
        message = f"{rows} rows, last date {df['date'].iloc[-1]}"
        if issues:
            message += f"  [WARN: {note}]"
        print(message)
        saved += 1
        time.sleep(1)

    conn.close()
    print(f"\nSaved: {saved}   Failed: {len(failed)}")
    if failed:
        print("Failed symbols:", failed)
        print("Wait a minute, then run this script again.")


main()