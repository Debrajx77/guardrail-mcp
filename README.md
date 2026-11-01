Guardrail MCP — Policy Check Server
A production-inspired Model Context Protocol (MCP) server that validates submitted text against a SQLite-backed blocked-term policy store. Built to demonstrate resilient AI integration: when the data source fails, the server degrades gracefully instead of crashing the conversation.

🎯 Problem Statement
Most MCP demo servers wrap clean, always-available APIs. Real enterprise systems fail. When an LLM agent calls a tool and the backend is down, the default behavior is a traceback — which corrupts the conversation and leaves the user with an unintelligible error.

Guardrail solves this by inserting a resilience layer between the LLM and the data source. The AI host never sees a crash; it receives a structured, actionable degradation message it can relay to the user.

✨ Key Features
MCP-compliant stdio server — built on the official Python SDK (FastMCP). Exposes a check_text tool that the AI host can invoke.

SQLite-backed policy engine — queries a local blocked_terms table to match submitted text against configured policies.

Resilience layer — all database operations are wrapped in a structured try/except. When the database is unreachable, the server returns a user-readable degradation message instead of throwing a traceback.

Protocol-safe logging — all logs are routed to stderr, ensuring the JSON-RPC stream on stdout remains uncorrupted.

VS Code MCP client verified — tested end-to-end in VS Code's native MCP client (Agent mode) after bypassing a known Claude Desktop MSIX configuration bug.

🏗️ Architecture
text
┌─────────────────────┐
│ AI Host │ (VS Code Copilot Agent Mode / Claude Desktop)
└──────────┬──────────┘
│ JSON-RPC over stdio
▼
┌─────────────────────┐
│ server.py │ FastMCP protocol layer
│ @mcp.tool() │ → check_text(text)
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Resilience Layer │ try/except → degraded message on failure
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ guardrail_demo.db │ SQLite: blocked_terms table
└─────────────────────┘
🚀 Setup
Prerequisites
Python 3.11 or newer

uv package manager

Installation
bash

# Clone the repository

git clone https://github.com/Debrajx77/guardrail-mcp.git
cd guardrail-mcp

# Install dependencies

uv sync

# Seed the SQLite database

uv run python seed_db.py
This creates .venv/, uv.lock, and guardrail_demo.db with sample blocked-term policies.

🧪 Testing
Option 1: MCP Inspector (Browser-based)
bash
uv run mcp dev server.py
Opens the MCP Inspector. Navigate to the Tools tab, select check_text, and submit text. You will see either ALLOWED or BLOCKED: <matched term>.

Option 2: VS Code MCP Client (Recommended for local development)
The repository includes a .vscode/mcp.json configuration. Open it in VS Code, click the Start CodeLens, then switch Copilot Chat to Agent mode. The check_text tool will be available.

Resilience Test
To verify graceful degradation:

Rename guardrail_demo.db to guardrail_demo.db.bak

Invoke check_text again

The server should return "Policy check is temporarily degraded..." instead of a traceback

Restore the database file

📁 Project Structure
File Purpose
server.py MCP server — tools, logging, resilience layer
seed_db.py One-time database seeding script
guardrail_demo.db SQLite database (generated)
manifest.json MCPB bundle manifest for extension packaging
.vscode/mcp.json VS Code MCP client configuration
pyproject.toml Dependencies and project metadata
🔧 Technical Decisions
Why try/except instead of a retry library?
The demo prioritizes clarity over configurability. The try/except block makes the degradation path explicit and easy to audit. In production, this would be replaced by a circuit breaker with exponential backoff.

Why SQLite?
SQLite provides a real, queryable data source with zero infrastructure overhead. It lets the project demonstrate the full LLM → MCP tool → database → response data flow without requiring a running database server.

Why stderr logging?
MCP's stdio transport uses stdout exclusively for JSON-RPC messages. Any print() or stdout log corrupts the protocol stream. All application logs are routed to stderr via Python's logging module.

🐛 Known Issues
Claude Desktop (MSIX version): The Windows MSIX distribution has a confirmed configuration virtualization bug that silently ignores claude_desktop_config.json. The .mcpb extension installation is also affected by a regression in version 2.37337.1. The VS Code MCP client is the recommended workaround.

Full-table scan: check_text fetches all blocked terms and matches in Python. For large policy sets, this should be moved to a SQL WHERE clause with an indexed column.

📄 License
MIT
