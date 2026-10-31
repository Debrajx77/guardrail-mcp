# Guardrail MCP Demo

A small MCP server that checks submitted text against blocked-term policies stored in SQLite. This is a local demo, not a complete content-safety system.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)

## Set up

```powershell
uv sync
uv run python seed_db.py
```

This creates `.venv/` and `uv.lock`, then generates `guardrail_demo.db` with sample policies.

## Run

```powershell
uv run mcp dev server.py
```

The MCP Inspector opens for testing. Call the `check_text` tool with text to see whether it is allowed or which sample policy matched. The server communicates over stdio when launched by an MCP host.

The workspace MCP configuration is in `.vscode/mcp.json` and launches the server with `uv` after the database has been seeded.
