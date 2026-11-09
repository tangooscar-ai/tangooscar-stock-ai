def source_score(tier, source, rules):
    cfg = rules["reliability"]
    name = (source or "").lower()
    for outlet, score in cfg["outlets"].items():
        if outlet.lower() in name:
            return float(score)
    return float(cfg["tier_base"].get(tier, 0.4))