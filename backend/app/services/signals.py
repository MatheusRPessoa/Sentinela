from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)


class SignalsService:
    def __init__(
        self,
        repository: EpidemiologicalRepository,
    ):
        self.repository = repository

    def get_signals(
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

        df = self.repository.get_signal_evaluation(
            region=region,
            year=year,
        )

        required_columns = {
            "region",
            "epi_year",
            "epi_week",
            "week_start",
            "week_end",
            "record_count",
            "historical_median",
            "q75",
            "median_threshold",
            "ratio_to_median",
            "historical_years",
            "data_status",
            "signal_status",
            "signal_reason",
        }

        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                "Colunas obrigatórias ausentes: "
                f"{sorted(missing_columns)}"
            )

        df = df.loc[
            df["region"].eq(region)
            & df["epi_year"].eq(year)
            & df["signal_status"].eq("SIGNAL")
        ].copy()

        df = df.sort_values("epi_week")

        return [
            {
                "epi_week": int(row.epi_week),
                "week_start": row.week_start,
                "week_end": row.week_end,
                "record_count": float(row.record_count),
                "historical_median": float(
                    row.historical_median
                ),
                "q75": float(row.q75),
                "median_threshold": float(
                    row.median_threshold
                ),
                "ratio_to_median": float(
                    row.ratio_to_median
                ),
                "historical_years": int(
                    row.historical_years
                ),
                "data_status": row.data_status,
                "signal_status": row.signal_status,
                "signal_reason": row.signal_reason,
            }
            for row in df.itertuples(index=False)
        ]
