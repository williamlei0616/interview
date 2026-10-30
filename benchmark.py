from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from dashboard import build_dashboard
from seed_db import create_database

REFERENCE_DEFAULT_DIGEST = "9044e5a579f3c4b0"


class QueryCounter:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def __call__(self, statement: str) -> None:
        self.statements.append(statement)


def is_valid_dashboard(value: dict[str, Any]) -> bool:
    return (
        set(value) == {"filters", "summary", "by_category", "top_articles"}
        and set(value["summary"]) == {
            "article_count",
            "total_views",
            "average_sentiment",
        }
        and len(value["top_articles"]) <= 5
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure the intentionally slow dashboard.")
    parser.add_argument("--db", default="article_dashboard.db")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-01-01")
    parser.add_argument("--category")
    args = parser.parse_args()

    if not Path(args.db).exists():
        create_database(args.db)

    counter = QueryCounter()
    started = time.perf_counter()
    result = build_dashboard(
        args.db,
        args.start,
        args.end,
        args.category,
        trace_callback=counter,
    )
    elapsed = time.perf_counter() - started
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()[:16]

    matches_reference = None
    if (
        args.start == "2025-01-01"
        and args.end == "2026-01-01"
        and args.category is None
    ):
        matches_reference = digest == REFERENCE_DEFAULT_DIGEST

    print(json.dumps(
        {
            "result_correct_shape": is_valid_dashboard(result),
            "result_matches_reference": matches_reference,
            "sql_statement_count": len(counter.statements),
            "elapsed_seconds": round(elapsed, 4),
            "rows_processed": result["summary"]["article_count"],
            "result_digest": digest,
            "summary": result["summary"],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()

