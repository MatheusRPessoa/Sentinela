import pandas as pd
import pytest

from backend.app.services.metadata import MetadataService


class FakeEpidemiologicalRepository:
    def get_coverage(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        _ = region, year

        return pd.DataFrame(
            {
                "epi_week": [1, 2, 3, 4],
                "epi_year": [2026, 2026, 2026, 2026],
                "week_start": [
                    "2026-01-04",
                    "2026-01-11",
                    "2026-01-18",
                    "2026-01-25",
                ],
                "week_end": [
                    "2026-01-10",
                    "2026-01-17",
                    "2026-01-24",
                    "2026-01-31",
                ],
                "record_count": [
                    436.0,
                    415.0,
                    376.0,
                    None,
                ],
                "calendar_status": [
                    "encerrada",
                    "encerrada",
                    "encerrada",
                    "futura",
                ],
                "data_status": [
                    "observado",
                    "observado",
                    "observado",
                    "sem_cobertura_confirmada",
                ],
            }
        )


def test_get_metadata_calculates_observed_period():
    repository = FakeEpidemiologicalRepository()
    service = MetadataService(repository)

    result = service.get_metadata(
        region="mg",
        year=2026,
    )

    assert result["source"] == "OpenDataSUS"
    assert result["region"] == "MG"
    assert result["year"] == 2026

    assert result["observed_through"] == "2026-01-24"
    assert result["first_observed_week"] == 1
    assert result["last_observed_week"] == 3
    assert result["observed_weeks"] == 3

    assert len(result["limitations"]) == 3


class DuplicateWeekRepository(
    FakeEpidemiologicalRepository
):
    def get_coverage(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        data = super().get_coverage(
            region=region,
            year=year,
        )

        duplicate = data.iloc[[0]].copy()

        return pd.concat(
            [data, duplicate],
            ignore_index=True,
        )

def test_get_metadata_rejects_duplicate_weeks():
    repository = DuplicateWeekRepository()
    service = MetadataService(repository)

    with pytest.raises(
        ValueError,
        match="duplicadas",
    ):
        service.get_metadata(
            region="MG",
            year=2026,
        )

class NoObservedWeekRepository(
    FakeEpidemiologicalRepository
):
    def get_coverage(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        data = super().get_coverage(
            region=region,
            year=year,
        )

        data["data_status"] = "sem_cobertura_confirmada"
        data["record_count"] = None

        return data


def test_get_metadata_rejects_absense_of_observed_weeks():
    repository = NoObservedWeekRepository()
    service = MetadataService(repository)

    with pytest.raises(
        ValueError,
        match="Nenhuma semana observada encontrada",
    ):
        service.get_metadata(
            region="MG",
            year=2026,
        )
