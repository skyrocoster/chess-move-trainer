"""
Disposable smoke test (non-canonical): one representative Caro-Kann position,
Stockfish 18, fixed depth 1, MultiPV 3.

Reuses the already-verified/extracted SF18 archive under the sibling prototype's
ignored artifact dir; hard-fails on SHA-256 mismatch and never re-downloads when the
archive exists. Reads only the five lichess-org/chess-openings TSV files used by
the sibling epd-lookup prototype. Writes nothing to disk; prints a structured
report to stdout. The engine subprocess is always quit + closed in a `finally`
block, and the analysis call is guarded by an internal wall-clock timeout (the
external 30s Git Bash `timeout --signal=KILL` wrapper remains the hard stop).
"""

import hashlib
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout

import chess
import chess.engine

# ---------------------------------------------------------------------------
# Provenance constants (identical to the main Caro-Kann checkpoint prototype)
# ---------------------------------------------------------------------------
TAG = "sf_18"
ASSET = "stockfish-windows-x86-64-avx2.zip"
EXPECTED_SHA256 = "6f6c272ebd6ea594377715235c8a7326f75940ef4f4f856f45106028fe6ae900"

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "stockfish-caro-kann", ".artifacts")
ARCHIVE_PATH = os.path.join(DATA_DIR, ASSET)
EXTRACT_DIR = os.path.join(DATA_DIR, "stockfish-windows-x86-64-avx2")
OPENINGS_DATA_DIR = os.path.join(HERE, "..", "chess-openings-epd-lookup", ".artifacts")
TSV_FILES = ["a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv"]

ENGINE_SETTINGS = {
    "Threads": 1,
    "Hash": 64,
    "MultiPV": 3,
    "Skill Level": 20,
    "Move Overhead": 10,
}
DEPTH = 1
PLY_CAP = 26
ECO_TARGET = "B12"
INTERNAL_TIMEOUT_S = 20.0

SOURCE_NOTE = (
    "lichess-org/chess-openings (CC0 1.0 public domain dedication); "
    "https://github.com/lichess-org/chess-openings"
)


# ---------------------------------------------------------------------------
# Step 1: reuse verified archive (never download in the smoke test)
# ---------------------------------------------------------------------------
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_exe() -> tuple:
    if not os.path.isfile(ARCHIVE_PATH):
        raise SystemExit(f"archive missing: {ARCHIVE_PATH} (refusing to download in smoke test)")
    actual = sha256_file(ARCHIVE_PATH)
    if actual != EXPECTED_SHA256:
        raise SystemExit(
            f"SHA-256 MISMATCH for {ASSET}\n  expected {EXPECTED_SHA256}\n"
            f"  actual   {actual}\nrefusing to proceed."
        )
    exe_candidates = []
    for root, _dirs, files in os.walk(EXTRACT_DIR):
        for f in files:
            if f.endswith(".exe"):
                exe_candidates.append(os.path.join(root, f))
    if len(exe_candidates) != 1:
        raise SystemExit(f"expected exactly one .exe, found {exe_candidates}")
    return exe_candidates[0], actual


# ---------------------------------------------------------------------------
# Step 2: B12 sample selection (exact rule from the main prototype, one code)
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
            rows.append((parts[0], parts[1], parts[2]))
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


def select_one(rows: list) -> dict:
    """Main prototype's rule restricted to ECO B12: deepest named row, plies <= cap,
    unique EPD, ties by name then PGN. Returns the chosen position dict."""
    candidates = [r for r in rows if r[0] == ECO_TARGET and r[1].startswith("Caro-Kann Defense")]
    by_name = {}
    for r in candidates:
        plies = count_plies(r[2])
        if r[1] not in by_name or plies > by_name[r[1]][0]:
            by_name[r[1]] = (plies, r)
    pool = [v for v in by_name.values() if v[0] <= PLY_CAP] or list(by_name.values())
    pool.sort(key=lambda v: (-v[0], v[1][1], v[1][2]))
    skips = []
    used_epds = set()
    for plies, row in pool:
        try:
            board = replay(row[2])
        except ValueError as exc:
            skips.append((row[1], f"replay failed: {exc}"))
            continue
        epd = epd_of(board)
        if epd in used_epds:
            skips.append((row[1], f"duplicate EPD {epd}"))
            continue
        used_epds.add(epd)
        return {
            "eco": row[0],
            "name": row[1],
            "pgn": row[2],
            "plies": plies,
            "epd": epd,
            "board": board,
            "skips": skips,
        }
    raise SystemExit(f"no selectable row for {ECO_TARGET}; skips: {skips}")


# ---------------------------------------------------------------------------
# Step 3: score handling (identical semantics to the main prototype)
# ---------------------------------------------------------------------------
def score_to_dict(score: chess.engine.Score) -> dict:
    mate = score.mate()
    if mate is not None:
        return {"kind": "mate", "plies": mate}
    return {"kind": "cp", "cp": score.score()}


def mating_side_for(rec: dict, stm_is_white: bool) -> str:
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
# Step 4: engine setup + guarded depth-1 MultiPV-3 analysis
# ---------------------------------------------------------------------------
def setup_engine(exe_path: str):
    engine = chess.engine.SimpleEngine.popen_uci(exe_path)
    applied = {}
    try:
        for name, value in ENGINE_SETTINGS.items():
            # python-chess >= 1.9 auto-manages MultiPV; it must be passed as the
            # multipv= kwarg to analyse() (the main prototype's configure() call
            # for MultiPV raises EngineError - the root cause being fixed here).
            if name == "MultiPV":
                applied[name] = "auto (passed per-analysis: multipv=3)"
                continue
            if name in engine.options:
                engine.configure({name: value})
                applied[name] = value
            else:
                applied[name] = None
    except Exception:
        # Never leak the engine subprocess if any setup step fails.
        try:
            engine.quit()
        except Exception:
            pass
        try:
            engine.close()
        except Exception:
            pass
        raise
    return engine, applied


def analyze(engine, board: chess.Board) -> dict:
    stm_is_white = board.turn == chess.WHITE
    t0 = time.perf_counter()

    def run():
        return engine.analyse(
            board, chess.engine.Limit(depth=DEPTH), multipv=ENGINE_SETTINGS["MultiPV"]
        )

    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(run)
        try:
            infos = fut.result(timeout=INTERNAL_TIMEOUT_S)
        except FutTimeout:
            fut.cancel()
            raise SystemExit(
                f"INTERNAL TIMEOUT: analysis exceeded {INTERNAL_TIMEOUT_S}s; "
                f"external 30s wrapper is the hard stop"
            )
    wall_s = time.perf_counter() - t0
    pvs = []
    for info in infos:
        pv = info.get("pv", [])
        # python-chess 1.11: PovScore.pov(color) requires the perspective color.
        stm_rec = score_to_dict(info["score"].pov(board.turn))
        wht_rec = score_to_dict(info["score"].white())
        pvs.append(
            {
                "multipv": info.get("multipv", len(pvs) + 1),
                "depth": info.get("depth"),
                "nodes": info.get("nodes"),
                "time_ms": info.get("time"),
                "nps": info.get("nps"),
                "hashfull": info.get("hashfull"),
                "pv_first_move": board.san(pv[0]) if pv else None,
                "pv_first_move_uci": pv[0].uci() if pv else None,
                "pv_san": board.variation_san(pv) if pv else "",
                "pv_len": len(pv),
                "stm_score": stm_rec,
                "white_score": wht_rec,
                "stm_label": render_score(stm_rec, "stm", stm_is_white),
                "white_label": render_score(wht_rec, "white", stm_is_white),
            }
        )
    return {
        "side_to_move": "white" if stm_is_white else "black",
        "wall_seconds": round(wall_s, 3),
        "pvs": pvs,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print("=" * 82)
    print("SMOKE TEST: Stockfish 18 - one Caro-Kann position, depth 1, MultiPV 3")
    print("=" * 82)
    print(f"python        : {sys.version.split()[0]}")
    print(f"python-chess  : {chess.__version__}")
    print(f"engine tag    : {TAG}   asset: {ASSET}")
    print(f"openings data : {SOURCE_NOTE}")
    print()

    # 1. archive (reuse only; SHA-256 hard-fail)
    print("[1] Archive reuse + SHA-256 verification (no download)")
    exe_path, actual = find_exe()
    print(f"  archive : {ARCHIVE_PATH}")
    print(f"  sha256  : {actual}")
    print(f"  verified: {actual == EXPECTED_SHA256}")
    print(f"  exe     : {exe_path}")
    print()

    # 2. sample
    print(f"[2] Sample selection (main prototype rule, ECO {ECO_TARGET} only)")
    rows = load_tsv_rows()
    pos = select_one(rows)
    print(f"  skipped : {len(pos['skips'])} (replay/dup issues within B12)")
    for name, why in pos["skips"]:
        print(f"    {name!r}: {why}")
    stm = "white" if pos["board"].turn == chess.WHITE else "black"
    print(f"  chosen  : {pos['eco']} {pos['name']}  (plies={pos['plies']}, stm={stm})")
    print(f"  line    : {' '.join(pos['pgn'].split())}")
    print(f"  epd     : {pos['epd']}")
    print()

    # 3+4. engine + guarded analysis
    print(
        "[3] Engine startup + settings + depth-1 MultiPV-3 analysis (internal "
        f"timeout {INTERNAL_TIMEOUT_S}s; external 30s wrapper is the hard stop)"
    )
    engine = None
    try:
        engine, applied = setup_engine(exe_path)
        print(f"  engine id : {engine.id.get('name')!r} by {engine.id.get('author')!r}")
        for name, value in applied.items():
            status = f"{value}" if value is not None else "NOT OFFERED - left at default"
            print(f"  option {name:<14} = {status}")
        print(f"  search    : fixed depth {DEPTH}, MultiPV {ENGINE_SETTINGS['MultiPV']}")
        print()

        res = analyze(engine, pos["board"])
        print(
            f"[4] Result for {pos['eco']} {pos['name']} "
            f"(stm={res['side_to_move']}, wall={res['wall_seconds']}s)"
        )
        for pv in res["pvs"]:
            print(
                f"  PV{pv['multipv']}: {pv['pv_first_move'] or '-'}  "
                f"d={pv['depth']} n={pv['nodes']} t={pv['time_ms']}ms  "
                f"stm[{pv['stm_label']}]  white[{pv['white_label']}]"
            )
        print(f"  PV1 SAN: {res['pvs'][0]['pv_san'] if res['pvs'] else '-'}")
        print(f"  PV2 SAN: {res['pvs'][1]['pv_san'] if len(res['pvs']) > 1 else '-'}")
        print(f"  PV3 SAN: {res['pvs'][2]['pv_san'] if len(res['pvs']) > 2 else '-'}")
        print()
    finally:
        if engine is not None:
            try:
                engine.quit()
                # SimpleEngine is asyncio-based; the subprocess exit code lives
                # on the SubprocessTransport, not on the engine object.
                rc = engine.transport.get_returncode()
                print(f"  [shutdown] engine.quit() ok; process exit code = {rc}")
            except Exception as exc:  # noqa: BLE001 - best-effort shutdown logging
                print(f"  [shutdown] engine.quit() raised {type(exc).__name__}: {exc}")
            try:
                engine.close()
                print("  [shutdown] engine.close() ok (subprocess terminated)")
            except Exception as exc:  # noqa: BLE001
                print(f"  [shutdown] engine.close() raised {type(exc).__name__}: {exc}")

    print("[done] smoke test completed without external timeout (exit != 124/137)")


if __name__ == "__main__":
    main()
