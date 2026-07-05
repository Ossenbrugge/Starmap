"""Nation endpoints (nations_blueprint)."""


class TestGetNations:
    """GET /api/v1/nations — public."""

    def test_returns_all_nations(self, client):
        response = client.get("/api/v1/nations")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        assert payload["count"] == 2
        ids = {nation["id"] for nation in payload["data"]}
        assert ids == {"terran_directorate", "felgenland_union"}

    def test_nations_are_enriched(self, client):
        payload = client.get("/api/v1/nations").get_json()
        by_id = {nation["id"]: nation for nation in payload["data"]}

        terran = by_id["terran_directorate"]
        assert terran["appearance"]["color"] == "#0066cc"
        assert terran["capital"]["star_id"] == 0
        assert terran["government"]["type"] == "directorate"
        assert sorted(terran["territories"]) == [0, 53879, 71456]
        assert terran["era_start"] == 2091
        assert terran["era_end"] is None

        felgenland = by_id["felgenland_union"]
        assert felgenland["era_start"] == 2210
        assert felgenland["era_end"] == 2357
        assert felgenland["capital"]["star_id"] == 8087


class TestGetNationById:
    """GET /api/v1/nations/<id> — public read."""

    def test_public_read(self, client):
        assert client.get("/api/v1/nations/terran_directorate").status_code == 200

    def test_returns_nation(self, client, jwt_headers):
        response = client.get(
            "/api/v1/nations/terran_directorate", headers=jwt_headers
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        assert payload["data"]["name"] == "Terran Directorate"

    def test_unknown_nation_reports_failure(self, client, jwt_headers):
        response = client.get("/api/v1/nations/atlantis", headers=jwt_headers)
        payload = response.get_json()
        assert payload["success"] is False
        assert payload["error"] == "Nation not found"


class TestNationStars:
    """GET /api/v1/nations/<id>/stars — public read."""

    def test_public_read(self, client):
        assert client.get("/api/v1/nations/terran_directorate/stars").status_code == 200

    def test_returns_stars_controlled_by_nation(self, client, jwt_headers):
        payload = client.get(
            "/api/v1/nations/terran_directorate/stars", headers=jwt_headers
        ).get_json()
        assert payload["success"] is True
        ids = sorted(star["id"] for star in payload["data"])
        assert ids == [0, 53879, 71456]


class TestNationTerritories:
    """GET /api/v1/nations/<id>/territories — public read."""

    def test_public_read(self, client):
        assert (
            client.get("/api/v1/nations/felgenland_union/territories").status_code
            == 200
        )

    def test_returns_territory_summary(self, client, jwt_headers):
        payload = client.get(
            "/api/v1/nations/felgenland_union/territories", headers=jwt_headers
        ).get_json()
        assert payload["success"] is True
        assert payload["data"] == {
            "nation_id": "felgenland_union",
            "territories": [8087],
            "territory_count": 1,
        }
