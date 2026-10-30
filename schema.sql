CREATE TABLE IF NOT EXISTS articles (
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

