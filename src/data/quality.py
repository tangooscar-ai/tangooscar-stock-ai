import pandas as pd


def check_quality(df, is_index=False):
    issues = []
    if df is None or df.empty:
        return ["no rows"]

    if len(df) < 600:
        issues.append(f"only {len(df)} rows (expected about 740 for 3 years)")

    if (df[["open", "high", "low", "close"]] <= 0).any().any():
        issues.append("zero or negative prices found")

    bad = int((df["high"] < df["low"]).sum())
    if bad:
        issues.append(f"{bad} day(s) where high is below low")

    dates = pd.to_datetime(df["date"])
    gaps = int((dates.diff().dt.days > 7).sum())
    if gaps:
        issues.append(f"{gaps} gap(s) longer than 7 days")

    age = (pd.Timestamp.now().normalize() - dates.max()).days
    if age > 5:
        issues.append(f"latest data is {age} days old")

    if not is_index:
        zero_volume = int((df["volume"] == 0).sum())
        if zero_volume:
            issues.append(f"{zero_volume} day(s) with zero volume")

    return issues