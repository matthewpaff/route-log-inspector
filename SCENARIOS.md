# Synthetic scenario library

This library contains 460 generated input/expected-output cases, created November 6, 2026. Every case declares `synthetic: true`, a schema version, a unique ID, and an explicit expected result or expected validation error. The fixtures contain no live customer data.

Run `python scenarios.py` or `python -m unittest discover -s tests -v`. The runner makes no network requests and installs nothing. Intent cases use disposable SQLite databases. The standard test suite replays the entire library in CI. Exact expected outputs are stored in the fixture rather than calculated by the function under test.

| Case family | Count |
| --- | ---: |
| baseline | 57 |
| parse | 114 |
| slo | 96 |
| summary | 98 |
| timeline | 19 |
| window | 76 |

Parameters vary times, versions, ordering, source channels, rows, sample sizes, and invalid inputs. This is a parameter matrix, not a claim of that many independent bugs or feature changes. One-case commits deliberately support the disclosed illustrative calendar.
