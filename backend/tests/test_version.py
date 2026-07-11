import json

from app.config import BASE_DIR


def test_version_endpoint_returns_version_json(client):
    expected = json.loads((BASE_DIR / "version.json").read_text(encoding="utf-8"))

    response = client.get("/api/public/version")

    assert response.status_code == 200
    assert response.json() == expected
