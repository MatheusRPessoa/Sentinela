from datetime import datetime

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)

SOURCE_UPDATED_AT = datetime.fromisoformat(
    "2026-09-28T00:47:00-03:00"
)

class MetadataService:
    def __init__(
        self,
        repository: EpidemiologicalRepository,
    ):
        self.repository = repository

    def get_metadata(
        self,
        region: str,
        year: int,
    ) -> dict:
        region = region.strip().upper()

        if not self.repository.dataset_exists(
            region=region,
            year=year,
        ):
            return {}

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

        missing_columns = required_columns - set(coverage.columns)

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
                "A cobertura contém semanas epidemiológicas duplicadas."
            )

        observed = coverage.loc[
            coverage["data_status"].eq("observado")
        ].copy()

        if observed.empty:
            raise ValueError(
                "Nenhuma semana observada encontrada."
            )

        observed = observed.sort_values("epi_week")

        if coverage["epi_week"].duplicated().any():
            raise ValueError(
                "A cobertura contém semanas epidemiológicas duplicadas."
        )

        last_observed = observed.iloc[-1]

        return {
            "source": "OpenDataSUS",
            "region": region,
            "year": year,
            "source_updated_at": SOURCE_UPDATED_AT,
            "observed_through": last_observed["week_end"],
            "first_observed_week": int(
                observed["epi_week"].min()
            ),
            "last_observed_week": int(
                observed["epi_week"].max()
            ),
            "observed_weeks": int(
                observed["epi_week"].nunique()
            ),
            "limitations": [
                (
                    "Semanas sem cobertura confirmada não são "
                    "tratadas como zero."
                ),
                (
                    "Um sinal estatístico não representa "
                    "confirmação de surto."
                ),
                (
                    "A referência histórica utiliza os anos "
                    "de 2019 a 2025."
                ),
            ],
        }
