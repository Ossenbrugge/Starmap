"""Timeline snapshot endpoint (timeline_blueprint) and era logic.

Seeded eras:
  - Terran Directorate: 2091 - (open)
  - Felgenland Union:   2210 - 2357
  - Sol-Centauri Run:   2100 - (open)
  - Tau Ceti Loop:      2210 - 2357
  - Colonization years: Lalande 21185 = 2080, Rigil Kentaurus = 2091,
    Tau Ceti = 2200; three real stars have no discovery_year (always counted).
"""

import pytest


def snapshot(client, year):
    response = client.get(f"/api/v1/timeline?year={year}")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    return payload["data"]


def test_year_parameter_is_required(client):
    response = client.get("/api/v1/timeline")
    assert response.status_code == 400
    assert response.get_json()["success"] is False


@pytest.mark.parametrize(
    "year, nation_ids, colonized, routes",
    [
        (2000, set(), 3, 0),
        (2100, {"terran_directorate"}, 5, 1),
        (2250, {"terran_directorate", "felgenland_union"}, 6, 2),
        (2400, {"terran_directorate"}, 6, 1),
    ],
)
def test_snapshot_by_year(client, year, nation_ids, colonized, routes):
    data = snapshot(client, year)
    assert data["year"] == year
    assert {nation["id"] for nation in data["active_nations"]} == nation_ids
    assert data["nation_count"] == len(nation_ids)
    assert data["colonized_stars"] == colonized
    assert data["active_routes"] == routes


def test_active_nation_shape(client):
    data = snapshot(client, 2250)
    felgenland = next(
        nation for nation in data["active_nations"]
        if nation["id"] == "felgenland_union"
    )
    assert felgenland == {
        "id": "felgenland_union",
        "name": "Felgenland Union",
        "color": "#cc3300",
        "era_start": 2210,
        "era_end": 2357,
        "capital_star_id": 8087,
    }


def test_nation_active_on_boundary_years(client):
    # era_start and era_end are inclusive.
    assert "felgenland_union" in {
        nation["id"] for nation in snapshot(client, 2210)["active_nations"]
    }
    assert "felgenland_union" in {
        nation["id"] for nation in snapshot(client, 2357)["active_nations"]
    }
    assert "felgenland_union" not in {
        nation["id"] for nation in snapshot(client, 2358)["active_nations"]
    }
