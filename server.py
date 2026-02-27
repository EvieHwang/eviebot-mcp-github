from fastmcp import FastMCP

from tools import (
    create_branch,
    create_issue,
    create_repo,
    get_pr,
    get_repo,
    list_files,
    list_issues,
    list_prs,
    list_repos,
    merge_pr,
    read_file,
    search_code,
    write_file,
)

mcp = FastMCP(
    name="GitHub",
    instructions=(
        "Manage GitHub repositories for EvieHwang. "
        "Use list_repos to browse repos, read_file/write_file for repo content, "
        "list_issues/create_issue for issue management, list_prs for pull requests. "
        "Repo names can be 'repo-name' (defaults to EvieHwang) or 'owner/repo'."
    ),
)

READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}

WRITE = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}

mcp.tool(annotations=READ_ONLY)(list_repos)
mcp.tool(annotations=READ_ONLY)(get_repo)
mcp.tool(annotations=READ_ONLY)(list_files)
mcp.tool(annotations=READ_ONLY)(read_file)
mcp.tool(annotations=WRITE)(write_file)
mcp.tool(annotations=WRITE)(create_repo)
mcp.tool(annotations=READ_ONLY)(list_issues)
mcp.tool(annotations=WRITE)(create_issue)
mcp.tool(annotations=READ_ONLY)(list_prs)
mcp.tool(annotations=WRITE)(create_branch)
mcp.tool(annotations=READ_ONLY)(search_code)
mcp.tool(annotations=READ_ONLY)(get_pr)
mcp.tool(annotations=WRITE)(merge_pr)

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=3002,
    )
