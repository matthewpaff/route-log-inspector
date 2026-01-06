> **Illustrative Git calendar:** 2024-01-08 through 2026-10-23, assigned November 6, 2026.
> Actual development occurred in November 2026. These dates are simulated,
> not evidence of historical work or employment. This supersedes older
> statements below about actual Git dates. See [HISTORY.md](HISTORY.md).

# Route Log Inspector

A dependency-free CLI for inspecting supplied JSONL request logs. It calculates deterministic nearest-rank p50/p95 latency, 5xx rate by route, optional trace filtering, and explicit sample-based SLO checks. Created in November 2026 with actual commit dates as a practical utility inspired by the blueprint's 2024–2026 operations theme.

## Run

Python 3.10+ and its standard library are sufficient. No package installation or live service is needed.

```powershell
python cli.py sample.jsonl
python cli.py sample.jsonl --route /tours/bookings --format csv
python cli.py sample.jsonl --slo-p95-ms 500 --slo-5xx-pct 1
python -m unittest discover -s tests -v
```

The SLO command returns exit code 0 when every selected route passes, 3 when a threshold fails or no rows match, 2 for invalid input, and 1 for file errors. It reports only on **supplied sample rows**, not production service health. A timestamp must have a timezone; each row must contain `timestamp`, a route template, HTTP `status`, `duration_ms`, and `trace_id`. Inputs are bounded to 50,000 rows, 8 MiB total, and 16 KiB per row. Duplicate JSON keys, malformed UTF-8, query-bearing routes, and invalid numeric types are rejected.

No requests are made to a log service, and no third-party packages are installed. The sample is synthetic. See [HISTORY.md](HISTORY.md) for provenance.
