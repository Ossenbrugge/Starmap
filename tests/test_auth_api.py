"""Authentication: session login, JWT issuance, and API auth middleware."""

import jwt as pyjwt

from tests.conftest import ADMIN_PASSWORD, ADMIN_USERNAME


class TestLogin:
    def test_login_with_valid_credentials_redirects(self, client):
        response = client.post(
            "/login",
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        )
        assert response.status_code == 302

    def test_login_with_invalid_credentials_stays_on_login_page(self, client):
        response = client.post(
            "/login",
            data={"username": ADMIN_USERNAME, "password": "wrong-password"},
        )
        assert response.status_code == 200  # login page re-rendered

    def test_session_grants_access_to_protected_endpoint(self, logged_in_client):
        response = logged_in_client.get("/api/v1/stars/0")
        assert response.status_code == 200


class TestJwtToken:
    def test_token_endpoint_requires_session(self, client):
        response = client.post("/api/auth/token", json={})
        assert response.status_code == 401

    def test_token_issued_via_session_works_for_api(self, app, logged_in_client):
        response = logged_in_client.post(
            "/api/auth/token", json={"expires_hours": 1}
        )
        assert response.status_code == 200
        token_payload = response.get_json()["data"]
        assert token_payload["user"] == ADMIN_USERNAME

        # A brand-new client using only the JWT can reach protected routes.
        fresh_client = app.test_client()
        response = fresh_client.get(
            "/api/v1/stars/0",
            headers={"Authorization": f"Bearer {token_payload['token']}"},
        )
        assert response.status_code == 200


class TestApiAuthMiddleware:
    def test_garbage_bearer_token_is_rejected(self, client):
        response = client.post(
            "/api/v1/fictional/stars", json={},
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        assert response.status_code == 401
        payload = response.get_json()
        assert payload["success"] is False
        assert payload["details"]["accepted_methods"] == ["session", "jwt"]

    def test_token_signed_with_wrong_secret_is_rejected(self, client):
        forged = pyjwt.encode(
            {"user": {"id": 1, "username": "admin", "role": "admin"}},
            "wrong-secret",
            algorithm="HS256",
        )
        response = client.post(
            "/api/v1/fictional/stars", json={},
            headers={"Authorization": f"Bearer {forged}"},
        )
        assert response.status_code == 401

    def test_star_reads_are_intentionally_public(self, client):
        # Bulk star reads power the public map and must not require auth.
        assert client.get("/api/v1/stars").status_code == 200
