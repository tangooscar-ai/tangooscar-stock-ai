import sys
from datetime import datetime, timezone

from src.analysis.events import classify_event, compile_event_rules, load_rules
from src.analysis.reliability import source_score
from src.storage.database import get_connection
from src.storage.enrichment_store import (
    create_enrichment_tables,
    get_to_enrich,
    save_enrichment,
)
from src.utils.config import load_settings

redo = len(sys.argv) > 1 and sys.argv[1] == "all"

settings = load_settings()
rules = load_rules()
compiled = compile_event_rules(rules)
conn = get_connection(settings["database_path"])
create_enrichment_tables(conn)

rows = get_to_enrich(conn, redo)
stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
version = str(rules.get("version", 1))

records = []
for news_id, title, tier, source in rows:
    event = classify_event(title, compiled)
    records.append(
        (
            news_id,
            event["events"],
            event["primary"],
            int(event["reaction_only"]),
            source_score(tier, source, rules),
            version,
            stamp,
        )
    )

save_enrichment(conn, records)
print(f"Items enriched: {len(records)} (rules version {version})")
conn.close()