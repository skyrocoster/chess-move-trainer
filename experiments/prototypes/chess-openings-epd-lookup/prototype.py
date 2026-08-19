"""
Prototype (disposable, non-canonical): rule-aware EPD-keyed opening-name lookup.

Source data: lichess-org/chess-openings
  URL:        https://github.com/lichess-org/chess-openings
  License:    CC0 1.0 Universal (public domain dedication)
              https://creativecommons.org/publicdomain/zero/1.0/
  Raw files:  https://raw.githubusercontent.com/lichess-org/chess-openings/master/{a,b,c,d,e}.tsv
  Schema (raw TSV): 3 tab-separated columns: eco | name | pgn  (header row present)
  The repository's own README defines `epd` as "FEN without move numbers" and derives it
  with `pip3 install chess` + make; this prototype derives the same thing at runtime.

What this prototype does:
  1. Downloads the five raw TSV files into this topic's ignored artifact directory.
  2. Reports the observed schema and row counts per file.
  3. Builds an EPD-keyed opening-name index with python-chess:
       - replays each row's SAN PGN move by move on a chess.Board() (rule-aware;
         illegal moves / unparsable SAN are reported, never silently dropped),
       - canonical key = final board FEN minus halfmove/fullmove counters, i.e. the
         EPD ("FEN without move numbers") of the opening position,
       - duplicate EPD/name entries are grouped and reported explicitly.
  4. Looks up representative Caro-Kann positions (built from SAN move lists) and runs a
     transposition check: two different move orders must produce the same canonical key
     and the same lookup result set.

This prototype does NOT read or join any game database and does not modify production
code, requirements, lockfiles, or canonical documentation.
"""

import os
import sys
import urllib.request
from collections import Counter, defaultdict

import chess

SOURCE_URL = "https://github.com/lichess-org/chess-openings"
LICENSE = "CC0 1.0 Universal (public domain dedication)"
RAW_BASE = "https://raw.githubusercontent.com/lichess-org/chess-openings/master"
FILES = ["a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv"]

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".artifacts",
)

EXPECTED_HEADER = ["eco", "name", "pgn"]


def download() -> dict:
    """Fetch the raw TSV files into the ignored topic artifact dir (cached)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    paths = {}
    for name in FILES:
        dest = os.path.join(DATA_DIR, name)
        if not os.path.exists(dest):
            url = f"{RAW_BASE}/{name}"
            print(f"  download  {url}")
            urllib.request.urlretrieve(url, dest)
        else:
            print(f"  cached    {dest}")
        paths[name] = dest
    return paths


def parse_file(path: str):
    """Return (rows, schema_report, bad_lines) for one TSV file."""
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    if not lines:
        return [], ("EMPTY FILE", 0), []
    header = lines[0].split("\t")
    schema_report = (header, len(lines) - 1)
    rows = []
    bad = []
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            bad.append((lineno, "field_count", len(parts), line[:90]))
            continue
        rows.append(tuple(parts))  # (eco, name, pgn)
    return rows, schema_report, bad


def replay_pgn(pgn: str) -> str:
    """Replay a SAN PGN line with python-chess and return the EPD (FEN w/o move numbers)."""
    board = chess.Board()
    for tok in pgn.split():
        if tok.endswith("."):  # move-number token such as "1." or "10..."
            continue
        board.push_san(tok)
    return " ".join(board.fen().split(" ")[:4])


def build_index(paths: dict):
    """index[epd] -> list of (eco, name, pgn); also report duplicates and failures."""
    index = defaultdict(list)
    verbatim = Counter()  # (eco, name, pgn) -> occurrences
    failures = []
    per_file = {}
    for name, path in paths.items():
        rows, schema, bad = parse_file(path)
        per_file[name] = {"data_rows": len(rows), "header": schema[0]}
        failures.extend((name, lineno, kind, detail) for lineno, kind, detail in bad)
        for eco, name_, pgn in rows:
            verbatim[(eco, name_, pgn)] += 1
            try:
                epd = replay_pgn(pgn)
            except ValueError as exc:
                failures.append((name, "?", f"san_error:{exc}", pgn[:90]))
                continue
            index[epd].append((eco, name_, pgn))
    return index, verbatim, failures, per_file


def board_from_moves(san_moves):
    board = chess.Board()
    for m in san_moves:
        board.push_san(m)
    return board


def lookup(index, board):
    epd = " ".join(board.fen().split(" ")[:4])
    return epd, index.get(epd, [])


def format_entries(entries):
    return "; ".join(f'{e[0]} "{e[1]}"' for e in entries)


def main():
    print("=" * 78)
    print("PROTOTYPE: rule-aware EPD-keyed opening-name lookup (Caro-Kann focus)")
    print("=" * 78)
    print(f"python-chess version : {chess.__version__}")
    print(f"python version       : {sys.version.split()[0]}")
    print(f"data source          : {SOURCE_URL}")
    print(f"raw files            : {RAW_BASE}/{{a,b,c,d,e}}.tsv")
    print(f"license              : {LICENSE} (no rights reserved; attribution kept per request)")
    print(f"data dir             : {DATA_DIR}")
    print()

    # 1. Download ------------------------------------------------------------
    print("[1] Downloading primary-source TSV files")
    paths = download()
    print()

    # 2. Schema + counts -----------------------------------------------------
    print("[2] Schema and counts")
    index, verbatim, failures, per_file = build_index(paths)
    total_rows = 0
    for name in FILES:
        info = per_file[name]
        total_rows += info["data_rows"]
        header_ok = info["header"] == EXPECTED_HEADER
        print(
            f"  {name:<6} rows={info['data_rows']:<6} header={info['header']} "
            f"{'OK' if header_ok else 'UNEXPECTED!'}"
        )
    print(f"  TOTAL data rows: {total_rows}")
    print()

    # 3. Index + duplicate handling ------------------------------------------
    print("[3] EPD-keyed index (keys derived from PGN via python-chess)")
    key_sizes = Counter(len(v) for v in index.values())
    dup_keys = [k for k, v in index.items() if len(v) > 1]
    verbatim_dups = [(e, c) for e, c in verbatim.items() if c > 1]
    print(f"  index entries            : {sum(len(v) for v in index.values())}")
    print(f"  distinct EPD keys        : {len(index)}")
    print(f"  keys with 1 name entry   : {key_sizes.get(1, 0)}")
    print(f"  keys with >1 name entry  : {len(dup_keys)}  (expected: transpositions)")
    dup_rows = sum(len(index[k]) - 1 for k in dup_keys)
    print(f"  rows absorbed into dup   : {dup_rows}")
    print(
        f"  verbatim (eco,name,pgn)  : {len(verbatim_dups)} duplicated rows "
        f"({sum(c for _, c in verbatim_dups)} extra occurrences)"
    )
    if verbatim_dups:
        print("    examples:")
        for e, c in verbatim_dups[:5]:
            print(f"      x{c}  {e[0]} {e[1]!r} :: {e[2][:60]}")
    # duplicate EPD groups that involve Caro-Kann (B1x) names
    ck_groups = [(k, index[k]) for k in dup_keys if any(e[0].startswith("B1") for e in index[k])]
    print(f"  Caro-Kann (B1x) dup groups: {len(ck_groups)}")
    for k, entries in ck_groups[:4]:
        print(f"      EPD {k}")
        for e in entries:
            print(f"        {e[0]} {e[1]!r} :: {e[2]}")
    print(f"  parse/illegal-move failures : {len(failures)}")
    for f in failures[:5]:
        print(f"      {f}")
    print()

    # 4. Caro-Kann lookups ---------------------------------------------------
    print("[4] Representative Caro-Kann lookups (SAN move lists, python-chess built)")
    tests = [
        ("Caro-Kann Defense, base 1.e4 c6", ["e4", "c6"]),
        ("Caro-Kann 2.d4 d5", ["e4", "c6", "d4", "d5"]),
        ("Caro-Kann Advance 3.e5", ["e4", "c6", "d4", "d5", "e5"]),
        ("Caro-Kann Advance 3...Bf5", ["e4", "c6", "d4", "d5", "e5", "Bf5"]),
        ("Caro-Kann Exchange 3...cxd5", ["e4", "c6", "d4", "d5", "exd5", "cxd5"]),
        ("Caro-Kann Panov 4.c4", ["e4", "c6", "d4", "d5", "exd5", "cxd5", "c4"]),
        ("Caro-Kann Classical 4...Bf5", ["e4", "c6", "d4", "d5", "Nc3", "dxe4", "Nxe4", "Bf5"]),
    ]
    for label, moves in tests:
        board = board_from_moves(moves)
        epd, hits = lookup(index, board)
        status = "FOUND" if hits else "NOT FOUND"
        print(f"  {label:<32} [{status}] EPD {epd}")
        if hits:
            for e in hits:
                print(f"      {e[0]} {e[1]!r} :: {e[2]}")
    print()

    # 5. Transposition-oriented check ----------------------------------------
    print("[5] Transposition check (same position via two move orders)")
    trans_a = ["e4", "c6", "d4", "d5", "exd5", "cxd5", "c4", "Nf6", "Nc3", "e6"]
    trans_b = ["c4", "c6", "e4", "d5", "exd5", "cxd5", "d4", "Nf6", "Nc3", "e6"]
    ba = board_from_moves(trans_a)
    bb = board_from_moves(trans_b)
    epd_a, hits_a = lookup(index, ba)
    epd_b, hits_b = lookup(index, bb)
    same_key = epd_a == epd_b
    same_hits = hits_a == hits_b
    print("  order A '1.e4 c6 2.d4 d5 3.exd5 cxd5 4.c4 Nf6 5.Nc3 e6'")
    print(f"    EPD  = {epd_a}")
    print(f"    hits = {format_entries(hits_a) if hits_a else 'NOT FOUND'}")
    print("  order B '1.c4 c6 2.e4 d5 3.exd5 cxd5 4.d4 Nf6 5.Nc3 e6'")
    print(f"    EPD  = {epd_b}")
    print(f"    hits = {format_entries(hits_b) if hits_b else 'NOT FOUND'}")
    print(f"  identical canonical EPD key : {same_key}")
    print(f"  identical lookup result set : {same_hits}")
    assert same_key, "transposition must yield the same canonical EPD key"
    assert same_hits, "transposition must yield the same lookup result set"
    print("  ASSERT OK: rule-aware EPD keying is transposition-stable")
    print()

    # 6. Backtrack classification demo (README convention) ------------------
    print("[6] Backtrack demo (README convention: walk back to first named position)")
    deep = ["e4", "c6", "d4", "d5", "Nc3", "dxe4", "Nxe4", "Bf5", "Ng3", "e6", "Nf3"]
    board = board_from_moves(deep)
    found = None
    for ply in range(len(deep), 0, -1):
        probe = board_from_moves(deep[:ply])
        epd, hits = lookup(index, probe)
        if hits:
            found = (ply, epd, hits)
            break
    if found:
        ply, epd, hits = found
        print(f"  deep line: {' '.join(deep)}")
        print(f"  first named position at ply {ply}: EPD {epd}")
        print(f"  -> {format_entries(hits)}")
    else:
        print("  no named position found walking back (unexpected for Caro-Kann)")
    print()
    print("[done]")

    # Return a compact machine-readable summary too.
    return {
        "chess_version": chess.__version__,
        "total_rows": total_rows,
        "distinct_keys": len(index),
        "dup_keys": len(dup_keys),
        "failures": len(failures),
    }


if __name__ == "__main__":
    summary = main()
    print(f"SUMMARY {summary}")
