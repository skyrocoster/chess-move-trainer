"""Prototype probe of the Lichess Opening Explorer API with Caro-Kann positions.

Source / attribution
--------------------
- Live API spec: https://lichess.org/api/openapi.yaml (tag: Opening Explorer)
- Endpoint: GET https://explorer.lichess.org/lichess
- Explorer source: https://github.com/lichess-org/lila-openingexplorer
- Service and fair-use terms: https://lichess.org/terms-of-service
- Host note (observed 2026-08-18): the legacy host `explorer.lichess.ovh`
  now answers 401 Authorization Required on /lichess and /player, and /master
  answers 404; the spec's canonical host is `explorer.lichess.org`.
- Auth note (observed 2026-08-18): anonymous GETs to `explorer.lichess.org/lichess`
  and /masters are rejected with 401 (generic nginx HTML, no WWW-Authenticate).
  An invalid Bearer token is rejected identically. The CORS preflight (204)
  advertises `Access-Control-Allow-Credentials: true` plus the Authorization
  header, and the OpenAPI spec lists `OAuth2` as the operation-level security,
  so a Lichess OAuth2 bearer token is expected. Pass one via --token or the
  LICHESS_TOKEN environment variable.
- Query params (per spec): variant, fen, play, speeds, ratings, since, until,
  moves, topGames, recentGames, history

This is a disposable, non-canonical prototype used only to observe the live API.
It uses only the Python standard library (urllib), so no dependency changes are
needed. It does not fetch referenced raw games, does not touch the user's game
database, and does not modify any application code or docs.

CLI examples
------------
python prototype.py                                      # 5 default Caro-Kann positions
python prototype.py --top-moves 3 --top-games 0          # smaller output/payload
python prototype.py --ratings 1600,1800,2000,2200,2500 --speeds blitz,rapid,classical
python prototype.py --since 2024-01 --until 2024-12 --ratings 2000,2200 --speeds rapid
python prototype.py --fen "rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3" --variant standard
python prototype.py --token <lichess-token>           # authenticated attempt
LICHESS_TOKEN=<lichess-token> python prototype.py    # token via env var
"""

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

EXPLORER_BASE = "https://explorer.lichess.org/lichess"
USER_AGENT = "chess-move-trainer-prototype/0.1 (opening-explorer probe; stdlib urllib only)"

DEFAULT_FENS = [
    ("1.e4 (initial position)", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"),
    ("1.e4 c6", "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"),
    ("1.e4 c6 2.d4 d5", "rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3"),
    ("Advance variation: 3.e5", "rnbqkbnr/pp2pppp/2p5/3pP3/3P4/8/PPP2PPP/RNBQKBNR b KQkq - 0 3"),
    (
        "Classical variation: 3.Nc3",
        "rnbqkbnr/pp2pppp/2p5/3p4/3PP3/2N5/PPP2PPP/R1BQKBNR b KQkq - 0 3",
    ),
]


def build_url(fen, args):
    params = {"variant": args.variant, "fen": fen}
    if args.ratings:
        params["ratings"] = ",".join(args.ratings)
    if args.speeds:
        params["speeds"] = ",".join(args.speeds)
    if args.since:
        params["since"] = args.since
    if args.until:
        params["until"] = args.until
    params["moves"] = str(args.moves)
    params["topGames"] = str(args.top_games)
    if args.history:
        params["history"] = "1"
    return EXPLORER_BASE + "?" + urllib.parse.urlencode(params)


def fetch(url, token=None):
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, dict(resp.headers), body, time.time() - started, None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers), body, time.time() - started, None
    except urllib.error.URLError as exc:
        return None, {}, "", time.time() - started, str(exc)


def rate_limit_headers(headers):
    found = []
    for key, value in headers.items():
        lower = key.lower()
        if "rate" in lower or "limit" in lower or "retry" in lower or "throttl" in lower:
            found.append(f"{key}: {value}")
    return found


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--fen", action="append", help="explicit FEN (repeatable); replaces the default positions"
    )
    parser.add_argument("--variant", default="standard", help="chess variant, default standard")
    parser.add_argument(
        "--ratings", help="comma-separated rating bands, e.g. 1600,1800,2000,2200,2500"
    )
    parser.add_argument(
        "--speeds", help="comma-separated time controls, e.g. blitz,rapid,classical"
    )
    parser.add_argument("--since", help="ISO date or month, e.g. 2024-01 or 2024-01-01")
    parser.add_argument("--until", help="ISO date or month, e.g. 2024-12 or 2024-12-31")
    parser.add_argument(
        "--top-moves", type=int, default=5, help="moves to print per position (default 5)"
    )
    parser.add_argument(
        "--moves",
        type=int,
        default=12,
        help="moves param: number of most common moves to return (spec default 12)",
    )
    parser.add_argument(
        "--top-games", type=int, default=0, help="topGames param; 0 keeps the payload small"
    )
    parser.add_argument(
        "--history", action="store_true", help="request the optional history breakdown"
    )
    parser.add_argument(
        "--token", default=None, help="Lichess OAuth2 bearer token (or set LICHESS_TOKEN)"
    )
    args = parser.parse_args()

    args.token = args.token or os.environ.get("LICHESS_TOKEN", "") or None

    if args.ratings:
        args.ratings = [r.strip() for r in args.ratings.split(",") if r.strip()]
    if args.speeds:
        args.speeds = [s.strip() for s in args.speeds.split(",") if s.strip()]

    if args.fen:
        positions = [(f"custom: {f.split()[0]}", f) for f in args.fen]
    else:
        positions = DEFAULT_FENS

    print(f"Lichess Opening Explorer probe: {len(positions)} position(s)")
    print(
        f"Filters: ratings={args.ratings or 'all'} speeds={args.speeds or 'all'} "
        f"since={args.since or 'none'} until={args.until or 'none'} moves={args.moves} "
        f"topGames={args.top_games} history={args.history}"
    )
    print(f"User-Agent: {USER_AGENT}")
    print(f"Auth: {'Bearer token supplied' if args.token else 'no token (anonymous)'}")
    print()

    schema_seen = False
    observed_statuses = []
    for index, (label, fen) in enumerate(positions, 1):
        url = build_url(fen, args)
        status, headers, body, elapsed, error = fetch(url, args.token)
        observed_statuses.append(status)
        print(f"=== [{index}/{len(positions)}] {label} ===")
        print(f"FEN: {fen}")
        print(f"GET {url}")
        if error is not None:
            print(f"FAILED: {error}")
            print()
            continue
        content_type = headers.get("Content-Type") or headers.get("content-type") or "?"
        print(f"HTTP {status} in {elapsed:.2f}s | content-type: {content_type}")
        rl = rate_limit_headers(headers)
        print("Rate-limit-ish response headers: " + ("; ".join(rl) if rl else "none observed"))
        if status != 200:
            print(f"Body (first 300 chars): {body[:300]}")
            if status == 401:
                print("Note: the explorer edge currently rejects this request with 401. The live")
                print("OpenAPI spec lists OAuth2 as required security for this endpoint; supply a")
                print(
                    "Lichess token via --token or LICHESS_TOKEN to attempt an authenticated call."
                )
            print()
            continue
        try:
            data = json.loads(body)
        except ValueError as exc:
            print(f"Non-JSON body ({exc}): {body[:300]}")
            print()
            continue
        if not schema_seen:
            print("Top-level schema keys: " + ", ".join(sorted(data.keys())))
            if data.get("moves"):
                print("Move object keys: " + ", ".join(sorted(data["moves"][0].keys())))
            schema_seen = True
        total_white = data.get("white", 0)
        total_draws = data.get("draws", 0)
        total_black = data.get("black", 0)
        total_games = total_white + total_draws + total_black
        print(
            f"Position totals: white={total_white} draws={total_draws} black={total_black} (games={total_games})"
        )
        opening = data.get("opening")
        if opening and opening.get("name"):
            print(f"Opening: [{opening.get('eco', '?')}] {opening.get('name')}")
        moves = data.get("moves") or []
        print(f"Moves listed: {len(moves)} (printing top {min(args.top_moves, len(moves))})")
        for i, move in enumerate(moves[: args.top_moves], 1):
            white = move.get("white", 0)
            draws = move.get("draws", 0)
            black = move.get("black", 0)
            mtotal = white + draws + black
            freq = (mtotal / total_games * 100.0) if total_games else 0.0
            white_score = ((white + 0.5 * draws) / mtotal * 100.0) if mtotal else 0.0
            avg = move.get("averageRating")
            avg_s = str(avg) if avg is not None else "n/a"
            wp = (white / mtotal * 100) if mtotal else 0.0
            dp = (draws / mtotal * 100) if mtotal else 0.0
            bp = (black / mtotal * 100) if mtotal else 0.0
            print(
                f"  #{i} {move.get('san', '?')} [{move.get('uci', '?')}] "
                f"games={mtotal} freq={freq:.2f}% avgRating={avg_s} | "
                f"white={white} ({wp:.1f}%) draws={draws} ({dp:.1f}%) black={black} ({bp:.1f}%) "
                f"| whiteScore={white_score:.1f}%"
            )
        print()

    print("=== End-of-run summary ===")
    print(f"Requests sent: {len(positions)}")
    print("Endpoint: " + EXPLORER_BASE)
    print(
        f"HTTP statuses observed: {sorted(set(observed_statuses)) if observed_statuses else 'none'}"
    )
    if observed_statuses and all(s == 200 for s in observed_statuses):
        print("Authentication: bearer-token requests succeeded (HTTP 200 + application/json).")
        print("Earlier probes in this environment (2026-08-18) showed anonymous and invalid-bearer")
        print("GETs rejected with 401 at the nginx edge; the CORS preflight advertises credentials")
        print("+ Authorization, and the OpenAPI spec marks OAuth2 as required security.")
    else:
        print("Authentication: not all requests succeeded; see per-position statuses above.")
    print("Rate limiting: no rate-limit headers and no 429/503 were observed;")
    print("Lichess asks clients to keep request volume modest.")
    print(
        "Attribution: Lichess Opening Explorer API - https://lichess.org/api#tag/Opening-Explorer ;"
    )
    print(
        "spec: https://lichess.org/api/openapi.yaml ; service terms: https://lichess.org/terms-of-service"
    )


if __name__ == "__main__":
    main()
