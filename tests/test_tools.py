"""Tests for GitHub MCP tools."""

import asyncio
import os
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from github_client import GitHubClient, GitHubClientError


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestGitHubClient:
    def test_no_token_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            c = GitHubClient()
            with pytest.raises(GitHubClientError, match="GITHUB_TOKEN"):
                _ = c.github

    def test_get_repo_adds_owner(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake"}):
            c = GitHubClient()
            with patch.object(c, "_github") as mock_gh:
                mock_gh.get_repo = MagicMock()
                # Need to set _github so it doesn't try to init
                c._github = mock_gh
                c.get_repo("my-repo")
                mock_gh.get_repo.assert_called_with("EvieHwang/my-repo")

    def test_get_repo_full_name(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake"}):
            c = GitHubClient()
            mock_gh = MagicMock()
            c._github = mock_gh
            c.get_repo("other/repo")
            mock_gh.get_repo.assert_called_with("other/repo")


class TestToolErrorHandling:
    def test_list_repos_without_token(self):
        """Tools should return an error string when no token is set."""
        with patch.dict(os.environ, {}, clear=True):
            # Re-import to get fresh client
            import importlib
            import github_client
            importlib.reload(github_client)
            import tools
            importlib.reload(tools)

            result = run(tools.list_repos())
            assert "GITHUB_TOKEN" in result
