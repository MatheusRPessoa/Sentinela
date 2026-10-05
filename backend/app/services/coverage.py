import pandas as pd

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)

class CoverageService:
    def __init__(
        self,
        repository: EpidemiologicalRepository,
    ):
        self.repository = repository

    def get_coverage(
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

        coverage = self.repository.get_coverage(
            region=region,
            year=year,
        )

        required_columns = {
            "epi_week",
            "epi_year",
            "week_start",
            "week_end",
            "record_count",
            "calendar_status",
            "data_status",
        }

        missing_columns = (
            required_columns - set(coverage.columns)
        )

        if missing_columns:
            raise ValueError(
                "Colunas obrigatórias ausentes: "
                f"{sorted(missing_columns)}"
            )
        
        coverage = coverage.loc[
            coverage["epi_year"].eq(year)
        ].copy()

        if coverage["epi_week"].duplicated().any():
            raise ValueError(
                "A cobertura contém semanas "
                "epidemiológicas duplicadas."
            )

        coverage = coverage.sort_values("epi_week")

        return [
            {
                "epi_week": int(row.epi_week),
                "week_start": row.week_start,
                "week_end": row.week_end,
                "record_count": (
                    None
                    if pd.isna(row.record_count)
                    else int(row.record_count)
                ),
                "calendar_status": row.calendar_status,
                "data_status": row.data_status,
            }
            for row in coverage.itertuples(index=False)
        ]
