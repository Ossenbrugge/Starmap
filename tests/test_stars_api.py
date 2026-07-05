"""Public and protected star endpoints (stars_blueprint)."""


def get_names(payload):
    return [star["name"] for star in payload["data"]]


class TestGetStars:
    """GET /api/v1/stars — public, paginated."""

    def test_default_returns_stars_within_magnitude_8(self, client):
        response = client.get("/api/v1/stars")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        # Seeded stars with magnitude <= 8.0, sorted brightest first.
        assert get_names(payload) == [
            "Sol", "Rigil Kentaurus", "Tau Ceti", "HIP 90001", "Lalande 21185",
        ]
        assert payload["count"] == 5
        assert payload["pagination"]["total_count"] == 5

    def test_star_shape_has_client_fields(self, client):
        payload = client.get("/api/v1/stars").get_json()
        sol = payload["data"][0]
        assert sol["id"] == 0
        assert sol["name"] == "Sol"
        assert sol["spectral_class"] == "G2V"
        assert sol["nation_id"] == "terran_directorate"
        assert {"x", "y", "z", "magnitude", "constellation"} <= set(sol)

    def test_mag_limit_filter(self, client):
        payload = client.get("/api/v1/stars?mag_limit=4").get_json()
        assert get_names(payload) == ["Sol", "Rigil Kentaurus", "Tau Ceti"]

    def test_spectral_type_filter(self, client):
        payload = client.get("/api/v1/stars?spectral_type=M").get_json()
        assert get_names(payload) == ["Lalande 21185"]

    def test_constellation_filter(self, client):
        payload = client.get("/api/v1/stars?constellation=Cen").get_json()
        assert get_names(payload) == ["Rigil Kentaurus"]

    def test_pagination(self, client):
        page1 = client.get("/api/v1/stars?limit=2&page=1").get_json()
        assert len(page1["data"]) == 2
        assert page1["pagination"] == {
            "page": 1,
            "limit": 2,
            "total_count": 5,
            "total_pages": 3,
            "has_next": True,
            "has_prev": False,
        }
        page3 = client.get("/api/v1/stars?limit=2&page=3").get_json()
        assert len(page3["data"]) == 1
        assert page3["pagination"]["has_next"] is False
        assert page3["pagination"]["has_prev"] is True

    def test_invalid_spectral_type_is_error(self, client):
        response = client.get("/api/v1/stars?spectral_type=X")
        assert response.status_code == 500
        assert response.get_json()["success"] is False

    def test_out_of_range_mag_limit_is_error(self, client):
        response = client.get("/api/v1/stars?mag_limit=99")
        assert response.status_code == 500
        assert response.get_json()["success"] is False


class TestGetStarById:
    """GET /api/v1/stars/<id> — public read."""

    def test_public_read(self, client):
        response = client.get("/api/v1/stars/0")
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_returns_star_details_with_jwt(self, client, jwt_headers):
        response = client.get("/api/v1/stars/0", headers=jwt_headers)
        assert response.status_code == 200
        star = response.get_json()["data"]
        assert star["name"] == "Sol"
        # Sol is an endpoint of both seeded trade routes.
        route_ids = {route["id"] for route in star["trade_routes"]}
        assert route_ids == {"sol_centauri_run", "tau_ceti_loop"}

    def test_returns_star_details_with_session(self, logged_in_client):
        response = logged_in_client.get("/api/v1/stars/8087")
        assert response.status_code == 200
        assert response.get_json()["data"]["name"] == "Tau Ceti"

    def test_unknown_star_is_404(self, client, jwt_headers):
        response = client.get("/api/v1/stars/12345678", headers=jwt_headers)
        assert response.status_code == 404
        assert response.get_json()["error"] == "Star not found"


class TestStarSearch:
    """GET /api/v1/stars/search — public read."""

    def test_public_read(self, client):
        assert client.get("/api/v1/stars/search?q=Sol").status_code == 200

    def test_search_by_proper_name(self, client, jwt_headers):
        payload = client.get(
            "/api/v1/stars/search?q=Tau", headers=jwt_headers
        ).get_json()
        assert payload["success"] is True
        assert "Tau Ceti" in get_names(payload)

    def test_search_by_fictional_name(self, client, jwt_headers):
        payload = client.get(
            "/api/v1/stars/search?q=Hawking", headers=jwt_headers
        ).get_json()
        assert [star["id"] for star in payload["data"]] == [71456]


class TestNearbyStars:
    """GET /api/v1/stars/nearby — public read."""

    def test_public_read(self, client):
        assert client.get("/api/v1/stars/nearby").status_code == 200

    def test_radius_search_around_sol(self, client, jwt_headers):
        payload = client.get(
            "/api/v1/stars/nearby?x=0&y=0&z=0&radius=5", headers=jwt_headers
        ).get_json()
        assert payload["success"] is True
        # Only Sol and Rigil Kentaurus (~4.3 units away) are within 5 units.
        assert get_names(payload) == ["Sol", "Rigil Kentaurus"]
        assert payload["data"][0]["distance_from_center"] == 0


class TestExoplanets:
    """GET /api/v1/exoplanets — public, real planets only."""

    def test_returns_real_exoplanets(self, client):
        response = client.get("/api/v1/exoplanets")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        names = {planet["name"] for planet in payload["data"]}
        assert names == {"Tau Ceti e", "Lalande b"}
