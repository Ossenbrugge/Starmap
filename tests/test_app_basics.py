"""App-level behavior: health check, error handlers, legacy redirect, headers."""


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["status"] == "healthy"


def test_unknown_route_returns_json_404(client):
    response = client.get("/definitely-not-a-real-page")
    assert response.status_code == 404
    payload = response.get_json()
    assert payload == {"success": False, "error": "Endpoint not found"}


def test_legacy_api_prefix_redirects_to_v1(client):
    response = client.get("/api/stars")
    assert response.status_code == 301
    assert response.headers["Location"].endswith("/api/v1/stars")


def test_security_headers_applied(client):
    response = client.get("/health")
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "Content-Security-Policy" in response.headers
