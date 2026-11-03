import re


def compile_aliases(companies):
    compiled = {}
    for symbol, names in companies.items():
        patterns = []
        for name in names:
            flags = 0 if (name.isupper() and len(name) <= 4) else re.IGNORECASE
            patterns.append(re.compile(r"\b" + re.escape(name) + r"\b", flags))
        compiled[symbol] = patterns
    return compiled


def find_symbols(text, compiled):
    return sorted(
        symbol
        for symbol, patterns in compiled.items()
        if any(p.search(text) for p in patterns)
    )