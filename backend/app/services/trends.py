from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)

class TrendsService:
    def __init__(
        self,
        repository: EpidemiologicalRepository,
    ):
        self.repository = repository

    def get_trends(
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

        weekly = self.repository.get_weekly(
            region=region,
            year=year,
        )

        reference = self.repository.get_historical_reference(
            region=region,
        )

        weekly_required = {
            "epi_week",
            "record_count",
        }

        reference_required = {
            "epi_week",
            "historical_median",
            "q25",
            "q75",
        }

        missing_weekly = weekly_required - set(weekly.columns)
        missing_reference = reference_required - set(
            reference.columns
        )

        if missing_weekly:
            raise ValueError(
                "Colunas ausentes na série semanal: "
                f"{sorted(missing_weekly)}"
            )

        if missing_reference:
            raise ValueError(
                "Colunas ausentes na referência histórica: "
                f"{sorted(missing_reference)}"
            )

        if weekly["epi_week"].duplicated().any():
            raise ValueError(
                "A série semanal contém semanas duplicadas."
            )

        if reference["epi_week"].duplicated().any():
            raise ValueError(
                "A referência histórica contém semanas duplicadas."
            )

        trends = weekly.merge(
            reference[
                [
                    "epi_week",
                    "historical_median",
                    "q25",
                    "q75",
                ]
            ],
            on="epi_week",
            how="left",
            validate="one_to_one",
        )

        historical_columns = [
            "historical_median",
            "q25",
            "q75",
        ]

        if trends[historical_columns].isna().any().any():
            raise ValueError(
                "Existem semanas observadas sem referência histórica."
            )

        trends = trends.sort_values("epi_week")

        return [
            {
                "epi_week": int(row.epi_week),
                "record_count": int(row.record_count),
                "historical_median": float(
                    row.historical_median
                ),
                "q25": float(row.q25),
                "q75": float(row.q75),
            }
            for row in trends.itertuples(index=False)
        ]
