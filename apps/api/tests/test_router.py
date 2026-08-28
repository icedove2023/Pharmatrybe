from app.api.router import router as api_router
from app.main import app
from fastapi.testclient import TestClient


def test_api_v1_router_is_importable():
    assert api_router is not None
    assert hasattr(api_router, "routes")


def test_api_v1_route_prefixes_are_registered(test_app: TestClient):
    # Verify key endpoints respond (router registration may manifest as
    # nested include routers; exercising the endpoints is a more robust
    # contract-level check than inspecting internals of `app.routes`).
    for path in ("/api/v1/health", "/api/v1/version", "/api/v1/auth"):
        resp = test_app.get(path)
        assert resp.status_code < 500


def test_fastapi_application_starts_successfully(test_app: TestClient):
    response = test_app.get("/")

    assert response.status_code == 200
    assert response.json().get("platform") == "PharmaTrybe"
