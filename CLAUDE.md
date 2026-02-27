# GitHub MCP Server

GitHub repository management server for the Eviebot MCP gateway.

## What This Is

A FastMCP server that provides GitHub API tools (repos, files, issues, PRs, branches). Runs on `127.0.0.1:3002`, proxied by the gateway at `~/projects/eviebot-MCP-gateway/`.

## Authentication

`GITHUB_TOKEN` fetched from 1Password (`op://Eviebot/GITHUB_TOKEN/credential`) at startup via `scripts/start.sh`. Owner: `EvieHwang`.

## Key Files

- `server.py` — FastMCP entry point, tool registration
- `tools.py` — Tool implementations (11+ tools)
- `github_client.py` — Lazy-init PyGithub wrapper
- `scripts/start.sh` — Startup script that fetches token from 1Password

## Running

```bash
# Production (via launchd):
scripts/start.sh

# Development:
export GITHUB_TOKEN=ghp_...
python server.py  # Starts on 127.0.0.1:3002
pytest             # Run tests
```
