from fastapi.testclient import TestClient


def test_health_endpoint_returns_json_status(test_app: TestClient):
    response = test_app.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"service": "Platform Health", "status": "available"}
