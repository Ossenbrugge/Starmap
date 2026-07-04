"""Unit tests for the SQLite Database layer (models/database.py)."""


class TestStarNames:
    def test_nan_proper_name_falls_back_to_hip(self, database):
        star = database.get_star_by_id(90001)
        assert star["proper_name"] == ""  # 'nan' is cleaned away
        assert star["name"] == "HIP 90001"

    def test_fictional_star_uses_fictional_name(self, database):
        star = database.get_star_by_id(999001)
        assert star["name"] == "Nova Testia"
        assert star["is_fictional"] is True

    def test_star_dict_exposes_era_fields(self, database):
        star = database.get_star_by_id(71456)
        assert star["discovery_year"] == 2091
        assert star["discovery_number"] == 2
        assert star["fictional_name"] == "Hawking"


class TestStarQueries:
    def test_get_stars_respects_magnitude_limit(self, database):
        stars = database.get_stars(mag_limit=4.0)
        assert [star["id"] for star in stars] == [0, 71456, 8087]

    def test_get_stars_paginated_reports_total(self, database):
        rows, total = database.get_stars_paginated(page=2, limit=2, mag_limit=8.0)
        assert total == 5
        assert len(rows) == 2

    def test_get_stars_in_radius(self, database):
        stars = database.get_stars_in_radius(0.0, 0.0, 0.0, 5.0)
        # Sorted nearest-first; the fictional star at (10,10,10) is outside.
        assert [star["id"] for star in stars] == [0, 71456]

    def test_search_stars_matches_fictional_name(self, database):
        results = database.search_stars("Hawking")
        assert [star["id"] for star in results] == [71456]


class TestFictionalExoplanets:
    def test_union_of_both_tables(self, database):
        planets = database.get_fictional_exoplanets()
        names = {planet["name"] for planet in planets}
        assert names == {"New Brandenburg", "Legacy Colony World"}

    def test_legacy_rows_carry_parent_planet_and_map_url(self, database):
        legacy = next(
            planet for planet in database.get_fictional_exoplanets()
            if planet["name"] == "Legacy Colony World"
        )
        assert "parent_planet" in legacy
        assert legacy["map_url"] == "http://example.com/map"


class TestStats:
    def test_get_stats_counts(self, database):
        assert database.get_stats() == {
            "stars": 6,
            "fictional_stars": 1,
            "nations": 2,
            "exoplanets": 2,
            "fictional_exoplanets": 1,
            "trade_routes": 2,
            "stellar_regions": 1,
        }

    def test_get_system_stats_groups_planets_by_host(self, database):
        system = database.get_system_stats(8087)
        assert system["star"]["name"] == "Tau Ceti"
        # host_star_name query returns both real and fictional planets.
        assert {p["name"] for p in system["exoplanets"]} == {
            "Tau Ceti e",
            "New Brandenburg",
        }
        assert [p["name"] for p in system["fictional_exoplanets"]] == [
            "New Brandenburg"
        ]

    def test_get_system_stats_unknown_star(self, database):
        assert database.get_system_stats(123456789) is None


class TestSavedViews:
    def test_save_get_delete_roundtrip(self, database):
        view_id = database.save_view(1, "test view", '{"era": 2300}')
        assert view_id is not None
        try:
            views = database.get_saved_views(1)
            assert any(view["id"] == view_id for view in views)
            assert database.get_saved_views(2) == []
        finally:
            assert database.delete_saved_view(view_id, 1) is True
        assert not any(
            view["id"] == view_id for view in database.get_saved_views(1)
        )
