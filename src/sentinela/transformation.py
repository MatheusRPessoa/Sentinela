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


def build_flu_weekly_for_state_year(
    path,
    region: str,
    year: int,
) -> pd.DataFrame:

    df = pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
        usecols=[
            "SG_UF",
            "DT_SIN_PRI",
            "SEM_PRI",
            "POS_PCRFLU",
        ],
        dtype="string",
        low_memory=False,
    )

    df["SG_UF"] = (
        df["SG_UF"]
        .str.strip()
        .str.upper()
    )

    return build_flu_weekly_from_df(
        df=df,
        region=region,
        year=year,
    )


def build_flu_weekly_from_df(
    df: pd.DataFrame,
    region: str,
    year: int,
) -> pd.DataFrame:

    state_df = df.loc[
        df["SG_UF"].eq(region)
    ].copy()

    state_df["DT_SIN_PRI"] = (
        pd.to_datetime(
            state_df["DT_SIN_PRI"],
            errors="coerce",
            utc=True,
        )
        .dt.tz_localize(None)
    )

    state_df = state_df.loc[
        state_df["DT_SIN_PRI"]
        .dt.year
        .eq(year)
    ].copy()

    state_df["SEM_PRI"] = pd.to_numeric(
        state_df["SEM_PRI"],
        errors="coerce",
    )

    state_df["POS_PCRFLU"] = pd.to_numeric(
        state_df["POS_PCRFLU"],
        errors="coerce",
    )

    # Semana epidemiológica oficial
    state_df["epi_week"] = (
        state_df["SEM_PRI"]
        .astype("Int64")
    )

    state_df["flu_tested"] = (
        state_df["POS_PCRFLU"]
        .isin([1, 2])
    )

    state_df["flu_positive"] = (
        state_df["POS_PCRFLU"]
        .eq(1)
    )

    weekly = (
        state_df.loc[
            state_df["epi_week"].notna()
        ]
        .groupby(
            "epi_week",
            as_index=False,
        )
        .agg(
            flu_tests=(
                "flu_tested",
                "sum",
            ),
            flu_positive=(
                "flu_positive",
                "sum",
            ),
        )
    )

    weekly["flu_positivity"] = (
        weekly["flu_positive"]
        / weekly["flu_tests"]
    )

    weekly["region"] = region
    weekly["epi_year"] = year

    return weekly
