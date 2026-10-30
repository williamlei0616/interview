from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from dashboard import build_dashboard
from seed_db import create_database


ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db_path = ROOT / "test_fixture.db"
        if self.db_path.exists():
            self.db_path.unlink()
        connection = sqlite3.connect(self.db_path)
        connection.executescript(
            """
            CREATE TABLE articles (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                published_at TEXT NOT NULL,
                views INTEGER NOT NULL,
                sentiment REAL,
                word_count INTEGER NOT NULL
            );
            INSERT INTO articles VALUES
                (1, 'Alpha', 'technology', 'wire', 'published', '2025-01-01', 10, 0.5, 500),
                (2, 'Beta', 'technology', 'wire', 'published', '2025-01-02', 20, NULL, 600),
                (3, 'Draft', 'technology', 'wire', 'draft', '2025-01-03', 999, 0.9, 700),
                (4, 'Delta', 'finance', 'research', 'published', '2025-02-01', 20, -0.5, 800),
                (5, 'Echo', 'technology', 'staff', 'published', '2025-03-01', 30, 0.1, 900);
            """
        )
        connection.commit()
        connection.close()

    def tearDown(self) -> None:
        for name in ("test_fixture.db", "seeded.db"):
            path = ROOT / name
            if path.exists():
                path.unlink()

    def test_dashboard_contract_and_aggregates(self) -> None:
        result = build_dashboard(
            str(self.db_path),
            "2025-01-01",
            "2025-03-01",
        )

        self.assertEqual(result["summary"]["article_count"], 3)
        self.assertEqual(result["summary"]["total_views"], 50)
        self.assertEqual(result["summary"]["average_sentiment"], 0.0)
        self.assertEqual(
            result["by_category"],
            [
                {"category": "finance", "article_count": 1, "total_views": 20},
                {"category": "technology", "article_count": 2, "total_views": 30},
            ],
        )
        self.assertEqual(
            [article["id"] for article in result["top_articles"]],
            [2, 4, 1],
        )

    def test_end_date_is_exclusive_and_category_is_optional(self) -> None:
        result = build_dashboard(
            str(self.db_path),
            "2025-01-01",
            "2025-03-01",
            category="technology",
        )

        self.assertEqual(result["filters"]["category"], "technology")
        self.assertEqual(result["summary"]["article_count"], 2)
        self.assertEqual(result["summary"]["total_views"], 30)
        self.assertEqual([item["id"] for item in result["top_articles"]], [2, 1])

    def test_seed_creates_requested_number_of_rows(self) -> None:
        seeded_path = ROOT / "seeded.db"
        create_database(seeded_path, rows=20_000)
        connection = sqlite3.connect(seeded_path)
        count = connection.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        connection.close()
        self.assertEqual(count, 20_000)


if __name__ == "__main__":
    unittest.main()

