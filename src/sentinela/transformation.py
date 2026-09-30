import pandas as pd

CALENDAR_START_2026 = pd.Timestamp("2026-01-04", tz="UTC")
CALENDAR_END_2026 = pd.Timestamp("2027-01-03", tz="UTC")

def add_epidemiological_week_2026(
    records: pd.DataFrame,
) -> pd.DataFrame:
    transformed = records.copy()

    transformed["RESIDENCE_UF_NORMALIZED"] = (
        transformed["SG_UF"]
        .str.strip()
        .str.upper()
        .replace("", pd.NA)
    )

    symptom_dates = transformed["DT_SIN_PRI_PARSED"].dt.normalize()

    in_calendar = (
        symptom_dates.notna()
        & symptom_dates.ge(CALENDAR_START_2026)
        & symptom_dates.lt(CALENDAR_END_2026)
    ).fillna(False)

    transformed["EPI_YEAR_CALCULATED"] = pd.Series(
        pd.NA,
        index=transformed.index,
        dtype="Int64"
    )

    transformed["EPI_WEEK_CALCULATED"] = pd.Series(
        pd.NA,
        index=transformed.index,
        dtype="Int64"
    )

    transformed.loc[in_calendar, "EPI_YEAR_CALCULATED"] = 2026

    calculated_weeks = (
        (
            symptom_dates.loc[in_calendar]
            - CALENDAR_START_2026
        ).dt.days // 7
    ) + 1

    transformed.loc[in_calendar, "EPI_WEEK_CALCULATED"] = (
        calculated_weeks.astype("Int64")
    )

    return transformed
