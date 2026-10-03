import pandas as pd
import pytest

from backend.app.services.trends import TrendsService


class FakeEpidemiologicalRepository:
    def get_weekly(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        # Mantém o contrato do repositório; os dados deste fake são fixos.
        # pylint: disable=unused-argument
        return pd.DataFrame(
            {
                "epi_week": [1, 2],
                "record_count": [100, 150],
            }
        )

    def get_historical_reference(
        self,
        region: str,
    ) -> pd.DataFrame:
        # Mantém o contrato do repositório; os dados deste fake são fixos.
        # pylint: disable=unused-argument
        return pd.DataFrame(
            {
                "epi_week": [1, 2],
                "historical_median": [80.0, 120.0],
                "q25": [70.0, 100.0],
                "q75": [90.0, 140.0],
            }
        )

def test_get_trends_merges_weekly_and_historical_data():
    repository = FakeEpidemiologicalRepository()
    service = TrendsService(repository)

    result  = service.get_trends(
        region="mg",
        year=2026,
    )

    assert result == [
        {
            "epi_week": 1,
            "record_count": 100,
            "historical_median": 80.0,
            "q25": 70.0,
            "q75": 90.0,
        },
        {
            "epi_week": 2,
            "record_count": 150,
            "historical_median": 120.0,
            "q25": 100.0,
            "q75": 140.0,
        },
    ]

class IncompleteReferenceRepository(
    FakeEpidemiologicalRepository
):
    def get_historical_reference(
        self,
        region: str,
    ) -> pd.DataFrame:
        # Mantém o contrato do repositório; os dados deste fake são fixos.
        # pylint: disable=unused-argument
        return  pd.DataFrame(
            {
               "epi_week": [1],
                "historical_median": [80.0],
                "q25": [70.0],
                "q75": [90.0] 
            }
        )

def test_get_trends_rejects_missing_historical_reference():
    repository = IncompleteReferenceRepository()
    service = TrendsService(repository)

    with pytest.raises(
        ValueError,
        match="sem referência histórica",
    ):
        service.get_trends(
            region="MG",
            year=2026,
        )
