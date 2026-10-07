import pandas as pd

from fastapi.testclient import TestClient

from backend.app.main import app

from backend.app.services.operational_status import (
    OperationalStatusService,
)


client = TestClient(app)


class FakeEpidemiologicalRepository:
    def dataset_exists(
        self,
        region: str,
        year: int,
    ) -> bool:
        _ = region, year
        return True

    def get_operational_status(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        _ = region, year
        return pd.DataFrame(
            {
                "epi_week": [17, 18, 24, 25],
                "has_signal": [
                    True,
                    True,
                    False,
                    False,
                ],
                "operational_state": [
                    "SIGNAL",
                    "ALERT",
                    "ALERT",
                    "NORMAL",
                ],
                "consecutive_signals": [
                    1,
                    2,
                    0,
                    0,
                ],
                "consecutive_no_signals": [
                    0,
                    0,
                    1,
                    2,
                ],
            }
        )


def test_get_operational_status_preserves_state_machine():
    repository = FakeEpidemiologicalRepository()
    service = OperationalStatusService(repository)

    result = service.get_operational_status(
        region="mg",
        year=2025,
    )

    assert result == [
        {
            "epi_week": 17,
            "is_mature": True,
            "has_signal": True,
            "operational_state": "SIGNAL",
            "last_stable_state": "SIGNAL",
            "consecutive_signals": 1,
            "consecutive_no_signals": 0,
        },
        {
            "epi_week": 18,
            "is_mature": True,
            "has_signal": True,
            "operational_state": "ALERT",
            "last_stable_state": "ALERT",
            "consecutive_signals": 2,
            "consecutive_no_signals": 0,
        },
        {
            "epi_week": 24,
            "is_mature": True,
            "has_signal": False,
            "operational_state": "ALERT",
            "last_stable_state": "ALERT",
            "consecutive_signals": 0,
            "consecutive_no_signals": 1,
        },
        {
            "epi_week": 25,
            "is_mature": True,
            "has_signal": False,
            "operational_state": "NORMAL",
            "last_stable_state": "NORMAL",
            "consecutive_signals": 0,
            "consecutive_no_signals": 2,
        },
    ]


def test_get_mg_2025_nowcast():
    response = client.get(
        "/api/nowcast",
        params={
            "region": "MG",
            "year": 2025,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["region"] == "MG"
    assert data["year"] == 2025
    assert len(data["weeks"]) == 7

    assert data["weeks"][0]["epi_week"] == 17
    assert data["weeks"][0]["lag_days"] == 7
    assert data["weeks"][0]["would_signal"] is True


def test_get_mg_2025_operational_status():
    response = client.get(
        "/api/status",
        params={
            "region": "MG",
            "year": 2025,
        },
    )

    assert response.status_code == 200

    data = response.json()

    weeks = {
        week["epi_week"]: week
        for week in data["weeks"]
    }

    assert weeks[17]["operational_state"] == "SIGNAL"
    assert weeks[18]["operational_state"] == "ALERT"
    assert weeks[24]["operational_state"] == "ALERT"
    assert weeks[25]["operational_state"] == "NORMAL"
