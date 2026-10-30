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
    assert england["flag"] == "/raster/country_flags/189.png"


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


def test_selected_club_returns_its_squad(client: TestClient):
    response = client.get("/api/clubs/11/players")
    assert response.status_code == 200
    squad = response.json()
    assert len(squad) >= 20
    assert all(player["club_id"] == "11" for player in squad)
    assert any(player["name"] == "David Raya" for player in squad)


def test_player_detail_has_stats(client: TestClient):
    response = client.get("/api/players/262749")
    assert response.status_code == 200
    player = response.json()
    assert player["name"] == "David Raya"
    assert len(player["stats"]) >= 22


def test_unknown_records_return_404(client: TestClient):
    assert client.get("/api/clubs/does-not-exist").status_code == 404
    assert client.get("/api/clubs/does-not-exist/players").status_code == 404
    assert client.get("/api/players/does-not-exist").status_code == 404
