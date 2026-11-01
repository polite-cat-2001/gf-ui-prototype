from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_meta_endpoint(client: TestClient):
    response = client.get("/api/meta")
    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == 1
    counts = payload["counts"]
    assert counts["countries"] == 106
    assert counts["leagues"] == 279
    assert counts["clubs"] == 4406
    assert counts["players"] == 121927
    assert counts["national_teams"] == 246
    assert counts["stats_per_player"] >= 22
    assert counts["free_agents"] == 1895
    assert counts["free_agents_enriched"] == 1895


def test_countries_endpoint(client: TestClient):
    response = client.get("/api/countries")
    assert response.status_code == 200
    countries = response.json()
    assert len(countries) == 106
    england = next(country for country in countries if country["name"] == "England")
    assert england["id"] == "189"
    assert england["flag"].startswith("/raster/country_flags/189.png")


def test_country_to_league_filter(client: TestClient):
    response = client.get("/api/leagues", params={"country_id": "189"})
    assert response.status_code == 200
    leagues = response.json()
    assert leagues
    assert all(league["country_id"] == "189" for league in leagues)
    assert any(league["id"] == "GB1" for league in leagues)


def test_league_to_club_filter(client: TestClient):
    response = client.get("/api/clubs", params={"league_id": "GB1"})
    assert response.status_code == 200
    clubs = response.json()
    assert len(clubs) >= 20
    assert all(club["league_id"] == "GB1" for club in clubs)
    arsenal = next(club for club in clubs if club["name"] == "Arsenal FC")
    assert arsenal["logo"] == "/raster/teams_emblems/11.png"


def test_kits_endpoint(client: TestClient):
    response = client.get("/api/clubs/11/kits")
    assert response.status_code == 200
    payload = response.json()
    assert payload["club_id"] == "11"
    assert payload["main"] == "/raster/teams_kits/11/main.png"


def test_kit_specs_resolve_club_colors(client: TestClient):
    response = client.get("/api/teams/131/kit-specs")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "FC Barcelona"
    kits = {kit["id"]: kit for kit in payload["kits"]}
    assert list(kits) == ["main", "white", "black", "reserve"]
    assert kits["main"] == {
        "id": "main",
        "shirt": "#004C99",
        "shorts": "#004C99",
        "pattern": "stripes",
        "pattern_color": "#A60042",
    }
    assert kits["reserve"]["pattern"] == "plain"
    assert kits["reserve"]["pattern_color"] is None


def test_kit_specs_match_national_teams_by_name(client: TestClient):
    response = client.get("/api/teams/3377/kit-specs")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "France"
    assert payload["kits"][0]["shirt"] == "#123163"


def test_unknown_team_kit_specs_return_404(client: TestClient):
    assert client.get("/api/teams/does-not-exist/kit-specs").status_code == 404


def test_selected_club_returns_its_squad(client: TestClient):
    response = client.get("/api/clubs/11/players")
    assert response.status_code == 200
    squad = response.json()
    assert len(squad) >= 20
    assert all(player["club_id"] == "11" for player in squad)
    assert any(player["name"] == "David Raya" for player in squad)


def test_selected_national_team_returns_its_squad(client: TestClient):
    response = client.get("/api/national-teams/3375/players")
    assert response.status_code == 200
    squad = response.json()
    assert len(squad) >= 20
    assert all(player["national_team_id"] == "3375" for player in squad)


def test_player_detail_has_stats(client: TestClient):
    response = client.get("/api/players/262749")
    assert response.status_code == 200
    player = response.json()
    assert player["name"] == "David Raya"
    assert len(player["stats"]) >= 22


def test_club_ratings_are_computed_from_the_squad(client: TestClient):
    response = client.get("/api/clubs/131/ratings")
    assert response.status_code == 200
    payload = response.json()
    assert payload["club_id"] == "131"
    assert 80 <= payload["attack"] <= 95
    assert 80 <= payload["midfield"] <= 95
    assert 80 <= payload["defence"] <= 95
    assert payload["stars"] == 5


def test_league_ratings_cover_every_club(client: TestClient):
    response = client.get("/api/leagues/ES1/ratings")
    assert response.status_code == 200
    ratings = response.json()
    assert len(ratings) == 20
    assert all({"club_id", "attack", "midfield", "defence", "stars"} <= set(row) for row in ratings)
    assert {"club_id": "131", "attack": 88} == {key: next(r for r in ratings if r["club_id"] == "131")[key] for key in ("club_id", "attack")}


def test_national_teams_come_with_ratings(client: TestClient):
    response = client.get("/api/national-teams")
    assert response.status_code == 200
    teams = response.json()
    assert len(teams) == 101
    argentina = next(team for team in teams if team["name"] == "Argentina")
    assert argentina["flag"].startswith("/raster/country_flags/")
    assert argentina["emblem"].startswith("/raster/teams_emblems/")
    assert argentina["stars"] == 5.0
    assert argentina["attack"] >= argentina["defence"]


def test_unknown_records_return_404(client: TestClient):
    assert client.get("/api/clubs/does-not-exist").status_code == 404
    assert client.get("/api/clubs/does-not-exist/players").status_code == 404
    assert client.get("/api/clubs/does-not-exist/ratings").status_code == 404
    assert client.get("/api/leagues/does-not-exist/ratings").status_code == 404
    assert client.get("/api/players/does-not-exist").status_code == 404
