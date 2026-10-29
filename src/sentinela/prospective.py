import pandas as pd

from sentinela.config import (
    ALPHA,
    WEEK_START,
    MIN_WEEKS_EACH_SIDE,
    MAX_CHANGE_POINTS,
)

from sentinela.detector import (
    detect_recursive_length_calibrated,
)


def run_prospective_week(
    prospective_weekly,
    epi_year,
    current_week,
):
    rows = []

    for region, weekly in (
        prospective_weekly.items()
    ):

        observed_years = (
            weekly["epi_year"]
            .dropna()
            .unique()
        )

        if (
            len(observed_years) != 1
            or int(observed_years[0])
            != epi_year
        ):
            raise ValueError(
                f"{region}: ano incompatível: "
                f"{observed_years}"
            )

        partial = weekly.loc[
            weekly["epi_week"].between(
                WEEK_START,
                current_week,
            )
        ].copy()

        detected = (
            detect_recursive_length_calibrated(
                weekly_df=partial,
                alpha=ALPHA,
                week_start=WEEK_START,
                week_end=current_week,
                min_weeks_each_side=
                    MIN_WEEKS_EACH_SIDE,
                max_change_points=
                    MAX_CHANGE_POINTS,
            )
        )

        if detected.empty:
            continue

        detected["region"] = region
        rows.append(detected)

    if not rows:
        return pd.DataFrame()

    return pd.concat(
        rows,
        ignore_index=True,
    )
