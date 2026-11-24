# API benchmarks

The benchmark tests are in [`backend/tests/benchmarks/`](../../../backend/tests/benchmarks/).

```bash
timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/benchmarks -v
```

Set `CHESS_RUN_API_BENCHMARK_REAL=1` to run the opt-in real-database cases.
Timestamped JSON reports written here are local generated output and are not
committed. The complete maintenance runner writes its reports under
`.stage-check/full-test/`; see [`docs/TESTING.md`](../../TESTING.md).
