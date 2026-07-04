"""Stats, galactic directions, and stellar regions endpoints."""


EXPECTED_COUNTS = {
    "stars": 6,
    "fictional_stars": 1,
    "nations": 2,
    "exoplanets": 2,
    "fictional_exoplanets": 1,
    "trade_routes": 2,
    "stellar_regions": 1,
}


class TestStats:
    """GET /api/v1/stats — entity counts are public (they back the sidebar
    statistics panel); `authenticated` reflects the caller."""

    def test_public_stats_include_entity_counts(self, client):
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["authenticated"] is False
        assert "timestamp" in data
        for key, value in EXPECTED_COUNTS.items():
            assert data[key] == value, f"{key}: {data.get(key)} != {value}"

    def test_authenticated_stats_include_entity_counts(self, client, jwt_headers):
        data = client.get("/api/v1/stats", headers=jwt_headers).get_json()["data"]
        assert data["authenticated"] is True
        for key, value in EXPECTED_COUNTS.items():
            assert data[key] == value


class TestGalacticDirections:
    """GET /api/v1/galactic-directions — public, computed markers."""

    def test_returns_direction_markers(self, client):
        response = client.get("/api/v1/galactic-directions")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        names = {marker["name"] for marker in payload["data"]}
        assert names == {
            "Galactic Center",
            "Galactic North",
            "Galactic South",
            "Galactic Anticenter",
            "Sol",
        }
        sol = next(m for m in payload["data"] if m["name"] == "Sol")
        assert sol["position"] == [0.0, 0.0, 0.0]


class TestStellarRegions:
    """GET /api/v1/stellar-regions — public."""

    def test_returns_regions_with_computed_fields(self, client):
        response = client.get("/api/v1/stellar-regions")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        assert payload["count"] == 1

        region = payload["data"][0]
        assert region["name"] == "Test Octant"
        assert region["x_range"] == [0.0, 10.0]
        assert region["y_range"] == [-10.0, 0.0]
        assert region["z_range"] == [0.0, 20.0]
        # Center is the midpoint of each axis range.
        assert region["center"] == [5.0, -5.0, 10.0]
        assert region["color"] == [100, 150, 200]
