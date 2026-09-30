"""Standalone Stockfish thread/hash timing for browser quick coverage.

No application imports (stdlib only). Mirrors the worker's per-analysis
UCI sequence: setoption Threads/Hash/MultiPV/UCI_ShowWDL, Clear Hash,
isready, position fen, go nodes 200000 (browser profile nodes, MultiPV 1).

Phase 1: single-process wall per position for 4 combos.
Phase 2: six concurrent processes (like six workers) for 2 configs.

Usage (inside worker image, repo mounted at /workspace):
  python experiments/prototypes/threads/timing.py
"""

from __future__ import annotations

import concurrent.futures
import contextlib
import json
import os
import random
import statistics
import subprocess
import sys
import time

STOCKFISH = "/usr/local/bin/stockfish"
NODES = 200_000
SEARCH_TIMEOUT = 60.0

FENS = (
    # startpos
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    # italian middlegame after 1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.d3 Nf6
    "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5",
    # sicilian-ish middlegame
    "rnbqkb1r/pp2pppp/3p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 1",
    # king + pawn endgame
    "8/8/4k3/8/8/4K3/4P3/8 w - - 0 1",
    # french-ish middlegame
    "rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 0 1",
)

COMBOS = ((6, 1024), (2, 1024), (1, 1024), (2, 256))
REPS = 2


def spawn() -> subprocess.Popen[str]:
    proc = subprocess.Popen(
        [STOCKFISH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    send(proc, "uci")
    expect(proc, "uciok")
    return proc


def send(proc: subprocess.Popen[str], cmd: str) -> None:
    assert proc.stdin is not None
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()


def readline(proc: subprocess.Popen[str], deadline: float) -> str:
    assert proc.stdout is not None
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("stockfish read timed out")
        line = proc.stdout.readline()
        if line == "":
            raise RuntimeError("stockfish process exited")
        return line.strip()


def expect(proc: subprocess.Popen[str], token: str) -> None:
    deadline = time.monotonic() + SEARCH_TIMEOUT
    while True:
        line = readline(proc, deadline)
        if line == token or line.endswith(token):
            return


def search_once(proc: subprocess.Popen[str], fen: str, threads: int, hash_mb: int) -> float:
    start = time.monotonic()
    send(proc, f"setoption name Threads value {threads}")
    send(proc, f"setoption name Hash value {hash_mb}")
    send(proc, "setoption name MultiPV value 1")
    send(proc, "setoption name UCI_ShowWDL value true")
    send(proc, "setoption name Clear Hash")
    send(proc, "isready")
    expect(proc, "readyok")
    send(proc, f"position fen {fen}")
    send(proc, f"go nodes {NODES}")
    deadline = time.monotonic() + SEARCH_TIMEOUT
    while True:
        line = readline(proc, deadline)
        if line.startswith("bestmove "):
            return time.monotonic() - start


def close(proc: subprocess.Popen[str]) -> None:
    with contextlib.suppress(OSError):
        send(proc, "quit")
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def single_phase() -> dict[str, list[float]]:
    results: dict[str, list[float]] = {}
    for rep in range(REPS):
        order = list(COMBOS)
        random.Random(1000 + rep).shuffle(order)
        for threads, hash_mb in order:
            key = f"t{threads}-h{hash_mb}"
            proc = spawn()
            try:
                for fen in FENS:
                    elapsed = search_once(proc, fen, threads, hash_mb)
                    results.setdefault(key, []).append(elapsed)
            finally:
                close(proc)
    return results


def parallel_batch(threads: int, hash_mb: int, n_procs: int = 6) -> float:
    """Run n_procs concurrent processes, each searching a slice of FENS.

    Returns wall seconds for (n_procs * 3) searches; 15 searches total
    across 5 FENS split round-robin (3 per process).
    """

    slices = [FENS[i::n_procs] for i in range(n_procs)]

    def drive(fens: tuple[str, ...]) -> float:
        proc = spawn()
        total = 0.0
        try:
            for fen in fens:
                total += search_once(proc, fen, threads, hash_mb)
        finally:
            close(proc)
        return total

    start = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_procs) as pool:
        futures = [pool.submit(drive, tuple(s)) for s in slices]
        for future in concurrent.futures.as_completed(futures):
            future.result()
    return time.monotonic() - start


def summarize(times: list[float]) -> dict[str, float]:
    return {
        "n": float(len(times)),
        "median": statistics.median(times),
        "mean": statistics.fmean(times),
        "min": min(times),
        "max": max(times),
    }


def main() -> int:
    t0 = time.monotonic()
    single = single_phase()
    single_summary = {key: summarize(times) for key, times in single.items()}

    batch_6 = parallel_batch(6, 1024)
    batch_2 = parallel_batch(2, 1024)
    # 6 procs x 3 searches = 18 searches per batch
    parallel_summary = {
        "six-procs-t6-h1024": {"wall": batch_6, "per_position": batch_6 / 18.0},
        "six-procs-t2-h1024": {"wall": batch_2, "per_position": batch_2 / 18.0},
    }

    total_wall = time.monotonic() - t0
    payload = {
        "nodes": NODES,
        "multipv": 1,
        "positions": len(FENS),
        "reps": REPS,
        "single_times": single,
        "single_summary": single_summary,
        "parallel_summary": parallel_summary,
        "total_wall": total_wall,
    }
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".artifacts")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print("single-process per-position seconds (configure+search):")
    for key in sorted(single_summary):
        summary = single_summary[key]
        print(
            f"  {key}: n={summary['n']:.0f} "
            f"median={summary['median']:.3f} mean={summary['mean']:.3f} "
            f"min={summary['min']:.3f} max={summary['max']:.3f}"
        )
    print("six-concurrent-process batches (18 searches each):")
    for key, summary in parallel_summary.items():
        print(f"  {key}: wall={summary['wall']:.2f}s per_position={summary['per_position']:.3f}s")
    print(f"total_wall={total_wall:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
