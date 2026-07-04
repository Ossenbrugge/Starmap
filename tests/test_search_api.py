"""Global search endpoint (search_blueprint)."""


class TestSearch:
    """GET /api/v1/search — requires auth."""

    def test_requires_auth(self, client):
        assert client.get("/api/v1/search?q=Sol").status_code == 401

    def test_empty_query_returns_empty_result(self, client, jwt_headers):
        payload = client.get("/api/v1/search?q=", headers=jwt_headers).get_json()
        assert payload["success"] is True
        assert payload["data"] == []
        assert payload["count"] == 0

    def test_search_by_name(self, client, jwt_headers):
        payload = client.get("/api/v1/search?q=Tau", headers=jwt_headers).get_json()
        assert payload["success"] is True
        assert "Tau Ceti" in [star["name"] for star in payload["data"]]

    def test_search_by_fictional_name(self, client, jwt_headers):
        payload = client.get(
            "/api/v1/search?q=Hawking", headers=jwt_headers
        ).get_json()
        assert [star["id"] for star in payload["data"]] == [71456]

    def test_spectral_type_narrows_results(self, client, jwt_headers):
        matching = client.get(
            "/api/v1/search?q=Tau&spectral_type=G8", headers=jwt_headers
        ).get_json()
        assert [star["name"] for star in matching["data"]] == ["Tau Ceti"]

        non_matching = client.get(
            "/api/v1/search?q=Tau&spectral_type=M", headers=jwt_headers
        ).get_json()
        assert non_matching["data"] == []

    def test_no_match_returns_empty_list(self, client, jwt_headers):
        payload = client.get(
            "/api/v1/search?q=zzzznothing", headers=jwt_headers
        ).get_json()
        assert payload["success"] is True
        assert payload["data"] == []
