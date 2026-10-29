import math

import pandas as pd

from sentinela.config import LENGTH_THRESHOLDS


def bernoulli_log_likelihood(
    positives: int,
    tests: int,
) -> float:
    """
    Log-verossimilhança binomial/Bernoulli para dados agregados.

    positives:
        Número de testes positivos.

    tests:
        Número total de testes.
    """

    if tests <= 0:
        raise ValueError(
            "tests deve ser maior que zero"
        )

    if positives < 0:
        raise ValueError(
            "positives não pode ser negativo"
        )

    if positives > tests:
        raise ValueError(
            "positives não pode ser maior que tests"
        )

    p = positives / tests

    if p == 0:
        return 0.0

    if p == 1:
        return 0.0

    negatives = tests - positives

    return (
        positives * math.log(p)
        +
        negatives * math.log(1 - p)
    )


def detect_flu_change_point(
    weekly_df: pd.DataFrame,
    week_start: int = 8,
    week_end: int = 26,
    min_weeks_each_side: int = 3,
) -> pd.DataFrame:

    data = (
        weekly_df.loc[
            weekly_df["epi_week"].between(
                week_start,
                week_end,
            )
        ]
        .sort_values("epi_week")
        .reset_index(drop=True)
        .copy()
    )

    columns = [
        "split_after_week",
        "next_week",
        "left_positivity",
        "right_positivity",
        "llr",
    ]

    if len(data) < (
        2 * min_weeks_each_side
    ):
        return pd.DataFrame(
            columns=columns
        )

    total_positive = int(
        data["flu_positive"].sum()
    )

    total_tests = int(
        data["flu_tests"].sum()
    )

    if total_tests <= 0:
        return pd.DataFrame(
            columns=columns
        )

    null_ll = bernoulli_log_likelihood(
        positives=total_positive,
        tests=total_tests,
    )

    results = []

    for split_idx in range(
        min_weeks_each_side,
        len(data)
        - min_weeks_each_side
        + 1,
    ):
        left = data.iloc[:split_idx]
        right = data.iloc[split_idx:]

        left_positive = int(
            left["flu_positive"].sum()
        )

        left_tests = int(
            left["flu_tests"].sum()
        )

        right_positive = int(
            right["flu_positive"].sum()
        )

        right_tests = int(
            right["flu_tests"].sum()
        )

        if (
            left_tests <= 0
            or right_tests <= 0
        ):
            continue

        alternative_ll = (
            bernoulli_log_likelihood(
                positives=left_positive,
                tests=left_tests,
            )
            +
            bernoulli_log_likelihood(
                positives=right_positive,
                tests=right_tests,
            )
        )

        llr = 2 * (
            alternative_ll
            - null_ll
        )

        results.append(
            {
                "split_after_week": int(
                    left[
                        "epi_week"
                    ].iloc[-1]
                ),
                "next_week": int(
                    right[
                        "epi_week"
                    ].iloc[0]
                ),
                "left_positivity": (
                    left_positive
                    / left_tests
                ),
                "right_positivity": (
                    right_positive
                    / right_tests
                ),
                "llr": float(llr),
            }
        )

    if not results:
        return pd.DataFrame(
            columns=columns
        )

    return (
        pd.DataFrame(results)
        .sort_values(
            "llr",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def get_length_threshold(
    segment_length: int,
    alpha: str = "P99",
) -> float:

    if alpha not in {
        "P95",
        "P99",
        "P995",
    }:
        raise ValueError(
            f"Alpha inválido: {alpha}"
        )

    thresholds = (
        LENGTH_THRESHOLDS.get(
            segment_length
        )
    )

    if thresholds is None:
        raise ValueError(
            "Nenhum threshold calibrado "
            f"para segmento de tamanho "
            f"{segment_length}"
        )

    return float(
        thresholds[alpha]
    )


def detect_recursive_length_calibrated(
    weekly_df: pd.DataFrame,
    alpha: str = "P99",
    week_start: int = 8,
    week_end: int = 40,
    min_weeks_each_side: int = 3,
    max_change_points: int = 5,
) -> pd.DataFrame:

    segments = [
        (
            week_start,
            week_end,
        )
    ]

    detected = []

    while segments:

        candidates = []

        for (
            segment_start,
            segment_end,
        ) in segments:

            segment_length = (
                segment_end
                - segment_start
                + 1
            )

            if (
                segment_length
                <
                2 * min_weeks_each_side
            ):
                continue

            result = (
                detect_flu_change_point(
                    weekly_df=weekly_df,
                    week_start=
                        segment_start,
                    week_end=
                        segment_end,
                    min_weeks_each_side=
                        min_weeks_each_side,
                )
            )

            if result.empty:
                continue

            # IMPORTANTE:
            # seleciona o melhor split
            # DESTE segmento.
            best_idx = (
                result["llr"]
                .astype(float)
                .idxmax()
            )

            best = result.loc[
                best_idx
            ]

            left_positivity = float(
                best[
                    "left_positivity"
                ]
            )

            right_positivity = float(
                best[
                    "right_positivity"
                ]
            )

            direction = (
                "UP"
                if (
                    right_positivity
                    > left_positivity
                )
                else "DOWN"
            )

            threshold = (
                get_length_threshold(
                    segment_length=
                        segment_length,
                    alpha=alpha,
                )
            )

            llr = float(
                best["llr"]
            )

            if llr < threshold:
                continue

            candidates.append(
                {
                    "segment_start":
                        segment_start,

                    "segment_end":
                        segment_end,

                    "segment_length":
                        segment_length,

                    "change_week":
                        int(
                            best[
                                "next_week"
                            ]
                        ),

                    "direction":
                        direction,

                    "left_positivity":
                        left_positivity,

                    "right_positivity":
                        right_positivity,

                    "absolute_change":
                        (
                            right_positivity
                            -
                            left_positivity
                        ),

                    "llr":
                        llr,

                    "threshold":
                        threshold,
                }
            )

        if not candidates:
            break

        strongest = max(
            candidates,
            key=lambda x: x["llr"],
        )

        detected.append(
            strongest
        )

        if (
            len(detected)
            >= max_change_points
        ):
            break

        old_segment = (
            strongest[
                "segment_start"
            ],
            strongest[
                "segment_end"
            ],
        )

        segments.remove(
            old_segment
        )

        change_week = int(
            strongest[
                "change_week"
            ]
        )

        left = (
            old_segment[0],
            change_week - 1,
        )

        right = (
            change_week,
            old_segment[1],
        )

        left_length = (
            left[1]
            - left[0]
            + 1
        )

        right_length = (
            right[1]
            - right[0]
            + 1
        )

        if (
            left_length
            >=
            2 * min_weeks_each_side
        ):
            segments.append(
                left
            )

        if (
            right_length
            >=
            2 * min_weeks_each_side
        ):
            segments.append(
                right
            )

    return pd.DataFrame(
        detected
    )


__all__ = [
    "bernoulli_log_likelihood",
    "detect_flu_change_point",
    "get_length_threshold",
    "detect_recursive_length_calibrated",
]
