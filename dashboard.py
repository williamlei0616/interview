from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Callable, Iterator

TraceCallback = Callable[[str], None] | None


@contextmanager
def open_connection(db_path: str, trace_callback: TraceCallback = None) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    if trace_callback is not None:
        connection.set_trace_callback(trace_callback)
    try:
        yield connection
    finally:
        connection.close()


def find_article_ids(
    db_path: str,
    start_date: str,
    end_date: str,
    category: str | None,
    trace_callback: TraceCallback = None,
) -> list[int]:
    sql = (
        "SELECT id FROM articles "
        "WHERE status = 'published' AND published_at >= ? AND published_at < ?"
    )
    params: list[Any] = [start_date, end_date]
    if category is not None:
        sql += " AND category = ?"
        params.append(category)

    with open_connection(db_path, trace_callback) as connection:
        return [row["id"] for row in connection.execute(sql, params).fetchall()]


def read_one_article(
    connection: sqlite3.Connection,
    article_id: int,
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM articles WHERE id = ?",
        (article_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def build_summary(
    db_path: str,
    article_ids: list[int],
    trace_callback: TraceCallback = None,
) -> dict[str, Any]:
    count = 0
    total_views = 0
    sentiment_total = 0.0
    sentiment_count = 0

    with open_connection(db_path, trace_callback) as connection:
        for article_id in article_ids:
            article = read_one_article(connection, article_id)
            if article is None:
                continue
            count += 1
            total_views += article["views"]
            if article["sentiment"] is not None:
                sentiment_total += article["sentiment"]
                sentiment_count += 1

    average = sentiment_total / sentiment_count if sentiment_count else None
    return {
        "article_count": count,
        "total_views": total_views,
        "average_sentiment": average,
    }


def build_category_breakdown(
    db_path: str,
    article_ids: list[int],
    trace_callback: TraceCallback = None,
) -> list[dict[str, Any]]:
    categories: dict[str, dict[str, int]] = {}

    with open_connection(db_path, trace_callback) as connection:
        for article_id in article_ids:
            article = read_one_article(connection, article_id)
            if article is None:
                continue
            category = article["category"]
            if category not in categories:
                categories[category] = {"article_count": 0, "total_views": 0}
            categories[category]["article_count"] += 1
            categories[category]["total_views"] += article["views"]

    return [
        {
            "category": category,
            "article_count": values["article_count"],
            "total_views": values["total_views"],
        }
        for category, values in sorted(categories.items())
    ]


def build_top_articles(
    db_path: str,
    article_ids: list[int],
    trace_callback: TraceCallback = None,
) -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []

    with open_connection(db_path, trace_callback) as connection:
        for article_id in article_ids:
            article = read_one_article(connection, article_id)
            if article is None:
                continue
            articles.append(
                {
                    "id": article["id"],
                    "title": article["title"],
                    "category": article["category"],
                    "views": article["views"],
                }
            )

    articles.sort(key=lambda item: (-item["views"], item["id"]))
    return articles[:5]


def build_dashboard(
    db_path: str,
    start_date: str,
    end_date: str,
    category: str | None = None,
    trace_callback: TraceCallback = None,
) -> dict[str, Any]:
    article_ids = find_article_ids(
        db_path,
        start_date,
        end_date,
        category,
        trace_callback,
    )
    summary = build_summary(db_path, article_ids, trace_callback)
    breakdown = build_category_breakdown(db_path, article_ids, trace_callback)
    top_articles = build_top_articles(db_path, article_ids, trace_callback)

    return {
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "category": category,
        },
        "summary": summary,
        "by_category": breakdown,
        "top_articles": top_articles,
    }

