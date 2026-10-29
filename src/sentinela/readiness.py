import pandas as pd

from sentinela.config import (
    REGIONS,
    READINESS_REFERENCE_START,
    READINESS_REFERENCE_END,
    READINESS_RATIO,
    MIN_READY_STATE_FRACTION,
)


def calculate_readiness(
    weekly_by_region: dict[str, pd.DataFrame],
):

    weekly = pd.concat(
        weekly_by_region.values(),
        ignore_index=True,
    )

    reference = (
        weekly.loc[
            weekly["epi_week"].between(
                READINESS_REFERENCE_START,
                READINESS_REFERENCE_END,
            )
        ]
        .groupby("region")["flu_tests"]
        .median()
        .rename("reference_tests")
        .reset_index()
    )

    max_week = int(
        weekly["epi_week"].max()
    )

    weeks = range(
        READINESS_REFERENCE_END + 1,
        max_week + 1,
    )

    grid = (
        pd.MultiIndex.from_product(
            [
                REGIONS,
                weeks,
            ],
            names=[
                "region",
                "epi_week",
            ],
        )
        .to_frame(index=False)
    )

    grid = (
        grid
        .merge(
            weekly[
                [
                    "region",
                    "epi_week",
                    "flu_tests",
                ]
            ],
            on=[
                "region",
                "epi_week",
            ],
            how="left",
        )
        .merge(
            reference,
            on="region",
            how="left",
        )
    )

    # Zero somente para o gate,
    # nunca como positividade observada.
    grid["flu_tests"] = (
        grid["flu_tests"]
        .fillna(0)
    )

    denominator = (
        grid["reference_tests"]
        .replace(0, pd.NA)
    )

    grid["test_volume_ratio"] = (
        grid["flu_tests"]
        / denominator
    )

    grid["state_ready"] = (
        grid["test_volume_ratio"]
        .ge(READINESS_RATIO)
        .fillna(False)
    )

    summary = (
        grid
        .groupby(
            "epi_week",
            as_index=False,
        )
        .agg(
            states=(
                "region",
                "nunique",
            ),
            ready_states=(
                "state_ready",
                "sum",
            ),
            median_volume_ratio=(
                "test_volume_ratio",
                "median",
            ),
        )
    )

    summary[
        "ready_state_fraction"
    ] = (
        summary["ready_states"]
        / len(REGIONS)
    )

    summary[
        "snapshot_ready"
    ] = (
        summary[
            "ready_state_fraction"
        ]
        .ge(
            MIN_READY_STATE_FRACTION
        )
    )

    ready = summary.loc[
        summary["snapshot_ready"],
        "epi_week",
    ]

    latest_ready_week = (
        None
        if ready.empty
        else int(ready.max())
    )

    return (
        grid,
        summary,
        latest_ready_week,
    )
