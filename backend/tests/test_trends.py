from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_get_mg_2026_trends():
    response = client.get(
        "/api/trends",
        params={
            "region": "MG",
            "year": 2026,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["region"] == "MG"
    assert data["year"] == 2026

    weeks = data["weeks"]

    assert len(weeks) == 38

    assert weeks[0]["epi_week"] == 1
    assert weeks[0]["record_count"] == 436

    assert weeks[-1]["epi_week"] == 38
    assert weeks[-1]["record_count"] == 102

    assert sum(
        week["record_count"]
        for week in weeks
    ) == 29_087

    assert all(
        week["historical_median"] is not None
        and week["q25"] is not None
        and week["q75"] is not None
        for week in weeks
    )

    week_15 = next(
        week
        for week in weeks
        if week["epi_week"] == 15
    )

    assert week_15["record_count"] == 1066
    assert week_15["historical_median"] == 698.0
    assert week_15["q75"] == 933.5


def test_get_trends_normalizes_region():
    response = client.get(
        "/api/trends",
        params={
            "region": "mg",
            "year": 2026,
        },
    )

    assert response.status_code == 200
    assert response.json()["region"] == "MG"


def test_get_trends_returns_404_for_unavailable_region():
    response = client.get(
        "/api/trends",
        params={
            "region": "SP",
            "year": 2026,
        },
    )

    assert response.status_code == 404


def test_get_trends_returns_404_for_unavailable_year():
    response = client.get(
        "/api/trends",
        params={
            "region": "MG",
            "year": 2025,
        },
    )

    assert response.status_code == 404