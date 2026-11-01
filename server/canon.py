from __future__ import annotations

import json
import os
import sqlite3
from datetime import date
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "canon.db"
CUTOUT_FACES_DIR = REPO_ROOT / "data" / "raster" / "players_faces_cutout"
KIT_SPECS_PATH = REPO_ROOT / "data" / "raster" / "teams_kits" / "specs.json"
NATIONAL_KIT_SPECS_PATH = REPO_ROOT / "data" / "raster" / "teams_kits" / "national_specs.json"


def _cutout_face_ids() -> frozenset[str]:
    if not CUTOUT_FACES_DIR.is_dir():
        return frozenset()
    return frozenset(path.stem for path in CUTOUT_FACES_DIR.iterdir() if path.suffix == ".png")


CUTOUT_FACE_IDS = _cutout_face_ids()
EMBLEM_DIR = REPO_ROOT / "data" / "raster" / "teams_emblems"

COUNTRY_COLUMNS = "co.id, co.name, co.flag"
LEAGUE_COLUMNS = "l.id, l.name, l.country_id, l.tier, l.tier_rank, l.logo"
CLUB_COLUMNS = (
    "c.id, c.name, c.league_id, c.country_id, c.logo, c.colors, "
    "c.stadium_name, c.stadium_seats, c.founded_on"
)
PLAYER_COLUMNS = (
    "p.id, p.name, p.first_name, p.last_name, p.birth_date, p.height, p.foot, "
    "p.citizenship, p.position, p.position_other, p.club_id, p.national_team_id, "
    "p.shirt_number, p.market_value, p.overall, p.pot, p.weight, p.weak_foot, "
    "p.skill_moves, p.role, p.stats"
)

ROLE_ORDER = {
    "GK": 0,
    "CB": 1,
    "LB": 2,
    "RB": 3,
    "DM": 4,
    "CM": 5,
    "LM": 6,
    "RM": 7,
    "AM": 8,
    "CF": 9,
}

LINE_ROLES = {
    "attack": ("CF", "LM", "RM"),
    "midfield": ("DM", "CM", "AM"),
    "defence": ("CB", "LB", "RB"),
}

LINE_SIZE = {"attack": 3, "midfield": 3, "defence": 4}

KIT_IDS = ("main", "white", "black", "reserve")
KIT_PATTERNS = {"plain", "stripes", "halves", "hoops", "sash"}
FALLBACK_PALETTE = ["#F5F7FA", "#171B3F", "#5A5F78", "#1D2138"]
FALLBACK_KITS = {
    "main": {"shirt": 0, "shorts": 1, "pattern": "plain", "pattern_color": None},
    "white": {"shirt": 0, "shorts": 0, "pattern": "plain", "pattern_color": None},
    "black": {"shirt": 1, "shorts": 1, "pattern": "plain", "pattern_color": None},
    "reserve": {"shirt": 2, "shorts": 1, "pattern": "plain", "pattern_color": None},
}

STAR_FLOOR = 59.0
STAR_STEP = 7.0


def stars_for(average: float | None) -> float | None:
    if average is None:
        return None
    raw = 1 + (average - STAR_FLOOR) / STAR_STEP
    stepped = round(raw * 2) / 2
    return max(0.5, min(5.0, stepped))


def _line_rating(overalls: list[float], size: int) -> int | None:
    if not overalls:
        return None
    best = sorted(overalls, reverse=True)[:size]
    return int(round(sum(best) / len(best)))


def club_ratings(club_id: str, players: list[tuple[str, float]]) -> dict:
    overalls = [overall for _, overall in players]
    top = sorted(overalls, reverse=True)[:11]
    average = sum(top) / len(top) if top else None

    payload = {"club_id": club_id}
    for line, roles in LINE_ROLES.items():
        value = _line_rating([overall for role, overall in players if role in roles], LINE_SIZE[line])
        if value is None and average is not None:
            value = int(round(average))
        payload[line] = value
    payload["stars"] = stars_for(average)
    return payload



def default_db_path() -> Path:
    return Path(os.environ.get("GF_CANON_DB", DEFAULT_DB))


def _versioned(asset_path: str | None) -> str | None:
    """Append the file mtime so a replaced asset busts the browser cache."""
    if not asset_path:
        return asset_path
    relative = asset_path.removeprefix("/raster/")
    try:
        stamp = int((REPO_ROOT / "data" / "raster" / relative).stat().st_mtime)
    except OSError:
        return asset_path
    return f"{asset_path}?v={stamp}"


def age_from_birth_date(birth_date: str | None) -> int | None:
    if not birth_date:
        return None
    try:
        born = date.fromisoformat(birth_date)
    except ValueError:
        return None
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def _json_list(value: str | None) -> list:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


@lru_cache(maxsize=1)
def _club_spec_index() -> dict[str, dict]:
    if not KIT_SPECS_PATH.exists():
        return {}
    rows = json.loads(KIT_SPECS_PATH.read_text(encoding="utf-8"))
    return {str(row["id"]): row for row in rows}


@lru_cache(maxsize=1)
def _national_spec_index() -> dict[str, dict]:
    if not NATIONAL_KIT_SPECS_PATH.exists():
        return {}
    rows = json.loads(NATIONAL_KIT_SPECS_PATH.read_text(encoding="utf-8"))
    return {row["name"].strip().lower(): row for row in rows}


def _palette_color(palette: list[str], index: int | None, fallback: str) -> str:
    if isinstance(index, int) and 0 <= index < len(palette):
        return palette[index]
    return fallback


def _kit_colors(palette: list[str], spec: dict | None) -> dict:
    spec = spec or {}
    pattern = spec.get("pattern")
    if pattern not in KIT_PATTERNS:
        pattern = "plain"
    return {
        "shirt": _palette_color(palette, spec.get("shirt"), FALLBACK_PALETTE[0]),
        "shorts": _palette_color(palette, spec.get("shorts"), FALLBACK_PALETTE[0]),
        "pattern": pattern,
        "pattern_color": _palette_color(palette, spec.get("pattern_color"), "#000000")
        if pattern != "plain"
        else None,
    }


class Canon:
    def __init__(self, path: Path | None = None):
        self.path = Path(path or default_db_path())
        if not self.path.exists():
            raise FileNotFoundError(
                f"canon.db not found at {self.path}; run `python scripts/build_canon_db.py`"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(f"file:{self.path.as_posix()}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def meta(self) -> dict:
        with self._connect() as connection:
            rows = connection.execute("SELECT key, value FROM meta").fetchall()
        raw = {row["key"]: row["value"] for row in rows}
        integer_keys = {
            "countries",
            "leagues",
            "clubs",
            "players",
            "national_teams",
            "stats_per_player",
            "free_agents",
            "free_agents_enriched",
        }
        counts = {key: int(raw[key]) for key in integer_keys if key in raw}
        return {
            "schema_version": int(raw.get("schema_version", 0)),
            "source_snapshot_date": raw.get("source_snapshot_date"),
            "counts": counts,
        }

    def countries(self) -> list[dict]:
        query = f"""
            SELECT {COUNTRY_COLUMNS},
                (SELECT COUNT(*) FROM leagues l WHERE l.country_id = co.id) AS leagues_count,
                (SELECT COUNT(*) FROM clubs c WHERE c.country_id = co.id) AS clubs_count
            FROM countries co
            ORDER BY co.name
        """
        with self._connect() as connection:
            rows = connection.execute(query).fetchall()
        countries = [dict(row) for row in rows]
        for country in countries:
            country["flag"] = _versioned(country["flag"])
        return countries

    def country(self, country_id: str) -> dict | None:
        query = f"SELECT {COUNTRY_COLUMNS} FROM countries co WHERE co.id = ?"
        with self._connect() as connection:
            row = connection.execute(query, (country_id,)).fetchone()
        return dict(row) if row else None

    def leagues(self, country_id: str | None = None) -> list[dict]:
        query = f"""
            SELECT {LEAGUE_COLUMNS}, co.name AS country_name, co.flag AS country_flag,
                (SELECT COUNT(*) FROM clubs c WHERE c.league_id = l.id) AS clubs_count
            FROM leagues l
            JOIN countries co ON co.id = l.country_id
            WHERE (? IS NULL OR l.country_id = ?)
            ORDER BY co.name, l.tier_rank, l.name
        """
        with self._connect() as connection:
            rows = connection.execute(query, (country_id, country_id)).fetchall()
        return [dict(row) for row in rows]

    def clubs(
        self,
        league_id: str | None = None,
        country_id: str | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[dict]:
        query = f"""
            SELECT {CLUB_COLUMNS}, l.name AS league_name, l.tier, l.tier_rank,
                co.name AS country_name, co.flag AS country_flag
            FROM clubs c
            JOIN leagues l ON l.id = c.league_id
            JOIN countries co ON co.id = c.country_id
            WHERE (? IS NULL OR c.league_id = ?)
              AND (? IS NULL OR c.country_id = ?)
            ORDER BY co.name, l.tier_rank, l.name, c.name
            LIMIT ? OFFSET ?
        """
        with self._connect() as connection:
            rows = connection.execute(
                query, (league_id, league_id, country_id, country_id, limit, offset)
            ).fetchall()
        return [self._club_row(row) for row in rows]

    def club(self, club_id: str) -> dict | None:
        query = f"""
            SELECT {CLUB_COLUMNS}, l.name AS league_name, l.tier, l.tier_rank,
                co.name AS country_name, co.flag AS country_flag
            FROM clubs c
            JOIN leagues l ON l.id = c.league_id
            JOIN countries co ON co.id = c.country_id
            WHERE c.id = ?
        """
        with self._connect() as connection:
            row = connection.execute(query, (club_id,)).fetchone()
        return self._club_row(row) if row else None

    def club_ratings(self, club_id: str) -> dict | None:
        with self._connect() as connection:
            exists = connection.execute("SELECT 1 FROM clubs WHERE id = ?", (club_id,)).fetchone()
            if exists is None:
                return None
            rows = connection.execute(
                "SELECT role, overall FROM players WHERE club_id = ?", (club_id,)
            ).fetchall()
        return club_ratings(club_id, [(row["role"], row["overall"]) for row in rows])

    def league_ratings(self, league_id: str) -> list[dict] | None:
        with self._connect() as connection:
            exists = connection.execute("SELECT 1 FROM leagues WHERE id = ?", (league_id,)).fetchone()
            if exists is None:
                return None
            rows = connection.execute(
                "SELECT c.id AS club_id, p.role AS role, p.overall AS overall "
                "FROM clubs c LEFT JOIN players p ON p.club_id = c.id "
                "WHERE c.league_id = ? ORDER BY c.name",
                (league_id,),
            ).fetchall()
        grouped: dict[str, list[tuple[str, float]]] = {}
        for row in rows:
            players = grouped.setdefault(row["club_id"], [])
            if row["overall"] is not None:
                players.append((row["role"], row["overall"]))
        return [club_ratings(club_id, players) for club_id, players in grouped.items()]

    def national_teams(self) -> list[dict]:
        query = """
            SELECT nt.id, nt.name, c.flag
            FROM national_teams nt
            JOIN countries c ON c.name = nt.name
            ORDER BY nt.name
        """
        with self._connect() as connection:
            teams = [dict(row) for row in connection.execute(query).fetchall()]
            players = connection.execute(
                "SELECT p.national_team_id AS team_id, p.role AS role, p.overall AS overall "
                "FROM players p WHERE p.national_team_id IS NOT NULL"
            ).fetchall()

        grouped: dict[str, list[tuple[str, float]]] = {}
        for row in players:
            grouped.setdefault(row["team_id"], []).append((row["role"], row["overall"]))

        for team in teams:
            team["flag"] = _versioned(team["flag"])
            emblem = f"/raster/teams_emblems/{team['id']}.png"
            team["emblem"] = _versioned(emblem) if (EMBLEM_DIR / f"{team['id']}.png").exists() else None
            ratings = club_ratings(team["id"], grouped.get(team["id"], []))
            ratings.pop("club_id", None)
            team.update(ratings)
        return teams

    def kit_specs(self, team_id: str) -> dict | None:
        club = self.club(team_id)
        spec = None
        name = None
        if club is not None:
            name = club["name"]
            spec = _club_spec_index().get(team_id)
        else:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT name FROM national_teams WHERE id = ?", (team_id,)
                ).fetchone()
            if row is None:
                return None
            name = row["name"]
            spec = _national_spec_index().get(name.strip().lower())

        palette = spec.get("palette") if spec else FALLBACK_PALETTE
        kits = [
            {"id": kit_id, **_kit_colors(palette, (spec or {}).get(kit_id) or FALLBACK_KITS[kit_id])}
            for kit_id in KIT_IDS
        ]
        return {"team_id": team_id, "name": name, "kits": kits}

    def squad(self, club_id: str) -> list[dict]:
        rows = self._player_rows("WHERE p.club_id = ?", (club_id,))
        for player in rows:
            player.pop("stats", None)
        rows.sort(key=lambda player: (ROLE_ORDER.get(player["role"], 99), -player["overall"], player["name"]))
        return rows

    def national_squad(self, team_id: str) -> list[dict] | None:
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM national_teams WHERE id = ?", (team_id,)
            ).fetchone()
            if exists is None:
                return None
        rows = self._player_rows("WHERE p.national_team_id = ?", (team_id,))
        for player in rows:
            player.pop("stats", None)
        rows.sort(key=lambda player: (ROLE_ORDER.get(player["role"], 99), -player["overall"], player["name"]))
        return rows

    def players_by_ids(self, player_ids: list[str], with_stats: bool = False) -> list[dict]:
        if not player_ids:
            return []
        placeholders = ",".join("?" for _ in player_ids)
        rows = self._player_rows(f"WHERE p.id IN ({placeholders})", tuple(player_ids))
        by_id = {row["id"]: row for row in rows}
        players = [by_id[player_id] for player_id in player_ids if player_id in by_id]
        for player in players:
            if with_stats:
                player["stats"] = json.loads(player["stats"])
            else:
                player.pop("stats", None)
        return players

    def player(self, player_id: str) -> dict | None:
        rows = self._player_rows("WHERE p.id = ?", (player_id,))
        if not rows:
            return None
        player = rows[0]
        player["stats"] = json.loads(player.pop("stats"))
        return player

    def _player_rows(self, where: str, params: tuple) -> list[dict]:
        query = f"SELECT {PLAYER_COLUMNS} FROM players p {where}"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._player_row(row) for row in rows]

    @staticmethod
    def _club_row(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "name": row["name"],
            "league_id": row["league_id"],
            "league_name": row["league_name"],
            "tier": row["tier"],
            "tier_rank": row["tier_rank"],
            "country_id": row["country_id"],
            "country_name": row["country_name"],
            "country_flag": row["country_flag"],
            "logo": row["logo"],
            "colors": _json_list(row["colors"]),
            "stadium": {"name": row["stadium_name"], "seats": row["stadium_seats"]},
            "founded_on": row["founded_on"],
        }

    @staticmethod
    def _player_row(row: sqlite3.Row) -> dict:
        if row["id"] in CUTOUT_FACE_IDS:
            photo = f"/raster/players_faces_cutout/{row['id']}.png"
        else:
            photo = f"/raster/players_faces/{row['id']}.jpg"
        return {
            "id": row["id"],
            "name": row["name"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "birth_date": row["birth_date"],
            "age": age_from_birth_date(row["birth_date"]),
            "height": row["height"],
            "foot": row["foot"],
            "citizenship": _json_list(row["citizenship"]),
            "position": row["position"],
            "position_other": _json_list(row["position_other"]),
            "club_id": row["club_id"],
            "national_team_id": row["national_team_id"],
            "shirt_number": row["shirt_number"],
            "market_value": row["market_value"],
            "overall": round(row["overall"], 1),
            "pot": row["pot"],
            "weight": row["weight"],
            "weak_foot": row["weak_foot"],
            "skill_moves": row["skill_moves"],
            "role": row["role"],
            "stats": row["stats"],
            "photo": photo,
        }
