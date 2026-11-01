# Guardrail MCP Server

A local MCP (Model Context Protocol) server that checks submitted text against blocked-term policies stored in SQLite. Built with Python and the official MCP SDK.

## Features

- **MCP-compliant server** — exposes a `check_text` tool over stdio transport
- **SQLite-backed policies** — blocked terms and reasons stored in a local database
- **Graceful degradation** — returns a structured "temporarily degraded" message when the database is unreachable, instead of crashing the conversation
- **stderr logging** — all logs go to stderr, keeping stdout clean for JSON-RPC protocol messages
- **VS Code MCP client compatible** — tested with GitHub Copilot Agent mode

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

```bash
uv sync
uv run python seed_db.py
```

This creates `.venv/`, installs dependencies, and generates `guardrail_demo.db` with sample blocked-term policies.

## Run

### Option 1: MCP Inspector (local testing)

```bash
uv run mcp dev server.py
```

Opens the MCP Inspector in your browser. Call the `check_text` tool with sample text to verify allowed/blocked behavior.

### Option 2: VS Code MCP Client

Add the following to `.vscode/mcp.json`:

```json
{
  "servers": {
    "guardrail": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "${workspaceFolder}",
        "python",
        "server.py"
      ]
    }
  }
}
```

Open Copilot Chat in **Agent mode**, then prompt:

> Check this text: this is a test message

## Tool Reference

### `check_text(text: str) -> str`

Checks the submitted text against blocked-term policies stored in SQLite.

**Returns:**

- `ALLOWED: no blocked terms matched.` — no policy violation
- `BLOCKED: <term> (<reason>)` — one or more blocked terms matched
- `Policy check is temporarily degraded...` — database unavailable (resilience fallback)

## Resilience Behavior

The server wraps all database operations in a `try/except` block. If SQLite is unreachable (missing file, locked, corrupted), the tool returns a user-readable degraded message instead of raising an exception. This prevents the AI conversation from crashing and lets the model relay a meaningful status to the user.

To verify:

1. Rename `guardrail_demo.db` to `guardrail_demo.db.bak`
2. Call `check_text` — expect the degraded message, not a traceback
3. Restore the file and confirm normal operation resumes

## Project Structure

```
guardrail-mcp/
├── server.py              # MCP server (FastMCP, tools, resilience)
├── seed_db.py             # Database seeding script
├── guardrail_demo.db      # SQLite database (generated)
├── pyproject.toml         # Dependencies and project metadata
├── manifest.json          # MCPB packaging manifest
├── .vscode/mcp.json       # VS Code MCP client config
└── README.md
```

## Tech Stack

| Layer     | Technology                  |
| --------- | --------------------------- |
| Protocol  | MCP Python SDK (`mcp[cli]`) |
| Transport | stdio                       |
| Data      | SQLite (`sqlite3`)          |
| Logging   | Python `logging` → stderr   |

## Live Deployment

The server is deployed on Render and accessible at:
`https://guardrail-mcp.onrender.com/mcp`

Test with a Python client:

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
# ... (test code)

## Notes

- This is a local demo, not a production content-safety system.
- The server communicates over stdio when launched by an MCP host.
- `manifest.json` and the `.mcpb` bundle are included for extension packaging, but the primary tested path is the VS Code MCP client.
```
