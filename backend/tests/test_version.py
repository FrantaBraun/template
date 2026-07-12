# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

import json

from app.config import BASE_DIR


def test_version_endpoint_returns_version_json(client):
    expected = json.loads((BASE_DIR / "version.json").read_text(encoding="utf-8"))

    response = client.get("/api/public/version")

    assert response.status_code == 200
    assert response.json() == expected
