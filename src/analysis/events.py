import re
from pathlib import Path

import yaml

PRIORITY = [
    "scheduled_event", "results", "corporate_action", "deal", "regulatory",
    "management", "macro", "analyst_view", "price_move",
]


def load_rules():
    path = Path("config") / "news_rules.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def compile_event_rules(rules):
    compiled = {}
    for name, entries in rules["events"].items():
        patterns = []
        for entry in entries:
            body = entry[3:] if entry.startswith("re:") else re.escape(entry)
            patterns.append(re.compile(r"\b(?:" + body + r")\b", re.IGNORECASE))
        compiled[name] = patterns
    return compiled


def classify_event(title, compiled):
    found = [
        name
        for name in PRIORITY
        if any(p.search(title) for p in compiled.get(name, []))
    ]
    return {
        "events": ",".join(found),
        "primary": found[0] if found else "other",
        "reaction_only": found == ["price_move"],
    }