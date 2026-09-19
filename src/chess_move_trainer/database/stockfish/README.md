# Stockfish worker modules

`engine.py`, `queue.py`, and `benchmark.py` are the public compatibility
boundaries. Their focused sibling modules own models, parsing, persistence, and
runtime work. Import public values from those three modules unless a sibling is
explicitly package-internal.

The worker acquires the database mutex before it claims queue work. The engine
process, queue transactions, and benchmark artifact writes all use finite
timeouts or retry limits; do not introduce unbounded waits.
