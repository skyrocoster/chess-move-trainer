"""Fetch Chess.com player profiles for all opponents faced by the subject player.

Stores raw JSON responses per opponent under .artifacts/{username}.json.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "database" / "chess_games.db"
ARTIFACTS = Path(__file__).resolve().parent / ".artifacts"
BASE_URL = "https://api.chess.com/pub"
SUBJECT_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"
USER_AGENT = "ChessMoveTrainer-Prototype/1.0"


def get_opponent_usernames(db: sqlite3.Connection) -> list[str]:
    rows = db.execute(
        """
        SELECT DISTINCT
            CASE WHEN white_player_uuid = ? THEN black_player_uuid
                 ELSE white_player_uuid END AS opponent_uuid
        FROM games
        WHERE white_player_uuid = ? OR black_player_uuid = ?
        """,
        (SUBJECT_UUID, SUBJECT_UUID, SUBJECT_UUID),
    ).fetchall()

    uuids = [r[0] for r in rows]
    if not uuids:
        return []

    placeholders = ",".join("?" for _ in uuids)
    rows = db.execute(
        f"SELECT username FROM players WHERE uuid IN ({placeholders})",
        uuids,
    ).fetchall()
    return [r[0] for r in rows]


def fetch_profile(username: str) -> dict | None:
    url = f"{BASE_URL}/player/{username}"
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except HTTPError as exc:
        print(f"  HTTP {exc.code} for {username}")
        return None


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(str(DB_PATH))
    usernames = get_opponent_usernames(db)
    db.close()

    cached = {f.stem for f in ARTIFACTS.glob("*.json")}
    to_fetch = [u for u in usernames if u not in cached]

    print(
        f"Found {len(usernames)} unique opponents, {len(cached)} cached, {len(to_fetch)} to fetch"
    )

    for i, username in enumerate(to_fetch):
        print(f"[{i + 1}/{len(to_fetch)}] {username} ... ", end="", flush=True)
        profile = fetch_profile(username)
        if profile is None:
            continue

        dest = ARTIFACTS / f"{username}.json"
        dest.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
        status = profile.get("status", "?")
        title = profile.get("title", "")
        print(f"status={status} title={title or 'none'}")

        # Be polite with rate limits
        time.sleep(0.3)

    print(f"\nDone. Profiles saved to {ARTIFACTS}")


if __name__ == "__main__":
    main()
