import importlib
from importlib import metadata

packages = {
    "pandas": "pandas",
    "numpy": "numpy",
    "yfinance": "yfinance",
    "requests": "requests",
    "feedparser": "feedparser",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "plotly": "plotly",
    "streamlit": "streamlit",
    "sklearn": "scikit-learn",
    "lightgbm": "lightgbm",
    "statsmodels": "statsmodels",
    "ta": "ta",
    "dotenv": "python-dotenv",
    "yaml": "PyYAML",
    "pytest": "pytest",
}

failed = []
for module, dist in packages.items():
    try:
        importlib.import_module(module)
        print(f"OK    {dist:16} {metadata.version(dist)}")
    except Exception as err:
        failed.append(dist)
        print(f"FAIL  {dist:16} {err}")

print("\nLive data test (needs internet)...")
try:
    import yfinance as yf

    df = yf.Ticker("RELIANCE.NS").history(period="5d")
    if df.empty:
        print("WARNING: no price data returned. Try again in a minute.")
    else:
        print(df[["Close"]].tail(3))
except Exception as err:
    print(f"WARNING: live data test failed: {err}")

print("\nPHASE 2 COMPLETE" if not failed else f"\nFIX THESE: {failed}")