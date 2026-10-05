import pandas as pd

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)


class NowcastService:
    def __init__(
        self,
        repository: EpidemiologicalRepository,
    ):
        self.repository = repository

    def get_nowcast(
        self,
        region: str,
        year: int,
    ) -> list[dict]:
        region = region.strip().upper()

        if not self.repository.dataset_exists(
            region=region,
            year=year,
        ):
            return []

        
        df = self.repository.get_nowcast(
            region=region,
            year=year,
        )

        required_columns = {
            "epi_week",
            "lag_days",
            "snapshot_date",
            "known_cases",
            "nowcast",
            "q75",
            "median_threshold",
            "would_signal",
        }

        missing_columns = (
            required_columns
            - set(df.columns)
        )

        if missing_columns:
            raise ValueError(
                "Colunas obrigatórias ausentes no nowcast: "
                f"{sorted(missing_columns)}"
            )

        df["would_signal"] = (
            df["would_signal"]
            .astype(str)
            .str.lower()
            .eq("true")
        )

        signals = (
            df.loc[df["would_signal"]]
            .sort_values(
                [
                    "epi_week",
                    "lag_days",
                ]
            )
            .groupby(
                "epi_week",
                as_index=False,
            )
            .first()
        )

        return [
            {
                "epi_week": int(row.epi_week),
                "lag_days": int(row.lag_days),
                "snapshot_date": row.snapshot_date,
                "known_cases": int(
                    row.known_cases
                ),
                "nowcast": float(row.nowcast),
                "q75": float(row.q75),
                "median_threshold": float(
                    row.median_threshold
                ),
                "would_signal": bool(
                    row.would_signal
                ),
            }
            for row in signals.itertuples(
                index=False
            )
        ]
 