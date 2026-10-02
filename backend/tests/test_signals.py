from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_get_mg_2026_signals():
    response = client.get(
        "/api/signals",
        params={
            "region": "MG",
            "year": 2026,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["region"] == "MG"
    assert data["year"] == 2026

    signals = data["signals"]

    assert len(signals) == 1

    signal = signals[0]

    assert signal["epi_week"] == 15
    assert signal["week_start"] == "2026-04-12"
    assert signal["week_end"] == "2026-04-18"

    assert signal["record_count"] == 1066.0
    assert signal["historical_median"] == 698.0
    assert signal["q75"] == 933.5
    assert signal["median_threshold"] == 1047.0

    assert signal["historical_years"] == 7
    assert signal["data_status"] == "observado"
    assert signal["signal_status"] == "SIGNAL"

    assert signal["ratio_to_median"] > 1.5

    assert "1.5x" in signal["signal_reason"]

def test_get_signals_normalizes_region():
    response = client.get(
        "/api/signals",
        params={
            "region": "mg",
            "year": 2026,
        },
    )

    assert response.status_code == 200
    assert response.json()["region"] == "MG"

def test_get_signals_returns_empty_for_unavailable_region():
    response = client.get(
        "/api/signals",
        params={
            "region": "SP",
            "year": 2026,
        },
    )

    assert response.status_code == 200
    assert response.json()["signals"] == []

def test_get_signals_returns_empty_for_unavailable_year():
    response = client.get(
        "/api/signals",
        params={
            "region": "MG",
            "year": 2025,
        },
    )

    assert response.status_code == 200
    assert response.json()["signals"] == []
