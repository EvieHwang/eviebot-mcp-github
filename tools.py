"""GitHub MCP tool implementations."""

import base64
import functools

from github import GithubException

from github_client import client, GitHubClientError


def _handle_errors(func):
    """Decorator to catch common GitHub errors."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except GitHubClientError as e:
            return str(e)
        except GithubException as e:
            return f"GitHub API error ({e.status}): {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error: {e}"
    return wrapper


@_handle_errors
async def list_repos(visibility: str = "all") -> str:
    """List repositories for the authenticated user.

    Args:
        visibility: Filter by visibility: 'all', 'public', or 'private'.
    """
    repos = client.user.get_repos(visibility=visibility, sort="updated")
    lines = []
    for repo in repos[:50]:
        vis = "private" if repo.private else "public"
        lang = repo.language or "—"
        desc = repo.description or ""
        if len(desc) > 80:
            desc = desc[:77] + "..."
        lines.append(f"- **{repo.name}** [{vis}] ({lang}) {desc}")

    if not lines:
        return "No repositories found."
    return "\n".join(lines)


@_handle_errors
async def get_repo(repo: str) -> str:
    """Get repository details.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
    """
    r = client.get_repo(repo)
    return (
        f"Name: {r.full_name}\n"
        f"Description: {r.description or '—'}\n"
        f"Visibility: {'private' if r.private else 'public'}\n"
        f"Default branch: {r.default_branch}\n"
        f"Language: {r.language or '—'}\n"
        f"Last updated: {r.updated_at.isoformat()}\n"
        f"URL: {r.html_url}"
    )


@_handle_errors
async def list_files(repo: str, path: str = "", ref: str = "") -> str:
    """List files and directories at a path in a repository.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        path: Path within the repo (default: root).
        ref: Branch or commit ref (default: repo's default branch).
    """
    r = client.get_repo(repo)
    kwargs = {}
    if ref:
        kwargs["ref"] = ref
    contents = r.get_contents(path, **kwargs)

    if not isinstance(contents, list):
        contents = [contents]

    lines = []
    for item in sorted(contents, key=lambda x: (x.type != "dir", x.name.lower())):
        kind = "DIR" if item.type == "dir" else "FILE"
        size = f"  {item.size} bytes" if item.type == "file" else ""
        lines.append(f"[{kind}] {item.name}{size}")

    if not lines:
        return f"Empty directory: {path or '/'}"
    return "\n".join(lines)


@_handle_errors
async def read_file(repo: str, path: str, ref: str = "") -> str:
    """Read a file from a repository.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        path: File path within the repo.
        ref: Branch or commit ref (default: repo's default branch).
    """
    r = client.get_repo(repo)
    kwargs = {}
    if ref:
        kwargs["ref"] = ref
    content = r.get_contents(path, **kwargs)

    if isinstance(content, list):
        return f"Path is a directory, not a file: {path}"

    if content.encoding == "base64":
        try:
            return base64.b64decode(content.content).decode("utf-8")
        except UnicodeDecodeError:
            return (
                f"Binary file: {content.name}\n"
                f"Size: {content.size} bytes\n"
                f"SHA: {content.sha}"
            )

    return content.decoded_content.decode("utf-8")


@_handle_errors
async def write_file(
    repo: str, path: str, content: str, message: str, branch: str = ""
) -> str:
    """Create or update a file in a repository.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        path: File path within the repo.
        content: File content to write.
        message: Commit message.
        branch: Branch name (default: repo's default branch).
    """
    r = client.get_repo(repo)
    kwargs = {}
    if branch:
        kwargs["branch"] = branch

    # Check if file exists to get SHA for update
    try:
        existing = r.get_contents(path, **kwargs)
        if isinstance(existing, list):
            return f"Path is a directory: {path}"
        r.update_file(path, message, content, existing.sha, **kwargs)
        return f"Updated {path} in {r.full_name} (commit: {message})"
    except GithubException as e:
        if e.status == 404:
            r.create_file(path, message, content, **kwargs)
            return f"Created {path} in {r.full_name} (commit: {message})"
        raise


@_handle_errors
async def create_repo(
    name: str,
    description: str = "",
    private: bool = True,
    auto_init: bool = False,
) -> str:
    """Create a new repository.

    Args:
        name: Repository name.
        description: Repository description.
        private: Whether the repo should be private (default: True).
        auto_init: Initialize with a README (default: False).
    """
    r = client.user.create_repo(
        name=name,
        description=description,
        private=private,
        auto_init=auto_init,
    )
    return (
        f"Created repository: {r.full_name}\n"
        f"Visibility: {'private' if r.private else 'public'}\n"
        f"URL: {r.html_url}"
    )


@_handle_errors
async def list_issues(
    repo: str, state: str = "open", labels: str = ""
) -> str:
    """List issues for a repository.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        state: Filter by state: 'open', 'closed', or 'all'.
        labels: Comma-separated label names to filter by.
    """
    r = client.get_repo(repo)
    kwargs = {"state": state}
    if labels:
        kwargs["labels"] = [l.strip() for l in labels.split(",")]

    issues = r.get_issues(**kwargs)
    lines = []
    for issue in issues[:50]:
        if issue.pull_request:
            continue
        label_str = ", ".join(l.name for l in issue.labels) if issue.labels else ""
        label_part = f" [{label_str}]" if label_str else ""
        lines.append(f"#{issue.number} {issue.title}{label_part} ({issue.state})")

    if not lines:
        return f"No issues found in {r.full_name} with state={state}."
    return "\n".join(lines)


@_handle_errors
async def create_issue(
    repo: str,
    title: str,
    body: str = "",
    labels: str = "",
    assignees: str = "",
) -> str:
    """Create a new issue in a repository.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        title: Issue title.
        body: Issue body (supports markdown).
        labels: Comma-separated label names.
        assignees: Comma-separated GitHub usernames to assign.
    """
    r = client.get_repo(repo)
    kwargs = {"title": title}
    if body:
        kwargs["body"] = body
    if labels:
        kwargs["labels"] = [l.strip() for l in labels.split(",")]
    if assignees:
        kwargs["assignees"] = [a.strip() for a in assignees.split(",")]

    issue = r.create_issue(**kwargs)
    return f"Created issue #{issue.number}: {issue.title}\nURL: {issue.html_url}"


@_handle_errors
async def list_prs(repo: str, state: str = "open") -> str:
    """List pull requests for a repository.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        state: Filter by state: 'open', 'closed', or 'all'.
    """
    r = client.get_repo(repo)
    pulls = r.get_pulls(state=state)
    lines = []
    for pr in pulls[:50]:
        lines.append(
            f"#{pr.number} {pr.title} ({pr.state}) "
            f"[{pr.head.ref} -> {pr.base.ref}]"
        )

    if not lines:
        return f"No pull requests found in {r.full_name} with state={state}."
    return "\n".join(lines)


@_handle_errors
async def create_branch(repo: str, branch: str, from_branch: str = "") -> str:
    """Create a new branch in a repository.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        branch: Name for the new branch.
        from_branch: Base branch (default: repo's default branch).
    """
    r = client.get_repo(repo)
    base = from_branch or r.default_branch
    source = r.get_branch(base)
    r.create_git_ref(f"refs/heads/{branch}", source.commit.sha)
    return f"Created branch '{branch}' from '{base}' in {r.full_name}"


@_handle_errors
async def search_code(query: str, repo: str = "") -> str:
    """Search for code across repositories.

    Args:
        query: Search query (code to find).
        repo: Optional repo to scope search to (e.g., 'my-repo' or 'owner/repo').
    """
    if repo:
        if "/" not in repo:
            repo = f"{client._username}/{repo}"
        full_query = f"{query} repo:{repo}"
    else:
        full_query = f"{query} user:{client._username}"

    results = client.github.search_code(full_query)
    lines = []
    for item in results[:20]:
        lines.append(f"- {item.repository.full_name}/{item.path}")

    if not lines:
        return f"No code found matching: {query}"
    return "\n".join(lines)


# --- Stretch tools ---


@_handle_errors
async def get_pr(repo: str, pr_number: int) -> str:
    """Get pull request details.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        pr_number: Pull request number.
    """
    r = client.get_repo(repo)
    pr = r.get_pull(pr_number)
    return (
        f"#{pr.number} {pr.title}\n"
        f"State: {pr.state}\n"
        f"Branch: {pr.head.ref} -> {pr.base.ref}\n"
        f"Author: {pr.user.login}\n"
        f"Mergeable: {pr.mergeable}\n"
        f"Additions: +{pr.additions} Deletions: -{pr.deletions} Files: {pr.changed_files}\n"
        f"URL: {pr.html_url}"
    )


@_handle_errors
async def merge_pr(
    repo: str, pr_number: int, merge_method: str = "squash"
) -> str:
    """Merge a pull request.

    Args:
        repo: Repository name (e.g., 'my-repo' or 'owner/repo').
        pr_number: Pull request number.
        merge_method: Merge strategy: 'merge', 'squash', or 'rebase'.
    """
    r = client.get_repo(repo)
    pr = r.get_pull(pr_number)
    result = pr.merge(merge_method=merge_method)
    if result.merged:
        return f"Merged PR #{pr_number} via {merge_method}: {result.message}"
    return f"Failed to merge PR #{pr_number}: {result.message}"
