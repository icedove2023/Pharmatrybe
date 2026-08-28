from app.core.config import settings
from fastapi.testclient import TestClient


def test_version_endpoint_returns_expected_fields(test_app: TestClient):
    response = test_app.get("/version")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    body = response.json()
    assert "service" in body
    assert "version" in body
    assert body["service"] == "Platform Version"
    assert body["version"] == settings.app_version
