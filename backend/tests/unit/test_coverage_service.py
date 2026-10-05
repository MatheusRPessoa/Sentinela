import pandas as pd
import pytest

from backend.app.services.coverage import CoverageService


class FakeEpidemiologicalRepository:
    def dataset_exists(
        self,
        region: str,
        year: int,
    ) -> bool:
        _ = region, year
        return region == "MG" and year == 2026

    def get_coverage(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        _ = region, year
        return pd.DataFrame(
            {
                "epi_week": [1, 2, 3],
                "epi_year": [2026, 2026, 2026],
                "week_start": [
                    "2026-01-04",
                    "2026-01-11",
                    "2026-01-18",
                ],
                "week_end": [
                    "2026-01-10",
                    "2026-01-17",
                    "2026-01-24",
                ],
                "record_count": [
                    100.0,
                    150.0,
                    float("nan"),
                ],
                "calendar_status": [
                    "encerrada",
                    "encerrada",
                    "futura",
                ],
                "data_status": [
                    "observado",
                    "observado",
                    "sem_cobertura_confirmada",
                ],
            }
        )


def test_get_coverage_preserves_missing_data_as_none():
    repository = FakeEpidemiologicalRepository()
    service = CoverageService(repository)

    result = service.get_coverage(
        region="mg",
        year=2026,
    )

    assert len(result) == 3

    assert result[0]["record_count"] == 100
    assert result[1]["record_count"] == 150

    assert result[2]["record_count"] is None
    assert (
        result[2]["data_status"]
        == "sem_cobertura_confirmada"
    )


def test_get_coverage_normalizes_region():
    repository = FakeEpidemiologicalRepository()
    service = CoverageService(repository)

    result = service.get_coverage(
        region=" mg ",
        year=2026,
    )

    assert len(result) == 3


def test_get_coverage_returns_empty_for_unavailable_dataset():
    repository = FakeEpidemiologicalRepository()
    service = CoverageService(repository)

    result = service.get_coverage(
        region="SP",
        year=2026,
    )

    assert result == []

class DuplicateWeekRepository(
    FakeEpidemiologicalRepository
):
    def get_coverage(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        data = super().get_coverage(region, year)

        data.loc[1, "epi_week"] = 1

        return data


def test_get_coverage_rejects_duplicate_weeks():
    repository = DuplicateWeekRepository()
    service = CoverageService(repository)

    with pytest.raises(
        ValueError,
        match="duplicadas",
    ):
        service.get_coverage(
            region="MG",
            year=2026,
        )
