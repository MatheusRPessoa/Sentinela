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

def validate_calendar(
    records: pd.DataFrame,
) -> dict[str, int]:
    source_week = pd.to_numeric(
        records["SEM_PRI"].str.strip(),
        errors="coerce",
    )

    calculated_week = records["EPI_WEEK_CALCULATED"]

    source_valid = (
        source_week.notna()
        & source_week.between(1, 53)
        & source_week.mod(1).eq(0)
    ).fillna(False)

    comparable = source_valid & calculated_week.notna()
    difference = (
        source_week.loc[comparable]
        - calculated_week.loc[comparable]
    )

    return {
        "rows_checked": len(records),
        "calculated_week_missing": int(calculated_week.isna().sum()),
        "source_week_missing_or_invalid": int((~source_valid).sum()),
        "not_comparable": int((~comparable).sum()),
        "matching": int(difference.eq(0).sum()),
        "source_one_week_ahead": int(difference.eq(1).sum()),
        "other_differences": int(
            (~difference.isin([0, 1])).sum()
        ),
    }

def collect_record_issues(
    records: pd.DataFrame,
) -> pd.DataFrame:
    issues = []

    for column in DATE_COLUMNS:
        raw_dates = records[column].str.strip().replace("", pd.NA)
        parsed_dates = records[f"{column}_PARSED"]

        checks = [
            ("DATE_MISSING", raw_dates.isna()),
            (
                "DATE_INVALID",
                raw_dates.notna() & parsed_dates.isna()
            ),
        ]

        for code, mask in checks:
            for index in records.index[mask.fillna(False)]:
                issues.append({
                    "source_record_number": int(index) + 1,
                    "field": column,
                    "issue_code": code,
                })

    
    sympton_dates = records["DT_SIN_PRI_PARSED"].dt.normalize()
    notification_dates = records["DT_NOTIFIC_PARSED"].dt.normalize()

    negative_interval = (
        notification_dates - sympton_dates
    ).dt.days.lt(0).fillna(False)

    for index in records.index[negative_interval]:
        issues.append({
            "source_record_number": int(index) + 1,
            "field": "DT_NOTIFIC",
            "issue_code": "NOTIFICATION_BEFORE_SYMPTOMS",
        })
    
    outside_calendar = (
        sympton_dates.notna()
        & records["EPI_WEEK_CALCULATED"].isna()
    )

    for index in records.index[outside_calendar]:
        issues.append({
            "source_record_number": int(index) + 1,
            "field": "DT_SIN_PRI",
            "issue_code": "DATE_OUTSIDE_CALENDAR_2026"
        })

    return pd.DataFrame(
        issues,
        columns=["source_record_number", "field", "issue_code"],
    )