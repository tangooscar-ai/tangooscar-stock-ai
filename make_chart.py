import sys
import webbrowser
from pathlib import Path

from src.analysis.charts import build_chart
from src.analysis.pipeline import analyse_symbol
from src.storage.database import get_connection
from src.utils.config import load_settings

symbol = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
days = int(sys.argv[2]) if len(sys.argv) > 2 else 250

settings = load_settings()
conn = get_connection(settings["database_path"])
df, support, resistance = analyse_symbol(conn, symbol)
conn.close()

fig = build_chart(df, symbol, support, resistance, days=days)

folder = Path("reports")
folder.mkdir(exist_ok=True)
safe_name = symbol.replace("^", "").replace(".", "_")
path = folder / (safe_name + "_chart.html")
fig.write_html(str(path), include_plotlyjs="cdn")
print("Chart saved:", path.resolve())
webbrowser.open(path.resolve().as_uri())