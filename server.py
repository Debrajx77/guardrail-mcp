import sqlite3
import logging
import sys
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# --- Logging: MUST go to stderr ---
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("guardrail")

DATABASE_PATH = Path(__file__).with_name("guardrail_demo.db")
port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Guardrail Demo", host="127.0.0.1", port=8000)


@mcp.tool()
def check_text(text: str) -> str:
    """Check submitted text against blocked-term policies."""
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT term, reason FROM blocked_terms"
            )
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Database failure: {e}")
        return (
            "Policy check is temporarily degraded. "
            "Could not reach the policy database. Please try again later."
        )

    lowered = text.casefold()
    matches = [
        f"{term} ({reason})"
        for term, reason in rows
        if term.casefold() in lowered
    ]

    if matches:
        return "BLOCKED: " + "; ".join(matches)
    return "ALLOWED: no blocked terms matched."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")