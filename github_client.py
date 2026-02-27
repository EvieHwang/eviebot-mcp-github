"""Lazy-init GitHub client wrapper.

Wraps PyGithub with lazy initialization so the server can start
without a token and return clear errors when tools are invoked.
"""

import os

from github import Github, Auth


class GitHubClientError(Exception):
    """Raised when the GitHub client cannot be used."""


class GitHubClient:
    """Lazy-initializing GitHub API client."""

    def __init__(self):
        self._github: Github | None = None
        self._username: str = "EvieHwang"

    @property
    def github(self) -> Github:
        if self._github is None:
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                raise GitHubClientError(
                    "GITHUB_TOKEN environment variable is not set. "
                    "Cannot access GitHub API."
                )
            self._github = Github(auth=Auth.Token(token))
        return self._github

    @property
    def user(self):
        return self.github.get_user()

    def get_repo(self, repo_name: str):
        """Get a repo by name. Accepts 'owner/repo' or just 'repo' (defaults to user)."""
        if "/" not in repo_name:
            repo_name = f"{self._username}/{repo_name}"
        return self.github.get_repo(repo_name)


# Module-level singleton
client = GitHubClient()
