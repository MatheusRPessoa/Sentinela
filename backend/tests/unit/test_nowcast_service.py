import pandas as pd

from backend.app.services.nowcast import NowcastService


class FakeEpidemiologicalRepository:
    def dataset_exists(
        self,
        region: str,
        year: int,
    ) -> bool:
        _ = region, year
        return True

    def get_nowcast(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        _ = region, year
        return pd.DataFrame(
            {
                "epi_week": [17, 17, 18],
                "lag_days": [7, 8, 7],
                "snapshot_date": [
                    "2025-05-03",
                    "2025-05-04",
                    "2025-05-10",
                ],
                "known_cases": [879, 893, 1306],
                "nowcast": [
                    1086.9,
                    1058.3,
                    1614.9,
                ],
                "q75": [
                    1063.5,
                    1063.5,
                    1178.0,
                ],
                "median_threshold": [
                    1042.5,
                    1042.5,
                    1116.75,
                ],
                "would_signal": [
                    True,
                    False,
                    True,
                ],
            }
        )


def test_get_nowcast_returns_first_signal_per_week():
    repository = FakeEpidemiologicalRepository()
    service = NowcastService(repository)

    result = service.get_nowcast(
        region="mg",
        year=2025,
    )

    assert result == [
        {
            "epi_week": 17,
            "lag_days": 7,
            "snapshot_date": "2025-05-03",
            "known_cases": 879,
            "nowcast": 1086.9,
            "q75": 1063.5,
            "median_threshold": 1042.5,
            "would_signal": True,
        },
        {
            "epi_week": 18,
            "lag_days": 7,
            "snapshot_date": "2025-05-10",
            "known_cases": 1306,
            "nowcast": 1614.9,
            "q75": 1178.0,
            "median_threshold": 1116.75,
            "would_signal": True,
        },
    ]

class MissingDatasetRepository(
    FakeEpidemiologicalRepository
):
    def dataset_exists(
        self,
        region: str,
        year: int,
    ) -> bool:
        return False


def test_get_nowcast_returns_empty_for_unaivailable_dataset():
    repository = MissingDatasetRepository()
    service = NowcastService(repository)

    result = service.get_nowcast(
        region="MG",
        year=2024,
    )

    assert result == []
