from __future__ import annotations

import argparse
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

CATEGORIES = ("technology", "markets", "policy", "science", "business")
SOURCES = ("wire", "research", "staff", "partner", "community")
BASE_DATE = date(2025, 1, 1)


def create_database(db_path: str | Path, rows: int = 20_000) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")

    connection = sqlite3.connect(path)
    try:
        connection.executescript("DROP TABLE IF EXISTS articles;\n" + schema)
        records: Iterable[tuple[object, ...]] = (
            (
                article_id,
                f"Article {article_id:05d}",
                CATEGORIES[article_id % len(CATEGORIES)],
                SOURCES[article_id % len(SOURCES)],
                "published" if article_id % 5 else "draft",
                (BASE_DATE + timedelta(days=article_id % 365)).isoformat(),
                100 + ((article_id * 37) % 10_000),
                None if article_id % 11 == 0 else round(((article_id % 200) - 100) / 100, 2),
                300 + ((article_id * 17) % 2_000),
            )
            for article_id in range(1, rows + 1)
        )
        connection.executemany(
            """
            INSERT INTO articles
                (id, title, category, source, status, published_at,
                 views, sentiment, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        connection.commit()
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the deterministic interview database.")
    parser.add_argument("--db", default="article_dashboard.db")
    parser.add_argument("--rows", type=int, default=20_000)
    args = parser.parse_args()
    create_database(args.db, args.rows)
    print(f"Created {args.rows:,} articles in {args.db}")


if __name__ == "__main__":
    main()

