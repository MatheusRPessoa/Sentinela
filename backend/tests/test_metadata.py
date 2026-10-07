from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_get_mg_2026_metadata():
    response = client.get(
        "/api/metadata",
        params={
            "region": "MG",
            "year": 2026,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "OpenDataSUS"
    assert data["region"] == "MG"
    assert data["year"] == 2026

    assert data["source_updated_at"] == "2026-09-28T00:47:00-03:00"
    assert data["observed_through"] == "2026-09-26"

    assert data["first_observed_week"] == 1
    assert data["last_observed_week"] == 38
    assert data["observed_weeks"] == 38

    assert len(data["limitations"]) == 3

    assert (
        "Um sinal estatístico não representa confirmação de surto."
        in data["limitations"]
    )


def test_get_metadata_normalizes_region():
    response = client.get(
        "/api/metadata",
        params={
            "region": "mg",
            "year": 2026,
        },
    )

    assert response.status_code == 200
    assert response.json()["region"] == "MG"


def test_get_metadata_returns_404_for_unavailable_region():
    response = client.get(
        "/api/metadata",
        params={
            "region": "RJ",
            "year": 2026,
        },
    )

    assert response.status_code == 404


def test_get_metadata_returns_404_for_unavailable_year():
    response = client.get(
        "/api/metadata",
        params={
            "region": "MG",
            "year": 2024,
        },
    )

    assert response.status_code == 404

def test_get_metada_uses_correct_historical_period_for_2025():
    response = client.get(
        "/api/metadata",
        params={
            "region": "MG",
            "year": 2025,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["historical_start_year"] == 2019
    assert data["historical_end_year"] == 2024

def test_get_metadata_users_correct_historical_period_for_2026():
    response = client.get(
        "/api/metadata",
        params={
            "region": "MG",
            "year": 2026,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["historical_start_year"] == 2019
    assert data["historical_end_year"] == 2025
