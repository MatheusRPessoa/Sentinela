from pathlib import Path
import numpy as np
import pandas as pd

def build_epi_calendar(
    region: str,
    year: int,
    first_week_start: str,
    weeks: int = 52,
) -> pd.DataFrame:
    calendar = pd.DataFrame(
        {
            "epi_week": range(1, weeks + 1),
        }
    )

    calendar["region"] = region
    calendar["year"] = year

    first_start = pd.Timestamp(
        first_week_start
    )

    calendar["week_start"] = (
        first_start
        + pd.to_timedelta(
            (calendar["epi_week"] - 1) * 7,
            unit="D",
        )
    )

    calendar["week_end"] = (
        calendar["week_start"]
        + pd.Timedelta(days=6)
    )

    return calendar[
        [
            "region",
            "year",
            "epi_week",
            "week_start",
            "week_end",
        ]
    ]

def assign_epi_week(
    event_row: pd.Series,
    calendar: pd.DataFrame,
):
    candidates = calendar.loc[
        calendar["region"].eq(
            event_row["region"]
        )
        & (
            calendar["week_start"]
            <= event_row["event_date"]
        )
        & (
            calendar["week_end"]
            >= event_row["event_date"]
        )
    ]

    if candidates.empty:
        return pd.NA

    return int(
        candidates.iloc[0]["epi_week"]
    )

def classify_outcome(row):
    truth = row["ground_truth"]
    pred = row["sentinela_positive"]

    if truth == 1 and pred:
        return "TP"

    if truth == 0 and pred:
        return "FP"

    if truth == 1 and not pred:
        return "FN"

    if truth == 0 and not pred:
        return "TN"

    raise ValueError("Combinação inválida.")

def build_reference_for_parameters(
    historical_weekly: pd.DataFrame,
    target_year: int,
    quantile: float,
) -> pd.DataFrame:
    history = historical_weekly.loc[
        historical_weekly["epi_year"] < target_year
    ].copy()

    history = history.loc[
        history["epi_week"].between(1, 52)
    ].copy()


    return (
        history
        .groupby("epi_week")
        .agg(
            historical_median=(
                "record_count",
                "median",
            ),
            historical_quantile=(
                "record_count",
                lambda values: values.quantile(
                    quantile
                ),
            ),
        )
        .reset_index()
    )

def evaluate_parameters(
    weekly_observed: pd.DataFrame,
    historical_weekly: pd.DataFrame,
    ground_truth_subset: pd.DataFrame,
    target_year: int,
    quantile: float,
    median_factor: float, 
) -> dict:
    reference =build_reference_for_parameters(
        historical_weekly=historical_weekly,
        target_year=target_year,
        quantile=quantile
    )

    evaluated = (
        weeklly_observed[
            [
                "epi_week",
                "record_count", 
            ]
        ]
        .merge(
            reference,
            on="epi_week",
            how="left",
        )
    )

    evaluated["prediction"] =(
        (
            evaluated["record_count"]
            > evaluated[
                "historical_quantile"
            ]
        )
        & (
            evaluated["record_count"]
            >= (
                evaluated[
                    "historical_median"
                ]
                * median_factor
            )
        )
    )

    labeled = (
        ground_truth_subset[
            ground_truth_subset[
                "ground_truth"
            ].notna()
        ]
        .merge(
            evaluated[
                [
                    "epi_week",
                    "prediction",
                ]
            ],
            on="epi_week",
            how="inner",
        )
    )

    truth = labeled[
        "ground_truth"
    ].astype(int)

    pred = labeled[
        "prediction"
    ].astype(bool)

    TP = int(
        ((truth == 1) & pred).sum()
    )

    FP = int(
        ((truth == 0) & pred).sum()
    )

    FN = int(
        ((truth == 1) & ~pred).sum()
    )

    TN = int(
        ((truth == 0) & ~pred).sum()
    )

    sensitivity = (
        TP / (TP + FN)
        if TP + FN
        else float("nan")
    )

    specificity = (
        TN / (TN + FP)
        if TN + FP
        else float("nan")
    )

    f1 = (
        2 * TP
        / (2 * TP + FP + FN)
        if (2 * TP + FP + FN)
        else float("nan")
    )

    return {
        "quantile": quantile,
        "median_factor": median_factor,
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "TN": TN,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "f1": f1,
    }

def evaluate_combined_parameters(
    cases: list[dict],
    ground_truth: pd.DataFrame,
    quantile: float,
    median_factor: float,
) -> dict:
    prediction_frames = []

    for case in cases:
        region = case["region"]
        year = case["year"]

        weekly_observed = case[
            "weekly_observed"
        ].copy()

        historical_weekly = case[
            "historical_weekly"
        ].copy()

        reference = (
            build_reference_for_parameters(
                historical_weekly=historical_weekly,
                target_year=year,
                quantile=quantile,
            )
        )

        evaluated = (
            weekly_observed[
                [
                    "epi_week",
                    "record_count",
                ]
            ]
            .merge(
                reference,
                on="epi_week",
                how="left",
            )
        )

        evaluated["sentinela_positive"] = (
            (
                evaluated["record_count"]
                > evaluated[
                    "historical_quantile"
                ]
            )
            & (
                evaluated["record_count"]
                >= (
                    evaluated[
                        "historical_median"
                    ]
                    * median_factor
                )
            )
        )

        evaluated["region"] = region
        evaluated["year"] = year

        prediction_frames.append(
            evaluated[
                [
                    "region",
                    "year",
                    "epi_week",
                    "sentinela_positive", 
                ]
            ]
        )
    
    predictions = pd.concat(
        prediction_frames,
        ignore_index=True,
    )
    
    labeled = (
        ground_truth.loc[
            ground_truth[
                "ground_truth"
            ].notna()
        ][
            [
                "region",
                "year",
                "epi_week",
                "ground_truth",
            ]
        ]
        .merge(
            predictions,
            on=[
                "region",
                "year",
                "epi_week",
            ],
            how="inner",
        )
    )

    truth = (
        labeled["ground_truth"]
        .astype(int)
    )

    prediction = (
        labeled["sentinela_positive"]
        .astype(bool)
    )

    TP = int(
        (
            (truth == 1)
            & prediction
        ).sum()
    )

    FP = int(
        (
            (truth == 0)
            & prediction
        ).sum()
    )

    FN = int(
        (
            (truth == 1)
            & ~prediction
        ).sum()
    )

    TN = int(
        (
            (truth == 0)
            & ~prediction
        ).sum()
    )

    sensitivity = (
        TP / (TP + FN)
        if (TP + FN) > 0
        else float("nan")
    )

    specificity = (
        TN / (TN + FP)
        if (TN + FP) > 0
        else float("nan")
    )

    ppv = (
        TP / (TP + FP)
        if (TP + FP) > 0
        else float("nan")
    )

    npv = (
        TN / (TN + FN)
        if (TN + FN) > 0
        else float("nan")
    )

    f1 = (
        2 * TP
        / (
            2 * TP
            + FP
            + FN
        )
        if (
            2 * TP
            + FP
            + FN
        ) > 0
        else float("nan")
    )

    balanced_accuracy = (
        (
            sensitivity
            + specificity
        )
        / 2
    )

    return {
        "quantile": quantile,
        "median_factor": median_factor,
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "TN": TN,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "ppv": ppv,
        "npv": npv,
        "f1": f1,
        "balanced_accuracy":
            balanced_accuracy,
    }

def evaluate_combined_parameters(
    cases: list[dict],
    ground_truth: pd.DataFrame,
    quantile: float,
    median_factor: float,
    combination: str,
) -> dict:
    prediction_frames = []

    for case in cases:
        region = case["region"]
        year = case["year"]

        weekly_observed = case[
            "weekly_observed"
        ].copy()

        historical_weekly = case[
            "historical_weekly"
        ].copy()

        reference = build_reference_for_parameters(
            historical_weekly=historical_weekly,
            target_year=year,
            quantile=quantile,
        )

        evaluated = (
            weekly_observed[
                [
                    "epi_week",
                    "record_count",
                ]
            ]
            .merge(
                reference,
                on="epi_week",
                how="left",
            )
        )

        above_quantile = (
            evaluated["record_count"]
            > evaluated["historical_quantile"]
        )

        above_median_factor = (
            evaluated["record_count"]
            >= (
                evaluated["historical_median"]
                * median_factor
            )
        )

        if combination == "AND":
            prediction = (
                above_quantile
                & above_median_factor
            )

        elif combination == "OR":
            prediction = (
                above_quantile
                | above_median_factor
            )

        else:
            raise ValueError(
                f"Combinação inválida: {combination}"
            )

        evaluated[
            "sentinela_positive"
        ] = prediction

        evaluated["region"] = region
        evaluated["year"] = year

        prediction_frames.append(
            evaluated[
                [
                    "region",
                    "year",
                    "epi_week",
                    "sentinela_positive",
                ]
            ]
        )

    predictions = pd.concat(
        prediction_frames,
        ignore_index=True,
    )

    labeled = (
        ground_truth.loc[
            ground_truth[
                "ground_truth"
            ].notna()
        ][
            [
                "region",
                "year",
                "epi_week",
                "ground_truth",
            ]
        ]
        .merge(
            predictions,
            on=[
                "region",
                "year",
                "epi_week",
            ],
            how="inner",
        )
    )

    truth = labeled[
        "ground_truth"
    ].astype(int)

    pred = labeled[
        "sentinela_positive"
    ].astype(bool)

    TP = int(
        ((truth == 1) & pred).sum()
    )
    FP = int(
        ((truth == 0) & pred).sum()
    )
    FN = int(
        ((truth == 1) & ~pred).sum()
    )
    TN = int(
        ((truth == 0) & ~pred).sum()
    )

    sensitivity = (
        TP / (TP + FN)
        if (TP + FN) > 0
        else float("nan")
    )

    specificity = (
        TN / (TN + FP)
        if (TN + FP) > 0
        else float("nan")
    )

    ppv = (
        TP / (TP + FP)
        if (TP + FP) > 0
        else float("nan")
    )

    npv = (
        TN / (TN + FN)
        if (TN + FN) > 0
        else float("nan")
    )

    f1 = (
        2 * TP / (2 * TP + FP + FN)
        if (2 * TP + FP + FN) > 0
        else float("nan")
    )

    balanced_accuracy = (
        sensitivity + specificity
    ) / 2

    return {
        "quantile": quantile,
        "median_factor": median_factor,
        "combination": combination,
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "TN": TN,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "ppv": ppv,
        "npv": npv,
        "f1": f1,
        "balanced_accuracy":
            balanced_accuracy,
    }

def predict_configuration(
    cases: list[dict],
    quantile: float,
    median_factor: float,
    combination: str,
) -> pd.DataFrame:
    frames = []

    for case in cases:
        region = case["region"]
        year = case["year"]

        weekly = case[
            "weekly_observed"
        ].copy()

        historical = case[
            "historical_weekly"
        ].copy()

        reference = (
            build_reference_for_parameters(
                historical_weekly=historical,
                target_year=year,
                quantile=quantile,
            )
        )

        evaluated = (
            weekly[
                [
                    "epi_week",
                    "record_count",
                ]
            ]
            .merge(
                reference,
                on="epi_week",
                how="left",
            )
        )

        evaluated[
            "ratio_to_median"
        ] = (
            evaluated["record_count"]
            / evaluated[
                "historical_median"
            ]
        )

        evaluated[
            "above_quantile"
        ] = (
            evaluated["record_count"]
            > evaluated[
                "historical_quantile"
            ]
        )

        evaluated[
            "above_median_factor"
        ] = (
            evaluated["record_count"]
            >= (
                evaluated[
                    "historical_median"
                ]
                * median_factor
            )
        )

        if combination == "AND":
            prediction = (
                evaluated["above_quantile"]
                & evaluated[
                    "above_median_factor"
                ]
            )

        elif combination == "OR":
            prediction = (
                evaluated["above_quantile"]
                | evaluated[
                    "above_median_factor"
                ]
            )

        else:
            raise ValueError(
                f"Combinação inválida: {combination}"
            )

        evaluated[
            "sentinela_positive"
        ] = prediction

        evaluated["region"] = region
        evaluated["year"] = year

        frames.append(evaluated)

    return pd.concat(
        frames,
        ignore_index=True,
    )

def build_reference_selected_years(
    historical_weekly: pd.DataFrame,
    years: list[int],
    quantile: float,
) -> pd.DataFrame:
    history = historical_weekly.loc[
        historical_weekly[
            "epi_year"
        ].isin(years)
        & historical_weekly[
            "epi_week"
        ].between(1, 52)
    ].copy()

    reference = (
        history
        .groupby("epi_week")
        .agg(
            historical_median=(
                "record_count",
                "median",
            ),
            historical_quantile=(
                "record_count",
                lambda values: (
                    values.quantile(
                        quantile
                    )
                ),
            ),
            historical_years=(
                "epi_year",
                "nunique",
            ),
        )
        .reset_index()
    )

    return reference

def build_robust_reference(
    historical_weekly: pd.DataFrame,
    years: list[int],
) -> pd.DataFrame:
    history = historical_weekly.loc[
        historical_weekly["epi_year"].isin(years)
        & historical_weekly["epi_week"].between(1, 52)
    ].copy()

    rows = []

    for epi_week, group in history.groupby("epi_week"):
        values = group["record_count"].astype(float)

        median = values.median()

        mad = np.median(
            np.abs(values - median)
        )

        rows.append(
            {
                "epi_week": int(epi_week),
                "historical_median": median,
                "mad": mad,
                "historical_years": (
                    group["epi_year"].nunique()
                ),
            }
        )

    return pd.DataFrame(rows)

def apply_persistent_signal(
    df: pd.DataFrame,
    ratio_threshold: float,
    persistence: int,
) -> pd.DataFrame:
    result = (
        df.sort_values("epi_week")
        .copy()
    )

    result["above_ratio"] = (
        result["ratio_to_median"]
        >= ratio_threshold
    )

    result["persistent_signal"] = (
        result["above_ratio"]
        .rolling(
            window=persistence,
            min_periods=persistence,
        )
        .sum()
        .eq(persistence)
    )

    return result

def evaluate_persistent_ratio(
    cases: list[dict],
    ground_truth: pd.DataFrame,
    baseline_years_by_case: dict,
    ratio_threshold: float,
    persistence: int,
) -> dict:
    prediction_frames = []

    for case in cases:
        region = case["region"]
        year = case["year"]

        key = (region, year)

        historical = case["historical_weekly"]

        weekly = (
            case["weekly_observed"]
            .sort_values("epi_week")
            .copy()
        )

        reference = (
            build_reference_selected_years(
                historical_weekly=historical,
                years=baseline_years_by_case[key],
                quantile=0.75,
            )
        )

        evaluated = (
            weekly[
                [
                    "epi_week",
                    "record_count",
                ]
            ]
            .merge(
                reference[
                    [
                        "epi_week",
                        "historical_median",
                    ]
                ],
                on="epi_week",
                how="left",
            )
            .sort_values("epi_week")
        )

        evaluated["ratio_to_median"] = (
            evaluated["record_count"]
            / evaluated["historical_median"]
        )

        evaluated["above_ratio"] = (
            evaluated["ratio_to_median"]
            >= ratio_threshold
        )

        evaluated["sentinela_positive"] = (
            evaluated["above_ratio"]
            .rolling(
                window=persistence,
                min_periods=persistence,
            )
            .sum()
            .eq(persistence)
        )

        evaluated["region"] = region
        evaluated["year"] = year

        prediction_frames.append(
            evaluated[
                [
                    "region",
                    "year",
                    "epi_week",
                    "sentinela_positive",
                ]
            ]
        )

    predictions = pd.concat(
        prediction_frames,
        ignore_index=True,
    )

    labeled = (
        ground_truth.loc[
            ground_truth["ground_truth"].notna()
        ][
            [
                "region",
                "year",
                "epi_week",
                "ground_truth",
            ]
        ]
        .merge(
            predictions,
            on=[
                "region",
                "year",
                "epi_week",
            ],
            how="inner",
        )
    )

    truth = labeled["ground_truth"].astype(int)
    pred = labeled["sentinela_positive"].astype(bool)

    TP = int(((truth == 1) & pred).sum())
    FP = int(((truth == 0) & pred).sum())
    FN = int(((truth == 1) & ~pred).sum())
    TN = int(((truth == 0) & ~pred).sum())

    sensitivity = (
        TP / (TP + FN)
        if (TP + FN) > 0
        else float("nan")
    )

    specificity = (
        TN / (TN + FP)
        if (TN + FP) > 0
        else float("nan")
    )

    ppv = (
        TP / (TP + FP)
        if (TP + FP) > 0
        else float("nan")
    )

    npv = (
        TN / (TN + FN)
        if (TN + FN) > 0
        else float("nan")
    )

    f1 = (
        2 * TP / (2 * TP + FP + FN)
        if (2 * TP + FP + FN) > 0
        else float("nan")
    )

    balanced_accuracy = (
        sensitivity + specificity
    ) / 2

    return {
        "ratio_threshold": ratio_threshold,
        "persistence": persistence,
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "TN": TN,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "ppv": ppv,
        "npv": npv,
        "f1": f1,
        "balanced_accuracy": balanced_accuracy,
    }

def predict_persistent_ratio(
    cases: list[dict],
    baseline_years_by_case: dict,
    ratio_threshold: float,
    persistence: int,
) -> pd.DataFrame:
    frames = []

    for case in cases:
        region = case["region"]
        year = case["year"]
        key = (region, year)

        weekly = (
            case["weekly_observed"]
            .sort_values("epi_week")
            .copy()
        )

        reference = (
            build_reference_selected_years(
                historical_weekly=case["historical_weekly"],
                years=baseline_years_by_case[key],
                quantile=0.75,
            )
        )

        evaluated = (
            weekly[
                [
                    "epi_week",
                    "record_count", 
                ]
            ]
            .merge(
                reference[
                    [
                        "epi_week",
                        "historical_median",
                    ]
                ],
                on="epi_week",
                how="left",
            )
            .sort_values("epi_week")
        )

        evaluated["ratio_to_median"] = (
            evaluated["record_count"]
            / evaluated["historical_median"]
        )

        evaluated["above_ratio"] = (
            evaluated["ratio_to_median"]
            >= ratio_threshold
        )

        evaluated["sentinela_positive"] = (
            evaluated["above_ratio"]
            .rolling(
                window=persistence,
                min_periods=persistence,
            )
            .sum()
            .eq(persistence)
        )

        evaluated["region"] = region
        evaluated["year"] = year

        frames.append(evaluated)
    
    return pd.concat(
        frames,
        ignore_index=True,
    )

def predict_signal_and_alert(
    cases: list[dict],
    baseline_years_by_case: dict,
    ratio_threshold: float = 1.15,
    persistence: int = 2,
) -> pd.DataFrame:
    frames = []

    for case in cases:
        region = case["region"]
        year = case["year"]
        key = (region, year)

        weekly = (
            case["weekly_observed"]
            .sort_values("epi_week")
            .copy()
        )

        reference = (
            build_reference_selected_years(
                historical_weekly=case["historical_weekly"],
                years=baseline_years_by_case[key],
                quantile=0.75,
            )
        )

        evaluated = (
            weekly[
                [
                    "epi_week",
                    "record_count",
                ]
            ]
            .merge(
                reference[
                    [
                        "epi_week",
                        "historical_median",
                    ]
                ],
                on="epi_week",
                how="left",
            )
            .sort_values("epi_week")
        )

        evaluated["ratio_to_median"] = (
            evaluated["record_count"]
            / evaluated["historical_median"]
        )

        evaluated["signal_detected"] = (
            evaluated["ratio_to_median"]
            >= ratio_threshold
        )

        evaluated["alert_confirmed"] = (
            evaluated["signal_detected"]
            .rolling(
                window=persistence,
                min_periods=persistence,
            )
            .sum()
            .eq(persistence)
        )

        evaluated["region"] = region
        evaluated["year"] = year

        frames.append(evaluated)

    return pd.concat(
        frames,
        ignore_index=True,
    )

def build_week_nowcast_timeline(
    temporal_df: pd.DataFrame,
    week_start: pd.Timestamp,
    week_end: pd.Timestamp,
    epi_week: int,
    historical_median: float,
    completion_model: pd.DataFrame,
    min_completeness: float = 0.80,
    max_lag: int = 28,
) -> pd.DataFrame:
    week_cases = temporal_df.loc[
        temporal_df["DT_SIN_PRI"].between(
            week_start,
            week_end,
        )
    ].copy()

    rows = []

    for lag in range(0, max_lag + 1):
        completion_row = completion_model.loc[
            completion_model["lag_days"].eq(lag)
        ]

        if completion_row.empty:
            continue

        completeness = float(
            completion_row[
                "expected_completeness"
            ].iloc[0]
        )

        snapshot_date = (
            week_end
            + pd.Timedelta(days=lag)
        )

        known_cases = int(
            (
                week_cases["DT_NOTIFIC"]
                <= snapshot_date
            ).sum()
        )

        if completeness > 0:
            nowcast = (
                known_cases
                / completeness
            )
        else:
            nowcast = float("nan")

        ratio_to_median = (
            nowcast
            / historical_median
        )

        is_mature = (
            completeness
            >= min_completeness
        )

        signal_detected = (
            is_mature
            and ratio_to_median >= 1.15
        )

        rows.append(
            {
                "epi_week": epi_week,
                "lag_days": lag,
                "snapshot_date": snapshot_date,
                "known_cases": known_cases,
                "expected_completeness": completeness,
                "is_mature": is_mature,
                "nowcast": nowcast,
                "historical_median": historical_median,
                "ratio_to_median": ratio_to_median,
                "signal_detected": signal_detected,
            }
        )

    return pd.DataFrame(rows)

def load_notification_delays(
    path: Path,
    region: str,
    source_year: int,
) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
        usecols=[
            "SG_UF",
            "DT_SIN_PRI",
            "DT_NOTIFIC",
        ],
        dtype="string",
        low_memory=False,
    )

    df["SG_UF"] = (
        df["SG_UF"]
        .str.strip()
        .str.upper()
    )

    df = df.loc[
        df["SG_UF"].eq(region)
    ].copy()

    for column in [
        "DT_SIN_PRI",
        "DT_NOTIFIC",
    ]:
        df[column] = (
            pd.to_datetime(
                df[column],
                format="ISO8601",
                errors="coerce",
                utc=True,
            )
            .dt.tz_localize(None)
        )

    df["delay_days"] = (
        df["DT_NOTIFIC"]
        - df["DT_SIN_PRI"]
    ).dt.days

    df["source_year"] = source_year

    return df

def load_notification_delays_sp(
    path: Path,
    source_year: int,
) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
        usecols=[
            "SG_UF",
            "DT_SIN_PRI",
            "DT_NOTIFIC",
        ],
        dtype="string",
        low_memory=False,
    )

    df["SG_UF"] = (
        df["SG_UF"]
        .str.strip()
        .str.upper()
    )

    df = df.loc[
        df["SG_UF"].eq("SP")
    ].copy()

    for column in [
        "DT_SIN_PRI",
        "DT_NOTIFIC",
    ]:
        df[column] = (
            pd.to_datetime(
                df[column],
                format="ISO8601",
                errors="coerce",
                utc=True,
            )
            .dt.tz_localize(None)
        )

    df["delay_days"] = (
        df["DT_NOTIFIC"]
        - df["DT_SIN_PRI"]
    ).dt.days

    df["source_year"] = source_year

    return df

def build_uncertainty_nowcast_timeline(
    temporal_df: pd.DataFrame,
    week_start: pd.Timestamp,
    week_end: pd.Timestamp,
    epi_week: int,
    historical_median: float,
    completion_model: pd.DataFrame,
    ratio_threshold: float = 1.15,
    mature_completeness: float = 0.80,
    min_early_completeness: float = 0.30,
    max_lag: int = 28,
) -> pd.DataFrame:
    week_cases = temporal_df.loc[
        temporal_df["DT_SIN_PRI"].between(
            week_start,
            week_end,
        )
    ].copy()

    rows = []

    for lag in range(max_lag + 1):
        completion_row = completion_model.loc[
            completion_model["lag_days"].eq(lag)
        ]

        if completion_row.empty:
            continue

        expected = float(
            completion_row[
                "expected_completeness"
            ].iloc[0]
        )

        q75 = float(
            completion_row[
                "completeness_q75"
            ].iloc[0]
        )

        snapshot_date = (
            week_end
            + pd.Timedelta(days=lag)
        )

        known_cases = int(
            (
                week_cases["DT_NOTIFIC"]
                <= snapshot_date
            ).sum()
        )

        if expected <= 0 or q75 <= 0:
            continue

        nowcast = (
            known_cases
            / expected
        )

        conservative_nowcast = (
            known_cases
            / q75
        )

        ratio = (
            nowcast
            / historical_median
        )

        conservative_ratio = (
            conservative_nowcast
            / historical_median
        )

        is_mature = (
            expected
            >= mature_completeness
        )

        has_minimum_information = (
            expected
            >= min_early_completeness
        )

        # Regra:
        # - se maduro, usa estimativa central;
        # - se ainda imaturo, exige que até
        #   o cenário conservador ultrapasse
        #   o threshold.
        if is_mature:
            signal_detected = (
                ratio >= ratio_threshold
            )

            signal_mode = (
                "MATURE"
                if signal_detected
                else "NONE"
            )

        elif has_minimum_information:
            signal_detected = (
                conservative_ratio
                >= ratio_threshold
            )

            signal_mode = (
                "EARLY_CONSERVATIVE"
                if signal_detected
                else "NONE"
            )

        else:
            signal_detected = False
            signal_mode = "INSUFFICIENT_DATA"

        rows.append(
            {
                "epi_week": epi_week,
                "lag_days": lag,
                "snapshot_date": snapshot_date,
                "known_cases": known_cases,
                "expected_completeness": expected,
                "completeness_q75": q75,
                "is_mature": is_mature,
                "nowcast": nowcast,
                "conservative_nowcast":
                    conservative_nowcast,
                "historical_median":
                    historical_median,
                "ratio_to_median": ratio,
                "conservative_ratio":
                    conservative_ratio,
                "signal_detected":
                    signal_detected,
                "signal_mode":
                    signal_mode,
            }
        )

    return pd.DataFrame(rows)

def get_completion_at_age(
    completion_model: pd.DataFrame,
    age_days: int,
    column: str,
) -> float:
    age_days = max(age_days, 0)

    max_lag = int(
        completion_model["lag_days"].max()
    )

    age_days = min(
        age_days,
        max_lag,
    )

    row = completion_model.loc[
        completion_model[
            "lag_days"
        ].eq(age_days)
    ]

    if row.empty:
        return float("nan")

    return float(
        row[column].iloc[0]
    )

def calculate_age_adjusted_nowcast(
    week_cases: pd.DataFrame,
    snapshot_date: pd.Timestamp,
    completion_model: pd.DataFrame,
    completion_column: str,
) -> float:
    known_cases = week_cases.loc[
        week_cases[
            "DT_NOTIFIC"
        ].le(snapshot_date)
    ].copy()

    if known_cases.empty:
        return 0.0

    known_cases["age_days"] = (
        snapshot_date
        - known_cases["DT_SIN_PRI"]
    ).dt.days

    completion_by_age = {
        age: get_completion_at_age(
            completion_model=completion_model,
            age_days=int(age),
            column=completion_column,
        )
        for age in known_cases["age_days"].unique()
    }

    known_cases["completion_probability"] = (
        known_cases["age_days"].map(completion_by_age)
    )

    known_cases = known_cases.loc[
        known_cases[
            "completion_probability"
        ].notna()
        & known_cases[
            "completion_probability"
        ].gt(0)
    ]

    return (
        1
        / known_cases[
            "completion_probability"
        ]
    ).sum()

def build_age_adjusted_nowcast_timeline(
    temporal_df: pd.DataFrame,
    week_start: pd.Timestamp,
    week_end: pd.Timestamp,
    epi_week: int,
    historical_median: float,
    completion_model: pd.DataFrame,
    ratio_threshold: float = 1.15,
    min_early_completeness: float = 0.30,
    mature_completeness: float = 0.80,
    max_lag: int = 28,
) -> pd.DataFrame:
    week_cases = temporal_df.loc[
        temporal_df[
            "DT_SIN_PRI"
        ].between(
            week_start,
            week_end,
        )
    ].copy()

    rows = []

    for lag in range(
        max_lag + 1
    ):
        snapshot_date = (
            week_end
            + pd.Timedelta(
                days=lag
            )
        )

        known = week_cases.loc[
            week_cases[
                "DT_NOTIFIC"
            ].le(snapshot_date)
        ]

        known_cases = len(known)

        central_nowcast = (
            calculate_age_adjusted_nowcast(
                week_cases=week_cases,
                snapshot_date=snapshot_date,
                completion_model=completion_model,
                completion_column=(
                    "expected_completeness"
                ),
            )
        )

        conservative_nowcast = (
            calculate_age_adjusted_nowcast(
                week_cases=week_cases,
                snapshot_date=snapshot_date,
                completion_model=completion_model,
                completion_column=(
                    "completeness_q75"
                ),
            )
        )

        central_ratio = (
            central_nowcast
            / historical_median
        )

        conservative_ratio = (
            conservative_nowcast
            / historical_median
        )

        completion_row = (
            completion_model.loc[
                completion_model[
                    "lag_days"
                ].eq(lag)
            ]
        )

        expected_completion = float(
            completion_row[
                "expected_completeness"
            ].iloc[0]
        )

        if (
            expected_completion
            >= mature_completeness
        ):
            signal_detected = (
                central_ratio
                >= ratio_threshold
            )

            signal_mode = (
                "MATURE"
                if signal_detected
                else "NONE"
            )

        elif (
            expected_completion
            >= min_early_completeness
        ):
            signal_detected = (
                conservative_ratio
                >= ratio_threshold
            )

            signal_mode = (
                "EARLY_CONSERVATIVE"
                if signal_detected
                else "NONE"
            )

        else:
            signal_detected = False
            signal_mode = (
                "INSUFFICIENT_DATA"
            )

        rows.append(
            {
                "epi_week":
                    epi_week,
                "lag_days":
                    lag,
                "snapshot_date":
                    snapshot_date,
                "known_cases":
                    known_cases,
                "expected_completeness":
                    expected_completion,
                "age_adjusted_nowcast":
                    central_nowcast,
                "conservative_nowcast":
                    conservative_nowcast,
                "historical_median":
                    historical_median,
                "ratio_to_median":
                    central_ratio,
                "conservative_ratio":
                    conservative_ratio,
                "signal_detected":
                    signal_detected,
                "signal_mode":
                    signal_mode,
            }
        )

    return pd.DataFrame(rows)

def classify_early_outcome(row):
    if pd.isna(row["ground_truth"]):
        return "UNLABELED"

    truth = int(row["ground_truth"])
    predicted = bool(
        row["signal_detected"]
    )

    if truth == 1 and predicted:
        return "TP"

    if truth == 1 and not predicted:
        return "FN"

    if truth == 0 and predicted:
        return "FP"

    return "TN"

def evaluate_early_signal_case(
    temporal_df: pd.DataFrame,
    weeks_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    completion_model: pd.DataFrame,
    ground_truth_by_week: dict[int, int],
    ratio_threshold: float = 1.15,
    min_early_completeness: float = 0.30,
    mature_completeness: float = 0.80,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    timeline_frames = []

    for week in weeks_df.itertuples(
        index=False
    ):
        reference_row = (
            reference_df.loc[
                reference_df[
                    "epi_week"
                ].eq(week.epi_week)
            ]
        )

        if reference_row.empty:
            continue

        historical_median = float(
            reference_row[
                "historical_median"
            ].iloc[0]
        )

        timeline = (
            build_age_adjusted_nowcast_timeline(
                temporal_df=temporal_df,
                week_start=week.week_start,
                week_end=week.week_end,
                epi_week=week.epi_week,
                historical_median=(
                    historical_median
                ),
                completion_model=(
                    completion_model
                ),
                ratio_threshold=(
                    ratio_threshold
                ),
                min_early_completeness=(
                    min_early_completeness
                ),
                mature_completeness=(
                    mature_completeness
                ),
            )
        )

        timeline_frames.append(
            timeline
        )

    timeline_all = pd.concat(
        timeline_frames,
        ignore_index=True,
    )

    first_signal = (
        timeline_all.loc[
            timeline_all[
                "signal_detected"
            ]
        ]
        .sort_values(
            [
                "epi_week",
                "snapshot_date",
            ]
        )
        .groupby(
            "epi_week",
            as_index=False,
        )
        .first()
    )

    evaluation = (
        weeks_df[
            [
                "epi_week",
                "week_start",
                "week_end",
            ]
        ]
        .merge(
            first_signal[
                [
                    "epi_week",
                    "lag_days",
                    "snapshot_date",
                    "ratio_to_median",
                    "conservative_ratio",
                    "signal_mode",
                ]
            ],
            on="epi_week",
            how="left",
        )
    )

    evaluation[
        "signal_detected"
    ] = (
        evaluation[
            "snapshot_date"
        ].notna()
    )

    evaluation[
        "ground_truth"
    ] = (
        evaluation[
            "epi_week"
        ]
        .map(
            ground_truth_by_week
        )
        .astype("Int64")
    )

    evaluation[
        "outcome"
    ] = (
        evaluation.apply(
            classify_early_outcome,
            axis=1,
        )
    )

    return (
        timeline_all,
        evaluation,
    )

def build_weekly_history_for_region(
    historical_files,
    region: str,
    years: list[int],
) -> pd.DataFrame:
    frames = []

    for path in historical_files:
        name = path.name.upper()

        source_year = int(
            f"20{name.split('INFLUD')[1][:2]}"
        )

        if source_year not in years:
            continue

        df = pd.read_csv(
            path,
            sep=";",
            encoding="latin-1",
            usecols=[
                "SG_UF",
                "DT_SIN_PRI",
            ],
            dtype="string",
            low_memory=False,
        )

        df["SG_UF"] = (
            df["SG_UF"]
            .str.strip()
            .str.upper()
        )

        df = df.loc[
            df["SG_UF"].eq(region)
        ].copy()

        df["DT_SIN_PRI"] = (
            pd.to_datetime(
                df["DT_SIN_PRI"],
                format="ISO8601",
                errors="coerce",
                utc=True,
            )
            .dt.tz_localize(None)
        )

        df = df.loc[
            df["DT_SIN_PRI"].notna()
        ].copy()

        #
        # Importante:
        # usamos calendário epidemiológico
        # no padrão domingo-sábado.
        #
        df["epi_week"] = (
            df["DT_SIN_PRI"]
            .dt.strftime("%U")
            .astype(int)
            + 1
        )

        #
        # Mantém apenas as semanas
        # epidemiológicas válidas.
        #
        df = df.loc[
            df["epi_week"].between(
                1,
                53,
            )
        ].copy()

        weekly = (
            df.groupby(
                "epi_week",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "record_count",
                }
            )
        )

        weekly["source_year"] = (
            source_year
        )

        weekly["region"] = region

        frames.append(weekly)

    if not frames:
        raise ValueError(
            f"Nenhum dado encontrado "
            f"para {region} nos anos {years}."
        )

    result = pd.concat(
        frames,
        ignore_index=True,
    )

    result = (
        result[
            [
                "source_year",
                "epi_week",
                "record_count",
                "region",
            ]
        ]
        .sort_values(
            [
                "source_year",
                "epi_week",
            ]
        )
        .reset_index(drop=True)
    )

    return result

def get_epi_week(
    date: pd.Timestamp,
    epi_year: int,
) -> int | None:
    first_sunday = pd.Timestamp(
        f"{epi_year - 1}-12-28"
    )

    delta_days = (
        date.normalize()
        - first_sunday
    ).days

    epi_week = (
        delta_days // 7
        + 1
    )

    if 1 <= epi_week <= 53:
        return epi_week

    return None

def build_epi_calendar_for_year(
    year: int,
) -> pd.DataFrame:
    jan4 = pd.Timestamp(
        year=year,
        month=1,
        day=4,
    )

    #
    # Domingo imediatamente anterior
    # ou igual a 4 de janeiro.
    #
    days_since_sunday = (
        jan4.dayofweek + 1
    ) % 7

    first_week_start = (
        jan4
        - pd.Timedelta(
            days=days_since_sunday
        )
    )

    weeks = []

    for epi_week in range(1, 54):
        week_start = (
            first_week_start
            + pd.Timedelta(
                days=(epi_week - 1) * 7
            )
        )

        week_end = (
            week_start
            + pd.Timedelta(days=6)
        )

        weeks.append(
            {
                "epi_year": year,
                "epi_week": epi_week,
                "week_start": week_start,
                "week_end": week_end,
            }
        )

    return pd.DataFrame(weeks)

def assign_epi_week_from_calendar(
    dates: pd.Series,
    year: int,
) -> pd.Series:
    calendar = (
        build_epi_calendar_for_year(
            year
        )
    )

    result = pd.Series(
        pd.NA,
        index=dates.index,
        dtype="Int64",
    )

    for row in calendar.itertuples(
        index=False
    ):
        mask = dates.between(
            row.week_start,
            row.week_end,
        )

        result.loc[mask] = (
            row.epi_week
        )

    return result

def build_weekly_history_for_region(
    historical_files,
    region: str,
    years: list[int],
) -> pd.DataFrame:
    frames = []

    for path in historical_files:
        name = path.name.upper()

        source_year = int(
            f"20{name.split('INFLUD')[1][:2]}"
        )

        if source_year not in years:
            continue

        df = pd.read_csv(
            path,
            sep=";",
            encoding="latin-1",
            usecols=[
                "SG_UF",
                "DT_SIN_PRI",
            ],
            dtype="string",
            low_memory=False,
        )

        df["SG_UF"] = (
            df["SG_UF"]
            .str.strip()
            .str.upper()
        )

        df = df.loc[
            df["SG_UF"].eq(region)
        ].copy()

        df["DT_SIN_PRI"] = (
            pd.to_datetime(
                df["DT_SIN_PRI"],
                format="ISO8601",
                errors="coerce",
                utc=True,
            )
            .dt.tz_localize(None)
        )

        df = df.loc[
            df["DT_SIN_PRI"].notna()
        ].copy()

        df["epi_week"] = (
            assign_epi_week_from_calendar(
                dates=df["DT_SIN_PRI"],
                year=source_year,
            )
        )

        df = df.loc[
            df["epi_week"].notna()
        ].copy()

        weekly = (
            df.groupby(
                "epi_week",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size":
                        "record_count",
                }
            )
        )

        weekly[
            "source_year"
        ] = source_year

        weekly[
            "region"
        ] = region

        frames.append(
            weekly
        )

    if not frames:
        raise ValueError(
            f"Nenhum dado encontrado "
            f"para região {region}."
        )

    return (
        pd.concat(
            frames,
            ignore_index=True,
        )
        [
            [
                "source_year",
                "epi_week",
                "record_count",
                "region",
            ]
        ]
        .sort_values(
            [
                "source_year",
                "epi_week",
            ]
        )
        .reset_index(drop=True)
    )

def rolling_log_slope(
    series: pd.Series,
    window: int = 4,
) -> pd.Series:
    values = series.to_numpy(
        dtype=float
    )

    result = np.full(
        len(values),
        np.nan,
    )

    x = np.arange(
        window,
        dtype=float,
    )

    for i in range(
        window - 1,
        len(values),
    ):
        y = values[
            i - window + 1:
            i + 1
        ]

        slope = np.polyfit(
            x,
            y,
            1,
        )[0]

        result[i] = slope

    return pd.Series(
        result,
        index=series.index,
    )

def add_trend_features(
    weekly_df: pd.DataFrame,
    window: int = 4,
) -> pd.DataFrame:
    df = weekly_df.sort_values(
        "epi_week"
    ).copy()

    df["log_count"] = np.log1p(
        df["record_count"]
    )

    df["slope_4w"] = (
        rolling_log_slope(
            df["log_count"],
            window=window,
        )
    )

    df["weekly_growth_rate"] = (
        np.exp(df["slope_4w"]) - 1
    )

    df["week_over_week_growth"] = (
        df["record_count"]
        .pct_change()
    )

    df["positive_growth"] = (
        df["week_over_week_growth"] > 0
    )

    df["positive_growth_3of4"] = (
        df["positive_growth"]
        .rolling(
            window,
            min_periods=window,
        )
        .sum()
        >= 3
    )

    return df

def classify_combined(row):
    if pd.isna(
        row["ground_truth"]
    ):
        return "UNLABELED"

    truth = int(
        row["ground_truth"]
    )

    predicted = bool(
        row["combined_signal"]
    )

    if truth == 1 and predicted:
        return "TP"

    if truth == 1 and not predicted:
        return "FN"

    if truth == 0 and predicted:
        return "FP"

    return "TN"

def positive_cusum(
    series: pd.Series,
    drift: float = 0.0,
) -> pd.Series:
    values = (
        series
        .fillna(0.0)
        .to_numpy(dtype=float)
    )

    result = np.zeros(
        len(values),
        dtype=float,
    )

    running = 0.0

    for i, value in enumerate(values):
        running = max(
            0.0,
            running + value - drift,
        )

        result[i] = running

    return pd.Series(
        result,
        index=series.index,
    )

def build_cusum_for_year(
    historical_weekly: pd.DataFrame,
    target_year: int,
    baseline_years: list[int],
) -> pd.DataFrame:
    target = (
        historical_weekly.loc[
            historical_weekly["epi_year"].eq(
                target_year
            )
        ][
            [
                "epi_year",
                "epi_week",
                "record_count",
            ]
        ]
        .copy()
    )

    baseline = (
        historical_weekly.loc[
            historical_weekly["epi_year"].isin(
                baseline_years
            )
        ]
        .groupby(
            "epi_week",
            as_index=False,
        )
        .agg(
            historical_median=(
                "record_count",
                "median",
            )
        )
    )

    target = target.merge(
        baseline,
        on="epi_week",
        how="left",
    )

    target["ratio"] = (
        target["record_count"]
        / target["historical_median"]
    )

    target["log_ratio"] = np.log(
        target["ratio"]
    )

    target["delta_log_ratio"] = (
        target["log_ratio"]
        .diff()
    )

    target["cusum_positive"] = (
        positive_cusum(
            target["delta_log_ratio"],
            drift=0.0,
        )
    )

    return target

def build_local_cusum_reference(
    historical_cusum: pd.DataFrame,
    window_radius: int = 2,
) -> pd.DataFrame:
    rows = []

    for epi_week in range(1, 53):
        low = max(
            1,
            epi_week - window_radius,
        )

        high = min(
            52,
            epi_week + window_radius,
        )

        values = (
            historical_cusum.loc[
                historical_cusum[
                    "epi_week"
                ].between(
                    low,
                    high,
                ),
                "cusum_positive",
            ]
            .dropna()
        )

        if values.empty:
            continue

        rows.append(
            {
                "epi_week": epi_week,
                "historical_cusum_median":
                    values.median(),
                "historical_cusum_q90":
                    values.quantile(0.90),
                "historical_cusum_q95":
                    values.quantile(0.95),
                "historical_cusum_max":
                    values.max(),
                "historical_samples":
                    len(values),
            }
        )

    return pd.DataFrame(rows)

def rolling_positive_cusum(
    series: pd.Series,
    window: int = 4,
) -> pd.Series:
    values = (
        series
        .fillna(0.0)
        .to_numpy(dtype=float)
    )

    result = np.full(
        len(values),
        np.nan,
    )

    for i in range(
        window - 1,
        len(values),
    ):
        local = values[
            i - window + 1:
            i + 1
        ]

        running = 0.0

        for value in local:
            running = max(
                0.0,
                running + value,
            )

        result[i] = running

    return pd.Series(
        result,
        index=series.index,
    )
