"""Fictional stars and exoplanets endpoints (fictional_blueprint)."""


class TestFictionalStars:
    """GET /api/v1/fictional-stars — public read; POST requires auth."""

    def test_returns_fictional_stars(self, client):
        response = client.get("/api/v1/fictional-stars")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        assert payload["count"] == 1
        star = payload["data"][0]
        assert star["id"] == 999001
        assert star["name"] == "Nova Testia"
        assert star["is_fictional"] is True

    def test_post_requires_auth(self, client):
        response = client.post(
            "/api/v1/fictional-stars",
            json={"name": "Intruder", "x": 1, "y": 2, "z": 3},
        )
        assert response.status_code == 401

    def test_post_with_auth_creates_star_and_delete_removes_it(self, client, jwt_headers):
        # Writes are implemented: POST creates the star (is_fictional forced
        # on), and DELETE cleans it up so the session fixture DB stays
        # pristine for the stats-count tests.
        response = client.post(
            "/api/v1/fictional-stars",
            json={"id": 999321, "name": "New Star", "x": 1.0, "y": 2.0, "z": 3.0},
            headers=jwt_headers,
        )
        payload = response.get_json()
        assert payload["success"] is True

        names = [s.get("fictional_name") or s.get("name")
                 for s in client.get("/api/v1/fictional-stars").get_json()["data"]]
        assert "New Star" in names

        deleted = client.delete("/api/v1/fictional-stars/999321", headers=jwt_headers)
        assert deleted.get_json()["success"] is True
        names_after = [s.get("fictional_name") or s.get("name")
                       for s in client.get("/api/v1/fictional-stars").get_json()["data"]]
        assert "New Star" not in names_after

    def test_delete_requires_auth(self, client):
        assert client.delete("/api/v1/fictional-stars/999001").status_code == 401


class TestFictionalExoplanets:
    """GET /api/v1/fictional-exoplanets — public, unions both tables."""

    def test_unions_exoplanets_and_legacy_table(self, client):
        response = client.get("/api/v1/fictional-exoplanets")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        by_name = {planet["name"]: planet for planet in payload["data"]}
        assert set(by_name) == {"New Brandenburg", "Legacy Colony World"}

        # Legacy fictional_exoplanets rows are reshaped to the unified format.
        legacy = by_name["Legacy Colony World"]
        assert legacy["host_star_name"] == "Rigil Kentaurus"
        assert legacy["is_fictional"] == 1
        assert legacy["semi_major_axis_au"] == 1.2
        assert legacy["map_url"] == "http://example.com/map"

    def test_post_requires_auth(self, client):
        response = client.post(
            "/api/v1/fictional-exoplanets", json={"name": "Intruder"}
        )
        assert response.status_code == 401
