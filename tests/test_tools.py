"""Tests for GitHub MCP tools."""

import asyncio
import os
from unittest.mock import MagicMock, patch

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


class TestGetIssue:
    """Tests for get_issue and update_issue tools."""

    @pytest.fixture(autouse=True)
    def _import_tools(self):
        import tools

        self.tools = tools

    def test_returns_issue_details(self):
        mock_label = MagicMock()
        mock_label.name = "bug"
        mock_assignee = MagicMock()
        mock_assignee.login = "EvieHwang"

        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_issue.title = "Add get_issue tool"
        mock_issue.state = "open"
        mock_issue.labels = [mock_label]
        mock_issue.assignees = [mock_assignee]
        mock_issue.comments = 2
        mock_issue.created_at.isoformat.return_value = "2026-02-27T00:00:00"
        mock_issue.updated_at.isoformat.return_value = "2026-02-27T01:00:00"
        mock_issue.html_url = "https://github.com/EvieHwang/repo/issues/1"
        mock_issue.body = "We need this tool."

        mock_repo = MagicMock()
        mock_repo.get_issue.return_value = mock_issue

        with patch("tools.client") as mock_client:
            mock_client.get_repo.return_value = mock_repo
            result = run(self.tools.get_issue("repo", 1))

        assert "#1 Add get_issue tool" in result
        assert "State: open" in result
        assert "bug" in result
        assert "EvieHwang" in result
        assert "We need this tool." in result

    def test_issue_not_found(self):
        from github import GithubException

        mock_repo = MagicMock()
        mock_repo.get_issue.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )

        with patch("tools.client") as mock_client:
            mock_client.get_repo.return_value = mock_repo
            result = run(self.tools.get_issue("repo", 999))

        assert "404" in result


class TestUpdateIssue:
    @pytest.fixture(autouse=True)
    def _import_tools(self):
        import tools

        self.tools = tools

    def test_closes_issue(self):
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_issue.title = "Some issue"
        mock_issue.state = "closed"
        mock_issue.html_url = "https://github.com/EvieHwang/repo/issues/1"

        mock_repo = MagicMock()
        mock_repo.get_issue.return_value = mock_issue

        with patch("tools.client") as mock_client:
            mock_client.get_repo.return_value = mock_repo
            result = run(self.tools.update_issue("repo", 1, state="closed"))

        mock_issue.edit.assert_called_once_with(state="closed")
        assert "Updated issue #1" in result

    def test_update_multiple_fields(self):
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_issue.title = "New title"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/EvieHwang/repo/issues/1"

        mock_repo = MagicMock()
        mock_repo.get_issue.return_value = mock_issue

        with patch("tools.client") as mock_client:
            mock_client.get_repo.return_value = mock_repo
            result = run(
                self.tools.update_issue(
                    "repo", 1, title="New title", labels="bug, urgent"
                )
            )

        mock_issue.edit.assert_called_once_with(
            title="New title", labels=["bug", "urgent"]
        )
        assert "Updated issue #1" in result

    def test_no_fields_returns_message(self):
        mock_issue = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_issue.return_value = mock_issue

        with patch("tools.client") as mock_client:
            mock_client.get_repo.return_value = mock_repo
            result = run(self.tools.update_issue("repo", 1))

        mock_issue.edit.assert_not_called()
        assert "No fields to update" in result
