from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_get_available_options():
    response = client.get("/api/options")

    assert response.status_code == 200

    data = response.json()

    assert data["regions"] == [
        {
            "value": "MG",
            "label": "Minas Gerais",
        }
    ]

    assert data["years"] == [2026]
