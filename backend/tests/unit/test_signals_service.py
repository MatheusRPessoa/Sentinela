import pandas as pd

from backend.app.services.signals import SignalsService


class FakeEpidemiologicalRepository:
    def dataset_exists(
        self,
        region: str,
        year: int
    ) -> bool:
        _ = region, year
        return True

    def get_signal_evaluation(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        _ = region, year

        return pd.DataFrame(
            {
                "region": ["MG", "MG"],
                "epi_year": [2026, 2026],
                "epi_week": [14, 15],
                "week_start": [
                    "2026-04-05",
                    "2026-04-12",
                ],
                "week_end": [
                    "2026-04-11",
                    "2026-04-18",
                ],
                "record_count": [1003.0, 1066.0],
                "historical_median": [680.0, 698.0],
                "q75": [910.0, 933.5],
                "median_threshold": [1020.0, 1047.0],
                "ratio_to_median": [1.475, 1.527],
                "historical_years": [7, 7],
                "data_status": ["observado", "observado"],
                "signal_status": ["NO_SIGNAL", "SIGNAL"],
                "signal_reason": [
                    "Critérios não atendidos.",
                    (
                        "Observado (1066) acima de Q75 (933.5) "
                        "e pelo menos 1.5x a mediana histórica "
                        "(698.0)."
                    ),
                ],
            }
        )

def test_get_signals_returns_only_signals():
    repository = FakeEpidemiologicalRepository()
    service = SignalsService(repository)

    result = service.get_signals(
        region="mg",
        year=2026,
    )

    assert len(result) == 1

    signal = result[0]

    assert signal["epi_week"] == 15
    assert signal["record_count"] == 1066.0
    assert signal["historical_median"] == 698.0
    assert signal["q75"] == 933.5
    assert signal["signal_status"] == "SIGNAL"

class NoSignalsRepository(
    FakeEpidemiologicalRepository
):
    def get_signal_evaluation(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        data = super().get_signal_evaluation(
            region=region,
            year=year,
        )

        data["signal_status"] = "NO_SIGNAL"

        return data

def test_get_signals_returns_empty_list_when_no_signal_exists():
    repository = NoSignalsRepository()
    service = SignalsService(repository)

    result = service.get_signals(
        region="MG",
        year=2026,
    )

    assert result == []
