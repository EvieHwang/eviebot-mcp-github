# eviebot-mcp-github

MCP server for GitHub API access. Runs as a backend behind the [Eviebot MCP Gateway](https://github.com/EvieHwang/eviebot-MCP-gateway).

## Tools

| Tool | Description |
|------|-------------|
| `list_repos` | List repositories for a user |
| `get_repo` | Get repo details (description, stars, language, default branch) |
| `list_files` | List files in a repo directory |
| `read_file` | Read a file from a repo |
| `write_file` | Create or update a file in a repo |
| `create_repo` | Create a new repository |
| `list_issues` | List issues with optional state/label filters |
| `get_issue` | Get issue details (state, labels, assignees, body) |
| `create_issue` | Create a new issue |
| `update_issue` | Update an issue (title, body, state, labels, assignees) |
| `list_prs` | List pull requests |
| `get_pr` | Get PR details including diff stats |
| `merge_pr` | Merge a pull request |
| `create_branch` | Create a new branch |
| `search_code` | Search code across repos |

Repo names accept `owner/repo` or just `repo` (defaults to `EvieHwang`).

## Auth

`GITHUB_TOKEN` is fetched from 1Password at service start via `scripts/start.sh`. The token is stored at `op://Eviebot/GITHUB_TOKEN/credential`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

Runs as a launchd service (`com.evie.github-mcp`) on port 3002. The gateway proxies it under the `github` namespace.

```bash
# Manual start
export GITHUB_TOKEN=<token>
python server.py

# Service management
launchctl kickstart -k gui/$(id -u)/com.evie.github-mcp
```

## Tests

```bash
pytest
```
