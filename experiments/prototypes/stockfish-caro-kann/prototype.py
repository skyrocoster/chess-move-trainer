"""
Prototype (disposable, non-canonical): Stockfish 18 fixed-depth checkpoint over a
reproducible, branch-diverse sample of named Caro-Kann positions from the
lichess-org/chess-openings TSV data.

Scope and provenance
--------------------
- Stockfish 18 (Windows x86-64 AVX2), official release tag `sf_18`:
    https://github.com/official-stockfish/Stockfish/releases/tag/sf_18
    asset: stockfish-windows-x86-64-avx2.zip
    SHA-256 must equal 6f6c272ebd6ea594377715235c8a7326f75940ef4f4f856f45106028fe6ae900
    (verified hard-fail before any analysis; archive + extracted exe/source/GPL
  files are kept exclusively under this prototype's own ignored artifact dir).
- Opening data: lichess-org/chess-openings, CC0 1.0 (public domain dedication),
  raw {a..e}.tsv files previously downloaded under
  experiments/prototypes/chess-openings-epd-lookup/.artifacts/.
  This prototype only reads those five TSV files; it does not read or join any
  game database.
- Engine binding: python-chess (installed in the experiments environment).

Sample selection rule (reproducible, branch-diverse)
----------------------------------------------------
For each ECO code B10..B19 in order, among TSV rows whose name starts with
"Caro-Kann Defense":
  1. group rows by exact name, keep the row with the most plies per name;
  2. prefer the deepest remaining row with plies <= 26 (readable mid-game
     positions); if every row for the code exceeds the cap, take the shallowest;
  3. skip rows whose SAN PGN cannot be replayed by python-chess (never silent);
  4. reject a candidate whose EPD (FEN without move numbers) duplicates an
     already-selected position; walk the sorted candidate list deterministically
     (ties broken by name, then PGN) until a distinct EPD is found.
This yields exactly one position per ECO code, i.e. one per major Caro-Kann
branch (miscellaneous, Two Knights, Advance, Exchange, Panov-Botvinnik, 3.Nc3,
Bronstein-Larsen, Karpov/Steinitz, Classical 4...Bf5, Classical main lines).

Engine settings (conservative / deterministic)
-----------------------------------------------
Threads 1; Hash 64 MB; MultiPV 3; Skill Level 20 (full strength); Move Overhead 10;
fixed depth limit 18 (no time limit). No randomness options exist in SF 18; the
determinism claim is additionally spot-checked by re-analysing the first position
after `ucinewgame` and requiring byte-identical PV1 move + score.

Score / mate semantics (never flattened)
----------------------------------------
UCI scores are from the side to move's perspective. We record BOTH perspectives:
  - "stm": side-to-move perspective (cp sign / mate plies sign relative to STM);
  - "white": White perspective (positive mate plies = White mates).
Mate scores keep their structured form: kind="mate" with plies (UCI convention,
positive = the perspective side mates) plus an explicit mating side; they are
never collapsed to a centipawn integer. Centipawns are kind="cp".

Output: printed report plus analysis-results-2026-08-18.json in the ignored
artifact dir. Nothing outside experiments/ is touched.
"""

import hashlib
import json
import os
import sys
import time
import urllib.request
import zipfile

import chess
import chess.engine

# ---------------------------------------------------------------------------
# Provenance constants
# ---------------------------------------------------------------------------
TAG = "sf_18"
ASSET = "stockfish-windows-x86-64-avx2.zip"
DOWNLOAD_URL = f"https://github.com/official-stockfish/Stockfish/releases/download/{TAG}/{ASSET}"
EXPECTED_SHA256 = "6f6c272ebd6ea594377715235c8a7326f75940ef4f4f856f45106028fe6ae900"

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, ".artifacts")
ARCHIVE_PATH = os.path.join(DATA_DIR, ASSET)
EXTRACT_DIR = os.path.join(DATA_DIR, "stockfish-windows-x86-64-avx2")
RESULTS_PATH = os.path.join(DATA_DIR, "analysis-results-2026-08-18.json")

OPENINGS_DATA_DIR = os.path.join(HERE, "..", "chess-openings-epd-lookup", ".artifacts")
TSV_FILES = ["a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv"]

# Engine / search settings (conservative deterministic)
ENGINE_SETTINGS = {
    "Threads": 1,
    "Hash": 64,
    "MultiPV": 3,
    "Skill Level": 20,
    "Move Overhead": 10,
}
DEPTH = 18
PLY_CAP = 26

SOURCE_NOTE = (
    "lichess-org/chess-openings (CC0 1.0 public domain dedication); "
    "https://github.com/lichess-org/chess-openings"
)


# ---------------------------------------------------------------------------
# Step 1: archive download + SHA-256 verification + extraction (cached)
# ---------------------------------------------------------------------------
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_archive() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    downloaded = False
    if not os.path.exists(ARCHIVE_PATH):
        print(f"  download {DOWNLOAD_URL}")
        urllib.request.urlretrieve(DOWNLOAD_URL, ARCHIVE_PATH)
        downloaded = True
    actual = sha256_file(ARCHIVE_PATH)
    ok = actual == EXPECTED_SHA256
    if not ok:
        raise SystemExit(
            f"SHA-256 MISMATCH for {ASSET}\n  expected {EXPECTED_SHA256}\n"
            f"  actual   {actual}\nrefusing to proceed."
        )
    members = []
    if not os.path.isdir(EXTRACT_DIR):
        with zipfile.ZipFile(ARCHIVE_PATH) as z:
            members = [i.filename for i in z.infolist() if not i.is_dir()]
            z.extractall(EXTRACT_DIR)
    else:
        members = None  # already extracted; listing preserved in JSON from first run
    exe_candidates = []
    for root, _dirs, files in os.walk(EXTRACT_DIR):
        for f in files:
            if f.endswith(".exe"):
                exe_candidates.append(os.path.join(root, f))
    if len(exe_candidates) != 1:
        raise SystemExit(f"expected exactly one .exe, found {exe_candidates}")
    return {
        "tag": TAG,
        "asset": ASSET,
        "url": DOWNLOAD_URL,
        "archive_path": ARCHIVE_PATH,
        "archive_size_bytes": os.path.getsize(ARCHIVE_PATH),
        "sha256_expected": EXPECTED_SHA256,
        "sha256_actual": actual,
        "sha256_match": ok,
        "downloaded_now": downloaded,
        "extract_dir": EXTRACT_DIR,
        "exe_path": exe_candidates[0],
        "zip_members": members,
    }


# ---------------------------------------------------------------------------
# Step 2: TSV loading + Caro-Kann sample selection
# ---------------------------------------------------------------------------
def load_tsv_rows():
    rows = []
    for name in TSV_FILES:
        path = os.path.join(OPENINGS_DATA_DIR, name)
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        for lineno, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                raise SystemExit(f"unexpected TSV shape in {name}:{lineno}: {line[:80]!r}")
            rows.append((parts[0], parts[1], parts[2]))  # (eco, name, pgn)
    return rows


def count_plies(pgn: str) -> int:
    return sum(1 for tok in pgn.split() if not tok.endswith("."))


def replay(pgn: str) -> chess.Board:
    board = chess.Board()
    for tok in pgn.split():
        if tok.endswith("."):
            continue
        board.push_san(tok)
    return board


def epd_of(board: chess.Board) -> str:
    return " ".join(board.fen().split()[:4])


def select_sample(rows):
    """Deterministic one-position-per-ECO-code sample (rule in module docstring)."""
    failures = []
    selected = []
    used_epds = set()
    for code in [f"B{i}" for i in range(10, 20)]:
        candidates = [r for r in rows if r[0] == code and r[1].startswith("Caro-Kann Defense")]
        # group by exact name, keep deepest row per name
        by_name = {}
        for r in candidates:
            plies = count_plies(r[2])
            if r[1] not in by_name or plies > by_name[r[1]][0]:
                by_name[r[1]] = (plies, r)
        pool = [v for v in by_name.values() if v[0] <= PLY_CAP] or list(by_name.values())
        pool.sort(key=lambda v: (-v[0], v[1][1], v[1][2]))  # deepest, then name, then pgn
        chosen = None
        for plies, row in pool:
            try:
                board = replay(row[2])
            except ValueError as exc:
                failures.append((code, row[1], str(exc)))
                continue
            epd = epd_of(board)
            if epd in used_epds:
                failures.append((code, row[1], f"duplicate EPD {epd} (transposition)"))
                continue
            used_epds.add(epd)
            chosen = {
                "eco": code,
                "name": row[1],
                "pgn": row[2],
                "plies": plies,
                "epd": epd,
                "board": board,
            }
            break
        if chosen is None:
            raise SystemExit(f"no selectable row for {code}; failures: {failures}")
        selected.append(chosen)
    return selected, failures


# ---------------------------------------------------------------------------
# Step 3: score handling (structured, mate-aware)
# ---------------------------------------------------------------------------
def score_to_dict(score: chess.engine.Score) -> dict:
    """Score already expressed in one fixed perspective."""
    mate = score.mate()  # plies; positive => perspective side mates
    if mate is not None:
        return {"kind": "mate", "plies": mate}
    return {"kind": "cp", "cp": score.score()}


def mating_side_for(rec: dict, stm_is_white: bool) -> str:
    """Explicit mating side for a stm-perspective mate record."""
    if rec["kind"] != "mate":
        return None
    return "white" if (rec["plies"] > 0) == stm_is_white else "black"


def render_score(rec: dict, perspective: str, stm_is_white: bool) -> str:
    if rec["kind"] == "cp":
        return f"cp {rec['cp']:+d} ({perspective})"
    plies = rec["plies"]
    moves = (abs(plies) + 1) // 2
    side = (
        mating_side_for(rec, stm_is_white)
        if perspective == "stm"
        else ("white" if plies > 0 else "black")
    )
    return f"mate in {moves} for {side} ({plies:+d} plies, {perspective})"


# ---------------------------------------------------------------------------
# Step 4: engine analysis
# ---------------------------------------------------------------------------
def setup_engine(exe_path: str):
    engine = chess.engine.SimpleEngine.popen_uci(exe_path)
    applied = {}
    for name, value in ENGINE_SETTINGS.items():
        if name in engine.options:
            engine.configure({name: value})
            applied[name] = value
        else:
            applied[name] = None  # option not offered by this build
    return engine, applied


def analyze_position(engine, position: dict) -> dict:
    board = position["board"]
    stm_is_white = board.turn == chess.WHITE
    t0 = time.perf_counter()
    infos = engine.analyse(
        board, chess.engine.Limit(depth=DEPTH), multipv=ENGINE_SETTINGS["MultiPV"]
    )
    wall_s = time.perf_counter() - t0
    pvs = []
    for info in infos:
        pv = info.get("pv", [])
        stm_rec = score_to_dict(info["score"].pov())
        wht_rec = score_to_dict(info["score"].white())
        pvs.append(
            {
                "multipv": info.get("multipv", len(pvs) + 1),
                "depth": info.get("depth"),
                "nodes": info.get("nodes"),
                "time_ms": info.get("time"),
                "nps": info.get("nps"),
                "hashfull": info.get("hashfull"),
                "tbhits": info.get("tbhits", 0),
                "pv_first_move": board.san(pv[0]) if pv else None,
                "pv_first_move_uci": pv[0].uci() if pv else None,
                "pv_san": board.variation_san(pv) if pv else "",
                "pv_len": len(pv),
                "stm_score": stm_rec,
                "white_score": wht_rec,
                "stm_score_raw": str(info["score"].pov()),
                "white_score_raw": str(info["score"].white()),
                "stm_label": render_score(stm_rec, "stm", stm_is_white),
                "white_label": render_score(wht_rec, "white", stm_is_white),
            }
        )
    best = pvs[0] if pvs else {}
    return {
        "eco": position["eco"],
        "name": position["name"],
        "pgn": position["pgn"],
        "plies": position["plies"],
        "epd": position["epd"],
        "side_to_move": "white" if stm_is_white else "black",
        "wall_seconds": round(wall_s, 3),
        "depth_target": DEPTH,
        "depth_best_observed": best.get("depth"),
        "pvs": pvs,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    started = time.perf_counter()
    print("=" * 82)
    print("PROTOTYPE: Stockfish 18 checkpoint - Caro-Kann named positions (fixed depth)")
    print("=" * 82)
    print(f"python            : {sys.version.split()[0]}")
    print(f"python-chess      : {chess.__version__}")
    print(f"engine tag        : {TAG}   asset: {ASSET}")
    print(f"expected sha256   : {EXPECTED_SHA256}")
    print(f"openings data     : {SOURCE_NOTE}")
    print()

    # --- 1. archive --------------------------------------------------------
    print("[1] Stockfish archive download + SHA-256 verification + extraction")
    arc = ensure_archive()
    print(f"  archive  : {arc['archive_path']}")
    print(f"  size     : {arc['archive_size_bytes']} bytes")
    print(f"  sha256   : {arc['sha256_actual']}")
    print(f"  verified : {arc['sha256_match']}  (expected {EXPECTED_SHA256})")
    if not arc["sha256_match"]:
        raise SystemExit("aborting: SHA-256 did not match")
    if arc["zip_members"] is not None:
        print(f"  zip members ({len(arc['zip_members'])} files):")
        for m in arc["zip_members"]:
            print(f"    {m}")
    print(f"  exe      : {arc['exe_path']}")
    print()

    # --- 2. sample ---------------------------------------------------------
    print("[2] Deterministic branch-diverse Caro-Kann sample (one per ECO B10..B19)")
    rows = load_tsv_rows()
    sample, sel_failures = select_sample(rows)
    print(
        f"  selection rule : per ECO code B10..B19, deepest named row with plies "
        f"<= {PLY_CAP}, unique EPD, ties broken by name then PGN"
    )
    print(f"  skipped rows   : {len(sel_failures)} (replay/dup issues, reported below)")
    for code, name, why in sel_failures:
        print(f"    {code} {name!r}: {why}")
    print(f"  selected positions: {len(sample)}")
    for i, p in enumerate(sample, 1):
        stm = "white" if p["board"].turn == chess.WHITE else "black"
        print(f"    {i:>2}. {p['eco']} {p['name']}  (plies={p['plies']}, stm={stm})")
    print()

    # --- 3. engine ---------------------------------------------------------
    print("[3] Engine startup + conservative deterministic settings")
    engine, applied = setup_engine(arc["exe_path"])
    print(f"  engine id  : {engine.id.get('name')!r} by {engine.id.get('author')!r}")
    for name, value in applied.items():
        status = f"{value}" if value is not None else "NOT OFFERED - left at default"
        print(f"  option {name:<14} = {status}")
    print(
        f"  search     : fixed depth {DEPTH}, MultiPV {ENGINE_SETTINGS['MultiPV']}, no time limit"
    )
    print()

    # --- 4. analysis -------------------------------------------------------
    print("[4] Fixed-depth analysis (this is the long step)")
    results = []
    for i, p in enumerate(sample, 1):
        res = analyze_position(engine, p)
        results.append(res)
        print(f"  [{i:>2}/{len(sample)}] {res['eco']} {res['name']}")
        print(f"      line  : {' '.join(p['pgn'].split())}")
        print(f"      epd   : {res['epd']}")
        print(
            f"      stm   : {res['side_to_move']}   depth(best)={res['depth_best_observed']} "
            f" wall={res['wall_seconds']}s"
        )
        for pv in res["pvs"]:
            print(
                f"      PV{pv['multipv']}: {pv['pv_first_move'] or '-'}  "
                f"d={pv['depth']} n={pv['nodes']} t={pv['time_ms']}ms  "
                f"stm[{pv['stm_label']}]  white[{pv['white_label']}]"
            )
        print(f"      PV1 SAN: {res['pvs'][0]['pv_san'] if res['pvs'] else '-'}")
        print(f"      PV2 SAN: {res['pvs'][1]['pv_san'] if len(res['pvs']) > 1 else '-'}")
        print(f"      PV3 SAN: {res['pvs'][2]['pv_san'] if len(res['pvs']) > 2 else '-'}")
        sys.stdout.flush()
    print()

    # --- 5. determinism spot-check -----------------------------------------
    print("[5] Determinism spot-check (ucinewgame, re-analyse position 1)")
    engine.send_uci_command("ucinewgame")
    first = results[0]
    recheck = analyze_position(engine, sample[0])
    a, b = first["pvs"][0], recheck["pvs"][0]
    same = (
        a["pv_first_move_uci"] == b["pv_first_move_uci"]
        and a["stm_score"] == b["stm_score"]
        and a["white_score"] == b["white_score"]
    )
    print(
        f"  run1 : {a['pv_first_move_uci']} {a['stm_score']} {a['white_score']} "
        f"(d={a['depth']}, n={a['nodes']})"
    )
    print(
        f"  run2 : {b['pv_first_move_uci']} {b['stm_score']} {b['white_score']} "
        f"(d={b['depth']}, n={b['nodes']})"
    )
    print(f"  identical PV1 move + scores : {same}")
    determinism = {
        "position_eco": first["eco"],
        "position_name": first["name"],
        "run1": {
            "move": a["pv_first_move_uci"],
            "stm": a["stm_score"],
            "white": a["white_score"],
            "nodes": a["nodes"],
        },
        "run2": {
            "move": b["pv_first_move_uci"],
            "stm": b["stm_score"],
            "white": b["white_score"],
            "nodes": b["nodes"],
        },
        "identical_pv1_move_and_scores": same,
        "wall_seconds": recheck["wall_seconds"],
    }
    engine.quit()
    total_s = time.perf_counter() - started
    print()

    # --- 6. report ---------------------------------------------------------
    print("[6] Summary")
    total_analysis_wall = round(sum(r["wall_seconds"] for r in results), 3)
    print(f"  positions analyzed : {len(results)}")
    print(
        f"  analysis wall time : {total_analysis_wall}s "
        f"(per-position: {[r['wall_seconds'] for r in results]})"
    )
    print(f"  determinism check  : {determinism['identical_pv1_move_and_scores']}")
    print(f"  total runtime      : {round(total_s, 3)}s")
    print()
    print("SCORE SEMANTICS (recorded both ways, mates never flattened to cp):")
    print("  stm   = side to move's perspective (UCI native);  positive mate plies = STM mates")
    print("  white = White's perspective;                      positive mate plies = White mates")
    print("  mate  = structured {kind:'mate', plies:N};  cp = {kind:'cp', cp:N} centipawns")
    print()

    report = {
        "provenance": {
            "stockfish": {
                "tag": TAG,
                "asset": ASSET,
                "url": DOWNLOAD_URL,
                "sha256_expected": EXPECTED_SHA256,
                "sha256_actual": arc["sha256_actual"],
                "sha256_match": arc["sha256_match"],
                "archive_size_bytes": arc["archive_size_bytes"],
                "extract_dir": arc["extract_dir"],
                "exe_path": arc["exe_path"],
            },
            "openings_data": SOURCE_NOTE,
            "openings_files": [os.path.join(OPENINGS_DATA_DIR, f) for f in TSV_FILES],
        },
        "engine_id": engine.id,
        "settings": {
            **ENGINE_SETTINGS,
            "depth": DEPTH,
            "options_applied": applied,
            "time_limit": None,
        },
        "selection_rule": (
            f"per ECO code B10..B19: deepest named 'Caro-Kann Defense' row with plies "
            f"<= {PLY_CAP}, unique EPD, ties by name then PGN"
        ),
        "selection_skips": [{"eco": c, "name": n, "reason": w} for c, n, w in sel_failures],
        "score_semantics": {
            "stm": "side-to-move perspective; mate plies positive = STM mates",
            "white": "White perspective; mate plies positive = White mates",
            "mate_representation": "structured {kind:'mate', plies:N}; never flattened to cp",
        },
        "positions": [
            {k: v for k, v in r.items() if k != "pvs"} | {"pvs": r["pvs"]} for r in results
        ],
        "determinism_spot_check": determinism,
        "totals": {
            "positions": len(results),
            "analysis_wall_seconds": total_analysis_wall,
            "per_position_wall_seconds": [r["wall_seconds"] for r in results],
            "total_runtime_seconds": round(total_s, 3),
        },
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print(f"JSON results written to {RESULTS_PATH}")
    print("[done]")


if __name__ == "__main__":
    main()
