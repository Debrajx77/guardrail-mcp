import sqlite3
from pathlib import Path

from mcp.server import MCPServer


DATABASE_PATH = Path(__file__).with_name("guardrail_demo.db")
mcp = MCPServer("Guardrail Demo")


def load_blocked_terms() -> list[tuple[str, str]]:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Demo database not found. Run `uv run python seed_db.py` first."
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        return connection.execute(
            "SELECT term, reason FROM blocked_terms ORDER BY term"
        ).fetchall()


@mcp.tool()
def check_text(text: str) -> str:
    """Check text against the demo database's blocked-term policies."""
    lowered_text = text.casefold()
    matches = [
        f"{term} ({reason})"
        for term, reason in load_blocked_terms()
        if term.casefold() in lowered_text
    ]

    if matches:
        return "BLOCKED: " + "; ".join(matches)
    return "ALLOWED: no blocked terms matched."


if __name__ == "__main__":
    mcp.run()