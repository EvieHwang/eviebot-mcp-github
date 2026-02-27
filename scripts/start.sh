#!/usr/bin/env bash
set -euo pipefail

export PATH="/opt/homebrew/bin:$PATH"

# Fetch GitHub token from 1Password
export GITHUB_TOKEN=$(op read "op://Eviebot/GITHUB_TOKEN/credential")

# Start the server
exec /Users/evehwang/projects/eviebot-mcp-github/.venv/bin/python3 server.py
