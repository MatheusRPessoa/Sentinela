from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)

client = TestClient(app)

def test_get_available_options():
    response = client.get(
        "/api/options"
    )

    assert response.status_code == 200

    data = response.json()

    regions = {
        item["value"]: item
        for item in data["regions"]
    }

    assert regions["MG"] == {
        "value": "MG",
        "label": "Minas Gerais",
        "years": [2026, 2025],
    }

    assert regions["SP"] == {
        "value": "SP",
        "label": "São Paulo",
        "years": [2026],
    }

def test_sp_2026_dataset_exists():
    repository = EpidemiologicalRepository()

    assert (
        repository.dataset_exists(
            region="SP",
            year=2026,
        )
        is True
    )


def test_sp_2025_dataset_does_not_exist():
    repository = EpidemiologicalRepository()

    assert (
        repository.dataset_exists(
            region="SP",
            year=2025,
        )
        is False
    )
