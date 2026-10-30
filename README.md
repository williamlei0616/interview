# Article Dashboard Optimization Exercise

You have inherited a small Python and SQLite article dashboard. Your manager says the dashboard is too slow and wants the default request to complete in under **0.5 seconds** on the reference machine.

Use the repository and benchmark to understand the current behavior, make a focused improvement, and keep the dashboard output correct. You may use a coding agent with screen sharing, but you must review the changes, run the tests, and explain your decisions.

## Setup

The repository uses only Python's standard library and SQLite. A seeded database is included. To recreate it:

    python seed_db.py --db article_dashboard.db --rows 20000

Run the tests:

    python -m unittest discover -s tests -v

Run the benchmark:

    python benchmark.py --db article_dashboard.db --start 2025-01-01 --end 2026-01-01

The benchmark reports correctness, SQL statement count, elapsed time, processed rows, and a result digest.

## Requirements

- Preserve the existing dashboard output contract.
- Include only published articles.
- The start date is inclusive and the end date is exclusive.
- Support the optional category filter.
- Return the top five articles with deterministic tie-breaking.
- Keep the tests passing.
- Measure the result before and after your change.

Start by explaining what you observe. Make the smallest high-impact improvement you can, then describe what you would do next if this were a production service.

## AI usage

Coding agents are allowed with screen sharing. You are responsible for the final code: review the diff, verify the result, and explain important implementation and trade-off decisions.
