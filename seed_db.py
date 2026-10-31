import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("guardrail_demo.db")
DEFAULT_BLOCKED_TERMS = (
    ("password", "Credential disclosure"),
    ("secret key", "Credential disclosure"),
    ("social security number", "Sensitive personal information"),
)


def seed_database() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS blocked_terms (
                term TEXT PRIMARY KEY,
                reason TEXT NOT NULL
            )
            """
        )
        connection.executemany(
            "INSERT OR IGNORE INTO blocked_terms (term, reason) VALUES (?, ?)",
            DEFAULT_BLOCKED_TERMS,
        )


if __name__ == "__main__":
    seed_database()
    print(f"Seeded demo policies in {DATABASE_PATH}")