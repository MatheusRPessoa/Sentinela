import pandas as pd


DATE_COLUMNS = ["DT_SIN_PRI", "DT_NOTIFIC"]

def validate_dates(
    records: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    validated = records.copy()
    issues: dict[str, int] = {}

    for column in DATE_COLUMNS:
        raw_dates = (
            validated[column]
            .str.strip()
            .replace("", pd.NA)
        )

        parsed_dates = pd.to_datetime(
            raw_dates,
            format="ISO8601",
            utc=True,
            errors="coerce",
        )

        validated[f"{column}_PARSED"] = parsed_dates

        issues[f"{column}_missing"] = int(raw_dates.isna().sum())
        issues[f"{column}_invalid"] = int(
            (raw_dates.notna() & parsed_dates.isna()).sum()
        )

    intervals = (
        validated["DT_NOTIFIC_PARSED"].dt.normalize()
        - validated["DT_SIN_PRI_PARSED"].dt.normalize()
    ).dt.days

    issues["negative_notification_interval"] = int(
        intervals.lt(0).sum()
    )

    return validated, issues
