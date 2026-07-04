"""Trade route endpoint (trade_routes_blueprint)."""


def test_trade_routes_are_public(client):
    response = client.get("/api/v1/trade-routes")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["count"] == 2


def test_trade_route_shape(client):
    payload = client.get("/api/v1/trade-routes").get_json()
    by_id = {route["id"]: route for route in payload["data"]}
    assert set(by_id) == {"sol_centauri_run", "tau_ceti_loop"}

    run = by_id["sol_centauri_run"]
    assert run["name"] == "Sol-Centauri Run"
    assert run["nation_id"] == "terran_directorate"
    # Legacy nested endpoints format expected by the frontend.
    assert run["endpoints"]["from"]["star_id"] == 0
    assert run["endpoints"]["to"]["star_id"] == 71456
    # Era fields drive the timeline slider's route filtering.
    assert run["era_start"] == 2100
    assert run["era_end"] is None

    loop = by_id["tau_ceti_loop"]
    assert loop["era_start"] == 2210
    assert loop["era_end"] == 2357
